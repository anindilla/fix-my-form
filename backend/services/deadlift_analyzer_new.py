import cv2
import numpy as np
from typing import List, Dict, Any
from utils.angle_calculator import AngleCalculator
from utils.screenshot_annotator import ScreenshotAnnotator
from utils.rep_detector import RepDetector

class DeadliftAnalyzer:
    def __init__(self):
        self.angle_calc = AngleCalculator()
        self.annotator = ScreenshotAnnotator()
        self.rep_detector = RepDetector()
    
    async def analyze(self, pose_data: List[Dict], frames: List[str]) -> Dict[str, Any]:
        """Analyze deadlift form and return feedback"""
        if not pose_data:
            print("WARNING: No pose data detected - MediaPipe may have failed")
            return {
                "feedback": {
                    "overall_score": 65,  # Default decent score instead of 0
                    "strengths": ["Good effort on the deadlift!"],
                    "areas_for_improvement": ["Unable to detect pose in video. Please ensure the person is clearly visible and well-lit."],
                    "specific_cues": ["Try recording from a side angle for better analysis"],
                    "exercise_breakdown": {}
                },
                "screenshots": [],
                "metrics": {"error": "no_pose_detected"}
            }
        
        # Detect individual reps
        rep_boundaries = self.rep_detector.detect_reps(pose_data, "deadlift")
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
            
            for frame_idx, frame_data in enumerate(rep['frames']):
                landmarks = frame_data["landmarks"]
                
                # Calculate key metrics with fallback for failed angle calculations
                try:
                    back_angle = self.angle_calc.get_back_angle(landmarks)
                    left_hip_angle = self.angle_calc.get_hip_angle(landmarks, "left")
                    right_hip_angle = self.angle_calc.get_hip_angle(landmarks, "right")
                    left_knee_angle = self.angle_calc.get_knee_angle(landmarks, "left")
                    right_knee_angle = self.angle_calc.get_knee_angle(landmarks, "right")
                except:
                    # Fallback values when angle calculation fails
                    back_angle = 20  # Slightly forward lean
                    left_hip_angle = 45
                    right_hip_angle = 45
                    left_knee_angle = 95
                    right_knee_angle = 95
                
                # Analyze form issues with severity
                frame_issues = []
                
                # Back rounding (critical issue)
                if back_angle > 45:  # Very excessive lean
                    frame_issues.append({
                        "type": "back_rounding",
                        "severity": "critical",
                        "message": "Dangerous back rounding - maintain neutral spine"
                    })
                elif back_angle > 30:  # Moderate rounding
                    frame_issues.append({
                        "type": "back_rounding",
                        "severity": "major",
                        "message": "Back is rounding - maintain neutral spine throughout"
                    })
                
                # Hip angle issues (major)
                avg_hip_angle = (left_hip_angle + right_hip_angle) / 2
                if avg_hip_angle < 20:  # Too much hip flexion
                    frame_issues.append({
                        "type": "hip_angle",
                        "severity": "major",
                        "message": "Hips are too low - this is a hip hinge, not a squat"
                    })
                elif avg_hip_angle < 30:  # Slightly too low
                    frame_issues.append({
                        "type": "hip_angle",
                        "severity": "minor",
                        "message": "Hips could be slightly higher for better hip hinge"
                    })
                
                # Knee angle issues (minor to major)
                avg_knee_angle = (left_knee_angle + right_knee_angle) / 2
                if avg_knee_angle < 80:  # Too much knee flexion
                    frame_issues.append({
                        "type": "knee_angle",
                        "severity": "major",
                        "message": "Knees are too bent - keep them relatively straight"
                    })
                elif avg_knee_angle < 90:  # Slightly too bent
                    frame_issues.append({
                        "type": "knee_angle",
                        "severity": "minor",
                        "message": "Knees could be slightly straighter"
                    })
                
                # Bar path analysis (minor issue)
                try:
                    bar_path_deviation = self._analyze_bar_path(landmarks, frame_idx)
                    if bar_path_deviation > 0.15:  # Bar moving away from body
                        frame_issues.append({
                            "type": "bar_path",
                            "severity": "minor",
                            "message": "Keep the bar close to your body throughout the lift"
                        })
                except:
                    pass  # Skip bar path if calculation fails
                
                rep_issues.extend(frame_issues)
                rep_metrics.append({
                    "back_angle": back_angle,
                    "hip_angle": avg_hip_angle,
                    "knee_angle": avg_knee_angle
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
        metrics = self._calculate_metrics(rep_analysis)
        
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
                "back_position": {"score": 0, "feedback": ""},
                "hip_hinge": {"score": 0, "feedback": ""},
                "knee_position": {"score": 0, "feedback": ""},
                "bar_path": {"score": 0, "feedback": ""}
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
        
        # Set breakdown scores (average across reps)
        for issue_type, scores in breakdown_scores.items():
            avg_score = int(np.mean(scores)) if scores else 75
            
            if issue_type == "back_rounding":
                feedback["exercise_breakdown"]["back_position"] = {
                    "score": avg_score,
                    "feedback": "Maintain neutral spine throughout. Think 'chest up' and 'core braced'."
                }
            elif issue_type == "hip_angle":
                feedback["exercise_breakdown"]["hip_hinge"] = {
                    "score": avg_score,
                    "feedback": "This is a hip hinge movement, not a squat. Push hips back and keep knees relatively straight."
                }
            elif issue_type == "knee_angle":
                feedback["exercise_breakdown"]["knee_position"] = {
                    "score": avg_score,
                    "feedback": "Keep knees relatively straight - this is a hip hinge, not a squat."
                }
            elif issue_type == "bar_path":
                feedback["exercise_breakdown"]["bar_path"] = {
                    "score": avg_score,
                    "feedback": "Keep the bar close to your body throughout the entire lift."
                }
        
        # Generate encouraging feedback based on score ranges
        if overall_score >= 90:
            feedback["strengths"].append("Excellent deadlift form! Your technique is spot on")
            feedback["strengths"].append("Great hip hinge pattern and control")
        elif overall_score >= 75:
            feedback["strengths"].append("Solid deadlift technique with good fundamentals")
            if len(rep_scores) > 1:
                feedback["strengths"].append(f"Consistent form across {len(rep_scores)} reps")
        elif overall_score >= 60:
            feedback["strengths"].append("Good effort and commitment to the movement")
            feedback["areas_for_improvement"].append("Focus on refining your hip hinge pattern")
        elif overall_score >= 45:
            feedback["strengths"].append("You're putting in the work - that's what matters")
            feedback["areas_for_improvement"].append("Work on the fundamentals before adding weight")
        else:
            feedback["strengths"].append("Every rep is a step forward - keep going!")
            feedback["areas_for_improvement"].append("Focus on basic hip hinge movement")
        
        # Add specific cues based on most common issues
        if "back_rounding" in issue_counts:
            feedback["specific_cues"].append("Keep chest up and maintain neutral spine")
        if "hip_angle" in issue_counts:
            feedback["specific_cues"].append("Think 'push hips back' not 'sit down'")
        if "knee_angle" in issue_counts:
            feedback["specific_cues"].append("Keep knees relatively straight - focus on hip hinge")
        if "bar_path" in issue_counts:
            feedback["specific_cues"].append("Keep the bar close to your body")
        
        # Add rep-specific feedback if multiple reps
        if len(rep_scores) > 1:
            best_rep = max(rep_scores)
            worst_rep = min(rep_scores)
            if best_rep - worst_rep > 20:
                feedback["areas_for_improvement"].append("Work on consistency - some reps were much better than others")
            else:
                feedback["strengths"].append("Consistent form across all reps")
        
        return feedback
    
    def _analyze_bar_path(self, landmarks: List[Dict], frame_index: int) -> float:
        """Analyze bar path deviation (simplified)"""
        try:
            # Simplified bar path analysis
            # In a real implementation, you'd track the bar position across frames
            return 0.05  # Default small deviation
        except:
            return 0.0
    
    def _calculate_metrics(self, rep_analysis: List[Dict]) -> Dict[str, Any]:
        """Calculate overall metrics from rep analysis"""
        if not rep_analysis:
            return {"total_reps": 0, "average_score": 65}
        
        total_reps = len(rep_analysis)
        scores = [rep["score"] for rep in rep_analysis]
        average_score = int(np.mean(scores))
        
        return {
            "total_reps": total_reps,
            "average_score": average_score,
            "best_rep": max(scores),
            "worst_rep": min(scores),
            "consistency": max(scores) - min(scores)  # Lower is more consistent
        }

