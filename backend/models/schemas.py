from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class UploadResponse(BaseModel):
    file_id: str
    filename: str
    upload_url: str
    message: str

class AnalysisRequest(BaseModel):
    file_id: str
    filename: str
    exercise_type: str

class AnalysisResponse(BaseModel):
    file_id: str
    exercise_type: str
    feedback: Dict[str, Any]
    screenshots: List[str]
    metrics: Dict[str, Any]
    status: str

class PoseLandmark(BaseModel):
    x: float
    y: float
    z: float
    visibility: float

class PoseFrame(BaseModel):
    landmarks: List[PoseLandmark]
    timestamp: float

class AnalysisMetrics(BaseModel):
    hip_depth: Optional[float] = None
    knee_angle: Optional[float] = None
    back_angle: Optional[float] = None
    bar_path_deviation: Optional[float] = None
    knee_valgus: Optional[float] = None
