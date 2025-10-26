#!/usr/bin/env python3
"""
Test service initialization to find the root cause
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_service_initialization():
    """Test if all services can be initialized"""
    print("🔧 Testing Service Initialization")
    print("=" * 50)
    
    try:
        print("1. Testing imports...")
        from services.storage import StorageService
        print("   ✅ StorageService imported")
        
        from services.video_processor import VideoProcessor
        print("   ✅ VideoProcessor imported")
        
        from services.pose_analyzer import PoseAnalyzer
        print("   ✅ PoseAnalyzer imported")
        
        from services.movement_detector import MovementDetector
        print("   ✅ MovementDetector imported")
        
        from services.squat_analyzer import SquatAnalyzer
        print("   ✅ SquatAnalyzer imported")
        
        from services.deadlift_analyzer import DeadliftAnalyzer
        print("   ✅ DeadliftAnalyzer imported")
        
        from services.front_squat_analyzer import FrontSquatAnalyzer
        print("   ✅ FrontSquatAnalyzer imported")
        
        from services.sumo_deadlift_analyzer import SumoDeadliftAnalyzer
        print("   ✅ SumoDeadliftAnalyzer imported")
        
        from models.schemas import AnalysisRequest, AnalysisResponse
        print("   ✅ Schemas imported")
        
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        print("\n2. Testing service initialization...")
        
        storage_service = StorageService()
        print("   ✅ StorageService initialized")
        
        video_processor = VideoProcessor()
        print("   ✅ VideoProcessor initialized")
        
        pose_analyzer = PoseAnalyzer()
        print("   ✅ PoseAnalyzer initialized")
        
        movement_detector = MovementDetector()
        print("   ✅ MovementDetector initialized")
        
        squat_analyzer = SquatAnalyzer()
        print("   ✅ SquatAnalyzer initialized")
        
        deadlift_analyzer = DeadliftAnalyzer()
        print("   ✅ DeadliftAnalyzer initialized")
        
        front_squat_analyzer = FrontSquatAnalyzer()
        print("   ✅ FrontSquatAnalyzer initialized")
        
        sumo_deadlift_analyzer = SumoDeadliftAnalyzer()
        print("   ✅ SumoDeadliftAnalyzer initialized")
        
    except Exception as e:
        print(f"   ❌ Service initialization failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        print("\n3. Testing method availability...")
        
        # Test if methods exist
        assert hasattr(storage_service, 'download_video'), "StorageService missing download_video"
        assert hasattr(video_processor, 'extract_frames'), "VideoProcessor missing extract_frames"
        assert hasattr(pose_analyzer, 'analyze_poses'), "PoseAnalyzer missing analyze_poses"
        assert hasattr(movement_detector, 'detect_movement_period'), "MovementDetector missing detect_movement_period"
        assert hasattr(squat_analyzer, 'analyze'), "SquatAnalyzer missing analyze"
        
        print("   ✅ All required methods exist")
        
    except Exception as e:
        print(f"   ❌ Method check failed: {e}")
        return False
    
    print("\n✅ All service initialization tests passed!")
    return True

if __name__ == "__main__":
    success = test_service_initialization()
    sys.exit(0 if success else 1)
