from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Query
from fastapi.responses import Response, RedirectResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    UserRegister,
    UserLogin,
    UserProfileUpdate,
    UserResponse,
    LoginResponse,
    RegisterResponse
)
from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
    get_current_user,
    decode_token,
)
from app.services.audit_service import log_audit
from app.utils.file_upload import file_upload_service
from app.utils.logo_storage import (
    get_logo_bytes,
    is_durable_external_url,
    migrate_legacy_logo,
    set_user_logo,
    user_has_logo,
    verify_logo_saved,
)
import uuid
import logging

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
logger = logging.getLogger("quotmate.auth")
optional_bearer = HTTPBearer(auto_error=False)


def user_to_response(user: User, db: Session) -> UserResponse:
    """Build API user payload; migrates legacy logo formats when needed."""
    migrate_legacy_logo(user, db)
    external_url = None
    if not user.company_logo_data and is_durable_external_url(user.company_logo_url):
        external_url = user.company_logo_url

    return UserResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        company_name=user.company_name,
        phone=user.phone,
        address=user.address,
        gst_number=user.gst_number,
        company_logo_url=external_url,
        has_company_logo=user_has_logo(user),
        default_terms_conditions=user.default_terms_conditions,
        is_admin=user.is_admin,
        created_at=user.created_at,
        updated_at=user.updated_at,
    )


def _normalize_email(email: str) -> str:
    """Normalize email input for consistent auth lookups."""
    return email.strip().lower()


def _verify_with_legacy_fallback(user: User, input_password: str) -> bool:
    """
    Verify password with backwards-compatible fallbacks.

    Supports:
    - normal bcrypt check
    - accidental leading/trailing whitespace in user input
    - legacy plain-text stored password hashes (auto-migrated on success)
    """
    candidate_passwords = [input_password]
    stripped = input_password.strip()
    if stripped != input_password:
        candidate_passwords.append(stripped)

    # Primary path: bcrypt hash verification
    for candidate in candidate_passwords:
        try:
            if verify_password(candidate, user.password_hash):
                return True
        except Exception:
            # Keep trying compatibility paths below.
            pass

    # Legacy path: stored plain-text password (self-heal to bcrypt)
    for candidate in candidate_passwords:
        if user.password_hash == candidate:
            user.password_hash = hash_password(candidate)
            return True

    return False


def _find_login_user(db: Session, normalized_email: str, input_password: str) -> User | None:
    """
    Find the correct login user among normalized-email variants.

    This handles legacy rows where the same logical email may exist in multiple
    case/whitespace forms and ensures we authenticate the matching record.
    """
    candidates = db.query(User).filter(
        func.lower(func.trim(User.email)) == normalized_email
    ).all()

    if not candidates:
        return None

    # Prefer exact normalized row first for predictable behavior.
    candidates.sort(key=lambda u: 0 if u.email == normalized_email else 1)

    for user in candidates:
        if _verify_with_legacy_fallback(user, input_password):
            if user.email != normalized_email:
                user.email = normalized_email
                logger.info("login_email_normalized user_id=%s", user.id)
            return user

    return None


