#!/usr/bin/env python3
"""
Simple test script to debug analysis issues
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.storage import StorageService
from services.video_processor import VideoProcessor
from services.pose_analyzer import PoseAnalyzer
from services.movement_detector import MovementDetector
from services.squat_analyzer import SquatAnalyzer
from models.schemas import AnalysisRequest
import asyncio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_analysis_pipeline():
    """Test the analysis pipeline step by step"""
    try:
        logger.info("=== Testing Analysis Pipeline ===")
        
        # Initialize services
        logger.info("1. Initializing services...")
        storage_service = StorageService()
        video_processor = VideoProcessor()
        pose_analyzer = PoseAnalyzer()
        movement_detector = MovementDetector()
        squat_analyzer = SquatAnalyzer()
        
        logger.info("✅ All services initialized successfully")
        
        # Test with a dummy request
        logger.info("2. Testing with dummy request...")
        request = AnalysisRequest(
            file_id="test-123",
            filename="test.mp4",
            exercise_type="back-squat"
        )
        
        logger.info("✅ Dummy request created successfully")
        
        # Test service methods exist
        logger.info("3. Testing service methods...")
        
        # Check if methods exist
        assert hasattr(storage_service, 'download_video'), "StorageService missing download_video"
        assert hasattr(video_processor, 'extract_frames'), "VideoProcessor missing extract_frames"
        assert hasattr(pose_analyzer, 'analyze_poses'), "PoseAnalyzer missing analyze_poses"
        assert hasattr(movement_detector, 'detect_movement_period'), "MovementDetector missing detect_movement_period"
        assert hasattr(squat_analyzer, 'analyze'), "SquatAnalyzer missing analyze"
        
        logger.info("✅ All service methods exist")
        
        logger.info("=== Pipeline Test PASSED ===")
        return True
        
    except Exception as e:
        logger.error(f"❌ Pipeline Test FAILED: {e}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False

if __name__ == "__main__":
    result = asyncio.run(test_analysis_pipeline())
    sys.exit(0 if result else 1)
