from pydantic import BaseModel, EmailStr


class SignupRequest(BaseModel):
    """Request model for user registration."""
    email: EmailStr
    password: str
    full_name: str | None = None


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Response model for auth operations."""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: dict


class UserResponse(BaseModel):
    """Response model for user data."""
    id: str
    email: str
    email_confirmed_at: str | None = None
    full_name: str | None = None
    avatar_url: str | None = None
