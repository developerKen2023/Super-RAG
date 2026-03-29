import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.supabase import get_supabase, get_supabase_admin


class TestAuthSignup:
    """Tests for POST /api/auth/signup"""

    def test_signup_success(self, mock_supabase_admin):
        """Valid signup creates user and returns tokens."""
        app.dependency_overrides[get_supabase_admin] = lambda: mock_supabase_admin

        client = TestClient(app)

        response = client.post("/api/auth/signup", json={
            "email": "new@example.com",
            "password": "securepassword123",
            "full_name": "New User"
        })

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_signup_duplicate_email(self, mock_supabase_admin):
        """Duplicate email returns 400."""
        app.dependency_overrides[get_supabase_admin] = lambda: mock_supabase_admin

        # Make sign_up return None user to simulate error
        mock_supabase_admin.auth.sign_up.return_value = MagicMock(user=None)

        client = TestClient(app)

        response = client.post("/api/auth/signup", json={
            "email": "existing@example.com",
            "password": "securepassword123",
            "full_name": "Existing User"
        })

        app.dependency_overrides.clear()

        assert response.status_code == 400


class TestAuthLogin:
    """Tests for POST /api/auth/login"""

    def test_login_success(self, mock_supabase_client):
        """Valid credentials return tokens."""
        app.dependency_overrides[get_supabase] = lambda: mock_supabase_client

        client = TestClient(app)

        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "correctpassword"
        })

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_login_invalid_password(self, mock_supabase_client):
        """Invalid password returns 401."""
        app.dependency_overrides[get_supabase] = lambda: mock_supabase_client

        # Make sign_in_with_password return None to simulate failure
        mock_supabase_client.auth.sign_in_with_password.return_value = MagicMock(
            user=None, session=None
        )

        client = TestClient(app)

        response = client.post("/api/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })

        app.dependency_overrides.clear()

        assert response.status_code == 401


class TestAuthLogout:
    """Tests for POST /api/auth/logout"""

    def test_logout_success(self, mock_supabase_client):
        """Logout invalidates session."""
        app.dependency_overrides[get_supabase] = lambda: mock_supabase_client

        # Mock get_current_user dependency
        from app.deps import get_current_user

        async def mock_get_current_user():
            return MagicMock(id="test-user-id", email="test@example.com")

        app.dependency_overrides[get_current_user] = mock_get_current_user

        client = TestClient(app)

        response = client.post(
            "/api/auth/logout",
            headers={"Authorization": "Bearer test-token"}
        )

        app.dependency_overrides.clear()

        assert response.status_code == 200


class TestAuthMe:
    """Tests for GET /api/auth/me"""

    def test_me_authenticated(self, mock_supabase_client):
        """Authenticated user returns profile."""
        app.dependency_overrides[get_supabase] = lambda: mock_supabase_client

        # Mock get_current_user dependency
        from app.deps import get_current_user

        async def mock_get_current_user():
            return MagicMock(
                id="test-user-id",
                email="test@example.com",
                email_confirmed_at="2024-01-01T00:00:00Z",
                user_metadata={"full_name": "Test User"}
            )

        app.dependency_overrides[get_current_user] = mock_get_current_user

        client = TestClient(app)

        response = client.get(
            "/api/auth/me",
            headers={"Authorization": "Bearer test-token"}
        )

        app.dependency_overrides.clear()

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
