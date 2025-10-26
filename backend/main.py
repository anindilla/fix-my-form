from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import logging
from dotenv import load_dotenv
from services.storage import StorageService
from services.llm_analyzer import LLMAnalyzer
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
logger = logging.getLogger(__name__)
storage_service = StorageService()
llm_analyzer = LLMAnalyzer()

@app.get("/")
async def root():
    return {"message": "Workout Form Analyzer API"}

@app.get("/api/test-download")
async def test_download():
    """Test R2 video download"""
    try:
        # Test with a dummy filename
        test_filename = "test-download.mp4"
        result = await storage_service.download_video(test_filename)
        return {"status": "success", "message": f"Download test completed: {result}"}
    except Exception as e:
        return {"status": "error", "message": str(e), "error_type": type(e).__name__}

@app.get("/api/test-frames")
async def test_frames():
    """Test frame extraction"""
    try:
        # Create a dummy video path
        test_video_path = "/tmp/test_video.mp4"
        frames = await video_processor.extract_frames(test_video_path)
        return {"status": "success", "message": f"Frame extraction test completed: {len(frames)} frames"}
    except Exception as e:
        return {"status": "error", "message": str(e), "error_type": type(e).__name__}

@app.get("/api/test-pose")
async def test_pose():
    """Test pose detection"""
    try:
        import mediapipe as mp
        pose = mp.solutions.pose.Pose(
            model_complexity=1,
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3,
            smooth_landmarks=True
        )
        return {"status": "success", "message": "MediaPipe pose detection initialized successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e), "error_type": type(e).__name__}

@app.get("/api/test-movement")
async def test_movement():
    """Test movement detection"""
    try:
        # Test with dummy pose data
        dummy_pose_data = [{
            "landmarks": [
                {"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.9} for _ in range(33)
            ]
        }]
        dummy_frames = ["/tmp/test_frame.jpg"]
        
        start, end = movement_detector.detect_movement_period(dummy_pose_data, dummy_frames)
        return {"status": "success", "message": f"Movement detection test completed: {start}-{end}"}
    except Exception as e:
        return {"status": "error", "message": str(e), "error_type": type(e).__name__}

@app.get("/api/test-analysis")
async def test_analysis():
    """Test analysis pipeline with dummy data"""
    try:
        # Create dummy pose data
        dummy_pose_data = [{
            "landmarks": [
                {"x": 0.5, "y": 0.5, "z": 0.0, "visibility": 0.9} for _ in range(33)
            ]
        }]
        
        dummy_frames = ["/tmp/test_frame.jpg"]
        
        # Test squat analyzer
        result = await squat_analyzer.analyze(dummy_pose_data, dummy_frames)
        
        return {
            "status": "success", 
            "message": "Analysis pipeline works",
            "result_keys": list(result.keys())
        }
    except Exception as e:
        import traceback
        return {
            "status": "error", 
            "message": str(e),
            "error_type": type(e).__name__,
            "traceback": traceback.format_exc()
        }

@app.get("/api/test-pose")
async def test_pose():
    """Test if MediaPipe can be initialized"""
    try:
        import mediapipe as mp
        pose = mp.solutions.pose.Pose(
            model_complexity=1,
            min_detection_confidence=0.3,
            min_tracking_confidence=0.3,
            smooth_landmarks=True
        )
        return {"status": "success", "message": "MediaPipe initialized successfully"}
    except Exception as e:
        return {"status": "error", "message": str(e), "error_type": type(e).__name__}

@app.get("/api/test-opencv")
async def test_opencv():
    """Test if OpenCV can be imported"""
    try:
        import cv2
        return {"status": "success", "message": f"OpenCV version: {cv2.__version__}"}
    except Exception as e:
        return {"status": "error", "message": str(e), "error_type": type(e).__name__}

@app.get("/api/test-services")
async def test_services():
    """Test if all services can be initialized"""
    try:
        # Test each service initialization
        services = {
            "storage_service": storage_service,
            "video_processor": video_processor,
            "pose_analyzer": pose_analyzer,
            "movement_detector": movement_detector,
            "squat_analyzer": squat_analyzer,
            "deadlift_analyzer": deadlift_analyzer,
            "front_squat_analyzer": front_squat_analyzer,
            "sumo_deadlift_analyzer": sumo_deadlift_analyzer
        }
        
        results = {}
        for name, service in services.items():
            try:
                # Test if service has required methods
                if hasattr(service, 'analyze'):
                    results[name] = "✅ OK"
                elif hasattr(service, 'download_video'):
                    results[name] = "✅ OK"
                elif hasattr(service, 'extract_frames'):
                    results[name] = "✅ OK"
                elif hasattr(service, 'analyze_poses'):
                    results[name] = "✅ OK"
                elif hasattr(service, 'detect_movement_period'):
                    results[name] = "✅ OK"
                else:
                    results[name] = "⚠️ No known methods"
            except Exception as e:
                results[name] = f"❌ Error: {str(e)}"
        
        return {"status": "success", "services": results}
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.get("/api/debug/r2-contents")
async def debug_r2_contents():
    """List all objects in R2 bucket for debugging"""
    try:
        response = storage_service.s3_client.list_objects_v2(
            Bucket=storage_service.bucket_name,
            Prefix="videos/"
        )
        
        objects = []
        if 'Contents' in response:
            for obj in response['Contents']:
                objects.append({
                    "key": obj['Key'],
                    "size": obj['Size'],
                    "last_modified": obj['LastModified'].isoformat()
                })
        
        return {
            "bucket": storage_service.bucket_name,
            "total_objects": len(objects),
            "objects": objects
        }
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.1"}

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

@app.post("/api/analyze", response_model=AnalysisResponse)
async def analyze_video(request: AnalysisRequest):
    """Analyze video and return results with quality gates"""
    try:
        logger.info(f"Starting analysis for {request.exercise_type} - {request.file_id}")
        
        # Set timeout for entire analysis (5 minutes)
        analysis_task = asyncio.create_task(_perform_analysis(request))
        
        try:
            result = await asyncio.wait_for(analysis_task, timeout=300)  # 5 minutes
            return result
        except asyncio.TimeoutError:
            logger.error(f"Analysis timeout for {request.file_id}")
            raise HTTPException(status_code=504, detail="Analysis timeout - video may be too long or complex")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed for {request.file_id}: {str(e)}")
        logger.error(f"Error type: {type(e).__name__}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        # Return detailed error for debugging
        return JSONResponse(
            status_code=500,
            content={
                "detail": f"Analysis failed: {str(e)}",
                "error_type": type(e).__name__,
                "traceback": traceback.format_exc()
            }
        )

async def _perform_analysis(request: AnalysisRequest) -> AnalysisResponse:
    """Perform analysis using Gemini Vision"""
    logger.info("=== Starting Analysis Pipeline ===")
    logger.info(f"File ID: {request.file_id}")
    logger.info(f"Filename: {request.filename}")
    logger.info(f"Exercise Type: {request.exercise_type}")
    
    # Step 1: Download video from R2
    logger.info("Step 1: Downloading video from R2...")
    logger.info(f"  Looking for: videos/{request.filename}")
    
    try:
        video_path = await storage_service.download_video(request.filename)
        logger.info(f"✅ Video downloaded successfully: {video_path}")
        
        # Verify file exists locally
        import os
        if not os.path.exists(video_path):
            raise Exception(f"Video file not found at {video_path}")
        
        file_size = os.path.getsize(video_path)
        logger.info(f"  Local file size: {file_size} bytes ({file_size / (1024*1024):.2f} MB)")
        
    except Exception as e:
        logger.error(f"❌ Video download failed: {str(e)}")
        raise
    
    # Step 2: Analyze with Gemini (sends entire video!)
    logger.info("Step 2: Analyzing with Gemini Vision...")
    try:
        analysis_result = await llm_analyzer.analyze_exercise(video_path, request.exercise_type)
        logger.info("✅ Analysis completed!")
        
        # Log analysis results summary
        if "feedback" in analysis_result and "overall_score" in analysis_result["feedback"]:
            score = analysis_result["feedback"]["overall_score"]
            logger.info(f"  Overall score: {score}/100")
        
    except Exception as e:
        logger.error(f"❌ Gemini analysis failed: {str(e)}")
        raise
    
    # Step 3: Create response
    analysis_response = AnalysisResponse(
        file_id=request.file_id,
        exercise_type=request.exercise_type,
        status="completed",
        feedback=analysis_result["feedback"],
        screenshots=analysis_result["screenshots"],
        metrics=analysis_result["metrics"]
    )
    
    # Store the result
    analysis_results[request.file_id] = analysis_response
    logger.info(f"✅ Analysis completed successfully for {request.file_id}")
    logger.info("=== Analysis Pipeline Complete ===")
    
    return analysis_response

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)