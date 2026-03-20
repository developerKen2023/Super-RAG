from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from app.supabase import get_supabase

security = HTTPBearer()


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Validate JWT token and return current user.
    Used for endpoints that require authentication.
    """
    token = credentials.credentials
    supabase = get_supabase()

    try:
        user = supabase.auth.get_user(token)
        return user.user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict | None:
    """
    Optional auth - returns user if valid token, None otherwise.
    Used for endpoints that work with or without auth.
    """
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None


async def get_authenticated_supabase(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> tuple[dict, Client]:
    """
    Validate JWT token and return both user and a Supabase client with the user's session set.
    This ensures RLS policies work correctly.
    """
    token = credentials.credentials
    supabase = get_supabase()

    try:
        # Get user from token
        user_response = supabase.auth.get_user(token)
        user = user_response.user

        # Set the session so that subsequent operations use the correct user context
        # We need the refresh token too - get it from the current session if available
        # For now, we'll just set the access token which should work for RLS
        supabase.auth.set_session(token, token)  # Use token as placeholder for refresh

        return user, supabase
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
