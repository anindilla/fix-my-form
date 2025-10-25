import cv2
import numpy as np
from typing import List, Dict, Any
from utils.angle_calculator import AngleCalculator
from utils.screenshot_annotator import ScreenshotAnnotator

class SquatAnalyzer:
    def __init__(self):
        self.angle_calc = AngleCalculator()
        self.annotator = ScreenshotAnnotator()
    
    async def analyze(self, pose_data: List[Dict], frames: List[str]) -> Dict[str, Any]:
        """Analyze squat form and return feedback"""
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
            hip_depth = self.angle_calc.get_hip_depth(landmarks)
            left_knee_angle = self.angle_calc.get_knee_angle(landmarks, "left")
            right_knee_angle = self.angle_calc.get_knee_angle(landmarks, "right")
            back_angle = self.angle_calc.get_back_angle(landmarks)
            knee_valgus = self.angle_calc.get_knee_valgus(landmarks)
            
            # Analyze form issues
            frame_issues = []
            
            # Depth check
            if hip_depth < -0.05:  # Hips not low enough
                frame_issues.append({
                    "type": "depth",
                    "severity": "high",
                    "message": "Not reaching proper depth - aim to get hip crease below knee level"
                })
            
            # Knee tracking
            if abs(knee_valgus) > 0.1:  # Knees caving in
                frame_issues.append({
                    "type": "knee_tracking",
                    "severity": "medium",
                    "message": "Knees caving inward - focus on pushing knees out over toes"
                })
            
            # Back angle
            if back_angle > 45:  # Too much forward lean
                frame_issues.append({
                    "type": "back_angle",
                    "severity": "medium",
                    "message": "Excessive forward lean - maintain more upright torso"
                })
            
            # Knee angle (too shallow)
            avg_knee_angle = (left_knee_angle + right_knee_angle) / 2
            if avg_knee_angle > 120:  # Not deep enough
                frame_issues.append({
                    "type": "knee_angle",
                    "severity": "high",
                    "message": "Not reaching full depth - aim for 90 degrees or less at knees"
                })
            
            analysis_results.append({
                "frame_index": i,
                "hip_depth": hip_depth,
                "knee_angle": avg_knee_angle,
                "back_angle": back_angle,
                "knee_valgus": knee_valgus,
                "issues": frame_issues
            })
            
            issues_found.extend(frame_issues)
        
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
    
    def _generate_feedback(self, issues: List[Dict], analysis_results: List[Dict]) -> Dict[str, Any]:
        """Generate comprehensive feedback"""
        feedback = {
            "overall_score": 0,
            "strengths": [],
            "areas_for_improvement": [],
            "specific_cues": [],
            "exercise_breakdown": {
                "depth": {"score": 0, "feedback": ""},
                "knee_tracking": {"score": 0, "feedback": ""},
                "back_position": {"score": 0, "feedback": ""},
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
        if "depth" in issue_counts:
            feedback["exercise_breakdown"]["depth"] = {
                "score": max(0, 100 - issue_counts["depth"] * 20),
                "feedback": "Focus on reaching proper depth. Your hip crease should go below your knee level."
            }
        
        if "knee_tracking" in issue_counts:
            feedback["exercise_breakdown"]["knee_tracking"] = {
                "score": max(0, 100 - issue_counts["knee_tracking"] * 15),
                "feedback": "Keep your knees tracking over your toes. Push your knees out as you descend."
            }
        
        if "back_angle" in issue_counts:
            feedback["exercise_breakdown"]["back_position"] = {
                "score": max(0, 100 - issue_counts["back_angle"] * 15),
                "feedback": "Maintain a more upright torso. Keep your chest up and core braced."
            }
        
        # Calculate overall score
        total_issues = sum(issue_counts.values())
        feedback["overall_score"] = max(0, 100 - total_issues * 10)
        
        # Generate strengths and improvements
        if feedback["overall_score"] >= 80:
            feedback["strengths"].append("Great overall form!")
        elif feedback["overall_score"] >= 60:
            feedback["strengths"].append("Good foundation with room for improvement")
        else:
            feedback["areas_for_improvement"].append("Focus on the fundamentals before adding weight")
        
        # Add specific cues
        if "depth" in issue_counts:
            feedback["specific_cues"].append("Think 'sit back' and 'break at the hips'")
        if "knee_tracking" in issue_counts:
            feedback["specific_cues"].append("Push knees out over toes throughout the movement")
        if "back_angle" in issue_counts:
            feedback["specific_cues"].append("Keep chest up and maintain neutral spine")
        
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
            annotated_path = await self.annotator.annotate_squat(
                frame_path, 
                landmarks, 
                "squat_summary.jpg"
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
        avg_hip_depth = np.mean([r["hip_depth"] for r in analysis_results])
        avg_knee_angle = np.mean([r["knee_angle"] for r in analysis_results])
        avg_back_angle = np.mean([r["back_angle"] for r in analysis_results])
        avg_knee_valgus = np.mean([r["knee_valgus"] for r in analysis_results])
        
        return {
            "average_hip_depth": avg_hip_depth,
            "average_knee_angle": avg_knee_angle,
            "average_back_angle": avg_back_angle,
            "average_knee_valgus": avg_knee_valgus,
            "total_frames_analyzed": len(analysis_results)
        }
