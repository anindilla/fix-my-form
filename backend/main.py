from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from dotenv import load_dotenv
from services.storage import StorageService
from services.video_processor import VideoProcessor
from services.pose_analyzer import PoseAnalyzer
from services.video_quality_validator import VideoQualityValidator
from services.squat_analyzer import SquatAnalyzer
from services.deadlift_analyzer import DeadliftAnalyzer
from services.front_squat_analyzer import FrontSquatAnalyzer
from services.sumo_deadlift_analyzer import SumoDeadliftAnalyzer
from models.schemas import AnalysisRequest, AnalysisResponse, UploadResponse
import uuid
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('app.log')
    ]
)

load_dotenv()

app = FastAPI(title="Workout Form Analyzer", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
storage_service = StorageService()
video_processor = VideoProcessor()
pose_analyzer = PoseAnalyzer()
video_quality_validator = VideoQualityValidator()
squat_analyzer = SquatAnalyzer()
deadlift_analyzer = DeadliftAnalyzer()
front_squat_analyzer = FrontSquatAnalyzer()
sumo_deadlift_analyzer = SumoDeadliftAnalyzer()

@app.get("/")
async def root():
    return {"message": "Workout Form Analyzer API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/api/upload", response_model=UploadResponse)
async def upload_video(file: UploadFile = File(...)):
    """Upload video and return presigned URL for R2 storage"""
    try:
        print(f"Upload attempt: {file.filename}, Content-Type: {file.content_type}")
        
        # Validate file type
        allowed_types = ["video/mp4", "video/mov", "video/quicktime", "video/x-msvideo"]
        if file.content_type not in allowed_types:
            print(f"Invalid file type: {file.content_type}")
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Validate file size (50MB limit)
        max_size = 50 * 1024 * 1024  # 50MB in bytes
        file_content = await file.read()
        file_size = len(file_content)
        print(f"File size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
        
        if file_size > max_size:
            print(f"File too large: {file_size} > {max_size}")
            raise HTTPException(status_code=413, detail="File size exceeds 50MB limit")
        
        # Reset file pointer for upload
        await file.seek(0)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'mp4'
        filename = f"{file_id}.{file_extension}"
        
        print(f"Uploading to R2: {filename}")
        
        # Upload to R2
        upload_url = await storage_service.upload_video(file, filename)
        
        print(f"Upload successful: {upload_url}")
        
        return UploadResponse(
            file_id=file_id,
            filename=filename,
            upload_url=upload_url,
            message="Video uploaded successfully"
        )
    
    except HTTPException:
        # Re-raise HTTP exceptions (validation errors)
        raise
    except Exception as e:
        # Better error logging for debugging
        print(f"Upload error: {str(e)}")
        print(f"File: {file.filename if file else 'Unknown'}")
        print(f"Content-Type: {file.content_type if file else 'Unknown'}")
        print(f"File size: {len(file_content) if 'file_content' in locals() else 'Unknown'}")
        
        # Check for specific error types
        if "R2_ENDPOINT_URL" in str(e) or "R2_ACCESS_KEY_ID" in str(e):
            raise HTTPException(status_code=500, detail="Storage configuration error")
        elif "timeout" in str(e).lower():
            raise HTTPException(status_code=504, detail="Upload timeout - please try again")
        elif "connection" in str(e).lower():
            raise HTTPException(status_code=503, detail="Storage service unavailable")
        else:
            raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

# Store analysis results in memory (in production, use a database)
analysis_results = {}

@app.get("/api/analysis/{analysis_id}")
async def get_analysis(analysis_id: str):
    """Get analysis results by ID"""
    if analysis_id not in analysis_results:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return analysis_results[analysis_id]

# Update the analyze endpoint to store results
@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_video(request: AnalysisRequest):
    """Analyze video and return results with quality gates"""
    try:
        logger.info(f"Starting analysis for {request.exercise_type} - {request.file_id}")
        
        # Download video from R2
        logger.info("Downloading video from R2...")
        video_path = await storage_service.download_video(request.filename)
        logger.info(f"Video downloaded to: {video_path}")
        
        # 1. Validate video quality
        logger.info("Validating video quality...")
        quality_result = await video_quality_validator.validate_video(video_path)
        logger.info(f"Video quality check - Valid: {quality_result['valid']}, Score: {quality_result['quality_score']}")
        
        if not quality_result["valid"]:
            logger.warning(f"Video quality validation failed: {quality_result['issues']}")
            return AnalysisResponse(
                file_id=request.file_id,
                exercise_type=request.exercise_type,
                status="failed",
                diagnostic={
                    "quality_issues": quality_result["issues"],
                    "quality_score": quality_result["quality_score"],
                    "metadata": quality_result["metadata"],
                    "recommendations": [
                        "Ensure video is at least 480x360 resolution",
                        "Keep video between 2-60 seconds",
                        "Use good lighting and clear background",
                        "Ensure person is fully visible in frame"
                    ]
                }
            )
        
        # 2. Extract frames (adaptive)
        logger.info("Extracting frames from video...")
        frames = await video_processor.extract_frames(video_path)
        logger.info(f"Extracted {len(frames)} frames")
        
        # 3. Analyze poses with quality gate
        logger.info("Analyzing poses in frames...")
        pose_data = await pose_analyzer.analyze_poses(frames)
        logger.info(f"Analyzed {len(pose_data)} pose frames")
        
        # Check pose detection quality
        pose_success_rate = len(pose_data) / len(frames) if frames else 0
        if pose_success_rate < 0.3:  # Less than 30% success rate (more lenient)
            logger.warning(f"Pose detection quality too low: {pose_success_rate:.1%}")
            diagnostic_error = pose_analyzer.create_diagnostic_error(pose_data, len(frames))
            return AnalysisResponse(
                file_id=request.file_id,
                exercise_type=request.exercise_type,
                status="failed",
                diagnostic=diagnostic_error["diagnostic"]
            )
        
        # 4. Run exercise analysis
        exercise_type = request.exercise_type.lower()
        logger.info(f"Running {exercise_type} analysis...")
        
        if exercise_type == "back-squat":
            analysis_result = await squat_analyzer.analyze(pose_data, frames)
        elif exercise_type == "front-squat":
            analysis_result = await front_squat_analyzer.analyze(pose_data, frames)
        elif exercise_type == "conventional-deadlift":
            analysis_result = await deadlift_analyzer.analyze(pose_data, frames)
        elif exercise_type == "sumo-deadlift":
            analysis_result = await sumo_deadlift_analyzer.analyze(pose_data, frames)
        else:
            raise HTTPException(status_code=400, detail="Unsupported exercise type")
        
        logger.info("Exercise analysis completed successfully")
        
        # Generate and upload screenshots (optional)
        screenshot_urls = []
        try:
            if analysis_result.get("screenshots"):
                logger.info("Uploading screenshots...")
                screenshot_urls = await storage_service.upload_screenshots(
                    analysis_result["screenshots"], 
                    request.file_id
                )
                logger.info(f"Uploaded {len(screenshot_urls)} screenshots")
        except Exception as e:
            logger.warning(f"Screenshot upload failed: {e}")
            screenshot_urls = []
        
        # Create analysis response
        logger.info("Creating analysis response...")
        analysis_response = AnalysisResponse(
            file_id=request.file_id,
            exercise_type=request.exercise_type,
            status="completed",
            feedback=analysis_result["feedback"],
            screenshots=screenshot_urls,
            metrics=analysis_result["metrics"]
        )
        
        # Store the result
        analysis_results[request.file_id] = analysis_response
        logger.info(f"Analysis completed successfully for {request.file_id}")
        
        return analysis_response
    
    except Exception as e:
        logger.error(f"Analysis failed for {request.file_id}: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
