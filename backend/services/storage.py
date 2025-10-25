import boto3
import os
from botocore.exceptions import ClientError
from typing import List
import uuid

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
            # Create bucket if it doesn't exist
            try:
                self.s3_client.head_bucket(Bucket=self.bucket_name)
            except ClientError:
                self.s3_client.create_bucket(Bucket=self.bucket_name)
            
            # Upload file
            file_content = await file.read()
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=f"videos/{filename}",
                Body=file_content,
                ContentType=file.content_type
            )
            
            # Return public URL
            return f"https://{self.bucket_name}.{os.getenv('R2_ENDPOINT_URL', '').replace('https://', '')}/videos/{filename}"
            
        except Exception as e:
            raise Exception(f"Failed to upload video: {str(e)}")
    
    async def download_video(self, filename: str) -> str:
        """Download video from R2 to local temp file"""
        try:
            local_path = f"/tmp/{filename}"
            self.s3_client.download_file(
                self.bucket_name,
                f"videos/{filename}",
                local_path
            )
            return local_path
        except Exception as e:
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
