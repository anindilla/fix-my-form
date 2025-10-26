import numpy as np
import logging
from typing import List, Dict, Any
from utils.angle_calculator import AngleCalculator
from utils.screenshot_annotator import ScreenshotAnnotator
from services.scoring_engine import ScoringEngine

logger = logging.getLogger(__name__)

# Try to import RepDetector with fallback
try:
    from utils.rep_detector import RepDetector
    REP_DETECTOR_AVAILABLE = True
except ImportError as e:
    logger.warning(f"RepDetector not available: {e}")
    REP_DETECTOR_AVAILABLE = False

class SumoDeadliftAnalyzer:
    def __init__(self):
        self.annotator = ScreenshotAnnotator()
        self.angle_calc = AngleCalculator()
        self.scoring_engine = ScoringEngine("sumo-deadlift")
        if REP_DETECTOR_AVAILABLE:
            self.rep_detector = RepDetector()
        else:
            self.rep_detector = None
    
    async def analyze(self, pose_data: List[Dict[str, Any]], frames: List[str]) -> Dict[str, Any]:
        """Analyze sumo deadlift form"""
        if not pose_data:
            logger.warning("No pose data detected - MediaPipe may have failed")
            return {
                "feedback": {
                    "overall_score": 50,  # Give a reasonable fallback score
                    "strengths": ["Good effort on the sumo deadlift!"],
                    "areas_for_improvement": ["Unable to detect pose in video. Please ensure the person is clearly visible and well-lit."],
                    "specific_cues": ["Try recording from a side angle for better analysis"],
                    "exercise_breakdown": {
                        "hip_position": {"score": 50, "message": "Could not measure hip position - pose not detected"},
                        "knee_position": {"score": 50, "message": "Could not measure knee position - pose not detected"},
                        "torso_position": {"score": 50, "message": "Could not measure torso position - pose not detected"},
                        "stance_width": {"score": 50, "message": "Could not measure stance width - pose not detected"}
                    }
                },
                "screenshots": [],
                "metrics": {"error": "no_pose_detected"}
            }
        
        # Detect individual reps with error handling
        logger.info("Detecting reps in sumo deadlift video")
        if self.rep_detector is not None:
            try:
                rep_boundaries = self.rep_detector.detect_reps(pose_data, "sumo-deadlift")
                rep_data = self.rep_detector.get_rep_data(pose_data, rep_boundaries)
            except Exception as e:
                logger.error(f"Rep detection failed: {e}")
                rep_data = None
        else:
            logger.warning("RepDetector not available, treating entire video as one rep")
            rep_data = None
        
        if not rep_data:
            logger.warning("No reps detected, treating entire video as one rep")
            # Fallback: treat entire video as one rep
            rep_data = [{
                'start_frame': 0,
                'end_frame': len(pose_data) - 1,
                'frames': pose_data,
                'duration': len(pose_data)
            }]
        
        logger.info(f"Analyzing {len(rep_data)} reps")
        
        # Analyze each rep
        rep_scores = []
        all_issues = []
        rep_analysis = []
        
        for rep_idx, rep in enumerate(rep_data):
            logger.info(f"Analyzing rep {rep_idx + 1}/{len(rep_data)}")
            
            # Extract key metrics for this rep
            metrics = self._calculate_metrics(rep['frames'])
            
            # Generate feedback for this rep
            feedback = self._generate_feedback(metrics)
            
            rep_scores.append(feedback['overall_score'])
            all_issues.extend(feedback.get('areas_for_improvement', []))
            rep_analysis.append({
                'rep': rep_idx + 1,
                'score': feedback['overall_score'],
                'issues': feedback.get('areas_for_improvement', [])
            })
        
        # Calculate overall metrics from all reps
        overall_metrics = self._calculate_metrics(pose_data)
        
        # Generate overall feedback
        overall_feedback = self._generate_feedback(overall_metrics)
        
        # Skip screenshot generation for now
        logger.info("Skipping screenshot generation - visual analysis disabled")
        screenshots = []
        
        return {
            "feedback": overall_feedback,
            "metrics": overall_metrics,
            "screenshots": screenshots
        }
    
    def _calculate_metrics(self, pose_data: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate sumo deadlift specific metrics"""
        metrics = {}
        
        for i, frame_data in enumerate(pose_data):
            if not frame_data.get('landmarks'):
                continue
                
            landmarks = frame_data['landmarks']
            
            # Sumo deadlift specific angles
            # Hip angle (wider stance)
            hip_angle = self._calculate_hip_angle(landmarks)
            # Knee angle (more vertical shins)
            knee_angle = self._calculate_knee_angle(landmarks)
            # Torso angle (more upright than conventional)
            torso_angle = self._calculate_torso_angle(landmarks)
            # Stance width (wider than conventional)
            stance_width = self._calculate_stance_width(landmarks)
            
            # Only store valid angles (not None)
            if hip_angle is not None:
                metrics[f'frame_{i}_hip_angle'] = hip_angle
            if knee_angle is not None:
                metrics[f'frame_{i}_knee_angle'] = knee_angle
            if torso_angle is not None:
                metrics[f'frame_{i}_torso_angle'] = torso_angle
            if stance_width is not None:
                metrics[f'frame_{i}_stance_width'] = stance_width
        
        return metrics
    
    def _calculate_hip_angle(self, landmarks):
        """Calculate hip angle for sumo deadlift"""
        try:
            # Hip, knee, ankle landmarks
            hip = landmarks[23]  # Left hip
            knee = landmarks[25]  # Left knee
            ankle = landmarks[27]  # Left ankle
            
            # Check landmark visibility
            if not self._is_landmark_visible(hip) or not self._is_landmark_visible(knee) or not self._is_landmark_visible(ankle):
                logger.debug("Hip angle calculation skipped - landmarks not visible")
                return None
            
            angle = self.angle_calc.calculate_angle(hip, knee, ankle)
            if angle is None or angle <= 0:
                logger.warning(f"Invalid hip angle: {angle}")
                return None
            return angle
        except Exception as e:
            logger.error(f"Hip angle calculation failed: {e}")
            return None
    
    def _calculate_knee_angle(self, landmarks):
        """Calculate knee angle for sumo deadlift"""
        try:
            # Hip, knee, ankle landmarks
            hip = landmarks[23]  # Left hip
            knee = landmarks[25]  # Left knee
            ankle = landmarks[27]  # Left ankle
            
            # Check landmark visibility
            if not self._is_landmark_visible(hip) or not self._is_landmark_visible(knee) or not self._is_landmark_visible(ankle):
                logger.debug("Knee angle calculation skipped - landmarks not visible")
                return None
            
            angle = self.angle_calc.calculate_angle(hip, knee, ankle)
            if angle is None or angle <= 0:
                logger.warning(f"Invalid knee angle: {angle}")
                return None
            return angle
        except Exception as e:
            logger.error(f"Knee angle calculation failed: {e}")
            return None
    
    def _calculate_torso_angle(self, landmarks):
        """Calculate torso angle (should be more upright for sumo)"""
        try:
            # Shoulder, hip, knee landmarks
            shoulder = landmarks[11]  # Left shoulder
            hip = landmarks[23]  # Left hip
            knee = landmarks[25]  # Left knee
            
            # Check landmark visibility
            if not self._is_landmark_visible(shoulder) or not self._is_landmark_visible(hip) or not self._is_landmark_visible(knee):
                logger.debug("Torso angle calculation skipped - landmarks not visible")
                return None
            
            angle = self.angle_calc.calculate_angle(shoulder, hip, knee)
            if angle is None or angle <= 0:
                logger.warning(f"Invalid torso angle: {angle}")
                return None
            return angle
        except Exception as e:
            logger.error(f"Torso angle calculation failed: {e}")
            return None
    
    def _calculate_stance_width(self, landmarks):
        """Calculate stance width for sumo deadlift"""
        try:
            # Distance between feet
            left_ankle = landmarks[27]  # Left ankle
            right_ankle = landmarks[28]  # Right ankle
            
            # Check landmark visibility
            if not self._is_landmark_visible(left_ankle) or not self._is_landmark_visible(right_ankle):
                logger.debug("Stance width calculation skipped - ankle landmarks not visible")
                return None
            
            # Calculate distance
            distance = np.sqrt(
                (left_ankle['x'] - right_ankle['x'])**2 + 
                (left_ankle['y'] - right_ankle['y'])**2
            )
            
            if distance <= 0:
                logger.warning(f"Invalid stance width: {distance}")
                return None
                
            return distance * 100  # Convert to percentage
        except Exception as e:
            logger.error(f"Stance width calculation failed: {e}")
            return None
    
    def _is_landmark_visible(self, landmark, threshold=0.7):
        """Check if landmark is visible enough for accurate calculation"""
        return landmark.get('visibility', 0) >= threshold
    
    def _generate_feedback(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Generate sumo deadlift specific feedback"""
        # Analyze the metrics to provide feedback
        strengths = []
        improvements = []
        cues = []
        
        # Get average angles across all frames (filter out None and invalid values)
        hip_angles = [v for k, v in metrics.items() if 'hip_angle' in k and v is not None and v > 0]
        knee_angles = [v for k, v in metrics.items() if 'knee_angle' in k and v is not None and v > 0]
        torso_angles = [v for k, v in metrics.items() if 'torso_angle' in k and v is not None and v > 0]
        stance_widths = [v for k, v in metrics.items() if 'stance_width' in k and v is not None and v > 0]
        
        if hip_angles:
            avg_hip_angle = np.mean(hip_angles)
            if 70 <= avg_hip_angle <= 110:
                strengths.append("Good hip positioning for sumo stance")
            elif avg_hip_angle < 70:
                improvements.append("Hips are too low - work on setup position")
                cues.append("Start with hips higher, closer to the bar")
            else:
                improvements.append("Hips are too high - you're not using your legs enough")
                cues.append("Lower your hips and use more leg drive")
        
        if knee_angles:
            avg_knee_angle = np.mean(knee_angles)
            if 80 <= avg_knee_angle <= 120:
                strengths.append("Good knee positioning")
            else:
                improvements.append("Watch your knee position")
                cues.append("Keep your knees tracking over your toes")
        
        if torso_angles:
            avg_torso_angle = np.mean(torso_angles)
            if 85 <= avg_torso_angle <= 105:
                strengths.append("Excellent upright torso position")
            elif avg_torso_angle < 85:
                improvements.append("Torso is too upright - you may be compensating")
                cues.append("Allow slight forward lean while keeping chest up")
            else:
                improvements.append("Torso is leaning too far forward")
                cues.append("Keep your chest up and core tight")
        
        if stance_widths:
            avg_stance_width = np.mean(stance_widths)
            if avg_stance_width >= 15:  # Wider stance for sumo
                strengths.append("Good wide stance for sumo deadlift")
            else:
                improvements.append("Stance could be wider for sumo deadlift")
                cues.append("Widen your stance to get your hands inside your legs")
        
        # Sumo deadlift specific feedback
        if not strengths:
            strengths.append("Good effort on the sumo deadlift!")
        
        if not improvements:
            improvements.append("Continue practicing to refine your technique")
        
        if not cues:
            cues.append("Keep your chest up and core tight")
            cues.append("Drive through your heels and extend your hips")
            cues.append("Keep the bar close to your body")
        
        # Check if we have valid angle data (not just zeros)
        valid_hip_angles = [a for a in hip_angles if a > 0]
        valid_knee_angles = [a for a in knee_angles if a > 0]
        valid_torso_angles = [a for a in torso_angles if a > 0]
        valid_stance_widths = [w for w in stance_widths if w > 0]
        
        # If no valid angles detected, return error feedback
        if not valid_hip_angles and not valid_knee_angles and not valid_torso_angles and not valid_stance_widths:
            return {
                "overall_score": 0,
                "strengths": [],
                "areas_for_improvement": [
                    "Unable to analyze your form - pose detection failed",
                    "Please ensure you're fully visible in the frame",
                    "Try recording from a side angle with good lighting"
                ],
                "specific_cues": [
                    "Position camera to capture your full body",
                    "Ensure good lighting and clear background"
                ],
                "exercise_breakdown": {
                    "hip_position": {
                        "score": 0,
                        "feedback": "Could not measure hip position - pose not detected"
                    },
                    "knee_position": {
                        "score": 0,
                        "feedback": "Could not measure knee position - pose not detected"
                    },
                    "torso_position": {
                        "score": 0,
                        "feedback": "Could not measure torso position - pose not detected"
                    },
                    "stance_width": {
                        "score": 0,
                        "feedback": "Could not measure stance width - pose not detected"
                    }
                }
            }
        
        # Calculate breakdown scores with actual measurements
        breakdown_scores = {
            "hip_position": int(np.mean([85 if 70 <= a <= 110 else 65 for a in valid_hip_angles])) if valid_hip_angles else 0,
            "knee_position": int(np.mean([85 if 80 <= a <= 120 else 65 for a in valid_knee_angles])) if valid_knee_angles else 0,
            "torso_position": int(np.mean([90 if 85 <= a <= 105 else 70 for a in valid_torso_angles])) if valid_torso_angles else 0,
            "stance_width": int(np.mean([90 if w >= 15 else 70 for w in valid_stance_widths])) if valid_stance_widths else 0
        }
        
        # Overall score = average of breakdown scores
        overall_score = int(np.mean(list(breakdown_scores.values())))
        overall_score = max(30, overall_score)  # Ensure minimum score of 30
        
        return {
            "overall_score": overall_score,
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "specific_cues": cues,
            "exercise_breakdown": {
                "hip_position": {
                    "score": breakdown_scores["hip_position"],
                    "feedback": self._generate_hip_feedback(hip_angles, breakdown_scores["hip_position"])
                },
                "knee_position": {
                    "score": breakdown_scores["knee_position"],
                    "feedback": self._generate_knee_feedback(knee_angles, breakdown_scores["knee_position"])
                },
                "torso_position": {
                    "score": breakdown_scores["torso_position"],
                    "feedback": self._generate_torso_feedback(torso_angles, breakdown_scores["torso_position"])
                },
                "stance_width": {
                    "score": breakdown_scores["stance_width"],
                    "feedback": self._generate_stance_feedback(stance_widths, breakdown_scores["stance_width"])
                }
            }
        }
    
    def _generate_hip_feedback(self, hip_angles: List[float], score: int) -> str:
        """Generate dynamic feedback for hip position based on actual measurements"""
        if not hip_angles:
            return "Hip position is crucial for sumo deadlift efficiency."
        
        avg_hip_angle = np.mean(hip_angles)
        if score >= 85:
            return f"Perfect hip position! Averaged {avg_hip_angle:.1f}° hip angle (target: 70-110°)."
        elif score >= 70:
            return f"Good hip position at {avg_hip_angle:.1f}°. Fine-tune setup for optimal leverage (target: 70-110°)."
        else:
            return f"Hip angle at {avg_hip_angle:.1f}° needs adjustment. Focus on proper setup position (target: 70-110°)."
    
    def _generate_knee_feedback(self, knee_angles: List[float], score: int) -> str:
        """Generate dynamic feedback for knee position based on actual measurements"""
        if not knee_angles:
            return "Keep knees tracking over toes for proper alignment."
        
        avg_knee_angle = np.mean(knee_angles)
        if score >= 85:
            return f"Excellent knee position! Maintained {avg_knee_angle:.1f}° knee angle (target: 80-120°)."
        elif score >= 70:
            return f"Good knee position at {avg_knee_angle:.1f}°. Keep knees tracking over toes (target: 80-120°)."
        else:
            return f"Knee angle at {avg_knee_angle:.1f}° needs work. Focus on keeping knees over toes (target: 80-120°)."
    
    def _generate_torso_feedback(self, torso_angles: List[float], score: int) -> str:
        """Generate dynamic feedback for torso position based on actual measurements"""
        if not torso_angles:
            return "Maintain upright torso to keep the bar path straight."
        
        avg_torso_angle = np.mean(torso_angles)
        if score >= 85:
            return f"Perfect torso position! Maintained {avg_torso_angle:.1f}° angle (target: 85-105°)."
        elif score >= 70:
            return f"Good torso position at {avg_torso_angle:.1f}°. Keep chest up and core tight (target: 85-105°)."
        else:
            return f"Torso angle at {avg_torso_angle:.1f}° needs work. Focus on keeping chest up and core tight (target: 85-105°)."
    
    def _generate_stance_feedback(self, stance_widths: List[float], score: int) -> str:
        """Generate dynamic feedback for stance width based on actual measurements"""
        if not stance_widths:
            return "Wide stance allows for more upright torso."
        
        avg_stance_width = np.mean(stance_widths)
        if score >= 85:
            return f"Perfect stance width! Averaged {avg_stance_width:.1f}% width (target: >15%)."
        elif score >= 70:
            return f"Good stance width at {avg_stance_width:.1f}%. Consider going wider for better leverage (target: >15%)."
        else:
            return f"Stance width at {avg_stance_width:.1f}% is too narrow. Widen your stance to get hands inside legs (target: >15%)."
    
    async def _create_screenshots(self, pose_data: List[Dict[str, Any]], frames: List[str]) -> List[str]:
        """Create single annotated screenshot highlighting the most crucial improvement point"""
        screenshots = []
        
        print(f"Creating single summary screenshot for sumo deadlift from {len(pose_data)} pose data entries")
        
        if not pose_data or not frames:
            print("No pose data or frames available for screenshot generation")
            return screenshots
        
        # Select the middle frame as the most representative
        middle_index = len(pose_data) // 2
        frame_path = frames[middle_index]
        pose_frame = pose_data[middle_index]
        
        print(f"Creating summary screenshot from middle frame: {frame_path}")
        
        if pose_frame.get('landmarks'):
            try:
                annotated_path = await self.annotator.annotate_sumo_deadlift(
                    frame_path, 
                    pose_frame['landmarks'],
                    "sumo_deadlift_summary.jpg"
                )
                screenshots.append(annotated_path)
                print(f"Successfully created sumo deadlift summary screenshot: {annotated_path}")
            except Exception as e:
                print(f"Error creating sumo deadlift summary screenshot: {str(e)}")
        
        print(f"Final screenshot paths: {screenshots}")
        return screenshots
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Return default analysis when no pose data is available"""
        return {
            "feedback": {
                "overall_score": 75,
                "strengths": ["Good effort on the sumo deadlift!"],
                "areas_for_improvement": ["Continue practicing to refine your technique"],
                "specific_cues": [
                    "Keep your chest up and core tight",
                    "Drive through your heels and extend your hips",
                    "Keep the bar close to your body"
                ],
                "exercise_breakdown": {
                    "hip_position": {"score": 75, "feedback": "Work on hip positioning"},
                    "torso_position": {"score": 80, "feedback": "Keep your chest up"},
                    "stance_width": {"score": 80, "feedback": "Widen your stance"}
                }
            },
            "metrics": {},
            "screenshots": []
        }
