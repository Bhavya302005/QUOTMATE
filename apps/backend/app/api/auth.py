from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func
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
    get_current_user
)
from app.services.audit_service import log_audit
from app.utils.file_upload import file_upload_service
import uuid
import logging

router = APIRouter(prefix="/api/auth", tags=["Authentication"])
logger = logging.getLogger("quotmate.auth")


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
        user=UserResponse.from_orm(user)
    )


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user's profile
    
    Requires valid JWT token in Authorization header:
    `Authorization: Bearer <token>`
    """
    return UserResponse.from_orm(current_user)


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
    - **company_logo_url**: Update company logo URL
    """
    # Store old values for audit log
    old_values = {
        "email": current_user.email,
        "full_name": current_user.full_name,
        "company_name": current_user.company_name,
        "phone": current_user.phone,
        "address": current_user.address,
        "gst_number": current_user.gst_number,
        "company_logo_url": current_user.company_logo_url,
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
        "company_logo_url": current_user.company_logo_url,
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
    
    return UserResponse.from_orm(current_user)


@router.post("/upload-logo", response_model=UserResponse)
async def upload_company_logo(
    request: Request,
    file: UploadFile = File(..., description="Company logo image"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Upload company logo image and save URL in current user's profile.

    Accepts common image formats (jpg, jpeg, png, gif, bmp, tiff, webp).
    """
    is_valid, error_msg = file_upload_service.validate_image_file(file)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error_msg
        )

    _, file_url = await file_upload_service.save_upload_file(file, "images")
    old_logo_url = current_user.company_logo_url
    current_user.company_logo_url = file_url

    db.commit()
    db.refresh(current_user)

    log_audit(
        db=db,
        user_id=current_user.id,
        action="upload_logo",
        entity_type="user",
        entity_id=current_user.id,
        old_value={"company_logo_url": old_logo_url},
        new_value={"company_logo_url": file_url},
        ip_address=request.client.host if request.client else None
    )

    return UserResponse.from_orm(current_user)
