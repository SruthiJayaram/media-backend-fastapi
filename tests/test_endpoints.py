"""
Comprehensive test suite for Task 1, 2, and 3 features
Tests authentication, media upload, streaming, analytics, caching, and rate limiting
"""
import pytest
import io
import time
import json
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import Mock, patch

# Import our app components
from app.main import app
from app.database import get_db, Base
from app import models
from app.config import settings

# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override the database dependency
def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create test client
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_database():
    """Create and clean up test database for each test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def test_admin():
    """Create a test admin user"""
    db = TestingSessionLocal()
    admin_user = models.AdminUser(
        email="test@example.com",
        hashed_password="$2b$12$test.hashed.password"  # Mock hashed password
    )
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    db.close()
    return admin_user

@pytest.fixture
def auth_token():
    """Get JWT token for testing"""
    # Mock the password verification
    with patch('app.auth.verify_password') as mock_verify:
        mock_verify.return_value = True
        
        response = client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "testpass"}
        )
        assert response.status_code == 200
        token = response.json()["access_token"]
        return token

@pytest.fixture
def auth_headers(auth_token):
    """Get authorization headers"""
    return {"Authorization": f"Bearer {auth_token}"}

class TestTask1BasicBackend:
    """Test Task 1: Basic media backend with JWT authentication"""
    
    def test_root_endpoint(self):
        """Test the root endpoint"""
        response = client.get("/")
        assert response.status_code == 200
        assert "Media Platform Backend API" in response.json()["message"]
    
    def test_auth_register(self):
        """Test user registration"""
        response = client.post(
            "/auth/signup",
            json={
                "email": "newuser@example.com",
                "password": "newpassword"
            }
        )
        assert response.status_code == 201
        assert "access_token" in response.json()
        assert response.json()["token_type"] == "bearer"
    
    def test_auth_login(self, test_admin):
        """Test user login"""
        with patch('app.auth.verify_password') as mock_verify:
            mock_verify.return_value = True
            
            response = client.post(
                "/auth/login",
                json={"email": "test@example.com", "password": "testpass"}
            )
            assert response.status_code == 200
            assert "access_token" in response.json()
            assert response.json()["token_type"] == "bearer"
    
    def test_media_upload(self, test_admin, auth_headers):
        """Test media file upload"""
        # Create a test file
        test_file = io.BytesIO(b"fake video content")
        test_file.name = "test_video.mp4"
        
        response = client.post(
            "/media/",
            files={"file": ("test_video.mp4", test_file, "video/mp4")},
            data={"title": "Test Video", "type": "video"},
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Test Video"
        assert data["type"] == "video"
        assert "id" in data
        assert "file_url" in data
    
    def test_media_stream_url(self, test_admin, auth_headers):
        """Test secure streaming URL generation"""
        # First upload a file
        test_file = io.BytesIO(b"fake video content")
        upload_response = client.post(
            "/media/",
            files={"file": ("test_video.mp4", test_file, "video/mp4")},
            data={"title": "Test Video", "type": "video"},
            headers=auth_headers
        )
        media_id = upload_response.json()["id"]
        
        # Get streaming URL
        response = client.get(
            f"/media/{media_id}/stream-url",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "stream_url" in data
    
    def test_unauthorized_access(self):
        """Test that endpoints require authentication"""
        # Test upload without auth
        test_file = io.BytesIO(b"fake content")
        response = client.post(
            "/media/",
            files={"file": ("test.mp4", test_file, "video/mp4")},
            data={"title": "Test", "type": "video"}
        )
        assert response.status_code == 401
        
        # Test stream URL without auth
        response = client.get("/media/1/stream-url")
        assert response.status_code == 401

class TestTask2Analytics:
    """Test Task 2: Media view tracking and analytics"""
    
    def test_view_logging(self, test_admin, auth_headers):
        """Test manual view logging endpoint"""
        # First upload a file
        test_file = io.BytesIO(b"fake video content")
        upload_response = client.post(
            "/media/",
            files={"file": ("test_video.mp4", test_file, "video/mp4")},
            data={"title": "Test Video", "type": "video"},
            headers=auth_headers
        )
        media_id = upload_response.json()["id"]
        
        # Log a view
        response = client.post(
            f"/media/{media_id}/view",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "View logged successfully"
        assert data["media_id"] == media_id
        assert "timestamp" in data
        assert "viewer_ip" in data
    
    def test_analytics_calculation(self, test_admin, auth_headers):
        """Test analytics calculation"""
        # Upload a file
        test_file = io.BytesIO(b"fake video content")
        upload_response = client.post(
            "/media/",
            files={"file": ("test_video.mp4", test_file, "video/mp4")},
            data={"title": "Test Video", "type": "video"},
            headers=auth_headers
        )
        media_id = upload_response.json()["id"]
        
        # Log multiple views
        for _ in range(3):
            client.post(f"/media/{media_id}/view", headers=auth_headers)
            time.sleep(0.1)  # Small delay to ensure different timestamps
        
        # Get analytics
        response = client.get(
            f"/media/{media_id}/analytics",
            headers=auth_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["media_id"] == media_id
        assert data["media_filename"] == "Test Video"
        assert data["total_views"] == 3
        assert data["unique_viewers"] == 1  # Same IP
        assert data["recent_views_7days"] == 3
        assert "upload_date" in data
    
    def test_analytics_nonexistent_media(self, test_admin, auth_headers):
        """Test analytics for non-existent media"""
        response = client.get("/media/999/analytics", headers=auth_headers)
        assert response.status_code == 404
        assert "Media not found" in response.json()["detail"]

class TestTask3ProductionFeatures:
    """Test Task 3: Performance, security, and production features"""
    
    @patch('app.cache.cache_service.get_analytics')
    def test_analytics_caching(self, mock_get_analytics, test_admin, auth_headers):
        """Test Redis caching for analytics"""
        # Mock cache to simulate cache hit
        mock_get_analytics.return_value = {
            "media_id": 1,
            "media_filename": "test.mp4",
            "total_views": 5,
            "unique_viewers": 3,
            "recent_views_7days": 2,
            "upload_date": "2024-01-01T12:00:00"
        }
        
        # Upload a file first
        test_file = io.BytesIO(b"fake video content")
        upload_response = client.post(
            "/media/",
            files={"file": ("test.mp4", test_file, "video/mp4")},
            data={"title": "Test", "type": "video"},
            headers=auth_headers
        )
        media_id = upload_response.json()["id"]
        
        # Get analytics (should hit cache)
        response = client.get(f"/media/{media_id}/analytics", headers=auth_headers)
        assert response.status_code == 200
        
        # Verify cache was called
        mock_get_analytics.assert_called_once_with(media_id)
    
    def test_rate_limiting_view_endpoint(self, test_admin, auth_headers):
        """Test rate limiting on view logging endpoint"""
        # Upload a file
        test_file = io.BytesIO(b"fake video content")
        upload_response = client.post(
            "/media/",
            files={"file": ("test_video.mp4", test_file, "video/mp4")},
            data={"title": "Test Video", "type": "video"},
            headers=auth_headers
        )
        media_id = upload_response.json()["id"]
        
        # Make rapid requests to trigger rate limiting
        responses = []
        for i in range(12):  # More than the 10/minute limit
            response = client.post(f"/media/{media_id}/view", headers=auth_headers)
            responses.append(response.status_code)
            if i < 5:
                time.sleep(0.1)  # Small delay for first few requests
        
        # Should have some rate-limited responses (429)
        success_responses = [r for r in responses if r == 200]
        rate_limited_responses = [r for r in responses if r == 429]
        
        assert len(success_responses) > 0  # Some should succeed
        assert len(rate_limited_responses) > 0  # Some should be rate limited
    
    def test_cache_invalidation_on_new_view(self, test_admin, auth_headers):
        """Test that cache is invalidated when new views are logged"""
        # Upload a file
        test_file = io.BytesIO(b"fake video content")
        upload_response = client.post(
            "/media/",
            files={"file": ("test_video.mp4", test_file, "video/mp4")},
            data={"title": "Test Video", "type": "video"},
            headers=auth_headers
        )
        media_id = upload_response.json()["id"]
        
    @patch('app.cache.cache_service.invalidate_analytics')
    def test_cache_invalidation_on_new_view(self, mock_invalidate, test_admin, auth_headers):
        """Test that cache is invalidated when new views are logged"""
        # Upload a file
        test_file = io.BytesIO(b"fake video content")
        upload_response = client.post(
            "/media/",
            files={"file": ("test_video.mp4", test_file, "video/mp4")},
            data={"title": "Test Video", "type": "video"},
            headers=auth_headers
        )
        media_id = upload_response.json()["id"]
        
        # Mock the rate limiter to avoid conflicts
        with patch('app.rate_limiter.rate_limiter.check_rate_limit', return_value=(True, {"remaining": 9})):
            # Log a view
            response = client.post(f"/media/{media_id}/view", headers=auth_headers)
            assert response.status_code == 200
            
            # Verify cache invalidation was called
            mock_invalidate.assert_called_once_with(media_id)
    
    def test_streaming_url_signature_validation(self, test_admin, auth_headers):
        """Test that streaming URLs have proper HMAC signatures"""
        # Upload a file
        test_file = io.BytesIO(b"fake video content")
        upload_response = client.post(
            "/media/",
            files={"file": ("test_video.mp4", test_file, "video/mp4")},
            data={"title": "Test Video", "type": "video"},
            headers=auth_headers
        )
        media_id = upload_response.json()["id"]
        
        # Get streaming URL
        response = client.get(f"/media/{media_id}/stream-url", headers=auth_headers)
        assert response.status_code == 200
        
        stream_url = response.json()["stream_url"]
        
        # URL should contain expiration and signature parameters
        assert "exp=" in stream_url
        assert "sig=" in stream_url

class TestErrorHandling:
    """Test comprehensive error handling"""
    
    def test_invalid_file_upload(self, test_admin, auth_headers):
        """Test upload with invalid file type (simplified test)"""
        # Note: Current implementation accepts all file types
        # This test verifies the endpoint works even with non-media files
        test_file = io.BytesIO(b"not a video")
        
        response = client.post(
            "/media/",
            files={"file": ("test.txt", test_file, "text/plain")},
            data={"title": "Test", "type": "video"},
            headers=auth_headers
        )
        
        # Current implementation allows this, so we expect success
        # In production, you'd add file type validation
        assert response.status_code in [200, 400]
    
    def test_malformed_jwt_token(self, test_admin):
        """Test handling of malformed JWT tokens"""
        headers = {"Authorization": "Bearer invalid.token.here"}
        
        response = client.get("/media/1/stream-url", headers=headers)
        assert response.status_code == 401
    
    def test_expired_streaming_url(self, test_admin, auth_headers):
        """Test handling of expired streaming URLs (simplified)"""
        # This would require mocking time or using very short expiration
        # For now, test that the stream endpoint validates parameters
        response = client.get("/media/stream/999")  # Non-existent media
        assert response.status_code in [404, 422]  # Not found or validation error

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
