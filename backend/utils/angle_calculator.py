import numpy as np
from typing import List, Dict, Any, Tuple

class AngleCalculator:
    """Utility class for calculating joint angles and body positions"""
    
    # MediaPipe pose landmark indices
    NOSE = 0
    LEFT_EYE_INNER = 1
    LEFT_EYE = 2
    LEFT_EYE_OUTER = 3
    RIGHT_EYE_INNER = 4
    RIGHT_EYE = 5
    RIGHT_EYE_OUTER = 6
    LEFT_EAR = 7
    RIGHT_EAR = 8
    MOUTH_LEFT = 9
    MOUTH_RIGHT = 10
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_PINKY = 17
    RIGHT_PINKY = 18
    LEFT_INDEX = 19
    RIGHT_INDEX = 20
    LEFT_THUMB = 21
    RIGHT_THUMB = 22
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28
    LEFT_HEEL = 29
    RIGHT_HEEL = 30
    LEFT_FOOT_INDEX = 31
    RIGHT_FOOT_INDEX = 32
    
    @staticmethod
    def get_landmark_coords(landmarks: List[Dict], landmark_id: int) -> Tuple[float, float]:
        """Get coordinates for specific landmark"""
        if landmark_id < len(landmarks):
            landmark = landmarks[landmark_id]
            return (landmark["x"], landmark["y"])
        return (0.0, 0.0)
    
    @staticmethod
    def calculate_angle(point1: Tuple[float, float], point2: Tuple[float, float], point3: Tuple[float, float]) -> float:
        """Calculate angle between three points (point2 is the vertex)"""
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
    
    @staticmethod
    def calculate_distance(point1: Tuple[float, float], point2: Tuple[float, float]) -> float:
        """Calculate distance between two points"""
        try:
            p1 = np.array(point1)
            p2 = np.array(point2)
            return np.linalg.norm(p1 - p2)
        except:
            return 0.0
    
    @staticmethod
    def get_hip_depth(landmarks: List[Dict]) -> float:
        """Calculate hip depth relative to knees (for squat analysis)"""
        left_hip = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.LEFT_HIP)
        right_hip = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.RIGHT_HIP)
        left_knee = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.LEFT_KNEE)
        right_knee = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.RIGHT_KNEE)
        
        # Average hip and knee positions
        hip_y = (left_hip[1] + right_hip[1]) / 2
        knee_y = (left_knee[1] + right_knee[1]) / 2
        
        # Return difference (positive means hips below knees)
        return hip_y - knee_y
    
    @staticmethod
    def get_knee_angle(landmarks: List[Dict], side: str = "left") -> float:
        """Calculate knee angle"""
        if side == "left":
            hip = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.LEFT_HIP)
            knee = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.LEFT_KNEE)
            ankle = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.LEFT_ANKLE)
        else:
            hip = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.RIGHT_HIP)
            knee = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.RIGHT_KNEE)
            ankle = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.RIGHT_ANKLE)
        
        return AngleCalculator.calculate_angle(hip, knee, ankle)
    
    @staticmethod
    def get_hip_angle(landmarks: List[Dict], side: str = "left") -> float:
        """Calculate hip angle"""
        if side == "left":
            shoulder = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.LEFT_SHOULDER)
            hip = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.LEFT_HIP)
            knee = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.LEFT_KNEE)
        else:
            shoulder = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.RIGHT_SHOULDER)
            hip = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.RIGHT_HIP)
            knee = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.RIGHT_KNEE)
        
        return AngleCalculator.calculate_angle(shoulder, hip, knee)
    
    @staticmethod
    def get_back_angle(landmarks: List[Dict]) -> float:
        """Calculate back angle from vertical"""
        left_shoulder = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.LEFT_SHOULDER)
        right_shoulder = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.RIGHT_SHOULDER)
        left_hip = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.LEFT_HIP)
        right_hip = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.RIGHT_HIP)
        
        # Average shoulder and hip positions
        shoulder_center = ((left_shoulder[0] + right_shoulder[0]) / 2, (left_shoulder[1] + right_shoulder[1]) / 2)
        hip_center = ((left_hip[0] + right_hip[0]) / 2, (left_hip[1] + right_hip[1]) / 2)
        
        # Calculate angle from vertical
        dx = shoulder_center[0] - hip_center[0]
        dy = shoulder_center[1] - hip_center[1]
        
        if dx == 0:
            return 0
        
        angle = np.degrees(np.arctan2(dx, dy))
        return abs(angle)  # Return absolute value for back angle
    
    @staticmethod
    def get_knee_valgus(landmarks: List[Dict]) -> float:
        """Calculate knee valgus (knees caving inward)"""
        left_hip = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.LEFT_HIP)
        left_knee = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.LEFT_KNEE)
        left_ankle = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.LEFT_ANKLE)
        
        right_hip = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.RIGHT_HIP)
        right_knee = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.RIGHT_KNEE)
        right_ankle = AngleCalculator.get_landmark_coords(landmarks, AngleCalculator.RIGHT_ANKLE)
        
        # Calculate knee valgus for both sides
        left_valgus = left_knee[0] - left_ankle[0]  # Positive means knee inward
        right_valgus = right_ankle[0] - right_knee[0]  # Positive means knee inward
        
        return (left_valgus + right_valgus) / 2

# Convenience function for backward compatibility
def calculate_angle(point1: Tuple[float, float], point2: Tuple[float, float], point3: Tuple[float, float]) -> float:
    """Calculate angle between three points (point2 is the vertex)"""
    return AngleCalculator.calculate_angle(point1, point2, point3)
