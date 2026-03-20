from supabase import create_client, Client
from supabase.lib.client_options import SyncClientOptions
from app.config import get_settings

settings = get_settings()


def get_supabase() -> Client:
    """Get Supabase client configured for the application."""
    return create_client(
        settings.supabase_url,
        settings.supabase_anon_key,
        options=SyncClientOptions(
            postgrest_client_timeout=10,
        )
    )


def get_supabase_admin() -> Client:
    """Get Supabase admin client (bypasses RLS) for internal operations."""
    return create_client(
        settings.supabase_url,
        settings.supabase_service_role_key,
        options=SyncClientOptions(
            postgrest_client_timeout=10,
        )
    )
