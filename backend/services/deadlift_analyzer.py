import cv2
import numpy as np
import logging
from typing import List, Dict, Any
from utils.angle_calculator import AngleCalculator
from utils.screenshot_annotator import ScreenshotAnnotator

logger = logging.getLogger(__name__)

# Try to import RepDetector with fallback
try:
    from utils.rep_detector import RepDetector
    REP_DETECTOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"RepDetector not available: {e}")
    REP_DETECTOR_AVAILABLE = False

class DeadliftAnalyzer:
    def __init__(self):
        self.angle_calc = AngleCalculator()
        self.annotator = ScreenshotAnnotator()
        if REP_DETECTOR_AVAILABLE:
            self.rep_detector = RepDetector()
        else:
            self.rep_detector = None
    
    async def analyze(self, pose_data: List[Dict], frames: List[str]) -> Dict[str, Any]:
        """Analyze deadlift form and return feedback"""
        if not pose_data:
            print("WARNING: No pose data detected - MediaPipe may have failed")
            return {
                "feedback": {
                    "overall_score": 50,  # Consistent fallback score
                    "strengths": ["Good effort on the deadlift!"],
                    "areas_for_improvement": ["Unable to detect pose in video. Please ensure the person is clearly visible and well-lit."],
                    "specific_cues": ["Try recording from a side angle for better analysis"],
                    "exercise_breakdown": {
                        "hip_position": {"score": 50, "message": "Could not measure hip position - pose not detected"},
                        "knee_position": {"score": 50, "message": "Could not measure knee position - pose not detected"},
                        "torso_position": {"score": 50, "message": "Could not measure torso position - pose not detected"},
                        "bar_path": {"score": 50, "message": "Could not measure bar path - pose not detected"}
                    }
                },
                "screenshots": [],
                "metrics": {"error": "no_pose_detected"}
            }
        
        # Detect individual reps with error handling
        if self.rep_detector is not None:
            try:
                rep_boundaries = self.rep_detector.detect_reps(pose_data, "deadlift")
                rep_data = self.rep_detector.get_rep_data(pose_data, rep_boundaries)
            except Exception as e:
                logger.error(f"Rep detection failed: {e}")
                rep_data = None
        else:
            logger.warning("RepDetector not available, treating entire video as one rep")
            rep_data = None
        
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
        feedback = {
            "overall_score": 0,  # Will be calculated from breakdown scores
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
        
        # Calculate breakdown scores with better fallback logic
        # Back position score
        if "back_rounding" in breakdown_scores and breakdown_scores["back_rounding"]:
            back_score = int(np.mean(breakdown_scores["back_rounding"]))
        else:
            back_score = 75  # Default good score if no issues detected
        
        # Hip hinge score  
        if "hip_angle" in breakdown_scores and breakdown_scores["hip_angle"]:
            hip_score = int(np.mean(breakdown_scores["hip_angle"]))
        else:
            hip_score = 80  # Default good score if no issues detected
            
        # Knee position score
        if "knee_angle" in breakdown_scores and breakdown_scores["knee_angle"]:
            knee_score = int(np.mean(breakdown_scores["knee_angle"]))
        else:
            knee_score = 85  # Default good score if no issues detected
            
        # Bar path score - use improved analysis
        if "bar_path" in breakdown_scores and breakdown_scores["bar_path"]:
            bar_score = int(np.mean(breakdown_scores["bar_path"]))
        else:
            # Calculate bar path score from pose data
            bar_scores = []
            for rep in rep_analysis:
                for frame_data in rep['frames']:
                    landmarks = frame_data["landmarks"]
                    bar_deviation = self._analyze_bar_path(landmarks, 0)
                    # Convert deviation to score (0.02 = 95, 0.05 = 85, 0.1 = 70, 0.2 = 50)
                    if bar_deviation <= 0.02:
                        bar_scores.append(95)
                    elif bar_deviation <= 0.05:
                        bar_scores.append(85)
                    elif bar_deviation <= 0.1:
                        bar_scores.append(70)
                    else:
                        bar_scores.append(50)
            bar_score = int(np.mean(bar_scores)) if bar_scores else 80
        
        # Calculate average measurements across all reps for dynamic feedback
        avg_back_angle = self._calculate_average_metric(rep_analysis, "back_angle")
        avg_hip_angle = self._calculate_average_metric(rep_analysis, "hip_angle")
        avg_knee_angle = self._calculate_average_metric(rep_analysis, "knee_angle")
        avg_bar_deviation = self._calculate_average_metric(rep_analysis, "bar_deviation")
        
        # Set breakdown scores with dynamic feedback
        feedback["exercise_breakdown"]["back_position"] = {
            "score": back_score,
            "feedback": self._generate_back_feedback(avg_back_angle, back_score)
        }
        feedback["exercise_breakdown"]["hip_hinge"] = {
            "score": hip_score,
            "feedback": self._generate_hip_hinge_feedback(avg_hip_angle, hip_score)
        }
        feedback["exercise_breakdown"]["knee_position"] = {
            "score": knee_score,
            "feedback": self._generate_knee_position_feedback(avg_knee_angle, knee_score)
        }
        feedback["exercise_breakdown"]["bar_path"] = {
            "score": bar_score,
            "feedback": self._generate_bar_path_feedback(avg_bar_deviation, bar_score)
        }
        
        # Calculate overall score as LITERAL average of breakdown scores
        breakdown_scores_list = [back_score, hip_score, knee_score, bar_score]
        overall_score = int(np.mean(breakdown_scores_list))
        feedback["overall_score"] = overall_score
        
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
    
    def _generate_back_feedback(self, avg_back_angle: float, score: int) -> str:
        """Generate dynamic feedback for back position based on actual measurements"""
        if score >= 85:
            return f"Excellent spine position! Maintained {avg_back_angle:.1f}° forward lean (target: <30°)."
        elif score >= 70:
            return f"Good spine position with {avg_back_angle:.1f}° forward lean. Keep chest up and core braced (target: <30°)."
        else:
            return f"Back rounding at {avg_back_angle:.1f}°. Focus on neutral spine - think 'chest up' and 'core braced' (target: <30°)."
    
    def _generate_hip_hinge_feedback(self, avg_hip_angle: float, score: int) -> str:
        """Generate dynamic feedback for hip hinge based on actual measurements"""
        if score >= 85:
            return f"Perfect hip hinge! Averaged {avg_hip_angle:.1f}° hip angle (target: 30-45°)."
        elif score >= 70:
            return f"Good hip hinge at {avg_hip_angle:.1f}°. This is a hip hinge movement, not a squat (target: 30-45°)."
        else:
            return f"Hip angle at {avg_hip_angle:.1f}° needs work. Push hips back and keep knees relatively straight (target: 30-45°)."
    
    def _generate_knee_position_feedback(self, avg_knee_angle: float, score: int) -> str:
        """Generate dynamic feedback for knee position based on actual measurements"""
        if score >= 85:
            return f"Excellent knee position! Maintained {avg_knee_angle:.1f}° knee angle (target: 90-120°)."
        elif score >= 70:
            return f"Good knee position at {avg_knee_angle:.1f}°. Keep knees relatively straight for hip hinge (target: 90-120°)."
        else:
            return f"Knee angle at {avg_knee_angle:.1f}° needs adjustment. Keep knees relatively straight - this is a hip hinge, not a squat (target: 90-120°)."
    
    def _generate_bar_path_feedback(self, avg_bar_deviation: float, score: int) -> str:
        """Generate dynamic feedback for bar path based on actual measurements"""
        deviation_cm = avg_bar_deviation * 100
        if score >= 85:
            return f"Excellent bar path! Minimal deviation of {deviation_cm:.1f}cm (target: <2cm)."
        elif score >= 70:
            return f"Good bar path with {deviation_cm:.1f}cm deviation. Keep the bar close to your body (target: <2cm)."
        else:
            return f"Bar path needs work with {deviation_cm:.1f}cm deviation. Focus on keeping the bar close to your body throughout the lift (target: <2cm)."
    
    def _analyze_bar_path(self, landmarks: List[Dict], frame_index: int) -> float:
        """Analyze bar path deviation using shoulder and hip movement"""
        try:
            # Use shoulder and hip movement as proxy for bar path
            # If shoulders and hips move together smoothly, bar path is likely good
            if len(landmarks) >= 24:
                # Get shoulder and hip positions
                left_shoulder = landmarks[11]
                right_shoulder = landmarks[12]
                left_hip = landmarks[23]
                right_hip = landmarks[24]
                
                # Calculate shoulder-hip alignment
                shoulder_center_x = (left_shoulder['x'] + right_shoulder['x']) / 2
                hip_center_x = (left_hip['x'] + right_hip['x']) / 2
                
                # Good bar path: shoulders and hips should be roughly aligned
                alignment_deviation = abs(shoulder_center_x - hip_center_x)
                
                # Convert to deviation score (0.0 = perfect, 0.2 = poor)
                if alignment_deviation < 0.05:
                    return 0.02  # Very good alignment
                elif alignment_deviation < 0.1:
                    return 0.05  # Good alignment
                elif alignment_deviation < 0.15:
                    return 0.1   # Moderate deviation
                else:
                    return 0.2  # Poor alignment
            else:
                return 0.05  # Default good score when landmarks not available
        except:
            return 0.05  # Default good score on error
    
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
