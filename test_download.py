#!/usr/bin/env python3
"""
Test if the issue is with video download from R2
"""
import requests
import json

def test_video_download():
    """Test if we can download a video from R2"""
    print("🔍 Testing Video Download from R2")
    print("=" * 50)
    
    BACKEND_URL = "https://fix-my-form.onrender.com"
    
    # First, upload a video
    print("1. Uploading test video...")
    
    # Create a minimal video file
    with open('test_video.mp4', 'wb') as f:
        f.write(b'\x00\x00\x00\x20ftypmp42\x00\x00\x00\x00mp41mp42')
        f.write(b'\x00' * 1024)
    
    try:
        with open('test_video.mp4', 'rb') as f:
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
        
        # Now test analysis with this specific file
        print(f"\n2. Testing analysis with uploaded file...")
        print(f"   File ID: {file_id}")
        print(f"   Filename: {filename}")
        
        analysis_request = {
            "file_id": file_id,
            "filename": filename,
            "exercise_type": "back-squat"
        }
        
        print("   📤 Sending analysis request...")
        response = requests.post(
            f"{BACKEND_URL}/api/analyze",
            json=analysis_request,
            timeout=60
        )
        
        print(f"   📊 Response Status: {response.status_code}")
        print(f"   📊 Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("   ✅ Analysis successful!")
            data = response.json()
            print(f"   📋 Response keys: {list(data.keys())}")
        else:
            print(f"   ❌ Analysis failed: {response.status_code}")
            print(f"   📝 Error Response: {response.text}")
            
            # Try to parse as JSON for more details
            try:
                error_data = response.json()
                print(f"   📝 Error Details: {json.dumps(error_data, indent=2)}")
            except:
                print(f"   📝 Raw Error: {response.text}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    finally:
        # Cleanup
        import os
        if os.path.exists('test_video.mp4'):
            os.remove('test_video.mp4')
            print(f"\n🧹 Cleaned up test file")

if __name__ == "__main__":
    test_video_download()
