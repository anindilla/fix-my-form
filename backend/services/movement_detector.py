import cv2
import numpy as np
import logging
from typing import List, Dict, Any, Tuple
from collections import deque
import mediapipe as mp

logger = logging.getLogger(__name__)

class MovementDetector:
    """Detects when actual exercise movement starts and ends in video"""
    
    def __init__(self):
        self.motion_threshold = 0.02  # Minimum motion to consider movement
        self.stability_threshold = 0.01  # Maximum motion to consider stable
        self.min_movement_frames = 10  # Minimum frames for valid movement
        self.stability_frames = 15  # Frames of stability to consider rest
        
    def detect_movement_period(self, pose_data: List[Dict], frames: List[str]) -> Tuple[int, int]:
        """
        Detect the start and end of actual exercise movement
        
        Args:
            pose_data: List of pose detection results
            frames: List of frame paths
            
        Returns:
            Tuple of (start_frame_index, end_frame_index) for movement period
        """
        if not pose_data or len(pose_data) < 10:
            logger.warning("Insufficient pose data for movement detection")
            return 0, len(pose_data) - 1
        
        logger.info(f"Analyzing movement in {len(pose_data)} frames")
        
        # Calculate motion between consecutive frames
        motion_scores = self._calculate_motion_scores(pose_data)
        
        # Find movement periods
        movement_periods = self._find_movement_periods(motion_scores)
        
        if not movement_periods:
            logger.warning("No movement periods detected, using entire video")
            return 0, len(pose_data) - 1
        
        # Select the longest movement period (main exercise)
        main_period = max(movement_periods, key=lambda p: p[1] - p[0])
        
        start_idx, end_idx = main_period
        logger.info(f"Detected movement period: frames {start_idx}-{end_idx} ({end_idx - start_idx + 1} frames)")
        
        return start_idx, end_idx
    
    def _calculate_motion_scores(self, pose_data: List[Dict]) -> List[float]:
        """Calculate motion score between consecutive frames"""
        motion_scores = []
        
        for i in range(1, len(pose_data)):
            prev_landmarks = pose_data[i-1]["landmarks"]
            curr_landmarks = pose_data[i]["landmarks"]
            
            # Calculate average movement of key body points
            motion_score = self._calculate_frame_motion(prev_landmarks, curr_landmarks)
            motion_scores.append(motion_score)
        
        return motion_scores
    
    def _calculate_frame_motion(self, prev_landmarks: List[Dict], curr_landmarks: List[Dict]) -> float:
        """Calculate motion between two frames using key landmarks"""
        if len(prev_landmarks) != len(curr_landmarks):
            return 0.0
        
        # Key landmarks for movement detection (joints that move during exercise)
        key_landmarks = [11, 12, 13, 14, 15, 16, 23, 24, 25, 26, 27, 28]  # Shoulders, elbows, wrists, hips, knees, ankles
        
        total_motion = 0.0
        valid_points = 0
        
        for landmark_id in key_landmarks:
            if (landmark_id < len(prev_landmarks) and landmark_id < len(curr_landmarks) and
                prev_landmarks[landmark_id]["visibility"] > 0.5 and 
                curr_landmarks[landmark_id]["visibility"] > 0.5):
                
                # Calculate Euclidean distance between landmark positions
                prev_x, prev_y = prev_landmarks[landmark_id]["x"], prev_landmarks[landmark_id]["y"]
                curr_x, curr_y = curr_landmarks[landmark_id]["x"], curr_landmarks[landmark_id]["y"]
                
                motion = np.sqrt((curr_x - prev_x)**2 + (curr_y - prev_y)**2)
                total_motion += motion
                valid_points += 1
        
        return total_motion / valid_points if valid_points > 0 else 0.0
    
    def _find_movement_periods(self, motion_scores: List[float]) -> List[Tuple[int, int]]:
        """Find periods of significant movement"""
        if not motion_scores:
            return []
        
        movement_periods = []
        in_movement = False
        movement_start = 0
        
        for i, motion in enumerate(motion_scores):
            if motion > self.motion_threshold:
                if not in_movement:
                    # Start of movement period
                    in_movement = True
                    movement_start = i
            else:
                if in_movement:
                    # End of movement period
                    movement_end = i
                    if movement_end - movement_start >= self.min_movement_frames:
                        movement_periods.append((movement_start, movement_end))
                    in_movement = False
        
        # Handle case where movement continues to end of video
        if in_movement and len(motion_scores) - movement_start >= self.min_movement_frames:
            movement_periods.append((movement_start, len(motion_scores) - 1))
        
        return movement_periods
    
    def _detect_setup_and_rest_periods(self, motion_scores: List[float]) -> Tuple[int, int]:
        """Detect setup period at start and rest period at end"""
        setup_end = 0
        rest_start = len(motion_scores)
        
        # Find end of setup period (low motion at start)
        for i, motion in enumerate(motion_scores[:len(motion_scores)//3]):  # Check first third
            if motion > self.motion_threshold:
                setup_end = i
                break
        
        # Find start of rest period (low motion at end)
        for i in range(len(motion_scores) - 1, len(motion_scores)//2, -1):  # Check last half
            if motion_scores[i] > self.motion_threshold:
                rest_start = i + 1
                break
        
        return setup_end, rest_start
    
    def get_movement_analysis(self, pose_data: List[Dict], frames: List[str]) -> Dict[str, Any]:
        """Get comprehensive movement analysis"""
        if not pose_data:
            return {"error": "No pose data available"}
        
        motion_scores = self._calculate_motion_scores(pose_data)
        movement_periods = self._find_movement_periods(motion_scores)
        setup_end, rest_start = self._detect_setup_and_rest_periods(motion_scores)
        
        # Calculate statistics
        avg_motion = np.mean(motion_scores) if motion_scores else 0
        max_motion = np.max(motion_scores) if motion_scores else 0
        
        return {
            "total_frames": len(pose_data),
            "movement_periods": movement_periods,
            "setup_frames": setup_end,
            "rest_frames": len(pose_data) - rest_start,
            "active_frames": rest_start - setup_end,
            "avg_motion": avg_motion,
            "max_motion": max_motion,
            "motion_scores": motion_scores
        }
