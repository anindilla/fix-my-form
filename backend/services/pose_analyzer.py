import mediapipe as mp
import cv2
import numpy as np
from typing import List, Dict, Any
import json

class PoseAnalyzer:
    def __init__(self):
        self.mp_pose = mp.solutions.pose
        try:
            self.pose = self.mp_pose.Pose(
                static_image_mode=False,
                model_complexity=1,  # Reduced complexity for better compatibility
                enable_segmentation=False,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        except Exception as e:
            print(f"Warning: Could not initialize MediaPipe pose model: {e}")
            print("Falling back to basic pose detection...")
            self.pose = None
        self.mp_drawing = mp.solutions.drawing_utils
    
    async def analyze_poses(self, frame_paths: List[str]) -> List[Dict[str, Any]]:
        """Analyze poses in video frames"""
        pose_data = []
        
        if self.pose is None:
            print("MediaPipe not available, returning empty pose data")
            return pose_data
        
        for i, frame_path in enumerate(frame_paths):
            try:
                # Read frame
                frame = cv2.imread(frame_path)
                if frame is None:
                    continue
                
                # Convert BGR to RGB
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Process frame
                results = self.pose.process(rgb_frame)
                
                if results.pose_landmarks:
                    landmarks = []
                    for landmark in results.pose_landmarks.landmark:
                        landmarks.append({
                            "x": landmark.x,
                            "y": landmark.y,
                            "z": landmark.z,
                            "visibility": landmark.visibility
                        })
                    
                    pose_data.append({
                        "frame_index": i,
                        "timestamp": i / 30.0,  # Assuming 30 FPS
                        "landmarks": landmarks,
                        "frame_path": frame_path
                    })
                
            except Exception as e:
                print(f"Error processing frame {frame_path}: {str(e)}")
                continue
        
        return pose_data
    
    def get_landmark_coords(self, landmarks: List[Dict], landmark_id: int) -> tuple:
        """Get coordinates for specific landmark"""
        if landmark_id < len(landmarks):
            landmark = landmarks[landmark_id]
            return (landmark["x"], landmark["y"])
        return (0, 0)
    
    def calculate_angle(self, point1: tuple, point2: tuple, point3: tuple) -> float:
        """Calculate angle between three points"""
        try:
            # Convert to numpy arrays
            p1 = np.array(point1)
            p2 = np.array(point2)
            p3 = np.array(point3)
            
            # Calculate vectors
            v1 = p1 - p2
            v2 = p3 - p2
            
            # Calculate angle
            cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
            cos_angle = np.clip(cos_angle, -1.0, 1.0)  # Avoid numerical errors
            angle = np.arccos(cos_angle)
            
            return np.degrees(angle)
        except:
            return 0.0
    
    def calculate_distance(self, point1: tuple, point2: tuple) -> float:
        """Calculate distance between two points"""
        try:
            p1 = np.array(point1)
            p2 = np.array(point2)
            return np.linalg.norm(p1 - p2)
        except:
            return 0.0
