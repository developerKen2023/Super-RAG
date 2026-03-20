from fastapi import APIRouter, Depends, HTTPException, status
from supabase import Client
from app.supabase import get_supabase, get_supabase_admin
from app.deps import get_current_user
from app.schemas.auth import (
    SignupRequest,
    LoginRequest,
    AuthResponse,
    UserResponse
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse)
async def signup(
    request: SignupRequest,
    supabase: Client = Depends(get_supabase_admin)
):
    """
    Register a new user with email and password.
    Creates profile record and returns session tokens.
    """
    auth_response = supabase.auth.sign_up({
        "email": request.email,
        "password": request.password,
    })

    if auth_response.user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to create user"
        )

    user = auth_response.user
    session = auth_response.session

    # Create profile record
    supabase.table("profiles").insert({
        "id": user.id,
        "email": user.email,
        "full_name": request.full_name
    }).execute()

    return AuthResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        user={
            "id": user.id,
            "email": user.email,
            "full_name": request.full_name
        }
    )


@router.post("/login", response_model=AuthResponse)
async def login(
    request: LoginRequest,
    supabase: Client = Depends(get_supabase)
):
    """
    Login with email and password.
    Returns session tokens.
    """
    auth_response = supabase.auth.sign_in_with_password({
        "email": request.email,
        "password": request.password
    })

    if auth_response.user is None or auth_response.session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    user = auth_response.user
    session = auth_response.session

    return AuthResponse(
        access_token=session.access_token,
        refresh_token=session.refresh_token,
        user={
            "id": user.id,
            "email": user.email
        }
    )


@router.post("/logout")
async def logout(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase)
):
    """
    Logout current user (invalidate session).
    """
    supabase.auth.sign_out()
    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user)
):
    """
    Get current authenticated user.
    """
    return UserResponse(
        id=current_user.id,
        email=current_user.email,
        email_confirmed_at=current_user.email_confirmed_at,
        full_name=current_user.user_metadata.get("full_name"),
        avatar_url=current_user.user_metadata.get("avatar_url")
    )