@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserRegister,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    
    - **email**: Valid email address (must be unique)
    - **password**: Minimum 8 characters, must contain letters and digits
    - **full_name**: User's full name
    - **company_name**: Optional company name
    - **phone**: Optional phone number
    """
    normalized_email = _normalize_email(user_data.email)

    # Check if email already exists
    existing_user = db.query(User).filter(User.email == normalized_email).first()
    if existing_user:
        logger.warning("register_failed_email_exists email=%s", normalized_email)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)
    
    new_user = User(
        id=user_id,
        email=normalized_email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        company_name=user_data.company_name,
        phone=user_data.phone,
        gst_number=user_data.gst_number,
        is_admin=False
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Log registration
    log_audit(
        db=db,
        user_id=user_id,
        action="register",
        entity_type="user",
        entity_id=user_id,
        ip_address=request.client.host if request.client else None
    )
    
    return RegisterResponse(
        user_id=user_id,
        message="User registered successfully",
        email=normalized_email
    )


@router.post("/login", response_model=LoginResponse)
async def login(
    credentials: UserLogin,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Login with email and password to receive JWT access token
    
    - **email**: Registered email address
    - **password**: User's password
    
    Returns JWT token valid for 24 hours
    """
    normalized_email = _normalize_email(credentials.email)

    # Find correct user across normalized-email variants and verify password.
    user = _find_login_user(db, normalized_email, credentials.password)
    if not user:
        logger.warning("login_failed_invalid_credentials email=%s", normalized_email)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    # Persist any login-time self-healing (legacy email/password normalization).
    db.commit()
    db.refresh(user)
    
    # Create access token
    access_token = create_access_token(data={"sub": user.id, "email": user.email})
    
    # Log login
    log_audit(
        db=db,
        user_id=user.id,
        action="login",
        entity_type="user",
        entity_id=user.id,
        ip_address=request.client.host if request.client else None
    )
    logger.info("login_success user_id=%s email=%s", user.id, normalized_email)
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user=user_to_response(user, db),
    )


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get current user's profile
    
    Requires valid JWT token in Authorization header:
    `Authorization: Bearer <token>`
    """
    return user_to_response(current_user, db)


@router.get("/company-logo")
async def get_company_logo(
    access_token: Optional[str] = Query(None),
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(optional_bearer),
    db: Session = Depends(get_db),
):
    """
    Serve the authenticated user's company logo as image bytes.

    Accepts Bearer header or ?access_token= query param (for <img> tags).
    """
    raw_token = access_token or (credentials.credentials if credentials else None)
    if not raw_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required",
        )

    payload = decode_token(raw_token)
    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    migrate_legacy_logo(user, db)
    stored = get_logo_bytes(user)
    if stored:
        mime, data = stored
        return Response(
            content=data,
            media_type=mime,
            headers={"Cache-Control": "private, max-age=86400"},
        )

    if is_durable_external_url(user.company_logo_url):
        return RedirectResponse(url=user.company_logo_url, status_code=307)

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="No company logo",
    )


@router.put("/profile", response_model=UserResponse)
async def update_profile(
    profile_data: UserProfileUpdate,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    
    Requires valid JWT token. Only updates provided fields.
    
    - **full_name**: Update user's full name
    - **company_name**: Update company name
    - **phone**: Update phone number
    - **address**: Update address
    - **gst_number**: Update GST number (15 characters)
    Logo changes use POST /auth/upload-logo only.
    """
    # Store old values for audit log
    old_values = {
        "email": current_user.email,
        "full_name": current_user.full_name,
        "company_name": current_user.company_name,
        "phone": current_user.phone,
        "address": current_user.address,
        "gst_number": current_user.gst_number,
        "default_terms_conditions": current_user.default_terms_conditions
    }
    
    # Update only provided fields
    update_data = profile_data.dict(exclude_unset=True)
    if "email" in update_data and update_data["email"] != current_user.email:
        normalized_update_email = _normalize_email(update_data["email"])
        existing = db.query(User).filter(User.email == normalized_update_email).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already taken")
        update_data["email"] = normalized_update_email
            
    for field, value in update_data.items():
        setattr(current_user, field, value)
    
    db.commit()
    db.refresh(current_user)
    
    # Store new values for audit log
    new_values = {
        "email": current_user.email,
        "full_name": current_user.full_name,
        "company_name": current_user.company_name,
        "phone": current_user.phone,
        "address": current_user.address,
        "gst_number": current_user.gst_number,
        "default_terms_conditions": current_user.default_terms_conditions
    }
    
    # Log profile update
    log_audit(
        db=db,
        user_id=current_user.id,
        action="update_profile",
        entity_type="user",
        entity_id=current_user.id,
        old_value=old_values,
        new_value=new_values,
        ip_address=request.client.host if request.client else None
    )
    
    return user_to_response(current_user, db)


@router.post("/upload-logo", response_model=UserResponse)
async def upload_company_logo(
    request: Request,
    file: UploadFile = File(..., description="Company logo image"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload company logo image and persist it in the database.

    Accepts common image formats (jpg, jpeg, png, gif, bmp, tiff, webp).
    """
    is_valid, error_msg = file_upload_service.validate_image_file(file)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    file_bytes = await file.read()
    had_logo = user_has_logo(current_user)

    try:
        _mime, data = set_user_logo(current_user, file_bytes)
        db.commit()
        db.refresh(current_user)
        verify_logo_saved(current_user, len(data))
    except ValueError as e:
        db.rollback()
        logger.error("Logo persistence check failed: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) from e
    except Exception as e:
        db.rollback()
        logger.error("Error saving logo: %s", e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not process logo image. Try JPG or PNG under 5MB.",
        ) from e

    log_audit(
        db=db,
        user_id=current_user.id,
        action="upload_logo",
        entity_type="user",
        entity_id=current_user.id,
        old_value={"had_logo": had_logo},
        new_value={"had_logo": True, "bytes": len(current_user.company_logo_data or b"")},
        ip_address=request.client.host if request.client else None
    )

    return user_to_response(current_user, db)
