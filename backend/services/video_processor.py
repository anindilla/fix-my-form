import cv2
import os
import logging
from typing import List
import numpy as np

logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.temp_dir = "/tmp/frames"
        os.makedirs(self.temp_dir, exist_ok=True)
    
    async def extract_frames(self, video_path: str) -> List[str]:
        """
        Extract frames from video using adaptive sampling strategy:
        - Videos <= 10s: Extract ALL frames (max 300 at 30fps)
        - Videos 10-30s: 1 frame per second
        - Videos > 30s: 1 frame per 2 seconds (max 30 frames)
        """
        try:
            video_info = self.get_video_info(video_path)
            duration = video_info["duration"]
            fps = video_info["fps"]
            frame_count = video_info["frame_count"]
            
            logger.info(f"Extracting frames from video: {duration:.1f}s, {fps:.1f} fps, {frame_count} frames")
            
            # Determine sampling strategy
            if duration <= 10:
                # Short video: extract all frames
                frame_interval = 1
                max_frames = min(int(duration * fps), 300)  # Cap at 300 frames
                logger.info(f"Short video: extracting all frames (max {max_frames})")
            elif duration <= 30:
                # Medium video: 1 frame per second
                frame_interval = int(fps)
                max_frames = int(duration)
                logger.info(f"Medium video: extracting 1 frame per second ({max_frames} frames)")
            else:
                # Long video: 1 frame per 2 seconds, max 30
                frame_interval = int(fps * 2)
                max_frames = 30
                logger.info(f"Long video: extracting 1 frame per 2 seconds (max {max_frames} frames)")
            
            cap = cv2.VideoCapture(video_path)
            frame_paths = []
            frame_number = 0
            extracted_count = 0
            
            while cap.isOpened() and extracted_count < max_frames:
                ret, frame = cap.read()
                if not ret:
                    break
                
                if frame_number % frame_interval == 0:
                    frame_filename = f"{self.temp_dir}/frame_{frame_number}.jpg"
                    cv2.imwrite(frame_filename, frame)
                    frame_paths.append(frame_filename)
                    extracted_count += 1
                
                frame_number += 1
            
            cap.release()
            
            logger.info(f"Extracted {len(frame_paths)} frames from video")
            return frame_paths
            
        except Exception as e:
            logger.error(f"Failed to extract frames: {str(e)}")
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
