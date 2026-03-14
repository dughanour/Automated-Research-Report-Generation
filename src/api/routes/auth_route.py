from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from src.api.models.auth_model import LoginRequest, LoginResponse, RegisterRequest
from src.api.services.auth_service import AuthService
from src.database.db_config import get_db


router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=LoginResponse)
async def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user and return JWT token.
    """
    service = AuthService(db)
    result = service.login(credentials)

    if not result:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
         detail="Invalid credentials")
        
    return result

@router.post("/register", response_model=LoginResponse)
async def register(data: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user."""
    service = AuthService(db)
    result = service.register(data)

    if not result:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
         detail="Failed to register user")
        
    return result
