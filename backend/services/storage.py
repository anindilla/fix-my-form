import boto3
import os
from botocore.exceptions import ClientError
from typing import List
import uuid
import logging
from functools import wraps
import time

logger = logging.getLogger(__name__)

def retry_on_failure(max_attempts=3, delay=1):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            for attempt in range(1, max_attempts + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        raise
                    logger.warning(f"Attempt {attempt} failed: {e}. Retrying in {delay}s...")
                    time.sleep(delay * attempt)
            return None
        return wrapper
    return decorator

class StorageService:
    def __init__(self):
        self.s3_client = boto3.client(
            's3',
            endpoint_url=os.getenv('R2_ENDPOINT_URL'),
            aws_access_key_id=os.getenv('R2_ACCESS_KEY_ID'),
            aws_secret_access_key=os.getenv('R2_SECRET_ACCESS_KEY'),
            region_name='auto'
        )
        self.bucket_name = os.getenv('R2_BUCKET_NAME', 'fix-my-form')
    
    async def upload_video(self, file, filename: str) -> str:
        """Upload video file to R2 and return public URL"""
        try:
            print(f"Starting upload to R2: {filename}")
            print(f"Bucket: {self.bucket_name}")
            print(f"Endpoint: {os.getenv('R2_ENDPOINT_URL')}")
            
            # Create bucket if it doesn't exist
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
                print(f"Bucket {self.bucket_name} exists")
            except ClientError as e:
                print(f"Bucket {self.bucket_name} does not exist, creating...")
                if e.response['Error']['Code'] == '404':
                    self.s3_client.create_bucket(Bucket=self.bucket_name)
                    print(f"Bucket {self.bucket_name} created successfully")
                else:
                    raise Exception(f"Error checking bucket: {str(e)}")
            
            # Upload file
            file_content = await file.read()
            file_size = len(file_content)
            print(f"Uploading {file_size} bytes to R2...")
            
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"videos/{filename}",
                Body=file_content,
                ContentType=file.content_type
            )
            
            print(f"Upload completed successfully")
            
            # Verify upload by checking if object exists
            try:
                self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=f"videos/{filename}"
                )
                logger.info(f"✅ Verified: File exists in R2 at videos/{filename}")
            except ClientError as e:
                logger.error(f"❌ Verification failed: File NOT found in R2 after upload")
                raise Exception(f"Upload verification failed: {str(e)}")
            
            # Return public URL
            public_url = f"https://{self.bucket_name}.{os.getenv('R2_ENDPOINT_URL', '').replace('https://', '')}/videos/{filename}"
            print(f"Public URL: {public_url}")
            return public_url
            
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_message = e.response['Error']['Message']
            print(f"R2 ClientError: {error_code} - {error_message}")
            raise Exception(f"R2 upload failed ({error_code}): {error_message}")
        except Exception as e:
            print(f"Upload error: {str(e)}")
            raise Exception(f"Failed to upload video: {str(e)}")
    
    @retry_on_failure(max_attempts=3, delay=2)
    async def download_video(self, filename: str) -> str:
        """Download video from R2 to local temp file"""
        try:
            key = f"videos/{filename}"
            local_path = f"/tmp/{filename}"
            
            logger.info(f"Attempting to download from R2:")
            logger.info(f"  Bucket: {self.bucket_name}")
            logger.info(f"  Key: {key}")
            logger.info(f"  Local path: {local_path}")
            
            # Check if file exists first
            try:
                self.s3_client.head_object(
                    Bucket=self.bucket_name,
                    Key=key
                )
                logger.info(f"✅ File exists in R2, proceeding with download")
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    logger.error(f"❌ File not found in R2: {key}")
                    raise Exception(
                        f"Video not found in storage. The video may have expired or failed to upload. "
                        f"Please try uploading again."
                    )
                raise
            
            self.s3_client.download_file(
                self.bucket_name,
                key,
                local_path
            )
            
            logger.info(f"✅ Successfully downloaded video to {local_path}")
            
            # Verify local file exists and get size
            import os
            if not os.path.exists(local_path):
                raise Exception(f"Video file not found at {local_path}")
            
            file_size = os.path.getsize(local_path)
            logger.info(f"  Local file size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
            
            return local_path
        except Exception as e:
            logger.error(f"Failed to download video: {str(e)}")
            raise Exception(f"Failed to download video: {str(e)}")
    
    async def upload_screenshots(self, screenshot_paths: List[str], file_id: str) -> List[str]:
        """Upload annotated screenshots to R2 and return URLs"""
        urls = []
        
        print(f"Uploading {len(screenshot_paths)} screenshots for file_id: {file_id}")
        
        try:
            for i, screenshot_path in enumerate(screenshot_paths):
                print(f"Uploading screenshot {i+1}: {screenshot_path}")
                
                if not os.path.exists(screenshot_path):
                    print(f"Warning: Screenshot file does not exist: {screenshot_path}")
                    continue
                
                screenshot_key = f"screenshots/{file_id}/screenshot_{i+1}.jpg"
                
                with open(screenshot_path, 'rb') as f:
                    self.s3_client.put_object(
                        Bucket=self.bucket_name,
                        Key=screenshot_key,
                        Body=f.read(),
                        ContentType='image/jpeg',
                        ACL='public-read'
                    )
                
                # Use R2 public URL directly
                public_url = os.getenv('R2_PUBLIC_URL', '')
                if not public_url:
                    raise Exception("R2_PUBLIC_URL not configured")
                
                url = f"{public_url}/{screenshot_key}"
                urls.append(url)
                print(f"Uploaded screenshot to: {url}")
                
                # Clean up local file
                os.remove(screenshot_path)
                
        except Exception as e:
            print(f"Error uploading screenshots: {str(e)}")
            raise Exception(f"Failed to upload screenshots: {str(e)}")
        
        print(f"Successfully uploaded {len(urls)} screenshots")
        return urls
