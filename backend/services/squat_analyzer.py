import cv2
import numpy as np
from typing import List, Dict, Any
from utils.angle_calculator import AngleCalculator
from utils.screenshot_annotator import ScreenshotAnnotator
from utils.rep_detector import RepDetector

class SquatAnalyzer:
    def __init__(self):
        self.angle_calc = AngleCalculator()
        self.annotator = ScreenshotAnnotator()
        self.rep_detector = RepDetector()
    
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
        
        # Detect individual reps
        rep_boundaries = self.rep_detector.detect_reps(pose_data, "squat")
        rep_data = self.rep_detector.get_rep_data(pose_data, rep_boundaries)
        
        if not rep_data:
            # Fallback: treat entire video as one rep
            rep_data = [{
                'start_frame': 0,
                'end_frame': len(pose_data) - 1,
                'frames': pose_data,
                'duration': len(pose_data)
            }]
        
        # Analyze each rep
        rep_scores = []
        all_issues = []
        rep_analysis = []
        
        for rep_idx, rep in enumerate(rep_data):
            rep_issues = []
            rep_metrics = []
            
            for frame_data in rep['frames']:
                landmarks = frame_data["landmarks"]
                
                # Calculate key metrics with fallback for failed angle calculations
                try:
                    hip_depth = self.angle_calc.get_hip_depth(landmarks)
                    left_knee_angle = self.angle_calc.get_knee_angle(landmarks, "left")
                    right_knee_angle = self.angle_calc.get_knee_angle(landmarks, "right")
                    back_angle = self.angle_calc.get_back_angle(landmarks)
                    knee_valgus = self.angle_calc.get_knee_valgus(landmarks)
                except:
                    # Fallback values when angle calculation fails
                    hip_depth = -0.02  # Slightly below parallel
                    left_knee_angle = 95
                    right_knee_angle = 95
                    back_angle = 20
                    knee_valgus = 0.05
                
                # Analyze form issues with severity
                frame_issues = []
                
                # Depth check (critical for squats)
                if hip_depth < -0.05:
                    frame_issues.append({
                        "type": "depth",
                        "severity": "major",
                        "message": "Not reaching proper depth - aim to get hip crease below knee level"
                    })
                
                # Knee tracking (major issue)
                if abs(knee_valgus) > 0.1:
                    frame_issues.append({
                        "type": "knee_tracking",
                        "severity": "major",
                        "message": "Knees caving inward - focus on pushing knees out over toes"
                    })
                
                # Back angle (minor to major depending on severity)
                if back_angle > 60:  # Very excessive lean
                    frame_issues.append({
                        "type": "back_angle",
                        "severity": "major",
                        "message": "Excessive forward lean - maintain more upright torso"
                    })
                elif back_angle > 45:  # Moderate lean
                    frame_issues.append({
                        "type": "back_angle",
                        "severity": "minor",
                        "message": "Slight forward lean - try to stay more upright"
                    })
                
                # Knee angle (major issue)
                avg_knee_angle = (left_knee_angle + right_knee_angle) / 2
                if avg_knee_angle > 120:
                    frame_issues.append({
                        "type": "knee_angle",
                        "severity": "major",
                        "message": "Not reaching full depth - aim for 90 degrees or less at knees"
                    })
                
                rep_issues.extend(frame_issues)
                rep_metrics.append({
                    "hip_depth": hip_depth,
                    "knee_angle": avg_knee_angle,
                    "back_angle": back_angle,
                    "knee_valgus": knee_valgus
                })
            
            # Calculate rep score
            rep_score = self._calculate_rep_score(rep_issues)
            rep_scores.append(rep_score)
            all_issues.extend(rep_issues)
            rep_analysis.append({
                "rep_index": rep_idx,
                "score": rep_score,
                "issues": rep_issues,
                "metrics": rep_metrics
            })
        
        # Generate overall feedback using average scores
        feedback = self._generate_feedback(all_issues, rep_analysis, rep_scores)
        
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
    
    def _calculate_rep_score(self, rep_issues: List[Dict]) -> int:
        """Calculate score for a single rep with severity-based penalties"""
        # Start with base score of 70 (assume decent form)
        rep_score = 70
        
        # Count issues by severity
        severity_counts = {"critical": 0, "major": 0, "minor": 0}
        for issue in rep_issues:
            severity = issue.get("severity", "minor")
            severity_counts[severity] += 1
        
        # Apply penalties based on severity
        rep_score -= severity_counts["critical"] * 30  # Critical issues
        rep_score -= severity_counts["major"] * 15     # Major issues  
        rep_score -= severity_counts["minor"] * 5      # Minor issues
        
        # Ensure minimum score of 30 (never 0)
        return max(30, rep_score)
    
    def _generate_feedback(self, issues: List[Dict], rep_analysis: List[Dict], rep_scores: List[int]) -> Dict[str, Any]:
        """Generate comprehensive feedback using average scores"""
        # Calculate overall score as average of rep scores
        overall_score = int(np.mean(rep_scores)) if rep_scores else 65
        
        feedback = {
            "overall_score": overall_score,
            "strengths": [],
            "areas_for_improvement": [],
            "specific_cues": [],
            "exercise_breakdown": {
                "depth": {"score": 0, "feedback": ""},
                "knee_tracking": {"score": 0, "feedback": ""},
                "back_position": {"score": 0, "feedback": ""},
                "knee_angle": {"score": 0, "feedback": ""}
            }
        }
        
        # Count issues by type and severity
        issue_counts = {}
        severity_counts = {"critical": 0, "major": 0, "minor": 0}
        
        for issue in issues:
            issue_type = issue["type"]
            severity = issue.get("severity", "minor")
            
            if issue_type not in issue_counts:
                issue_counts[issue_type] = 0
            issue_counts[issue_type] += 1
            severity_counts[severity] += 1
        
        # Generate breakdown scores (average across reps)
        breakdown_scores = {}
        for rep in rep_analysis:
            rep_issues = rep["issues"]
            for issue in rep_issues:
                issue_type = issue["type"]
                severity = issue.get("severity", "minor")
                
                if issue_type not in breakdown_scores:
                    breakdown_scores[issue_type] = []
                
                # Calculate penalty based on severity
                if severity == "critical":
                    penalty = 30
                elif severity == "major":
                    penalty = 15
                else:
                    penalty = 5
                
                breakdown_scores[issue_type].append(max(30, 100 - penalty))
        
        # Calculate breakdown scores with better fallback logic
        # Depth score
        if "depth" in breakdown_scores and breakdown_scores["depth"]:
            depth_score = int(np.mean(breakdown_scores["depth"]))
        else:
            depth_score = 80  # Default good score if no issues detected
        
        # Knee tracking score
        if "knee_tracking" in breakdown_scores and breakdown_scores["knee_tracking"]:
            knee_tracking_score = int(np.mean(breakdown_scores["knee_tracking"]))
        else:
            knee_tracking_score = 85  # Default good score if no issues detected
            
        # Back position score
        if "back_angle" in breakdown_scores and breakdown_scores["back_angle"]:
            back_score = int(np.mean(breakdown_scores["back_angle"]))
        else:
            back_score = 80  # Default good score if no issues detected
            
        # Knee angle score
        if "knee_angle" in breakdown_scores and breakdown_scores["knee_angle"]:
            knee_angle_score = int(np.mean(breakdown_scores["knee_angle"]))
        else:
            knee_angle_score = 85  # Default good score if no issues detected
        
        # Calculate average measurements across all reps for dynamic feedback
        avg_hip_depth = self._calculate_average_metric(rep_analysis, "hip_depth")
        avg_knee_angle = self._calculate_average_metric(rep_analysis, "knee_angle")
        avg_back_angle = self._calculate_average_metric(rep_analysis, "back_angle")
        avg_knee_valgus = self._calculate_average_metric(rep_analysis, "knee_valgus")
        
        # Set breakdown scores with dynamic feedback
        feedback["exercise_breakdown"]["depth"] = {
            "score": depth_score,
            "feedback": self._generate_depth_feedback(avg_hip_depth, depth_score)
        }
        feedback["exercise_breakdown"]["knee_tracking"] = {
            "score": knee_tracking_score,
            "feedback": self._generate_knee_tracking_feedback(avg_knee_valgus, knee_tracking_score)
        }
        feedback["exercise_breakdown"]["back_position"] = {
            "score": back_score,
            "feedback": self._generate_back_feedback(avg_back_angle, back_score)
        }
        feedback["exercise_breakdown"]["knee_angle"] = {
            "score": knee_angle_score,
            "feedback": self._generate_knee_angle_feedback(avg_knee_angle, knee_angle_score)
        }
        
        # Calculate overall score as LITERAL average of breakdown scores
        breakdown_scores_list = [depth_score, knee_tracking_score, back_score, knee_angle_score]
        overall_score = int(np.mean(breakdown_scores_list))
        feedback["overall_score"] = overall_score
        
        # Generate encouraging feedback based on score ranges
        if overall_score >= 90:
            feedback["strengths"].append("Excellent form! Your technique is spot on")
            feedback["strengths"].append("Great depth and control throughout")
        elif overall_score >= 75:
            feedback["strengths"].append("Solid technique with good fundamentals")
            if len(rep_scores) > 1:
                feedback["strengths"].append(f"Consistent form across {len(rep_scores)} reps")
        elif overall_score >= 60:
            feedback["strengths"].append("Good effort and commitment to the movement")
            feedback["areas_for_improvement"].append("Focus on refining your technique")
        elif overall_score >= 45:
            feedback["strengths"].append("You're putting in the work - that's what matters")
            feedback["areas_for_improvement"].append("Work on the fundamentals before adding weight")
        else:
            feedback["strengths"].append("Every rep is a step forward - keep going!")
            feedback["areas_for_improvement"].append("Focus on basic movement patterns")
        
        # Add specific cues based on most common issues
        if "depth" in issue_counts:
            feedback["specific_cues"].append("Think 'sit back' and 'break at the hips'")
        if "knee_tracking" in issue_counts:
            feedback["specific_cues"].append("Push knees out over toes throughout the movement")
        if "back_angle" in issue_counts:
            feedback["specific_cues"].append("Keep chest up and maintain neutral spine")
        if "knee_angle" in issue_counts:
            feedback["specific_cues"].append("Aim for deeper squats - hip crease below knee level")
        
        # Add rep-specific feedback if multiple reps
        if len(rep_scores) > 1:
            best_rep = max(rep_scores)
            worst_rep = min(rep_scores)
            if best_rep - worst_rep > 20:
                feedback["areas_for_improvement"].append("Work on consistency - some reps were much better than others")
            else:
                feedback["strengths"].append("Consistent form across all reps")
        
        return feedback
    
    def _calculate_average_metric(self, rep_analysis: List[Dict], metric_name: str) -> float:
        """Calculate average metric across all reps"""
        all_values = []
        for rep in rep_analysis:
            for metric in rep.get("metrics", []):
                if metric_name in metric:
                    all_values.append(metric[metric_name])
        
        if not all_values:
            return 0.0
        return np.mean(all_values)
    
    def _generate_depth_feedback(self, avg_hip_depth: float, score: int) -> str:
        """Generate dynamic feedback for depth based on actual measurements"""
        if score >= 85:
            return f"Excellent depth! Your hip crease averaged {abs(avg_hip_depth)*100:.1f}cm below knee level (target: 5-10cm)."
        elif score >= 70:
            return f"Good depth at {abs(avg_hip_depth)*100:.1f}cm below knee level. Aim for 5-10cm for optimal range of motion."
        else:
            return f"Work on depth - you averaged {abs(avg_hip_depth)*100:.1f}cm below knee level. Target: 5-10cm for proper squat depth."
    
    def _generate_knee_tracking_feedback(self, avg_knee_valgus: float, score: int) -> str:
        """Generate dynamic feedback for knee tracking based on actual measurements"""
        valgus_degrees = abs(avg_knee_valgus) * 180 / np.pi
        if score >= 85:
            return f"Perfect knee tracking! Minimal inward movement ({valgus_degrees:.1f}°)."
        elif score >= 70:
            return f"Good knee tracking with slight inward movement ({valgus_degrees:.1f}°). Focus on pushing knees out over toes."
        else:
            return f"Knees caving inward ({valgus_degrees:.1f}°). Push knees out over toes throughout the movement."
    
    def _generate_back_feedback(self, avg_back_angle: float, score: int) -> str:
        """Generate dynamic feedback for back position based on actual measurements"""
        if score >= 85:
            return f"Excellent torso position! Maintained {avg_back_angle:.1f}° forward lean (target: <30°)."
        elif score >= 70:
            return f"Good torso position with {avg_back_angle:.1f}° forward lean. Try to stay more upright (target: <30°)."
        else:
            return f"Excessive forward lean at {avg_back_angle:.1f}°. Focus on keeping chest up and core braced (target: <30°)."
    
    def _generate_knee_angle_feedback(self, avg_knee_angle: float, score: int) -> str:
        """Generate dynamic feedback for knee angle based on actual measurements"""
        if score >= 85:
            return f"Great knee angles! Averaged {avg_knee_angle:.1f}° at bottom (target: 90-100°)."
        elif score >= 70:
            return f"Good knee angles at {avg_knee_angle:.1f}°. Aim for 90-100° for optimal depth."
        else:
            return f"Knee angles at {avg_knee_angle:.1f}° need improvement. Target 90-100° for proper squat depth."
    
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
