from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File
from sqlalchemy.orm import Session
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

router = APIRouter(prefix="/api/auth", tags=["Authentication"])


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
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new user
    user_id = str(uuid.uuid4())
    hashed_password = hash_password(user_data.password)
    
    new_user = User(
        id=user_id,
        email=user_data.email,
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
        email=user_data.email
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
    # Find user by email
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Verify password
    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
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
        existing = db.query(User).filter(User.email == update_data["email"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Email already taken")
            
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
    absolute_logo_url = f"{str(request.base_url).rstrip('/')}{file_url}"

    old_logo_url = current_user.company_logo_url
    current_user.company_logo_url = absolute_logo_url

    db.commit()
    db.refresh(current_user)

    log_audit(
        db=db,
        user_id=current_user.id,
        action="upload_logo",
        entity_type="user",
        entity_id=current_user.id,
        old_value={"company_logo_url": old_logo_url},
        new_value={"company_logo_url": absolute_logo_url},
        ip_address=request.client.host if request.client else None
    )

    return UserResponse.from_orm(current_user)
