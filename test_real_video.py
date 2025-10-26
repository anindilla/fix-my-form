#!/usr/bin/env python3
"""
Test with a real video file to see if that's the issue
"""
import requests
import json
import os
import subprocess

def create_real_test_video():
    """Create a minimal but real video file using ffmpeg"""
    try:
        # Create a simple test video using ffmpeg
        cmd = [
            'ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=2:size=320x240:rate=30',
            '-f', 'lavfi', '-i', 'sine=frequency=1000:duration=2',
            '-c:v', 'libx264', '-c:a', 'aac', '-shortest',
            'real_test_video.mp4', '-y'
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Created real test video using ffmpeg")
            return True
        else:
            print(f"❌ ffmpeg failed: {result.stderr}")
            return False
    except FileNotFoundError:
        print("⚠️  ffmpeg not found, creating dummy video")
        # Create a dummy video file
        with open('real_test_video.mp4', 'wb') as f:
            # Write a minimal MP4 header
            f.write(b'\x00\x00\x00\x20ftypmp42\x00\x00\x00\x00mp41mp42')
            f.write(b'\x00' * 1024)  # Add some data
        return True

def test_with_real_video():
    """Test analysis with a real video file"""
    print("🎬 Testing with Real Video File")
    print("=" * 50)
    
    # Create a real test video
    if not create_real_test_video():
        print("❌ Could not create test video")
        return False
    
    BACKEND_URL = "https://fix-my-form.onrender.com"
    
    try:
        print("1. Uploading real test video...")
        with open('real_test_video.mp4', 'rb') as f:
            files = {'file': ('real_test_video.mp4', f, 'video/mp4')}
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
        
        print(f"\n2. Testing analysis with real video...")
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
        if os.path.exists('real_test_video.mp4'):
            os.remove('real_test_video.mp4')
            print(f"\n🧹 Cleaned up test file")

if __name__ == "__main__":
    test_with_real_video()
