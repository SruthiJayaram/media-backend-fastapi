#!/usr/bin/env python3
"""
Test script for FastAPI Media Backend
Tests all endpoints: signup, login, media upload, and streaming
"""

import requests
import json
import os
from pathlib import Path

# Configuration
BASE_URL = "http://127.0.0.1:8000"
TEST_EMAIL = "test@example.com"
TEST_PASSWORD = "testpassword123"

def test_root():
    """Test root endpoint"""
    print("🔍 Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    print("✅ Root endpoint working!\n")

def test_signup():
    """Test user signup"""
    print("📝 Testing user signup...")
    signup_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    response = requests.post(f"{BASE_URL}/auth/signup", json=signup_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 201
    token = response.json()["access_token"]
    print("✅ Signup successful!\n")
    return token

def test_login():
    """Test user login"""
    print("🔐 Testing user login...")
    login_data = {
        "email": TEST_EMAIL,
        "password": TEST_PASSWORD
    }
    response = requests.post(f"{BASE_URL}/auth/login", json=login_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    token = response.json()["access_token"]
    print("✅ Login successful!\n")
    return token

def test_media_upload(token):
    """Test media upload"""
    print("📤 Testing media upload...")
    
    # Create a small test file
    test_file_path = "/tmp/test_video.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test video file content")
    
    headers = {"Authorization": f"Bearer {token}"}
    files = {"file": ("test_video.mp4", open(test_file_path, "rb"), "video/mp4")}
    data = {"title": "Test Video", "type": "video"}
    
    response = requests.post(f"{BASE_URL}/media/", headers=headers, files=files, data=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    media_id = response.json()["id"]
    print(f"✅ Media upload successful! Media ID: {media_id}\n")
    
    # Clean up test file
    os.unlink(test_file_path)
    return media_id

def test_stream_url(token, media_id):
    """Test stream URL generation"""
    print("🔗 Testing stream URL generation...")
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/media/{media_id}/stream-url", headers=headers)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    assert response.status_code == 200
    stream_url = response.json()["stream_url"]
    print(f"✅ Stream URL generated: {stream_url}\n")
    return stream_url

def test_stream_access(stream_url):
    """Test streaming the file (without auth)"""
    print("🎬 Testing file streaming...")
    response = requests.get(stream_url)
    print(f"Status: {response.status_code}")
    print(f"Content-Type: {response.headers.get('content-type')}")
    print(f"Content length: {len(response.content)} bytes")
    assert response.status_code == 200
    print("✅ File streaming successful!\n")

def main():
    """Run all tests"""
    print("🚀 Starting FastAPI Media Backend Tests\n")
    
    try:
        # Test basic API
        test_root()
        
        # Test authentication flow
        token = test_signup()
        
        # Test media operations
        media_id = test_media_upload(token)
        stream_url = test_stream_url(token, media_id)
        test_stream_access(stream_url)
        
        print("🎉 All tests passed! Your FastAPI Media Backend is working perfectly!")
        
        # Show useful info
        print("\n" + "="*60)
        print("🌐 Access your API:")
        print(f"   • Swagger UI: {BASE_URL}/docs")
        print(f"   • ReDoc: {BASE_URL}/redoc")
        print(f"   • Root endpoint: {BASE_URL}/")
        print("\n📝 Test credentials created:")
        print(f"   • Email: {TEST_EMAIL}")
        print(f"   • Password: {TEST_PASSWORD}")
        print(f"   • Token: {token[:50]}...")
        print("\n📁 Files stored in: ./storage/")
        print("="*60)
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
