from  typing import Optional
from sqlalchemy.orm import Session
from src.database.user_model import User
from src.logger import GLOBAL_LOGGER as log
from src.exceptions.custom_exception import CustomException

class UserRepository:
    """Handles all database operations for users."""
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[dict]:
        """Find user by email. Returns None if not found."""
        try:
            log.info("Fetching user by email", email=email)
            user = self.db.query(User).filter(User.email == email).first()
            return user

        except Exception as e:
            log.error("Database error whilefetching user by email", error=str(e))
            raise CustomException("Failed to fetch user by email", e)
    
    def create_user(self, email: str, hashed_password: str, full_name: Optional[str] = None) -> User:
        """Create a new user."""
        try:
            log.info("Creating new user", email=email)
            user = User(
                email=email,
                hashed_password=hashed_password,
                full_name=full_name
            )
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
            log.info("User created successfully", user_id=user.id)
            return user

        except Exception as e:
            self.db.rollback() # Undo on error
            log.error("Failed to create user", error=str(e))
            raise CustomException("Failed to create user", e)

