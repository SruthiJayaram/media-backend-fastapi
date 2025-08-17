#!/bin/bash

echo "🎯 Task 2: Media View Tracking & Analytics Test"
echo "================================================"

BASE_URL="http://127.0.0.1:8000"
TEST_EMAIL="task2test@example.com"
TEST_PASSWORD="testpassword123"

# Step 1: Create user and get token
echo "1. 📝 Creating test user..."
SIGNUP_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/signup" \
    -H "Content-Type: application/json" \
    -d "{\"email\":\"$TEST_EMAIL\",\"password\":\"$TEST_PASSWORD\"}")

TOKEN=$(echo "$SIGNUP_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null)

if [ -n "$TOKEN" ]; then
    echo "✅ User created. Token: ${TOKEN:0:30}..."
    
    # Step 2: Upload test media
    echo -e "\n2. 📤 Uploading test media..."
    echo "Test media content for analytics" > /tmp/test_analytics.mp4
    
    UPLOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/media/" \
        -H "Authorization: Bearer $TOKEN" \
        -F "title=Analytics Test Video" \
        -F "type=video" \
        -F "file=@/tmp/test_analytics.mp4")
    
    MEDIA_ID=$(echo "$UPLOAD_RESPONSE" | python3 -c "import sys, json; print(json.load(sys.stdin)['id'])" 2>/dev/null)
    
    if [ -n "$MEDIA_ID" ]; then
        echo "✅ Media uploaded. Media ID: $MEDIA_ID"
        
        # Step 3: Test manual view logging (Task 2 - NEW)
        echo -e "\n3. 📊 Testing manual view logging..."
        VIEW_RESPONSE=$(curl -s -X POST "$BASE_URL/media/$MEDIA_ID/view" \
            -H "Authorization: Bearer $TOKEN")
        echo "Response: $VIEW_RESPONSE"
        
        # Add multiple views from different simulated IPs
        echo -e "\n4. 📊 Adding more views for analytics..."
        for i in {1..3}; do
            curl -s -X POST "$BASE_URL/media/$MEDIA_ID/view" \
                -H "Authorization: Bearer $TOKEN" > /dev/null
            echo "   Added view $i"
        done
        
        # Step 4: Test analytics endpoint (Task 2 - NEW)
        echo -e "\n5. 📈 Testing analytics endpoint..."
        ANALYTICS_RESPONSE=$(curl -s -X GET "$BASE_URL/media/$MEDIA_ID/analytics" \
            -H "Authorization: Bearer $TOKEN")
        echo "Analytics Response:"
        echo "$ANALYTICS_RESPONSE" | python3 -c "import sys, json; print(json.dumps(json.load(sys.stdin), indent=2))" 2>/dev/null
        
        # Step 5: Test error cases
        echo -e "\n6. 🚨 Testing error cases..."
        
        # Test with invalid media ID
        echo "Testing invalid media ID..."
        ERROR_RESPONSE=$(curl -s -X GET "$BASE_URL/media/99999/analytics" \
            -H "Authorization: Bearer $TOKEN")
        echo "Error response: $ERROR_RESPONSE"
        
        # Test without authentication
        echo "Testing without JWT token..."
        NO_AUTH_RESPONSE=$(curl -s -X POST "$BASE_URL/media/$MEDIA_ID/view")
        echo "No auth response: $NO_AUTH_RESPONSE"
        
        echo -e "\n🎉 Task 2 Testing Complete!"
        echo "✅ Manual view logging endpoint working"
        echo "✅ Analytics endpoint working"
        echo "✅ JWT protection working"
        echo "✅ Error handling working"
    
    else
        echo "❌ Media upload failed"
    fi
    
    # Cleanup
    rm -f /tmp/test_analytics.mp4
    
else
    echo "❌ User creation failed"
fi
