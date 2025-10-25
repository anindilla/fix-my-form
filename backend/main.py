from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from services.storage import StorageService
from services.video_processor import VideoProcessor
from services.pose_analyzer import PoseAnalyzer
from services.squat_analyzer import SquatAnalyzer
from services.deadlift_analyzer import DeadliftAnalyzer
from services.front_squat_analyzer import FrontSquatAnalyzer
from services.sumo_deadlift_analyzer import SumoDeadliftAnalyzer
from models.schemas import AnalysisRequest, AnalysisResponse, UploadResponse
import uuid
import asyncio

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
        # Validate file type
        allowed_types = ["video/mp4", "video/mov", "video/quicktime", "video/x-msvideo"]
        if file.content_type not in allowed_types:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_extension = file.filename.split('.')[-1] if '.' in file.filename else 'mp4'
        filename = f"{file_id}.{file_extension}"
        
        # Upload to R2
        upload_url = await storage_service.upload_video(file, filename)
        
        return UploadResponse(
            file_id=file_id,
            filename=filename,
            upload_url=upload_url,
            message="Video uploaded successfully"
        )
    
    except Exception as e:
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
    """Analyze video and return results"""
    try:
        # Download video from R2
        video_path = await storage_service.download_video(request.filename)
        
        # Extract frames from video
        frames = await video_processor.extract_frames(video_path)
        
        # Analyze poses in frames
        pose_data = await pose_analyzer.analyze_poses(frames)
        
        # Run exercise-specific analysis
        exercise_type = request.exercise_type.lower()
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
        
        # Generate and upload screenshots
        screenshot_urls = await storage_service.upload_screenshots(
            analysis_result["screenshots"], 
            request.file_id
        )
        
        # Create analysis response
        analysis_response = AnalysisResponse(
            file_id=request.file_id,
            exercise_type=request.exercise_type,
            feedback=analysis_result["feedback"],
            screenshots=screenshot_urls,
            metrics=analysis_result["metrics"],
            status="completed"
        )
        
        # Store the result
        analysis_results[request.file_id] = analysis_response
        
        return analysis_response
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
