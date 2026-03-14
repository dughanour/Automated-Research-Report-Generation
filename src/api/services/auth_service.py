              # Business logic for authentication #
from typing import Optional
from sqlalchemy.orm import Session
from src.api.models.auth_model import LoginRequest, LoginResponse, RegisterRequest
from src.api.repositories.user_repository import UserRepository
from src.utils.security import verify_password, create_access_token, hash_password
from src.exceptions.custom_exception import CustomException
from src.logger import GLOBAL_LOGGER as log

class AuthService:
    """Handles all authentication logic."""
    def __init__(self, db: Session):
        self.repository = UserRepository(db)
    
    def login(self, credentials: LoginRequest) -> Optional[LoginResponse]:
        """
        Authenticate user and return token.
        Returns None if credentials invalid.
        """
        try:
            log.info("Login attempt", email=credentials.email)

            # 1. Find user in database
            user = self.repository.get_user_by_email(credentials.email)
            if not user:
                log.warning("Login failed - user not found", email=credentials.email)
                return None
            
            # 2. Verify password
            if not verify_password(credentials.password, user.hashed_password):
                log.warning("Login failed - invalid password", email=credentials.email)
                return None

            # 3. Generate JWT token
            access_token = create_access_token(data={"sub": user.email})

            log.info("Login successful", email=credentials.email)
            return LoginResponse(access_token=access_token)
        
        except Exception as e:
            log.error("Login failed",email=credentials.email, error=str(e))
            raise CustomException("Login failed", e)
            

    def register(self, data: RegisterRequest) -> LoginResponse:
        """Register new user and return token."""
        try:
            log.info("Registration attempt", email=data.email)

            # 1. Check if user already exists
            existing_user = self.repository.get_user_by_email(data.email)
            if existing_user:
                log.warning("Registration failed - user already exists", email=data.email)
                return None
            
            # 2. Hash password
            hashed_password = hash_password(data.password)

            # 3. Create user
            user = self.repository.create_user(data.email, hashed_password, data.full_name)

            # 4. Generate JWT token
            access_token = create_access_token(data={"sub": user.email})

            log.info("Registration successful", email=data.email)
            return LoginResponse(access_token=access_token)
        
        except Exception as e:
            log.error("Registration failed", email=data.email, error=str(e))
            raise CustomException("Registration failed", e)
            