"""User Pydantic schemas."""
from datetime import datetime
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    """Request body for registration."""
    email: EmailStr
    password: str
    full_name: str | None = None


class UserLogin(BaseModel):
    """Request body for login."""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """User in API responses."""
    id: int
    email: str
    full_name: str | None
    created_at: datetime

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
