import cv2
import os
import logging
from typing import Dict, List, Any
import numpy as np

logger = logging.getLogger(__name__)

class VideoQualityValidator:
    """Validates video quality before analysis to ensure good pose detection"""
    
    def __init__(self):
        self.min_resolution = (480, 360)  # Minimum width x height
        self.min_duration = 2.0  # seconds
        self.max_duration = 60.0  # seconds
        self.min_fps = 15
        self.min_visibility_frames = 0.5  # 50% of frames should have person visible
        
    async def validate_video(self, video_path: str) -> Dict[str, Any]:
        """
        Validates video quality for pose analysis
        
        Returns:
            {
                "valid": bool,
                "issues": List[str],
                "metadata": Dict,
                "quality_score": float  # 0-100
            }
        """
        try:
            logger.info(f"Validating video quality: {video_path}")
            
            # Get video metadata
            metadata = await self._get_video_metadata(video_path)
            if not metadata:
                return {
                    "valid": False,
                    "issues": ["Could not read video file - file may be corrupted"],
                    "metadata": {},
                    "quality_score": 0
                }
            
            issues = []
            quality_score = 100
            
            # Check resolution
            width, height = metadata["width"], metadata["height"]
            if width < self.min_resolution[0] or height < self.min_resolution[1]:
                issues.append(f"Resolution too low: {width}x{height} (minimum: {self.min_resolution[0]}x{self.min_resolution[1]})")
                quality_score -= 30
            
            # Check duration
            duration = metadata["duration"]
            if duration < self.min_duration:
                issues.append(f"Video too short: {duration:.1f}s (minimum: {self.min_duration}s)")
                quality_score -= 25
            elif duration > self.max_duration:
                issues.append(f"Video too long: {duration:.1f}s (maximum: {self.max_duration}s)")
                quality_score -= 15
            
            # Check FPS
            fps = metadata["fps"]
            if fps < self.min_fps:
                issues.append(f"Frame rate too low: {fps:.1f} fps (minimum: {self.min_fps} fps)")
                quality_score -= 20
            
            # Check if person is visible in frames
            visibility_score = await self._check_person_visibility(video_path)
            if visibility_score < self.min_visibility_frames:
                issues.append(f"Person not clearly visible: {visibility_score:.1%} of frames (minimum: {self.min_visibility_frames:.1%})")
                quality_score -= 25
            
            # Determine if video is valid
            valid = len(issues) == 0
            
            logger.info(f"Video validation complete - Valid: {valid}, Score: {quality_score}, Issues: {len(issues)}")
            
            return {
                "valid": valid,
                "issues": issues,
                "metadata": metadata,
                "quality_score": max(0, quality_score)
            }
            
        except Exception as e:
            logger.error(f"Video validation failed: {e}")
            return {
                "valid": False,
                "issues": [f"Validation error: {str(e)}"],
                "metadata": {},
                "quality_score": 0
            }
    
    async def _get_video_metadata(self, video_path: str) -> Dict[str, Any]:
        """Extract video metadata using OpenCV"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if not cap.isOpened():
                logger.error(f"Could not open video: {video_path}")
                return None
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                "frame_count": frame_count,
                "fps": fps,
                "width": width,
                "height": height,
                "duration": duration
            }
            
        except Exception as e:
            logger.error(f"Failed to get video metadata: {e}")
            return None
    
    async def _check_person_visibility(self, video_path: str) -> float:
        """
        Check if a person is visible in the video by sampling frames
        Returns the percentage of frames where a person is detected
        """
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return 0.0
            
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Sample up to 10 frames evenly distributed across the video
            sample_frames = min(10, frame_count)
            frame_interval = max(1, frame_count // sample_frames)
            
            person_detected_count = 0
            sampled_frames = 0
            
            frame_number = 0
            while cap.isOpened() and sampled_frames < sample_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_number % frame_interval == 0:
                    # Simple person detection: check for reasonable amount of movement/edges
                    # This is a basic heuristic - in production you might use a proper person detector
                    if self._has_person_like_content(frame):
                        person_detected_count += 1
                    sampled_frames += 1
                
                frame_number += 1
            
            cap.release()
            
            visibility_ratio = person_detected_count / sampled_frames if sampled_frames > 0 else 0.0
            logger.debug(f"Person visibility check: {person_detected_count}/{sampled_frames} frames ({visibility_ratio:.1%})")
            
            return visibility_ratio
            
        except Exception as e:
            logger.error(f"Person visibility check failed: {e}")
            return 0.0
    
    def _has_person_like_content(self, frame) -> bool:
        """
        Basic heuristic to detect if frame likely contains a person
        Uses edge detection and motion analysis
        """
        try:
            # Convert to grayscale
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply edge detection
            edges = cv2.Canny(gray, 50, 150)
            
            # Count edge pixels
            edge_pixels = np.sum(edges > 0)
            total_pixels = edges.shape[0] * edges.shape[1]
            edge_ratio = edge_pixels / total_pixels
            
            # Heuristic: if there are enough edges, likely contains a person
            # This is a simple approach - could be improved with proper person detection
            return edge_ratio > 0.05  # 5% of pixels are edges
            
        except Exception as e:
            logger.error(f"Person detection heuristic failed: {e}")
            return False
