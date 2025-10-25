import numpy as np
from typing import List, Dict, Any
from utils.angle_calculator import AngleCalculator
from utils.screenshot_annotator import ScreenshotAnnotator

class SumoDeadliftAnalyzer:
    def __init__(self):
        self.annotator = ScreenshotAnnotator()
        self.angle_calc = AngleCalculator()
    
    async def analyze(self, pose_data: List[Dict[str, Any]], frames: List[str]) -> Dict[str, Any]:
        """Analyze sumo deadlift form"""
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
        
        # Extract key metrics
        metrics = self._calculate_metrics(pose_data)
        
        # Generate feedback
        feedback = self._generate_feedback(metrics)
        
        # Skip screenshot generation for now
        print("Skipping screenshot generation - visual analysis disabled")
        screenshots = []
        
        return {
            "feedback": feedback,
            "metrics": metrics,
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
            
            metrics[f'frame_{i}_hip_angle'] = hip_angle
            metrics[f'frame_{i}_knee_angle'] = knee_angle
            metrics[f'frame_{i}_torso_angle'] = torso_angle
            metrics[f'frame_{i}_stance_width'] = stance_width
        
        return metrics
    
    def _calculate_hip_angle(self, landmarks):
        """Calculate hip angle for sumo deadlift"""
        try:
            # Hip, knee, ankle landmarks
            hip = landmarks[23]  # Left hip
            knee = landmarks[25]  # Left knee
            ankle = landmarks[27]  # Left ankle
            
            return self.angle_calc.calculate_angle(hip, knee, ankle)
        except:
            return 0
    
    def _calculate_knee_angle(self, landmarks):
        """Calculate knee angle for sumo deadlift"""
        try:
            # Hip, knee, ankle landmarks
            hip = landmarks[23]  # Left hip
            knee = landmarks[25]  # Left knee
            ankle = landmarks[27]  # Left ankle
            
            return self.angle_calc.calculate_angle(hip, knee, ankle)
        except:
            return 0
    
    def _calculate_torso_angle(self, landmarks):
        """Calculate torso angle (should be more upright for sumo)"""
        try:
            # Shoulder, hip, knee landmarks
            shoulder = landmarks[11]  # Left shoulder
            hip = landmarks[23]  # Left hip
            knee = landmarks[25]  # Left knee
            
            return self.angle_calc.calculate_angle(shoulder, hip, knee)
        except:
            return 0
    
    def _calculate_stance_width(self, landmarks):
        """Calculate stance width for sumo deadlift"""
        try:
            # Distance between feet
            left_ankle = landmarks[27]  # Left ankle
            right_ankle = landmarks[28]  # Right ankle
            
            # Calculate distance
            distance = np.sqrt(
                (left_ankle['x'] - right_ankle['x'])**2 + 
                (left_ankle['y'] - right_ankle['y'])**2
            )
            
            return distance * 100  # Convert to percentage
        except:
            return 0
    
    def _generate_feedback(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Generate sumo deadlift specific feedback"""
        # Analyze the metrics to provide feedback
        strengths = []
        improvements = []
        cues = []
        
        # Get average angles across all frames
        hip_angles = [v for k, v in metrics.items() if 'hip_angle' in k and v > 0]
        knee_angles = [v for k, v in metrics.items() if 'knee_angle' in k and v > 0]
        torso_angles = [v for k, v in metrics.items() if 'torso_angle' in k and v > 0]
        stance_widths = [v for k, v in metrics.items() if 'stance_width' in k and v > 0]
        
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
        
        # Calculate breakdown scores first
        breakdown_scores = {
            "hip_position": int(np.mean([85 if 70 <= a <= 110 else 65 for a in hip_angles])) if hip_angles else 75,
            "knee_position": int(np.mean([85 if 80 <= a <= 120 else 65 for a in knee_angles])) if knee_angles else 80,
            "torso_position": int(np.mean([90 if 85 <= a <= 105 else 70 for a in torso_angles])) if torso_angles else 80,
            "stance_width": int(np.mean([90 if w >= 15 else 70 for w in stance_widths])) if stance_widths else 80
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
                    "feedback": "Hip position is crucial for sumo deadlift efficiency"
                },
                "knee_position": {
                    "score": breakdown_scores["knee_position"],
                    "feedback": "Keep knees tracking over toes for proper alignment"
                },
                "torso_position": {
                    "score": breakdown_scores["torso_position"],
                    "feedback": "Maintain upright torso to keep the bar path straight"
                },
                "stance_width": {
                    "score": breakdown_scores["stance_width"],
                    "feedback": "Wide stance allows for more upright torso"
                }
            }
        }
    
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
