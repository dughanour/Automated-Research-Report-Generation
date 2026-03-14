from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# What frontend sends to backend api for login
class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(...,min_length=6)

# What api backend sends to frontend
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "Bearer"

# What frontend sends to backend api for registration
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(...,min_length=6)
    full_name: Optional[str] = None

