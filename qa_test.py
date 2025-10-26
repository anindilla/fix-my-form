#!/usr/bin/env python3
"""
End-to-end QA test script for Fix My Form
"""
import requests
import json
import time
import os
from pathlib import Path

# Configuration
BACKEND_URL = "https://fix-my-form.onrender.com"
FRONTEND_URL = "https://fix-my-form.vercel.app"

def test_upload_and_analysis():
    """Test the complete upload and analysis flow"""
    print("🧪 Starting End-to-End QA Test")
    print("=" * 50)
    
    # Test 1: Backend Health
    print("1. Testing Backend Health...")
    try:
        response = requests.get(f"{BACKEND_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ Backend is healthy")
        else:
            print(f"❌ Backend health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend health check failed: {e}")
        return False
    
    # Test 2: Create a test video (if we have one)
    print("\n2. Testing Video Upload...")
    
    # Check if we have any test videos
    test_videos = []
    for ext in ['mp4', 'mov', 'avi']:
        videos = list(Path('.').glob(f'**/*.{ext}'))
        test_videos.extend(videos)
    
    if not test_videos:
        print("⚠️  No test videos found, creating a dummy test...")
        # Create a minimal test video file
        test_video_path = "test_video.mp4"
        with open(test_video_path, 'wb') as f:
            # Write a minimal MP4 header (this won't be a real video, but tests the upload flow)
            f.write(b'\x00\x00\x00\x20ftypmp42\x00\x00\x00\x00mp41mp42')
        
        test_videos = [Path(test_video_path)]
    
    test_video = test_videos[0]
    print(f"📹 Using test video: {test_video}")
    
    # Test upload
    try:
        with open(test_video, 'rb') as f:
            files = {'file': (test_video.name, f, 'video/mp4')}
            response = requests.post(f"{BACKEND_URL}/api/upload", files=files, timeout=30)
        
        if response.status_code == 200:
            upload_data = response.json()
            print(f"✅ Upload successful: {upload_data['file_id']}")
            file_id = upload_data['file_id']
            filename = upload_data['filename']
        else:
            print(f"❌ Upload failed: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return False
    
    # Test 3: Analysis for each exercise type
    print("\n3. Testing Analysis Pipeline...")
    exercise_types = ["back-squat", "front-squat", "conventional-deadlift", "sumo-deadlift"]
    
    for exercise_type in exercise_types:
        print(f"\n   Testing {exercise_type}...")
        
        try:
            analysis_request = {
                "file_id": file_id,
                "filename": filename,
                "exercise_type": exercise_type
            }
            
            print(f"   📤 Sending analysis request...")
            response = requests.post(
                f"{BACKEND_URL}/api/analyze",
                json=analysis_request,
                timeout=300  # 5 minutes timeout
            )
            
            if response.status_code == 200:
                analysis_data = response.json()
                print(f"   ✅ {exercise_type} analysis completed")
                print(f"   📊 Status: {analysis_data.get('status', 'unknown')}")
                
                if 'feedback' in analysis_data:
                    feedback = analysis_data['feedback']
                    overall_score = feedback.get('overall_score', 'N/A')
                    print(f"   🎯 Overall Score: {overall_score}")
                    
                    if 'exercise_breakdown' in feedback:
                        breakdown = feedback['exercise_breakdown']
                        print(f"   📋 Breakdown scores:")
                        for key, value in breakdown.items():
                            if isinstance(value, dict):
                                score = value.get('score', 'N/A')
                                print(f"      - {key}: {score}")
                
                # Check for metrics
                if 'metrics' in analysis_data:
                    metrics = analysis_data['metrics']
                    if 'movement_analysis' in metrics:
                        movement = metrics['movement_analysis']
                        print(f"   🏃 Movement Analysis:")
                        print(f"      - Total frames: {movement.get('total_frames', 'N/A')}")
                        print(f"      - Movement frames: {movement.get('movement_frames', 'N/A')}")
                        print(f"      - Movement period: {movement.get('movement_period', 'N/A')}")
                
            elif response.status_code == 504:
                print(f"   ⏰ {exercise_type} analysis timed out")
            else:
                print(f"   ❌ {exercise_type} analysis failed: {response.status_code}")
                print(f"   📝 Error: {response.text}")
                
        except requests.exceptions.Timeout:
            print(f"   ⏰ {exercise_type} analysis timed out")
        except Exception as e:
            print(f"   ❌ {exercise_type} analysis failed: {e}")
    
    # Test 4: Check analysis results endpoint
    print(f"\n4. Testing Analysis Results Retrieval...")
    try:
        response = requests.get(f"{BACKEND_URL}/api/analysis/{file_id}", timeout=10)
        if response.status_code == 200:
            print("✅ Analysis results can be retrieved")
        else:
            print(f"❌ Analysis results retrieval failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Analysis results retrieval failed: {e}")
    
    # Cleanup
    if test_video.name == "test_video.mp4" and os.path.exists(test_video):
        os.remove(test_video)
        print(f"\n🧹 Cleaned up test file: {test_video}")
    
    print("\n" + "=" * 50)
    print("🎉 End-to-End QA Test Completed!")
    return True

if __name__ == "__main__":
    test_upload_and_analysis()
