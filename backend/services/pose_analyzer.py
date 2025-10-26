import mediapipe as mp
import cv2
import numpy as np
import logging
from typing import List, Dict, Any
import json

logger = logging.getLogger(__name__)

class PoseAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        try:
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,  # Balance speed/accuracy
                enable_segmentation=False,
                smooth_landmarks=True,
                min_detection_confidence=0.3,  # More lenient threshold
                min_tracking_confidence=0.3   # More lenient threshold
            )
            logger.info("MediaPipe pose model initialized with quality-focused configuration")
        except Exception as e:
            logger.error(f"Could not initialize MediaPipe pose model: {e}")
            logger.warning("Falling back to basic pose detection...")
            self.pose = None
        self.mp_drawing = mp.solutions.drawing_utils
    
    async def analyze_poses(self, frame_paths: List[str]) -> List[Dict[str, Any]]:
        """Analyze poses in video frames with improved validation"""
        pose_data = []
        
        if self.pose is None:
            logger.error("MediaPipe not available, returning empty pose data")
            return pose_data
        
        logger.info(f"Processing {len(frame_paths)} frames with improved MediaPipe configuration")
        
        for i, frame_path in enumerate(frame_paths):
            try:
                # Read frame
                frame = cv2.imread(frame_path)
                if frame is None:
                    logger.warning(f"Could not read frame: {frame_path}")
                    continue
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process frame
                results = self.pose.process(rgb_frame)
                
                if results.pose_landmarks:
                    landmarks = []
                    visible_count = 0
                    
                    for landmark in results.pose_landmarks.landmark:
                        lm = {
                            "x": landmark.x,
                            "y": landmark.y,
                            "z": landmark.z,
                            "visibility": landmark.visibility
                        }
                        landmarks.append(lm)
                        if landmark.visibility >= 0.5:  # More lenient confidence threshold
                            visible_count += 1
                    
                    # Only accept frames with sufficient landmark visibility
                    if visible_count >= 10:  # Require at least 10 visible landmarks (more lenient)
                        pose_data.append({
                            "frame_index": i,
                            "timestamp": i / 30.0,  # Assuming 30 FPS
                            "landmarks": landmarks,
                            "frame_path": frame_path,
                            "visible_landmarks": visible_count
                        })
                        logger.debug(f"Frame {i}: {visible_count}/33 landmarks visible")
                    else:
                        logger.warning(f"Frame {i}: Only {visible_count}/33 landmarks visible - skipping")
                else:
                    logger.warning(f"Frame {i}: No pose detected")
                
            except Exception as e:
                logger.error(f"Error processing frame {frame_path}: {e}")
                continue
        
        logger.info(f"Successfully processed {len(pose_data)}/{len(frame_paths)} frames")
        return pose_data
    
    def create_diagnostic_error(self, pose_data: List[Dict], total_frames: int) -> Dict[str, Any]:
        """Create detailed diagnostic error when pose detection fails"""
        success_rate = len(pose_data) / total_frames * 100 if total_frames > 0 else 0
        
        # Calculate average visible landmarks
        avg_visible_landmarks = 0
        if pose_data:
            total_visible = sum(frame.get("visible_landmarks", 0) for frame in pose_data)
            avg_visible_landmarks = total_visible / len(pose_data)
        
        issues = []
        recommendations = []
        
        if success_rate < 60:
            issues.append(f"Only {len(pose_data)}/{total_frames} frames had detectable pose (need {int(total_frames * 0.6)}+)")
        
        if avg_visible_landmarks < 15:
            issues.append(f"Average {avg_visible_landmarks:.1f}/33 landmarks visible (need 15+)")
        
        if success_rate < 30:
            issues.append("Person may be too far from camera")
            recommendations.append("Record from 6-10 feet away")
        
        if avg_visible_landmarks < 10:
            issues.append("Lighting may be insufficient")
            recommendations.append("Use good lighting (natural or bright indoor)")
        
        if not issues:
            issues.append("Pose detection failed for unknown reasons")
        
        if not recommendations:
            recommendations.extend([
                "Ensure full body is visible in frame",
                "Film from side angle (90° to movement)",
                "Avoid busy backgrounds",
                "Ensure person is wearing contrasting colors"
            ])
        
        return {
            "overall_score": 0,
            "diagnostic": {
                "total_frames": total_frames,
                "frames_with_pose": len(pose_data),
                "success_rate": round(success_rate, 1),
                "avg_visible_landmarks": round(avg_visible_landmarks, 1),
                "issues": issues,
                "recommendations": recommendations
            }
        }
    
    def get_landmark_coords(self, landmarks: List[Dict], landmark_id: int) -> tuple:
        """Get coordinates for specific landmark"""
        if landmark_id < len(landmarks):
            landmark = landmarks[landmark_id]
            return (landmark["x"], landmark["y"])
        return (0, 0)
    
    def calculate_angle(self, point1: tuple, point2: tuple, point3: tuple) -> float:
        """Calculate angle between three points with validation"""
        try:
            # Convert to numpy arrays
            p1 = np.array(point1)
            p2 = np.array(point2)
            p3 = np.array(point3)
            
            # Calculate vectors
            v1 = p1 - p2
            v2 = p3 - p2
            
            # Check for zero vectors
            norm1 = np.linalg.norm(v1)
            norm2 = np.linalg.norm(v2)
            
            if norm1 < 1e-6 or norm2 < 1e-6:
                logger.debug("Angle calculation skipped - zero vector detected")
                return None
            
            # Calculate angle
            cos_angle = np.dot(v1, v2) / (norm1 * norm2)
            cos_angle = np.clip(cos_angle, -1.0, 1.0)  # Avoid numerical errors
            angle = np.arccos(cos_angle)
            
            result = np.degrees(angle)
            # Validate result
            if 0 <= result <= 180:
                return result
            return None
        except Exception as e:
            logger.error(f"Angle calculation error: {e}")
            return None
    
    def calculate_distance(self, point1: tuple, point2: tuple) -> float:
        """Calculate distance between two points with validation"""
        try:
            p1 = np.array(point1)
            p2 = np.array(point2)
            distance = np.linalg.norm(p1 - p2)
            if distance < 0:
                logger.warning(f"Invalid distance: {distance}")
                return None
            return distance
        except Exception as e:
            logger.error(f"Distance calculation error: {e}")
            return None
