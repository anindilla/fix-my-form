import cv2
import os
from typing import List
import numpy as np

class VideoProcessor:
    def __init__(self):
        self.temp_dir = "/tmp/frames"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def extract_frames(self, video_path: str, max_frames: int = 30) -> List[str]:
        """Extract frames from video for analysis"""
        try:
            cap = cv2.VideoCapture(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Calculate frame interval to get representative frames
            frame_interval = max(1, frame_count // max_frames)
            
            frame_paths = []
            frame_number = 0
            
            while cap.isOpened() and len(frame_paths) < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_number % frame_interval == 0:
                    frame_filename = f"{self.temp_dir}/frame_{frame_number}.jpg"
                    cv2.imwrite(frame_filename, frame)
                    frame_paths.append(frame_filename)
                
                frame_number += 1
            
            cap.release()
            return frame_paths
            
        except Exception as e:
            raise Exception(f"Failed to extract frames: {str(e)}")
    
    def get_video_info(self, video_path: str) -> dict:
        """Get video metadata"""
        try:
            cap = cv2.VideoCapture(video_path)
            frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            duration = frame_count / fps if fps > 0 else 0
            
            cap.release()
            
            return {
                "frame_count": frame_count,
                "fps": fps,
                "width": width,
                "height": height,
                "duration": duration
            }
        except Exception as e:
            raise Exception(f"Failed to get video info: {str(e)}")
