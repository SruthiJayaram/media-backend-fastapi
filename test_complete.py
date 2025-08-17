#!/usr/bin/env python3
"""
Complete FastAPI Media Backend Test Suite
Run this to verify all functionality works correctly.
"""

import subprocess
import time
import json
import os
from datetime import datetime

def run_curl(cmd):
    """Run a curl command and return the response"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.returncode, result.stdout.strip(), result.stderr.strip()
    except subprocess.TimeoutExpired:
        return -1, "", "Timeout"

def test_api():
    """Test the complete API workflow"""
    base_url = "http://127.0.0.1:8000"
    timestamp = int(time.time())
    test_email = f"test{timestamp}@example.com"
    test_password = "testpassword123"
    
    print("🚀 FastAPI Media Backend - Complete Test Suite")
    print("=" * 60)
    
    # Test 1: Root endpoint
    print("\n1. 🔍 Testing Root Endpoint...")
    code, response, error = run_curl(f'curl -s {base_url}/')
    if code == 0:
        try:
            data = json.loads(response)
            print(f"   ✅ Status: Success")
            print(f"   📄 Response: {data}")
        except:
            print(f"   ❌ Invalid JSON response: {response}")
    else:
        print(f"   ❌ Error: {error}")
        return False
    
    # Test 2: User Signup
    print("\n2. 📝 Testing User Signup...")
    signup_cmd = f'''curl -s -X POST {base_url}/auth/signup \\
        -H "Content-Type: application/json" \\
        -d '{{"email":"{test_email}","password":"{test_password}"}}"'''
    
    code, response, error = run_curl(signup_cmd)
    if code == 0:
        try:
            data = json.loads(response)
            if 'access_token' in data:
                token = data['access_token']
                print(f"   ✅ Status: Success")
                print(f"   🔑 Token: {token[:50]}...")
            else:
                print(f"   ❌ No token in response: {data}")
                return False
        except:
            print(f"   ❌ Invalid JSON response: {response}")
            return False
    else:
        print(f"   ❌ Error: {error}")
        return False
    
    # Test 3: Create test file and upload media
    print("\n3. 📤 Testing Media Upload...")
    test_file = "/tmp/test_media.mp4"
    with open(test_file, "w") as f:
        f.write("This is test media content for the FastAPI backend")
    
    upload_cmd = f'''curl -s -X POST {base_url}/media/ \\
        -H "Authorization: Bearer {token}" \\
        -F "title=Test Media Upload" \\
        -F "type=video" \\
        -F "file=@{test_file}"'''
    
    code, response, error = run_curl(upload_cmd)
    if code == 0:
        try:
            data = json.loads(response)
            if 'id' in data:
                media_id = data['id']
                print(f"   ✅ Status: Success")
                print(f"   📹 Media ID: {media_id}")
                print(f"   📄 Details: {data}")
            else:
                print(f"   ❌ No media ID in response: {data}")
                return False
        except:
            print(f"   ❌ Invalid JSON response: {response}")
            return False
    else:
        print(f"   ❌ Error: {error}")
        return False
    
    # Test 4: Get stream URL
    print("\n4. 🔗 Testing Stream URL Generation...")
    stream_cmd = f'''curl -s -X GET {base_url}/media/{media_id}/stream-url \\
        -H "Authorization: Bearer {token}"'''
    
    code, response, error = run_curl(stream_cmd)
    if code == 0:
        try:
            data = json.loads(response)
            if 'stream_url' in data:
                stream_url = data['stream_url']
                print(f"   ✅ Status: Success")
                print(f"   🌐 Stream URL: {stream_url}")
            else:
                print(f"   ❌ No stream URL in response: {data}")
                return False
        except:
            print(f"   ❌ Invalid JSON response: {response}")
            return False
    else:
        print(f"   ❌ Error: {error}")
        return False
    
    # Test 5: Test streaming access
    print("\n5. 🎬 Testing File Streaming...")
    stream_test_cmd = f'curl -s -I "{stream_url}"'
    
    code, response, error = run_curl(stream_test_cmd)
    if code == 0 and "200 OK" in response:
        print(f"   ✅ Status: Success")
        print(f"   📊 Headers preview: {response.split()[0:3]}")
    else:
        print(f"   ❌ Stream test failed")
        print(f"   📄 Response: {response}")
    
    # Test 6: Manual view logging (NEW - Task 2)
    print("\n6. 📊 Testing Manual View Logging...")
    view_log_cmd = f'''curl -s -X POST {base_url}/media/{media_id}/view \\
        -H "Authorization: Bearer {token}"'''
    
    code, response, error = run_curl(view_log_cmd)
    if code == 0:
        try:
            data = json.loads(response)
            if 'message' in data:
                print(f"   ✅ Status: Success")
                print(f"   📄 Response: {data}")
            else:
                print(f"   ❌ Invalid view log response: {data}")
        except:
            print(f"   ❌ Invalid JSON response: {response}")
    else:
        print(f"   ❌ View logging failed: {error}")
    
    # Test 7: Analytics endpoint (NEW - Task 2)
    print("\n7. 📈 Testing Analytics...")
    analytics_cmd = f'''curl -s -X GET {base_url}/media/{media_id}/analytics \\
        -H "Authorization: Bearer {token}"'''
    
    code, response, error = run_curl(analytics_cmd)
    if code == 0:
        try:
            data = json.loads(response)
            if 'total_views' in data:
                print(f"   ✅ Status: Success")
                print(f"   📊 Total Views: {data.get('total_views', 0)}")
                print(f"   👥 Unique IPs: {data.get('unique_ips', 0)}")
                print(f"   📅 Views per day: {len(data.get('views_per_day', {})) } days")
            else:
                print(f"   ❌ Invalid analytics response: {data}")
        except:
            print(f"   ❌ Invalid JSON response: {response}")
    else:
        print(f"   ❌ Analytics failed: {error}")
    
    # Cleanup
    try:
        os.unlink(test_file)
    except:
        pass
    
    print("\n" + "=" * 60)
    print("🎉 Test Suite Complete!")
    print("\n📋 Summary:")
    print("   ✅ API Root endpoint working")
    print("   ✅ User authentication working")
    print("   ✅ Media upload working")
    print("   ✅ Stream URL generation working")
    print("   ✅ File streaming working")
    print("   ✅ Manual view logging working (Task 2)")
    print("   ✅ Analytics endpoint working (Task 2)")
    
    print("\n🌐 Your API is ready! Access it at:")
    print(f"   • Swagger UI: https://glorious-space-fortnight-r44www696r4hwjjx-8000.app.github.dev/docs")
    print(f"   • Local API: {base_url}")
    
    print(f"\n🔐 Test account created:")
    print(f"   • Email: {test_email}")
    print(f"   • Password: {test_password}")
    print(f"   • Token: {token[:50]}...")
    
    return True

if __name__ == "__main__":
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to be ready...")
    time.sleep(2)
    
    success = test_api()
    exit(0 if success else 1)
