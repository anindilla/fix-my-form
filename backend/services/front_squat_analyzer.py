import numpy as np
from typing import List, Dict, Any
from utils.angle_calculator import AngleCalculator
from utils.screenshot_annotator import ScreenshotAnnotator

class FrontSquatAnalyzer:
    def __init__(self):
        self.annotator = ScreenshotAnnotator()
        self.angle_calc = AngleCalculator()
    
    async def analyze(self, pose_data: List[Dict[str, Any]], frames: List[str]) -> Dict[str, Any]:
        """Analyze front squat form"""
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
            
            metrics[f'frame_{i}_hip_angle'] = hip_angle
            metrics[f'frame_{i}_knee_angle'] = knee_angle
            metrics[f'frame_{i}_ankle_angle'] = ankle_angle
            metrics[f'frame_{i}_torso_angle'] = torso_angle
        
        return metrics
    
    def _calculate_hip_angle(self, landmarks):
        """Calculate hip angle for front squat"""
        try:
            # Hip, knee, ankle landmarks
            hip = landmarks[23]  # Left hip
            knee = landmarks[25]  # Left knee
            ankle = landmarks[27]  # Left ankle
            
            return self.angle_calc.calculate_angle(hip, knee, ankle)
        except:
            return 0
    
    def _calculate_knee_angle(self, landmarks):
        """Calculate knee angle for front squat"""
        try:
            # Hip, knee, ankle landmarks
            hip = landmarks[23]  # Left hip
            knee = landmarks[25]  # Left knee
            ankle = landmarks[27]  # Left ankle
            
            return self.angle_calc.calculate_angle(hip, knee, ankle)
        except:
            return 0
    
    def _calculate_ankle_angle(self, landmarks):
        """Calculate ankle dorsiflexion"""
        try:
            # Knee, ankle, toe landmarks
            knee = landmarks[25]  # Left knee
            ankle = landmarks[27]  # Left ankle
            toe = landmarks[31]  # Left foot index
            
            return self.angle_calc.calculate_angle(knee, ankle, toe)
        except:
            return 0
    
    def _calculate_torso_angle(self, landmarks):
        """Calculate torso angle (should be more upright for front squat)"""
        try:
            # Shoulder, hip, knee landmarks
            shoulder = landmarks[11]  # Left shoulder
            hip = landmarks[23]  # Left hip
            knee = landmarks[25]  # Left knee
            
            return self.angle_calc.calculate_angle(shoulder, hip, knee)
        except:
            return 0
    
    def _generate_feedback(self, metrics: Dict[str, float]) -> Dict[str, Any]:
        """Generate front squat specific feedback"""
        # Analyze the metrics to provide feedback
        strengths = []
        improvements = []
        cues = []
        
        # Get average angles across all frames
        hip_angles = [v for k, v in metrics.items() if 'hip_angle' in k and v > 0]
        knee_angles = [v for k, v in metrics.items() if 'knee_angle' in k and v > 0]
        torso_angles = [v for k, v in metrics.items() if 'torso_angle' in k and v > 0]
        
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
        
        # Calculate overall score
        total_checks = len(hip_angles) + len(knee_angles) + len(torso_angles)
        good_checks = len([a for a in hip_angles if 80 <= a <= 120]) + \
                     len([a for a in knee_angles if 80 <= a <= 120]) + \
                     len([a for a in torso_angles if 80 <= a <= 100])
        
        overall_score = int((good_checks / total_checks * 100)) if total_checks > 0 else 75
        overall_score = max(30, overall_score)  # Ensure minimum score of 30
        
        return {
            "overall_score": overall_score,
            "strengths": strengths,
            "areas_for_improvement": improvements,
            "specific_cues": cues,
            "exercise_breakdown": {
                "depth": {
                    "score": int(np.mean([80 if 80 <= a <= 120 else 60 for a in hip_angles])) if hip_angles else 75,
                    "feedback": "Front squat depth is crucial for full range of motion"
                },
                "torso_position": {
                    "score": int(np.mean([90 if 80 <= a <= 100 else 70 for a in torso_angles])) if torso_angles else 80,
                    "feedback": "Maintain upright torso to keep the bar in position"
                },
                "knee_tracking": {
                    "score": int(np.mean([85 if 80 <= a <= 120 else 65 for a in knee_angles])) if knee_angles else 80,
                    "feedback": "Keep knees tracking over toes for proper alignment"
                }
            }
        }
    
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
