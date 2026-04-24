from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator
from typing import Optional, List
from dotenv import load_dotenv

load_dotenv()

_DEFAULT_JWT_SECRET = "your-secret-key-change-in-production"

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True, extra='ignore')
    
    # Database
    DATABASE_URL: str = "mysql://root:password@localhost:3306/quotmate"
    
    @model_validator(mode='after')
    def clean_database_url(self):
        if self.DATABASE_URL:
            # SQLAlchemy/PyMySQL does not accept ?ssl-mode=REQUIRED in the query string
            if "?ssl-mode=" in self.DATABASE_URL:
                self.DATABASE_URL = self.DATABASE_URL.split("?")[0]
            # Ensure pymysql driver is used if just mysql:// is provided
            if self.DATABASE_URL.startswith("mysql://"):
                self.DATABASE_URL = self.DATABASE_URL.replace("mysql://", "mysql+pymysql://", 1)
        return self
    
    # Authentication
    JWT_SECRET: str = _DEFAULT_JWT_SECRET
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_HOURS: int = 24
    
    # App
    APP_NAME: str = "QuotMate API"
    DEBUG: bool = True
    
    # CORS
    ALLOWED_ORIGINS: str = "http://localhost:3000,http://localhost:5173"
    
    # NVIDIA NIMs
    NVIDIA_API_KEY: Optional[str] = None
    
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "ap-south-1"
    S3_BUCKET_NAME: Optional[str] = None
    
    # Cloudinary
    CLOUDINARY_CLOUD_NAME: Optional[str] = None
    CLOUDINARY_API_KEY: Optional[str] = None
    CLOUDINARY_API_SECRET: Optional[str] = None
    
    @model_validator(mode="after")
    def _validate_jwt_secret(self):
        if self.JWT_SECRET == _DEFAULT_JWT_SECRET and not self.DEBUG:
            raise ValueError(
                "JWT_SECRET must be changed from the default value in production. "
                "Set a strong, unique JWT_SECRET in your .env file."
            )
        return self
    
    @property
    def allowed_origins_list(self) -> List[str]:
        """Parse comma-separated ALLOWED_ORIGINS into a list."""
        return [o.strip() for o in self.ALLOWED_ORIGINS.split(",") if o.strip()]

settings = Settings()

