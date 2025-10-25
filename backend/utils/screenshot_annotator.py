import cv2
import numpy as np
from typing import List, Dict, Any, Tuple
import os
from utils.angle_calculator import AngleCalculator

class ScreenshotAnnotator:
    def __init__(self):
        self.angle_calc = AngleCalculator()
        self.temp_dir = "/tmp/annotated"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def annotate_squat(self, frame_path: str, landmarks: List[Dict], filename: str) -> str:
        """Create annotated screenshot for squat analysis"""
        try:
            # Load image
            image = cv2.imread(frame_path)
            if image is None:
                raise Exception("Could not load image")
            
            # Create a copy for annotation
            annotated = image.copy()
            
            # Draw pose landmarks
            self._draw_pose_landmarks(annotated, landmarks)
            
            # Analyze and highlight issues
            issues = self._analyze_squat_issues(landmarks)
            
            # Draw annotations for each issue
            for i, issue in enumerate(issues):
                self._draw_squat_annotation(annotated, issue, i)
            
            # Save annotated image
            output_path = os.path.join(self.temp_dir, filename)
            cv2.imwrite(output_path, annotated)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Failed to annotate squat: {str(e)}")
    
    async def annotate_deadlift(self, frame_path: str, landmarks: List[Dict], filename: str) -> str:
        """Create annotated screenshot for deadlift analysis"""
        try:
            # Load image
            image = cv2.imread(frame_path)
            if image is None:
                raise Exception("Could not load image")
            
            # Create a copy for annotation
            annotated = image.copy()
            
            # Draw pose landmarks
            self._draw_pose_landmarks(annotated, landmarks)
            
            # Analyze and highlight issues
            issues = self._analyze_deadlift_issues(landmarks)
            
            # Draw annotations for each issue
            for i, issue in enumerate(issues):
                self._draw_deadlift_annotation(annotated, issue, i)
            
            # Save annotated image
            output_path = os.path.join(self.temp_dir, filename)
            cv2.imwrite(output_path, annotated)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Failed to annotate deadlift: {str(e)}")
    
    def _draw_pose_landmarks(self, image: np.ndarray, landmarks: List[Dict]):
        """Draw pose landmarks on image"""
        height, width = image.shape[:2]
        
        # Draw key landmarks
        key_points = [
            AngleCalculator.LEFT_SHOULDER,
            AngleCalculator.RIGHT_SHOULDER,
            AngleCalculator.LEFT_HIP,
            AngleCalculator.RIGHT_HIP,
            AngleCalculator.LEFT_KNEE,
            AngleCalculator.RIGHT_KNEE,
            AngleCalculator.LEFT_ANKLE,
            AngleCalculator.RIGHT_ANKLE
        ]
        
        for point_id in key_points:
            if point_id < len(landmarks):
                landmark = landmarks[point_id]
                x = int(landmark["x"] * width)
                y = int(landmark["y"] * height)
                
                if landmark["visibility"] > 0.5:  # Only draw if landmark is visible
                    cv2.circle(image, (x, y), 5, (0, 255, 0), -1)
    
    def _analyze_squat_issues(self, landmarks: List[Dict]) -> List[Dict]:
        """Analyze squat form issues"""
        issues = []
        
        # Check depth
        hip_depth = self.angle_calc.get_hip_depth(landmarks)
        if hip_depth < -0.05:
            issues.append({
                "type": "depth",
                "message": "Not reaching proper depth",
                "position": self._get_hip_position(landmarks)
            })
        
        # Check knee valgus
        knee_valgus = self.angle_calc.get_knee_valgus(landmarks)
        if abs(knee_valgus) > 0.1:
            issues.append({
                "type": "knee_tracking",
                "message": "Knees caving inward",
                "position": self._get_knee_position(landmarks)
            })
        
        # Check back angle
        back_angle = self.angle_calc.get_back_angle(landmarks)
        if back_angle > 45:
            issues.append({
                "type": "back_angle",
                "message": "Excessive forward lean",
                "position": self._get_shoulder_position(landmarks)
            })
        
        return issues
    
    def _analyze_deadlift_issues(self, landmarks: List[Dict]) -> List[Dict]:
        """Analyze deadlift form issues"""
        issues = []
        
        # Check back rounding
        back_angle = self.angle_calc.get_back_angle(landmarks)
        if back_angle > 30:
            issues.append({
                "type": "back_rounding",
                "message": "Back rounding detected",
                "position": self._get_shoulder_position(landmarks)
            })
        
        # Check hip angle
        left_hip_angle = self.angle_calc.get_hip_angle(landmarks, "left")
        right_hip_angle = self.angle_calc.get_hip_angle(landmarks, "right")
        avg_hip_angle = (left_hip_angle + right_hip_angle) / 2
        
        if avg_hip_angle > 120:
            issues.append({
                "type": "hip_angle",
                "message": "Hips too high - not a squat",
                "position": self._get_hip_position(landmarks)
            })
        
        return issues
    
    def _draw_squat_annotation(self, image: np.ndarray, issue: Dict, index: int):
        """Draw annotation for squat issue"""
        height, width = image.shape[:2]
        position = issue["position"]
        
        # Convert normalized coordinates to pixel coordinates
        x = int(position[0] * width)
        y = int(position[1] * height)
        
        # Choose color based on issue type
        colors = {
            "depth": (0, 0, 255),      # Red
            "knee_tracking": (0, 255, 255),  # Yellow
            "back_angle": (255, 0, 0)  # Blue
        }
        color = colors.get(issue["type"], (255, 255, 255))
        
        # Draw arrow pointing to issue
        cv2.arrowedLine(image, (x, y - 50), (x, y), color, 3)
        
        # Draw text box with issue message
        text = issue["message"]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Draw background rectangle
        cv2.rectangle(image, 
                     (x - text_width//2 - 10, y - text_height - 20),
                     (x + text_width//2 + 10, y + baseline),
                     (0, 0, 0), -1)
        
        # Draw text
        cv2.putText(image, text, 
                   (x - text_width//2, y - 5),
                   font, font_scale, color, thickness)
    
    def _draw_deadlift_annotation(self, image: np.ndarray, issue: Dict, index: int):
        """Draw annotation for deadlift issue"""
        height, width = image.shape[:2]
        position = issue["position"]
        
        # Convert normalized coordinates to pixel coordinates
        x = int(position[0] * width)
        y = int(position[1] * height)
        
        # Choose color based on issue type
        colors = {
            "back_rounding": (0, 0, 255),      # Red
            "hip_angle": (0, 255, 255),       # Yellow
            "bar_path": (255, 0, 0)           # Blue
        }
        color = colors.get(issue["type"], (255, 255, 255))
        
        # Draw arrow pointing to issue
        cv2.arrowedLine(image, (x, y - 50), (x, y), color, 3)
        
        # Draw text box with issue message
        text = issue["message"]
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 0.6
        thickness = 2
        
        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)
        
        # Draw background rectangle
        cv2.rectangle(image, 
                     (x - text_width//2 - 10, y - text_height - 20),
                     (x + text_width//2 + 10, y + baseline),
                     (0, 0, 0), -1)
        
        # Draw text
        cv2.putText(image, text, 
                   (x - text_width//2, y - 5),
                   font, font_scale, color, thickness)
    
    def _get_hip_position(self, landmarks: List[Dict]) -> Tuple[float, float]:
        """Get hip center position"""
        left_hip = self.angle_calc.get_landmark_coords(landmarks, AngleCalculator.LEFT_HIP)
        right_hip = self.angle_calc.get_landmark_coords(landmarks, AngleCalculator.RIGHT_HIP)
        return ((left_hip[0] + right_hip[0]) / 2, (left_hip[1] + right_hip[1]) / 2)
    
    def _get_knee_position(self, landmarks: List[Dict]) -> Tuple[float, float]:
        """Get knee center position"""
        left_knee = self.angle_calc.get_landmark_coords(landmarks, AngleCalculator.LEFT_KNEE)
        right_knee = self.angle_calc.get_landmark_coords(landmarks, AngleCalculator.RIGHT_KNEE)
        return ((left_knee[0] + right_knee[0]) / 2, (left_knee[1] + right_knee[1]) / 2)
    
    def _get_shoulder_position(self, landmarks: List[Dict]) -> Tuple[float, float]:
        """Get shoulder center position"""
        left_shoulder = self.angle_calc.get_landmark_coords(landmarks, AngleCalculator.LEFT_SHOULDER)
        right_shoulder = self.angle_calc.get_landmark_coords(landmarks, AngleCalculator.RIGHT_SHOULDER)
        return ((left_shoulder[0] + right_shoulder[0]) / 2, (left_shoulder[1] + right_shoulder[1]) / 2)
    
    async def annotate_front_squat(self, frame_path: str, landmarks: List[Dict], filename: str) -> str:
        """Create annotated screenshot for front squat analysis"""
        try:
            # Load image
            image = cv2.imread(frame_path)
            if image is None:
                raise Exception("Could not load image")
            
            # Create a copy for annotation
            annotated = image.copy()
            
            # Draw pose landmarks
            self._draw_pose_landmarks(annotated, landmarks)
            
            # Analyze and highlight issues
            issues = self._analyze_front_squat_issues(landmarks)
            
            # Draw annotations for each issue
            for issue in issues:
                self._draw_annotation(annotated, issue)
            
            # Save annotated image
            output_path = os.path.join(self.temp_dir, f"{filename}.jpg")
            cv2.imwrite(output_path, annotated)
            
            return output_path
            
        except Exception as e:
            print(f"Error annotating front squat: {e}")
            return frame_path
    
    async def annotate_sumo_deadlift(self, frame_path: str, landmarks: List[Dict], filename: str) -> str:
        """Create annotated screenshot for sumo deadlift analysis"""
        try:
            # Load image
            image = cv2.imread(frame_path)
            if image is None:
                raise Exception("Could not load image")
            
            # Create a copy for annotation
            annotated = image.copy()
            
            # Draw pose landmarks
            self._draw_pose_landmarks(annotated, landmarks)
            
            # Analyze and highlight issues
            issues = self._analyze_sumo_deadlift_issues(landmarks)
            
            # Draw annotations for each issue
            for issue in issues:
                self._draw_annotation(annotated, issue)
            
            # Save annotated image
            output_path = os.path.join(self.temp_dir, f"{filename}.jpg")
            cv2.imwrite(output_path, annotated)
            
            return output_path
            
        except Exception as e:
            print(f"Error annotating sumo deadlift: {e}")
            return frame_path
    
    def _analyze_front_squat_issues(self, landmarks: List[Dict]) -> List[Dict]:
        """Analyze front squat specific issues"""
        issues = []
        
        try:
            # Check torso position (should be more upright for front squat)
            torso_angle = self._calculate_torso_angle(landmarks)
            if torso_angle < 80:
                issues.append({
                    "type": "torso_too_upright",
                    "message": "Torso too upright - allow slight forward lean",
                    "position": self._get_torso_center(landmarks),
                    "color": (0, 255, 255)  # Yellow
                })
            elif torso_angle > 100:
                issues.append({
                    "type": "torso_too_forward",
                    "message": "Torso leaning too far forward",
                    "position": self._get_torso_center(landmarks),
                    "color": (0, 0, 255)  # Red
                })
            
            # Check hip depth
            hip_angle = self._calculate_hip_angle(landmarks)
            if hip_angle > 120:
                issues.append({
                    "type": "insufficient_depth",
                    "message": "Not reaching full depth",
                    "position": self._get_hip_position(landmarks),
                    "color": (0, 0, 255)  # Red
                })
            
            # Check knee tracking
            knee_angle = self._calculate_knee_angle(landmarks)
            if knee_angle < 80 or knee_angle > 120:
                issues.append({
                    "type": "knee_tracking",
                    "message": "Keep knees tracking over toes",
                    "position": self._get_knee_position(landmarks),
                    "color": (0, 255, 0)  # Green
                })
                
        except Exception as e:
            print(f"Error analyzing front squat issues: {e}")
        
        return issues
    
    def _analyze_sumo_deadlift_issues(self, landmarks: List[Dict]) -> List[Dict]:
        """Analyze sumo deadlift specific issues"""
        issues = []
        
        try:
            # Check stance width
            stance_width = self._calculate_stance_width(landmarks)
            if stance_width < 15:
                issues.append({
                    "type": "stance_too_narrow",
                    "message": "Stance too narrow for sumo deadlift",
                    "position": self._get_foot_center(landmarks),
                    "color": (0, 255, 255)  # Yellow
                })
            
            # Check hip position
            hip_angle = self._calculate_hip_angle(landmarks)
            if hip_angle < 70:
                issues.append({
                    "type": "hips_too_low",
                    "message": "Hips too low - raise them slightly",
                    "position": self._get_hip_position(landmarks),
                    "color": (0, 255, 0)  # Green
                })
            elif hip_angle > 110:
                issues.append({
                    "type": "hips_too_high",
                    "message": "Hips too high - lower them",
                    "position": self._get_hip_position(landmarks),
                    "color": (0, 0, 255)  # Red
                })
            
            # Check torso position
            torso_angle = self._calculate_torso_angle(landmarks)
            if torso_angle < 85:
                issues.append({
                    "type": "torso_too_upright",
                    "message": "Torso too upright",
                    "position": self._get_torso_center(landmarks),
                    "color": (0, 255, 255)  # Yellow
                })
            elif torso_angle > 105:
                issues.append({
                    "type": "torso_too_forward",
                    "message": "Torso leaning too far forward",
                    "position": self._get_torso_center(landmarks),
                    "color": (0, 0, 255)  # Red
                })
                
        except Exception as e:
            print(f"Error analyzing sumo deadlift issues: {e}")
        
        return issues
    
    def _calculate_stance_width(self, landmarks: List[Dict]) -> float:
        """Calculate stance width for sumo deadlift"""
        try:
            left_ankle = landmarks[27]
            right_ankle = landmarks[28]
            
            distance = np.sqrt(
                (left_ankle['x'] - right_ankle['x'])**2 + 
                (left_ankle['y'] - right_ankle['y'])**2
            )
            
            return distance * 100
        except:
            return 0
    
    def _get_foot_center(self, landmarks: List[Dict]) -> Tuple[int, int]:
        """Get center position between feet"""
        try:
            left_ankle = landmarks[27]
            right_ankle = landmarks[28]
            
            center_x = int((left_ankle['x'] + right_ankle['x']) // 2)
            center_y = int((left_ankle['y'] + right_ankle['y']) // 2)
            
            return (center_x, center_y)
        except:
            return (320, 400)
