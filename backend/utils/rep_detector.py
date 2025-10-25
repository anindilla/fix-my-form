import numpy as np
from typing import List, Dict, Tuple, Any
from scipy.signal import find_peaks

class RepDetector:
    """Detects individual reps from pose data by tracking angle cycles"""
    
    def __init__(self):
        self.min_rep_duration = 10  # Minimum frames for a rep
        self.smoothing_window = 5   # Smoothing window for angle data
    
    def detect_reps(self, pose_data: List[Dict], exercise_type: str) -> List[Tuple[int, int]]:
        """
        Detect individual reps from pose data
        
        Args:
            pose_data: List of pose data dictionaries
            exercise_type: Type of exercise ('squat', 'deadlift', etc.)
            
        Returns:
            List of (start_frame, end_frame) tuples for each rep
        """
        if not pose_data or len(pose_data) < self.min_rep_duration:
            return []
        
        # Extract angle data based on exercise type
        if exercise_type in ['squat', 'front_squat']:
            angles = self._extract_squat_angles(pose_data)
        elif exercise_type in ['deadlift', 'conventional_deadlift', 'sumo_deadlift']:
            angles = self._extract_deadlift_angles(pose_data)
        else:
            # Fallback to hip angle
            angles = self._extract_hip_angles(pose_data)
        
        if not angles:
            return []
        
        # Smooth the angle data
        smoothed_angles = self._smooth_angles(angles)
        
        # Find rep boundaries
        rep_boundaries = self._find_rep_boundaries(smoothed_angles)
        
        # Filter out very short reps
        valid_reps = []
        for start, end in rep_boundaries:
            if end - start >= self.min_rep_duration:
                valid_reps.append((start, end))
        
        return valid_reps
    
    def _extract_squat_angles(self, pose_data: List[Dict]) -> List[float]:
        """Extract hip angles for squat detection"""
        angles = []
        for frame_data in pose_data:
            landmarks = frame_data.get("landmarks", [])
            if landmarks and len(landmarks) >= 24:  # MediaPipe pose has 33 landmarks
                # Calculate hip angle (hip-knee-ankle)
                try:
                    hip_angle = self._calculate_hip_angle(landmarks)
                    angles.append(hip_angle)
                except:
                    angles.append(90)  # Default neutral angle
            else:
                angles.append(90)  # Default when landmarks not available
        return angles
    
    def _extract_deadlift_angles(self, pose_data: List[Dict]) -> List[float]:
        """Extract hip angles for deadlift detection"""
        angles = []
        for frame_data in pose_data:
            landmarks = frame_data.get("landmarks", [])
            if landmarks and len(landmarks) >= 24:
                try:
                    # For deadlift, use hip angle relative to vertical
                    hip_angle = self._calculate_hip_angle(landmarks)
                    angles.append(hip_angle)
                except:
                    angles.append(90)
            else:
                angles.append(90)
        return angles
    
    def _extract_hip_angles(self, pose_data: List[Dict]) -> List[float]:
        """Fallback hip angle extraction"""
        return self._extract_squat_angles(pose_data)
    
    def _calculate_hip_angle(self, landmarks: List[Dict]) -> float:
        """Calculate hip angle from landmarks"""
        try:
            # MediaPipe pose landmarks
            # Hip: 23 (left), 24 (right)
            # Knee: 25 (left), 26 (right) 
            # Ankle: 27 (left), 28 (right)
            
            left_hip = landmarks[23]
            right_hip = landmarks[24]
            left_knee = landmarks[25]
            right_knee = landmarks[26]
            left_ankle = landmarks[27]
            right_ankle = landmarks[28]
            
            # Use average of left and right sides
            left_angle = self._angle_between_points(
                left_hip, left_knee, left_ankle
            )
            right_angle = self._angle_between_points(
                right_hip, right_knee, right_ankle
            )
            
            return (left_angle + right_angle) / 2
            
        except (IndexError, KeyError, TypeError):
            return 90  # Default neutral angle
    
    def _angle_between_points(self, p1: Dict, p2: Dict, p3: Dict) -> float:
        """Calculate angle between three points (p2 is vertex)"""
        try:
            # Convert to numpy arrays for easier calculation
            a = np.array([p1['x'], p1['y']])
            b = np.array([p2['x'], p2['y']])
            c = np.array([p3['x'], p3['y']])
            
            # Calculate vectors
            ba = a - b
            bc = c - b
            
            # Calculate angle
            cos_angle = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
            cos_angle = np.clip(cos_angle, -1.0, 1.0)  # Avoid numerical errors
            angle = np.arccos(cos_angle)
            
            return np.degrees(angle)
            
        except (KeyError, TypeError, ValueError):
            return 90  # Default neutral angle
    
    def _smooth_angles(self, angles: List[float]) -> List[float]:
        """Smooth angle data to reduce noise"""
        if len(angles) < self.smoothing_window:
            return angles
        
        smoothed = []
        for i in range(len(angles)):
            start_idx = max(0, i - self.smoothing_window // 2)
            end_idx = min(len(angles), i + self.smoothing_window // 2 + 1)
            window_angles = angles[start_idx:end_idx]
            smoothed.append(np.mean(window_angles))
        
        return smoothed
    
    def _find_rep_boundaries(self, angles: List[float]) -> List[Tuple[int, int]]:
        """Find rep boundaries using peak detection"""
        if len(angles) < 10:
            return []
        
        # Convert to numpy array
        angle_array = np.array(angles)
        
        # Find peaks (standing position) and valleys (bottom position)
        # For squats: peaks are standing (larger angles), valleys are bottom (smaller angles)
        # For deadlifts: peaks are standing (larger angles), valleys are bottom (smaller angles)
        
        # Find valleys (bottom of movement)
        valleys, _ = find_peaks(-angle_array, distance=self.min_rep_duration)
        
        # Find peaks (top of movement) 
        peaks, _ = find_peaks(angle_array, distance=self.min_rep_duration)
        
        # Combine and sort all key points
        key_points = sorted(list(peaks) + list(valleys))
        
        if len(key_points) < 2:
            # If we can't find clear reps, treat the whole video as one rep
            return [(0, len(angles) - 1)]
        
        # Create rep boundaries
        rep_boundaries = []
        
        # Start from the beginning
        start = 0
        for i, point in enumerate(key_points):
            if i == 0:
                continue
            
            # End of current rep
            end = point
            if end - start >= self.min_rep_duration:
                rep_boundaries.append((start, end))
            
            # Start of next rep
            start = point
        
        # Add the last rep if it's long enough
        if len(angles) - start >= self.min_rep_duration:
            rep_boundaries.append((start, len(angles) - 1))
        
        return rep_boundaries
    
    def get_rep_data(self, pose_data: List[Dict], rep_boundaries: List[Tuple[int, int]]) -> List[Dict]:
        """Extract pose data for each rep"""
        rep_data = []
        
        for start, end in rep_boundaries:
            rep_frames = pose_data[start:end+1]
            rep_data.append({
                'start_frame': start,
                'end_frame': end,
                'frames': rep_frames,
                'duration': end - start + 1
            })
        
        return rep_data

