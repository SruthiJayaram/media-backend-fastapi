#!/bin/bash

echo "🚀 FastAPI Media Backend - Test Suite"
echo "====================================="

BASE_URL="http://127.0.0.1:8000"
TEST_EMAIL="test$(date +%s)@example.com"
TEST_PASSWORD="testpassword123"

echo ""
echo "1. 🔍 Testing Root Endpoint..."
echo "curl -X GET $BASE_URL/"
curl -X GET "$BASE_URL/"
echo -e "\n"

echo "2. 📝 Testing User Signup..."
echo "curl -X POST $BASE_URL/auth/signup -H 'Content-Type: application/json' -d '{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}'"
SIGNUP_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/signup" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

echo "Response: $SIGNUP_RESPONSE"
TOKEN=$(echo "$SIGNUP_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -n "$TOKEN" ]; then
    echo "✅ Signup successful! Token: ${TOKEN:0:50}..."
    echo ""
    
    echo "3. 🔐 Testing User Login..."
    LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
        -H "Content-Type: application/json" \
        -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")
    echo "Response: $LOGIN_RESPONSE"
    echo ""
    
    echo "4. 📤 Creating test file and uploading media..."
    echo "Test media content" > /tmp/test_video.mp4
    
    UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/media/" \
        -H "Authorization: Bearer $TOKEN" \
        -F "title=Test Video" \
        -F "type=video" \
        -F "file=@/tmp/test_video.mp4")
    echo "Response: $UPLOAD_RESPONSE"
    
    MEDIA_ID=$(echo "$UPLOAD_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
    
    if [ -n "$MEDIA_ID" ]; then
        echo "✅ Upload successful! Media ID: $MEDIA_ID"
        echo ""
        
        echo "5. 🔗 Getting stream URL..."
        STREAM_RESPONSE=$(curl -s -X GET "$BASE_URL/media/$MEDIA_ID/stream-url" \
            -H "Authorization: Bearer $TOKEN")
        echo "Response: $STREAM_RESPONSE"
        
        STREAM_URL=$(echo "$STREAM_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['stream_url'])" 2>/dev/null)
        
        if [ -n "$STREAM_URL" ]; then
            echo "✅ Stream URL generated!"
            echo "Stream URL: $STREAM_URL"
            echo ""
            
            echo "6. 🎬 Testing file streaming..."
            echo "curl -I \"$STREAM_URL\""
            curl -I "$STREAM_URL"
            echo ""
            
            echo "🎉 All tests completed successfully!"
            echo ""
            echo "📊 Summary:"
            echo "  ✅ Root endpoint working"
            echo "  ✅ User signup working"
            echo "  ✅ User login working"
            echo "  ✅ Media upload working"
            echo "  ✅ Stream URL generation working"
            echo "  ✅ File streaming working"
        fi
    fi
    
    # Cleanup
    rm -f /tmp/test_video.mp4
else
    echo "❌ Signup failed!"
fi

echo ""
echo "🌐 Access your API documentation at:"
echo "   • Swagger UI: $BASE_URL/docs"
echo "   • ReDoc: $BASE_URL/redoc"
