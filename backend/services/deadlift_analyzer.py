import cv2
import numpy as np
from typing import List, Dict, Any
from utils.angle_calculator import AngleCalculator
from utils.screenshot_annotator import ScreenshotAnnotator

class DeadliftAnalyzer:
    def __init__(self):
        self.angle_calc = AngleCalculator()
        self.annotator = ScreenshotAnnotator()
    
    async def analyze(self, pose_data: List[Dict], frames: List[str]) -> Dict[str, Any]:
        """Analyze deadlift form and return feedback"""
        if not pose_data:
            print("WARNING: No pose data detected - MediaPipe may have failed")
            return {
                "feedback": {
                    "overall_score": 0,
                    "strengths": [],
                    "areas_for_improvement": ["Unable to detect pose in video. Please ensure the person is clearly visible and well-lit."],
                    "specific_cues": [],
                    "exercise_breakdown": {}
                },
                "screenshots": [],
                "metrics": {"error": "no_pose_detected"}
            }
        
        # Analyze each frame
        analysis_results = []
        issues_found = []
        
        for i, frame_data in enumerate(pose_data):
            landmarks = frame_data["landmarks"]
            
            # Calculate key metrics
            back_angle = self.angle_calc.get_back_angle(landmarks)
            left_hip_angle = self.angle_calc.get_hip_angle(landmarks, "left")
            right_hip_angle = self.angle_calc.get_hip_angle(landmarks, "right")
            left_knee_angle = self.angle_calc.get_knee_angle(landmarks, "left")
            right_knee_angle = self.angle_calc.get_knee_angle(landmarks, "right")
            
            # Calculate setup position (first frame analysis)
            setup_issues = []
            if i == 0:  # Analyze setup position
                shoulder_pos = self._get_shoulder_position(landmarks)
                hip_pos = self._get_hip_position(landmarks)
                bar_position = self._estimate_bar_position(landmarks)
                
                # Check if shoulders are over bar
                if shoulder_pos[0] < bar_position[0] - 0.1:  # Shoulders behind bar
                    setup_issues.append({
                        "type": "shoulder_position",
                        "severity": "high",
                        "message": "Shoulders should be directly over the bar at setup"
                    })
                
                # Check hip position relative to knees
                if hip_pos[1] < self.angle_calc.get_landmark_coords(landmarks, AngleCalculator.LEFT_KNEE)[1] - 0.05:
                    setup_issues.append({
                        "type": "hip_position",
                        "severity": "medium",
                        "message": "Hips should be higher than knees at setup"
                    })
            
            # Analyze movement issues
            frame_issues = []
            
            # Back rounding
            if back_angle > 30:  # Excessive back rounding
                frame_issues.append({
                    "type": "back_rounding",
                    "severity": "high",
                    "message": "Back is rounding - maintain neutral spine throughout the lift"
                })
            
            # Hip angle too shallow (squatting the deadlift)
            avg_hip_angle = (left_hip_angle + right_hip_angle) / 2
            if avg_hip_angle > 120:  # Too upright, squatting motion
                frame_issues.append({
                    "type": "hip_angle",
                    "severity": "medium",
                    "message": "Hips too high - this is a hip hinge, not a squat"
                })
            
            # Knee angle too deep (squatting)
            avg_knee_angle = (left_knee_angle + right_knee_angle) / 2
            if avg_knee_angle < 90:  # Too deep, squatting motion
                frame_issues.append({
                    "type": "knee_angle",
                    "severity": "medium",
                    "message": "Knees too bent - focus on hip hinge movement"
                })
            
            # Bar path analysis (simplified)
            bar_path_deviation = self._analyze_bar_path(landmarks, i)
            if bar_path_deviation > 0.1:  # Bar drifting away from body
                frame_issues.append({
                    "type": "bar_path",
                    "severity": "medium",
                    "message": "Bar drifting away from body - keep it close throughout the lift"
                })
            
            analysis_results.append({
                "frame_index": i,
                "back_angle": back_angle,
                "hip_angle": avg_hip_angle,
                "knee_angle": avg_knee_angle,
                "bar_path_deviation": bar_path_deviation,
                "issues": frame_issues + setup_issues
            })
            
            issues_found.extend(frame_issues + setup_issues)
        
        # Generate overall feedback
        feedback = self._generate_feedback(issues_found, analysis_results)
        
        # Skip screenshot generation for now
        print("Skipping screenshot generation - visual analysis disabled")
        screenshots = []
        
        # Calculate overall metrics
        metrics = self._calculate_metrics(analysis_results)
        
        return {
            "feedback": feedback,
            "screenshots": screenshots,
            "metrics": metrics
        }
    
    def _get_shoulder_position(self, landmarks: List[Dict]) -> tuple:
        """Get shoulder position"""
        left_shoulder = self.angle_calc.get_landmark_coords(landmarks, AngleCalculator.LEFT_SHOULDER)
        right_shoulder = self.angle_calc.get_landmark_coords(landmarks, AngleCalculator.RIGHT_SHOULDER)
        return ((left_shoulder[0] + right_shoulder[0]) / 2, (left_shoulder[1] + right_shoulder[1]) / 2)
    
    def _get_hip_position(self, landmarks: List[Dict]) -> tuple:
        """Get hip position"""
        left_hip = self.angle_calc.get_landmark_coords(landmarks, AngleCalculator.LEFT_HIP)
        right_hip = self.angle_calc.get_landmark_coords(landmarks, AngleCalculator.RIGHT_HIP)
        return ((left_hip[0] + right_hip[0]) / 2, (left_hip[1] + right_hip[1]) / 2)
    
    def _estimate_bar_position(self, landmarks: List[Dict]) -> tuple:
        """Estimate bar position (simplified - in practice, you'd need computer vision)"""
        # Assume bar is at ankle level, centered
        left_ankle = self.angle_calc.get_landmark_coords(landmarks, AngleCalculator.LEFT_ANKLE)
        right_ankle = self.angle_calc.get_landmark_coords(landmarks, AngleCalculator.RIGHT_ANKLE)
        ankle_center_x = (left_ankle[0] + right_ankle[0]) / 2
        ankle_center_y = (left_ankle[1] + right_ankle[1]) / 2
        return (ankle_center_x, ankle_center_y)
    
    def _analyze_bar_path(self, landmarks: List[Dict], frame_index: int) -> float:
        """Analyze bar path deviation (simplified)"""
        # This is a simplified version - in practice, you'd track the bar position
        # For now, return a random value based on back angle
        back_angle = self.angle_calc.get_back_angle(landmarks)
        return abs(back_angle - 15) / 100  # Simulate bar path based on back angle
    
    def _generate_feedback(self, issues: List[Dict], analysis_results: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive feedback"""
        feedback = {
            "overall_score": 0,
            "strengths": [],
            "areas_for_improvement": [],
            "specific_cues": [],
            "exercise_breakdown": {
                "setup": {"score": 0, "feedback": ""},
                "back_position": {"score": 0, "feedback": ""},
                "hip_hinge": {"score": 0, "feedback": ""},
                "bar_path": {"score": 0, "feedback": ""}
            }
        }
        
        # Count issues by type
        issue_counts = {}
        for issue in issues:
            issue_type = issue["type"]
            if issue_type not in issue_counts:
                issue_counts[issue_type] = 0
            issue_counts[issue_type] += 1
        
        # Generate specific feedback
        if "shoulder_position" in issue_counts or "hip_position" in issue_counts:
            feedback["exercise_breakdown"]["setup"] = {
                "score": max(0, 100 - (issue_counts.get("shoulder_position", 0) + issue_counts.get("hip_position", 0)) * 25),
                "feedback": "Focus on proper setup: shoulders over bar, hips higher than knees."
            }
        
        if "back_rounding" in issue_counts:
            feedback["exercise_breakdown"]["back_position"] = {
                "score": max(0, 100 - issue_counts["back_rounding"] * 30),
                "feedback": "Maintain neutral spine throughout. Think 'chest up' and 'core braced'."
            }
        
        if "hip_angle" in issue_counts or "knee_angle" in issue_counts:
            feedback["exercise_breakdown"]["hip_hinge"] = {
                "score": max(0, 100 - (issue_counts.get("hip_angle", 0) + issue_counts.get("knee_angle", 0)) * 20),
                "feedback": "This is a hip hinge movement, not a squat. Push hips back and keep knees relatively straight."
            }
        
        if "bar_path" in issue_counts:
            feedback["exercise_breakdown"]["bar_path"] = {
                "score": max(0, 100 - issue_counts["bar_path"] * 15),
                "feedback": "Keep the bar close to your body throughout the entire lift."
            }
        
        # Calculate overall score
        total_issues = sum(issue_counts.values())
        feedback["overall_score"] = max(0, 100 - total_issues * 8)
        
        # Generate strengths and improvements
        if feedback["overall_score"] >= 80:
            feedback["strengths"].append("Excellent deadlift form!")
        elif feedback["overall_score"] >= 60:
            feedback["strengths"].append("Good technique with some areas to refine")
        else:
            feedback["areas_for_improvement"].append("Focus on the fundamentals - setup and hip hinge pattern")
        
        # Add specific cues
        if "back_rounding" in issue_counts:
            feedback["specific_cues"].append("Keep chest up and maintain neutral spine")
        if "hip_angle" in issue_counts or "knee_angle" in issue_counts:
            feedback["specific_cues"].append("Think 'push hips back' not 'sit down'")
        if "bar_path" in issue_counts:
            feedback["specific_cues"].append("Drag the bar up your legs")
        
        return feedback
    
    async def _create_screenshots(self, pose_data: List[Dict], frames: List[str], issues: List[Dict]) -> List[str]:
        """Create single annotated screenshot highlighting the most crucial improvement point"""
        screenshot_paths = []
        
        print(f"Creating single summary screenshot from {len(pose_data)} pose data entries")
        
        if not pose_data or not frames:
            print("No pose data or frames available for screenshot generation")
            return screenshot_paths
        
        # Select the middle frame as the most representative
        middle_index = len(pose_data) // 2
        frame_data = pose_data[middle_index]
        frame_path = frame_data["frame_path"]
        landmarks = frame_data["landmarks"]
        
        print(f"Creating summary screenshot from middle frame: {frame_path}")
        
        try:
            # Create single annotated screenshot with most crucial improvement
            annotated_path = await self.annotator.annotate_deadlift(
                frame_path, 
                landmarks, 
                "deadlift_summary.jpg"
            )
            screenshot_paths.append(annotated_path)
            print(f"Successfully created summary screenshot: {annotated_path}")
        except Exception as e:
            print(f"Error creating summary screenshot: {str(e)}")
        
        print(f"Final screenshot paths: {screenshot_paths}")
        return screenshot_paths
    
    def _calculate_metrics(self, analysis_results: List[Dict]) -> Dict[str, Any]:
        """Calculate overall metrics"""
        if not analysis_results:
            return {}
        
        # Calculate averages
        avg_back_angle = np.mean([r["back_angle"] for r in analysis_results])
        avg_hip_angle = np.mean([r["hip_angle"] for r in analysis_results])
        avg_knee_angle = np.mean([r["knee_angle"] for r in analysis_results])
        avg_bar_path_deviation = np.mean([r["bar_path_deviation"] for r in analysis_results])
        
        return {
            "average_back_angle": avg_back_angle,
            "average_hip_angle": avg_hip_angle,
            "average_knee_angle": avg_knee_angle,
            "average_bar_path_deviation": avg_bar_path_deviation,
            "total_frames_analyzed": len(analysis_results)
        }
