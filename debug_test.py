#!/usr/bin/env python3
"""
Detailed QA test to debug the 500 error
"""
import requests
import json
import time

BACKEND_URL = "https://fix-my-form.onrender.com"

def test_detailed_analysis():
    """Test analysis with detailed error reporting"""
    print("🔍 Detailed Analysis Debug Test")
    print("=" * 50)
    
    # First, let's upload a real video
    print("1. Uploading a test video...")
    
    # Create a minimal but valid MP4 file for testing
    # This is a very basic MP4 structure that should be readable
    mp4_header = bytes([
        0x00, 0x00, 0x00, 0x20, 0x66, 0x74, 0x79, 0x70, 0x6D, 0x70, 0x34, 0x32,
        0x00, 0x00, 0x00, 0x00, 0x6D, 0x70, 0x34, 0x31, 0x6D, 0x70, 0x34, 0x32,
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ])
    
    with open("test_video.mp4", "wb") as f:
        f.write(mp4_header)
        # Add some dummy data to make it look like a real video
        f.write(b'\x00' * 1024)  # 1KB of zeros
    
    try:
        with open("test_video.mp4", "rb") as f:
            files = {'file': ('test_video.mp4', f, 'video/mp4')}
            response = requests.post(f"{BACKEND_URL}/api/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            upload_data = response.json()
            print(f"✅ Upload successful: {upload_data['file_id']}")
            file_id = upload_data['file_id']
            filename = upload_data['filename']
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False
    
    # Test analysis with detailed error handling
    print(f"\n2. Testing analysis with file_id: {file_id}")
    print(f"   Filename: {filename}")
    
    analysis_request = {
        "file_id": file_id,
        "filename": filename,
        "exercise_type": "back-squat"
    }
    
    try:
        print("   📤 Sending analysis request...")
        response = requests.post(
            f"{BACKEND_URL}/api/analyze",
            json=analysis_request,
            timeout=60  # 1 minute timeout for debugging
        )
        
        print(f"   📊 Response Status: {response.status_code}")
        print(f"   📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("   ✅ Analysis successful!")
            data = response.json()
            print(f"   📋 Response keys: {list(data.keys())}")
            if 'feedback' in data:
                feedback = data['feedback']
                print(f"   🎯 Overall Score: {feedback.get('overall_score', 'N/A')}")
        else:
            print(f"   ❌ Analysis failed: {response.status_code}")
            print(f"   📝 Error Response: {response.text}")
            
            # Try to parse as JSON for more details
            try:
                error_data = response.json()
                print(f"   📝 Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   📝 Raw Error: {response.text}")
                
    except requests.exceptions.Timeout:
        print("   ⏰ Analysis timed out")
    except Exception as e:
        print(f"   ❌ Analysis request failed: {e}")
    
    # Cleanup
    import os
    if os.path.exists("test_video.mp4"):
        os.remove("test_video.mp4")
        print(f"\n🧹 Cleaned up test file")
    
    return True

if __name__ == "__main__":
    test_detailed_analysis()
