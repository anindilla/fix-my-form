import numpy as np
import logging
from typing import List, Dict, Any
from utils.angle_calculator import AngleCalculator
from utils.screenshot_annotator import ScreenshotAnnotator
from utils.rep_detector import RepDetector

logger = logging.getLogger(__name__)

class FrontSquatAnalyzer:
    def __init__(self):
        self.annotator = ScreenshotAnnotator()
        self.angle_calc = AngleCalculator()
        self.rep_detector = RepDetector()
    
    async def analyze(self, pose_data: List[Dict[str, Any]], frames: List[str]) -> Dict[str, Any]:
        """Analyze front squat form"""
        if not pose_data:
            logger.warning("No pose data detected - MediaPipe may have failed")
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
        logger.info("Detecting reps in front squat video")
        rep_boundaries = self.rep_detector.detect_reps(pose_data, "front-squat")
        rep_data = self.rep_detector.get_rep_data(pose_data, rep_boundaries)
        
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
        """Calculate front squat specific metrics"""
        metrics = {}
        
        for i, frame_data in enumerate(pose_data):
            if not frame_data.get('landmarks'):
                continue
                
            landmarks = frame_data['landmarks']
            
            # Front squat specific angles
            # Hip angle (more upright torso for front squat)
            hip_angle = self._calculate_hip_angle(landmarks)
            # Knee angle
            knee_angle = self._calculate_knee_angle(landmarks)
            # Ankle angle (dorsiflexion)
            ankle_angle = self._calculate_ankle_angle(landmarks)
            # Torso angle (should be more upright than back squat)
            torso_angle = self._calculate_torso_angle(landmarks)
            
            # Only store valid angles (not None)
            if hip_angle is not None:
                metrics[f'frame_{i}_hip_angle'] = hip_angle
            if knee_angle is not None:
                metrics[f'frame_{i}_knee_angle'] = knee_angle
            if ankle_angle is not None:
                metrics[f'frame_{i}_ankle_angle'] = ankle_angle
            if torso_angle is not None:
                metrics[f'frame_{i}_torso_angle'] = torso_angle
        
        return metrics
    
    def _calculate_hip_angle(self, landmarks):
        """Calculate hip angle for front squat"""
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
        """Calculate knee angle for front squat"""
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
    
    def _calculate_ankle_angle(self, landmarks):
        """Calculate ankle dorsiflexion"""
        try:
            # Knee, ankle, toe landmarks
            knee = landmarks[25]  # Left knee
            ankle = landmarks[27]  # Left ankle
            toe = landmarks[31]  # Left foot index
            
            # Check landmark visibility
            if not self._is_landmark_visible(knee) or not self._is_landmark_visible(ankle) or not self._is_landmark_visible(toe):
                logger.debug("Ankle angle calculation skipped - landmarks not visible")
                return None
            
            angle = self.angle_calc.calculate_angle(knee, ankle, toe)
            if angle is None or angle <= 0:
                logger.warning(f"Invalid ankle angle: {angle}")
                return None
            return angle
        except Exception as e:
            logger.error(f"Ankle angle calculation failed: {e}")
            return None
    
    def _calculate_torso_angle(self, landmarks):
        """Calculate torso angle (should be more upright for front squat)"""
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
    
    def _is_landmark_visible(self, landmark, threshold=0.7):
        """Check if landmark is visible enough for accurate calculation"""
        return landmark.get('visibility', 0) >= threshold
    
    def _generate_feedback(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Generate front squat specific feedback"""
        # Analyze the metrics to provide feedback
        strengths = []
        improvements = []
        cues = []
        
        # Get average angles across all frames (filter out None and invalid values)
        hip_angles = [v for k, v in metrics.items() if 'hip_angle' in k and v is not None and v > 0]
        knee_angles = [v for k, v in metrics.items() if 'knee_angle' in k and v is not None and v > 0]
        torso_angles = [v for k, v in metrics.items() if 'torso_angle' in k and v is not None and v > 0]
        
        if hip_angles:
            avg_hip_angle = np.mean(hip_angles)
            if 80 <= avg_hip_angle <= 120:
                strengths.append("Good hip mobility and depth")
            elif avg_hip_angle < 80:
                improvements.append("Work on hip mobility - you're not reaching full depth")
                cues.append("Focus on sitting back into the squat")
            else:
                improvements.append("You're not reaching full depth")
                cues.append("Aim to get your hips below your knees")
        
        if knee_angles:
            avg_knee_angle = np.mean(knee_angles)
            if 80 <= avg_knee_angle <= 120:
                strengths.append("Good knee tracking")
            else:
                improvements.append("Watch your knee position")
                cues.append("Keep your knees tracking over your toes")
        
        if torso_angles:
            avg_torso_angle = np.mean(torso_angles)
            if 80 <= avg_torso_angle <= 100:
                strengths.append("Excellent upright torso position")
            elif avg_torso_angle < 80:
                improvements.append("Torso is too upright - you may be compensating")
                cues.append("Allow slight forward lean while keeping chest up")
            else:
                improvements.append("Torso is leaning too far forward")
                cues.append("Keep your chest up and core tight")
        
        # Front squat specific feedback
        if not strengths:
            strengths.append("Good effort on the front squat!")
        
        if not improvements:
            improvements.append("Continue practicing to refine your technique")
        
        if not cues:
            cues.append("Keep your elbows up and chest proud")
            cues.append("Maintain a strong core throughout the movement")
        
        # Check if we have valid angle data (not just zeros)
        valid_hip_angles = [a for a in hip_angles if a > 0]
        valid_knee_angles = [a for a in knee_angles if a > 0]
        valid_torso_angles = [a for a in torso_angles if a > 0]
        
        # If no valid angles detected, return error feedback
        if not valid_hip_angles and not valid_knee_angles and not valid_torso_angles:
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
                    "depth": {
                        "score": 0,
                        "feedback": "Could not measure depth - pose not detected"
                    },
                    "torso_position": {
                        "score": 0,
                        "feedback": "Could not measure torso position - pose not detected"
                    },
                    "knee_tracking": {
                        "score": 0,
                        "feedback": "Could not measure knee tracking - pose not detected"
                    }
                }
            }
        
        # Calculate breakdown scores with actual measurements (stricter scoring)
        def score_depth(angles):
            scores = []
            for a in angles:
                if 85 <= a <= 115:  # Perfect range
                    scores.append(90)
                elif 80 <= a <= 120:  # Good range
                    scores.append(75)
                elif 70 <= a <= 130:  # Acceptable
                    scores.append(60)
                else:  # Poor
                    scores.append(40)
            return int(np.mean(scores))
        
        def score_torso(angles):
            scores = []
            for a in angles:
                if 85 <= a <= 95:  # Perfect upright
                    scores.append(95)
                elif 80 <= a <= 100:  # Good
                    scores.append(80)
                elif 75 <= a <= 105:  # Acceptable
                    scores.append(65)
                else:  # Poor
                    scores.append(45)
            return int(np.mean(scores))
        
        def score_knee(angles):
            scores = []
            for a in angles:
                if 85 <= a <= 115:  # Perfect tracking
                    scores.append(90)
                elif 80 <= a <= 120:  # Good
                    scores.append(75)
                elif 70 <= a <= 130:  # Acceptable
                    scores.append(60)
                else:  # Poor
                    scores.append(40)
            return int(np.mean(scores))
        
        breakdown_scores = {
            "depth": score_depth(valid_hip_angles) if valid_hip_angles else 0,
            "torso_position": score_torso(valid_torso_angles) if valid_torso_angles else 0,
            "knee_tracking": score_knee(valid_knee_angles) if valid_knee_angles else 0
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
                "depth": {
                    "score": breakdown_scores["depth"],
                    "feedback": self._generate_depth_feedback(hip_angles, breakdown_scores["depth"])
                },
                "torso_position": {
                    "score": breakdown_scores["torso_position"],
                    "feedback": self._generate_torso_feedback(torso_angles, breakdown_scores["torso_position"])
                },
                "knee_tracking": {
                    "score": breakdown_scores["knee_tracking"],
                    "feedback": self._generate_knee_tracking_feedback(knee_angles, breakdown_scores["knee_tracking"])
                }
            }
        }
    
    def _generate_depth_feedback(self, hip_angles: List[float], score: int) -> str:
        """Generate dynamic feedback for depth based on actual measurements"""
        valid_angles = [a for a in hip_angles if a > 0]
        if not valid_angles:
            return "Could not measure depth - ensure you're fully visible in the frame."
        
        avg_hip_angle = np.mean(valid_angles)
        if score >= 85:
            return f"Excellent depth! Averaged {avg_hip_angle:.1f}° hip angle (target: 80-120°)."
        elif score >= 70:
            return f"Good depth at {avg_hip_angle:.1f}° hip angle. Aim for 80-120° for optimal range of motion."
        else:
            return f"Work on depth - you averaged {avg_hip_angle:.1f}° hip angle. Target: 80-120° for proper front squat depth."
    
    def _generate_torso_feedback(self, torso_angles: List[float], score: int) -> str:
        """Generate dynamic feedback for torso position based on actual measurements"""
        valid_angles = [a for a in torso_angles if a > 0]
        if not valid_angles:
            return "Could not measure torso position - ensure you're fully visible in the frame."
        
        avg_torso_angle = np.mean(valid_angles)
        if score >= 85:
            return f"Perfect torso position! Maintained {avg_torso_angle:.1f}° angle (target: 80-100°)."
        elif score >= 70:
            return f"Good torso position at {avg_torso_angle:.1f}°. Keep chest up and core tight (target: 80-100°)."
        else:
            return f"Torso angle at {avg_torso_angle:.1f}° needs work. Focus on keeping chest up and core tight (target: 80-100°)."
    
    def _generate_knee_tracking_feedback(self, knee_angles: List[float], score: int) -> str:
        """Generate dynamic feedback for knee tracking based on actual measurements"""
        valid_angles = [a for a in knee_angles if a > 0]
        if not valid_angles:
            return "Could not measure knee tracking - ensure you're fully visible in the frame."
        
        avg_knee_angle = np.mean(valid_angles)
        if score >= 85:
            return f"Excellent knee tracking! Averaged {avg_knee_angle:.1f}° knee angle (target: 80-120°)."
        elif score >= 70:
            return f"Good knee tracking at {avg_knee_angle:.1f}°. Keep knees over toes (target: 80-120°)."
        else:
            return f"Knee angle at {avg_knee_angle:.1f}° needs improvement. Focus on keeping knees tracking over toes (target: 80-120°)."
    
    async def _create_screenshots(self, pose_data: List[Dict[str, Any]], frames: List[str]) -> List[str]:
        """Create single annotated screenshot highlighting the most crucial improvement point"""
        screenshots = []
        
        print(f"Creating single summary screenshot for front squat from {len(pose_data)} pose data entries")
        
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
                annotated_path = await self.annotator.annotate_front_squat(
                    frame_path, 
                    pose_frame['landmarks'],
                    "front_squat_summary.jpg"
                )
                screenshots.append(annotated_path)
                print(f"Successfully created front squat summary screenshot: {annotated_path}")
            except Exception as e:
                print(f"Error creating front squat summary screenshot: {str(e)}")
        
        print(f"Final screenshot paths: {screenshots}")
        return screenshots
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """Return default analysis when no pose data is available"""
        return {
            "feedback": {
                "overall_score": 75,
                "strengths": ["Good effort on the front squat!"],
                "areas_for_improvement": ["Continue practicing to refine your technique"],
                "specific_cues": [
                    "Keep your elbows up and chest proud",
                    "Maintain a strong core throughout the movement",
                    "Focus on sitting back into the squat"
                ],
                "exercise_breakdown": {
                    "depth": {"score": 75, "feedback": "Work on achieving full depth"},
                    "torso_position": {"score": 80, "feedback": "Keep your chest up"},
                    "knee_tracking": {"score": 80, "feedback": "Track knees over toes"}
                }
            },
            "metrics": {},
            "screenshots": []
        }
