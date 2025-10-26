import os
import logging
import subprocess
from typing import Tuple, Optional
import tempfile

logger = logging.getLogger(__name__)

class VideoProcessor:
    """Handles video preprocessing and validation for Gemini analysis"""
    
    def __init__(self):
        self.max_duration = 30  # seconds
        self.max_file_size = 50 * 1024 * 1024  # 50MB
        self.target_resolution = "720p"
        self.target_fps = 30
    
    async def validate_video(self, video_path: str) -> Tuple[bool, str]:
        """Validate video file and return (is_valid, error_message)"""
        try:
            # Check if file exists
            if not os.path.exists(video_path):
                return False, "Video file not found"
            
            # Check file size
            file_size = os.path.getsize(video_path)
            if file_size == 0:
                return False, "Video file is empty"
            
            if file_size > self.max_file_size:
                return False, f"Video file too large ({file_size / (1024*1024):.1f}MB > 50MB)"
            
            # Check if it's a valid video file using ffprobe
            try:
                result = subprocess.run([
                    'ffprobe', '-v', 'quiet', '-print_format', 'json', 
                    '-show_format', '-show_streams', video_path
                ], capture_output=True, text=True, timeout=10)
                
                if result.returncode != 0:
                    return False, "Invalid video file format"
                
                # Parse video info
                import json
                video_info = json.loads(result.stdout)
                
                # Check if it has video streams
                video_streams = [s for s in video_info.get('streams', []) if s.get('codec_type') == 'video']
                if not video_streams:
                    return False, "No video streams found in file"
                
                # Check duration
                duration = float(video_info.get('format', {}).get('duration', 0))
                if duration > self.max_duration:
                    return False, f"Video too long ({duration:.1f}s > {self.max_duration}s)"
                
                if duration < 1:
                    return False, "Video too short (less than 1 second)"
                
                logger.info(f"✅ Video validation passed: {duration:.1f}s, {file_size / (1024*1024):.1f}MB")
                return True, ""
                
            except subprocess.TimeoutExpired:
                return False, "Video validation timeout"
            except FileNotFoundError:
                logger.warning("ffprobe not found, skipping detailed validation")
                # Basic file validation only
                return True, ""
                
        except Exception as e:
            logger.error(f"Video validation error: {str(e)}")
            return False, f"Validation error: {str(e)}"
    
    async def optimize_video(self, input_path: str, output_path: str) -> bool:
        """Optimize video for Gemini analysis"""
        try:
            logger.info(f"Optimizing video: {input_path} -> {output_path}")
            
            # Use ffmpeg to optimize video
            cmd = [
                'ffmpeg', '-i', input_path,
                '-vf', f'scale=1280:720',  # Scale to 720p
                '-r', str(self.target_fps),  # Set frame rate
                '-c:v', 'libx264',  # Use H.264 codec
                '-preset', 'fast',  # Fast encoding
                '-crf', '23',  # Good quality/size balance
                '-c:a', 'aac',  # Audio codec
                '-b:a', '128k',  # Audio bitrate
                '-movflags', '+faststart',  # Optimize for streaming
                '-y',  # Overwrite output file
                output_path
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
            
            if result.returncode == 0:
                # Check output file size
                output_size = os.path.getsize(output_path)
                input_size = os.path.getsize(input_path)
                compression_ratio = (1 - output_size / input_size) * 100
                
                logger.info(f"✅ Video optimized: {input_size / (1024*1024):.1f}MB -> {output_size / (1024*1024):.1f}MB ({compression_ratio:.1f}% reduction)")
                return True
            else:
                logger.error(f"Video optimization failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Video optimization timeout")
            return False
        except FileNotFoundError:
            logger.warning("ffmpeg not found, skipping optimization")
            # Copy original file if ffmpeg not available
            import shutil
            shutil.copy2(input_path, output_path)
            return True
        except Exception as e:
            logger.error(f"Video optimization error: {str(e)}")
            return False
    
    async def process_video_for_analysis(self, video_path: str) -> Optional[str]:
        """Process video for Gemini analysis - validate and optimize"""
        try:
            logger.info(f"Processing video for analysis: {video_path}")
            
            # Step 1: Validate video
            is_valid, error_msg = await self.validate_video(video_path)
            if not is_valid:
                logger.error(f"❌ Video validation failed: {error_msg}")
                raise Exception(f"Invalid video: {error_msg}")
            
            # Step 2: Create optimized version
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as temp_file:
                optimized_path = temp_file.name
            
            # Step 3: Optimize video
            success = await self.optimize_video(video_path, optimized_path)
            if not success:
                logger.error("❌ Video optimization failed")
                raise Exception("Video optimization failed")
            
            # Step 4: Validate optimized video
            is_valid, error_msg = await self.validate_video(optimized_path)
            if not is_valid:
                logger.error(f"❌ Optimized video validation failed: {error_msg}")
                os.unlink(optimized_path)
                raise Exception(f"Optimized video invalid: {error_msg}")
            
            logger.info(f"✅ Video processed successfully: {optimized_path}")
            return optimized_path
            
        except Exception as e:
            logger.error(f"Video processing failed: {str(e)}")
            # Clean up temp file if it exists
            if 'optimized_path' in locals() and os.path.exists(optimized_path):
                os.unlink(optimized_path)
            raise
    
    def cleanup_temp_file(self, file_path: str):
        """Clean up temporary file"""
        try:
            if os.path.exists(file_path):
                os.unlink(file_path)
                logger.info(f"Cleaned up temp file: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup temp file {file_path}: {str(e)}")
