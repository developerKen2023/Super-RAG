from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from supabase import Client
from app.supabase import get_supabase
import time
import logging

logger = logging.getLogger(__name__)

security = HTTPBearer()

# Token cache: {token: (user_dict, expiry_timestamp)}
_token_cache: dict[str, tuple[dict, float]] = {}
_CACHE_TTL = 300  # 5 minutes


def _get_user_id(user) -> str:
    """Safely extract user ID from user object."""
    try:
        if isinstance(user, dict):
            return user.get('id', 'unknown')
        return getattr(user, 'id', 'unknown')
    except Exception:
        return 'unknown'


def _get_cached_user(token: str) -> dict | None:
    """Get user from cache if still valid."""
    if token in _token_cache:
        user, expiry = _token_cache[token]
        if time.time() < expiry:
            logger.info(f"[CACHE HIT] User {_get_user_id(user)} cached for {int(expiry - time.time())}s more")
            return user
        else:
            logger.info(f"[CACHE EXPIRED] Token expired, removing from cache")
            del _token_cache[token]
    else:
        logger.info(f"[CACHE MISS] Token not in cache")
    return None


def _set_cached_user(token: str, user: dict) -> None:
    """Cache user with 5 minute expiry."""
    _token_cache[token] = (user, time.time() + _CACHE_TTL)
    logger.info(f"[CACHE SET] User {_get_user_id(user)} cached for {_CACHE_TTL}s")


def _invalidate_cached_user(token: str) -> None:
    """Remove token from cache (on logout)."""
    _token_cache.pop(token, None)
    logger.info(f"[CACHE INVALIDATE] Token removed from cache")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> dict:
    """
    Validate JWT token and return current user.
    Used for endpoints that require authentication.
    Caches result for 5 minutes to reduce Supabase calls.
    """
    token = credentials.credentials

    # Check cache first
    cached_user = _get_cached_user(token)
    if cached_user:
        return cached_user

    logger.info("[AUTH] Cache miss - calling Supabase /auth/v1/user")
    supabase = get_supabase()

    try:
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        logger.info(f"[AUTH] Got user type: {type(user).__name__}, id: {_get_user_id(user)}")
        _set_cached_user(token, user)
        return user
    except Exception as e:
        logger.error(f"[AUTH] Exception: {type(e).__name__}: {e}")
        # Token invalid or expired - clear any stale cache
        _invalidate_cached_user(token)
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
    Uses cached user if available.
    """
    token = credentials.credentials
    supabase = get_supabase()

    # Check cache first
    cached_user = _get_cached_user(token)
    if cached_user:
        supabase.auth.set_session(token, token)
        return cached_user, supabase

    logger.info("[AUTH] Cache miss - calling Supabase /auth/v1/user")
    try:
        # Get user from token
        user_response = supabase.auth.get_user(token)
        user = user_response.user
        logger.info(f"[AUTH] Got user type: {type(user).__name__}, id: {_get_user_id(user)}")

        # Cache for future requests
        _set_cached_user(token, user)

        # Set the session so that subsequent operations use the correct user context
        supabase.auth.set_session(token, token)

        return user, supabase
    except Exception as e:
        logger.error(f"[AUTH] Exception: {type(e).__name__}: {e}")
        # Token invalid or expired - clear any stale cache
        _invalidate_cached_user(token)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )
