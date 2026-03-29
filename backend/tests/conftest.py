import pytest
import sys
import os
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


# =============================================================================
# MOCKS - Create mock objects before importing app modules
# =============================================================================

class MockUser:
    """Mock user object."""
    def __init__(self, id="test-user-id", email="test@example.com"):
        self.id = id
        self.email = email
        self.email_confirmed_at = "2024-01-01T00:00:00Z"
        self.user_metadata = {"full_name": "Test User"}


class MockSession:
    """Mock session object."""
    def __init__(self):
        self.access_token = "test-access-token"
        self.refresh_token = "test-refresh-token"


class MockAuthResponse:
    """Mock auth response."""
    def __init__(self, user=None, session=None):
        self.user = user or MockUser()
        self.session = session or MockSession()


class MockSupabaseTable:
    """Mock Supabase table interface."""
    def __init__(self, data=None):
        self._data = data or []

    def select(self, *args, **kwargs):
        result = MagicMock()
        result.eq = MagicMock(return_value=self)
        return self

    def insert(self, *args, **kwargs):
        result = MagicMock()
        result.execute = MagicMock(return_value=MagicMock(data=[{"id": "test-id"}]))
        return result

    def update(self, *args, **kwargs):
        result = MagicMock()
        result.eq = MagicMock(return_value=MagicMock(
            execute=MagicMock(return_value=MagicMock(data=self._data))
        ))
        return result

    def delete(self, *args, **kwargs):
        result = MagicMock()
        result.eq = MagicMock(return_value=MagicMock(
            execute=MagicMock(return_value=MagicMock(data=[]))
        ))
        return result

    def eq(self, *args, **kwargs):
        return self

    def order(self, *args, **kwargs):
        return self

    def execute(self):
        return MagicMock(data=self._data)


class MockSupabaseClient:
    """Mock Supabase client."""
    def __init__(self, data=None):
        self.auth = MagicMock()
        self.auth.get_user = MagicMock(return_value=MagicMock(user=MockUser()))
        self.auth.set_session = MagicMock()
        self.auth.sign_out = MagicMock()
        self.auth.sign_up = MagicMock(return_value=MockAuthResponse())
        self.auth.sign_in_with_password = MagicMock(return_value=MockAuthResponse())
        self._data = data or {}

    def table(self, *args, **kwargs):
        return MockSupabaseTable(self._data.get(args[0], []))

    def rpc(self, *args, **kwargs):
        """Mock RPC call for vector search."""
        return MagicMock(execute=MagicMock(return_value=MagicMock(data=[])))


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client for testing."""
    return MockSupabaseClient()


@pytest.fixture
def mock_supabase_admin():
    """Mock Supabase admin client for testing."""
    return MockSupabaseClient()


@pytest.fixture
def auth_headers():
    """Pre-configured auth headers for testing."""
    return {"Authorization": "Bearer test-token"}


@pytest.fixture
def test_user():
    """Test user fixture."""
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "email_confirmed_at": "2024-01-01T00:00:00Z",
        "user_metadata": {"full_name": "Test User"}
    }


@pytest.fixture
def test_conversation():
    """Test conversation fixture."""
    return {
        "id": "test-conv-id",
        "user_id": "test-user-id",
        "title": "Test Conversation",
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def test_message():
    """Test message fixture."""
    return {
        "id": "test-msg-id",
        "conversation_id": "test-conv-id",
        "user_id": "test-user-id",
        "role": "user",
        "content": "Hello, world!",
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def test_document():
    """Test document fixture."""
    return {
        "id": "test-doc-id",
        "user_id": "test-user-id",
        "filename": "test.txt",
        "file_path": "uploads/documents/test-doc-id_test.txt",
        "file_size": 1024,
        "mime_type": "text/plain",
        "status": "completed",
        "chunk_count": 2,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def test_chunk():
    """Test document chunk fixture."""
    return {
        "id": "test-chunk-id",
        "document_id": "test-doc-id",
        "user_id": "test-user-id",
        "chunk_index": 0,
        "content": "This is a test chunk content.",
        "embedding": [0.1] * 1536,
        "created_at": "2024-01-01T00:00:00Z"
    }


@pytest.fixture
def mock_app(mock_supabase_client, mock_supabase_admin):
    """FastAPI test client with mocked dependencies."""
    from app.main import app
    from app.supabase import get_supabase, get_supabase_admin

    # Override dependencies
    app.dependency_overrides[get_supabase] = lambda: mock_supabase_client
    app.dependency_overrides[get_supabase_admin] = lambda: mock_supabase_admin

    client = TestClient(app)
    yield client

    # Clear overrides after test
    app.dependency_overrides.clear()
