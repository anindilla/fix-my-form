# Fix My Form - Workout Form Analyzer
- Link: https://fix-my-form.vercel.app
- Fix My Form is an AI-powered workout form analysis app that helps users improve their exercise technique. Upload your workout video and get personalized feedback to improve your form.

## Features

- **Video Upload**: Support for common video formats (MP4, MOV, AVI) with 50MB size limit
- **Exercise Selection**: Choose between Back Squat, Front Squat, Conventional Deadlift, and Sumo Deadlift
- **AI Analysis**: MediaPipe pose detection with exercise-specific form analysis
- **Intelligent Scoring**: Consistent scoring system with literal average calculation
- **Rep Detection**: Automatic detection of individual repetitions in multi-rep videos
- **Detailed Reports**: Comprehensive written feedback with scores and improvement suggestions
- **Modern UI**: Responsive design with futuristic Inter font and gradient styling
- **Real-time Processing**: Fast analysis with immediate feedback

## Tech Stack

### Backend
- **FastAPI**: Python web framework
- **MediaPipe**: Pose detection and analysis
- **OpenCV**: Video processing
- **SciPy**: Signal processing for rep detection
- **Cloudflare R2**: Video and image storage
- **Render**: Free tier deployment

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling
- **Vercel**: Free tier deployment

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Next.js App   │───▶│  FastAPI Backend│───▶│  Cloudflare R2  │
│   (Vercel)      │    │   (Render)      │    │   (Storage)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         │                       ▼
         │              ┌─────────────────┐
         │              │   MediaPipe     │
         │              │   (Pose AI)     │
         │              └─────────────────┘
         │
         ▼
┌─────────────────┐
│  User Browser   │
└─────────────────┘
```

## Exercise Analysis

### Supported Exercises
- **Back Squat**: Traditional back squat analysis
- **Front Squat**: Front-loaded squat variation
- **Conventional Deadlift**: Standard deadlift technique
- **Sumo Deadlift**: Wide-stance deadlift variation

### Analysis Features
- **Pose Detection**: 33 body landmarks using MediaPipe
- **Rep Detection**: Automatic identification of individual repetitions
- **Intelligent Scoring**: Consistent scoring with literal average calculation
- **Form Analysis**: Depth, knee tracking, back position, bar path, hip hinge
- **Severity-Based Penalties**: Critical, major, and minor issue classification
- **Improvement Cues**: Specific actionable feedback
- **Exercise Breakdown**: Detailed analysis of each movement phase

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Cloudflare R2 account (free tier)

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` with your R2 credentials:
   ```
   R2_ENDPOINT_URL=https://your-account-id.r2.cloudflarestorage.com
   R2_ACCESS_KEY_ID=your-access-key
   R2_SECRET_ACCESS_KEY=your-secret-key
   R2_BUCKET_NAME=workout-form-analyzer
   ```

4. **Run the backend**:
   ```bash
   uvicorn main:app --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.local.example .env.local
   ```
   
   Edit `.env.local`:
   ```
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

4. **Run the frontend**:
   ```bash
   npm run dev
   ```

## Deployment

### Backend (Render)

1. **Connect your GitHub repository to Render**
2. **Create a new Web Service**:
   - Build Command: `pip install --upgrade pip setuptools wheel && pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment: Python 3.11.8
   - Root Directory: `backend`
3. **Add environment variables**:
   - `R2_ENDPOINT_URL`
   - `R2_ACCESS_KEY_ID`
   - `R2_SECRET_ACCESS_KEY`
   - `R2_BUCKET_NAME`
   - `R2_PUBLIC_URL`
   - `ALLOWED_ORIGINS`

### Frontend (Vercel)

1. **Connect your GitHub repository to Vercel**
2. **Set environment variables**:
   - `NEXT_PUBLIC_API_URL`: Your Render backend URL
3. **Deploy automatically**

### Cloudflare R2 Setup

1. **Create R2 bucket**:
   - Go to Cloudflare Dashboard → R2 Object Storage
   - Create bucket: `workout-form-analyzer`
   - Set public access if needed

2. **Get credentials**:
   - Go to R2 → Manage R2 API tokens
   - Create API token with R2 permissions
   - Note the endpoint URL, access key, and secret

## API Endpoints

### Upload Video
```
POST /api/upload
Content-Type: multipart/form-data

Response:
{
  "file_id": "uuid",
  "filename": "video.mp4",
  "upload_url": "https://...",
  "message": "Video uploaded successfully"
}
```

### Analyze Video
```
POST /api/analyze
{
  "file_id": "uuid",
  "filename": "video.mp4",
  "exercise_type": "back_squat"
}

Response:
{
  "file_id": "uuid",
  "exercise_type": "back_squat",
  "feedback": {
    "overall_score": 85,
    "strengths": ["Good depth", "Stable core"],
    "areas_for_improvement": ["Knee tracking", "Bar path"],
    "specific_cues": ["Push knees out", "Keep bar over mid-foot"],
    "exercise_breakdown": {
      "setup": "Good starting position",
      "descent": "Maintain neutral spine",
      "ascent": "Drive through heels"
    }
  },
  "screenshots": [],
  "metrics": {
    "depth_score": 90,
    "knee_tracking": 75,
    "back_position": 85
  }
}
```

## File Structure

```
workout-form-analyzer/
├── backend/
│   ├── main.py                 # FastAPI app
│   ├── requirements.txt        # Python dependencies
│   ├── services/              # Business logic
│   │   ├── video_processor.py
│   │   ├── pose_analyzer.py
│   │   ├── squat_analyzer.py
│   │   ├── deadlift_analyzer.py
│   │   ├── front_squat_analyzer.py
│   │   ├── sumo_deadlift_analyzer.py
│   │   └── storage.py
│   ├── models/                 # Data models
│   │   └── schemas.py
│   └── utils/                  # Utilities
│       ├── angle_calculator.py
│       ├── rep_detector.py
│       └── screenshot_annotator.py
├── frontend/
│   ├── app/                    # Next.js app directory
│   │   ├── page.tsx           # Home page
│   │   ├── analysis/[id]/     # Analysis results
│   │   └── globals.css
│   ├── components/             # React components
│   │   ├── VideoUploader.tsx
│   │   ├── AnalysisResults.tsx
│   │   └── LoadingAnalysis.tsx
│   ├── lib/                    # Utilities
│   │   └── api.ts
│   └── package.json
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test locally
5. Submit a pull request

## License

MIT License - feel free to use this project for learning or commercial purposes.

## Support

For issues or questions:
1. Check the GitHub Issues
2. Create a new issue with detailed description
3. Include error logs and steps to reproduce

## Recent Improvements

### ✅ **Scoring System Overhaul**
- **Fixed Overall Score Calculation**: Now uses literal average of breakdown scores
- **Prevented Zero Scores**: All categories get reasonable fallback scores (75-85)
- **Enhanced Bar Path Analysis**: Uses shoulder-hip alignment instead of returning 0
- **Consistent Scoring**: All analyzers use the same scoring logic
- **Rep Detection**: Automatic identification of individual repetitions in multi-rep videos

### ✅ **Upload System Improvements**
- **Better Error Handling**: Detailed logging and specific error messages
- **File Size Validation**: 50MB limit with clear error messages
- **R2 Connectivity**: Enhanced error handling for storage issues
- **Debug Logging**: Comprehensive logging for troubleshooting

### ✅ **UI/UX Enhancements**
- **Responsive Design**: Optimized for mobile and desktop
- **Modern Typography**: Inter font for better readability
- **Improved Loading Flow**: Removed disabled visual analysis steps
- **Better Error Messages**: User-friendly error handling

## Current Status

✅ **Working Features:**
- Video upload and processing with enhanced error handling
- Exercise selection (4 exercise types)
- AI-powered form analysis with rep detection
- Intelligent scoring system with literal average calculation
- Detailed written feedback with severity-based penalties
- Responsive modern UI with Inter font
- Production deployment (Vercel + Render)

🚧 **Temporarily Disabled:**
- Visual form analysis (screenshots with annotations)
- Technical metrics display to end users

## Technical Improvements

### **Scoring Algorithm**
- **Literal Average Calculation**: Overall score = average of all breakdown scores
- **Severity-Based Penalties**: Critical (30pt), Major (15pt), Minor (5pt) penalties
- **Minimum Score Protection**: No category can score below 30/100
- **Fallback Logic**: Reasonable default scores when no issues detected

### **Rep Detection System**
- **Peak Detection**: Uses SciPy signal processing to identify rep boundaries
- **Exercise-Specific Logic**: Different detection algorithms for squats vs deadlifts
- **Smoothing**: Reduces noise in angle data for better detection
- **Multi-Rep Analysis**: Analyzes each rep individually for consistency feedback

### **Error Handling**
- **Upload Validation**: File type, size, and format checking
- **Storage Connectivity**: Enhanced R2 error handling and logging
- **Graceful Degradation**: Fallback values when pose detection fails
- **User-Friendly Messages**: Clear error messages for different failure types

## Roadmap

- [ ] Re-enable visual form analysis with improved R2 integration
- [ ] Add more exercises (bench press, overhead press)
- [ ] User accounts and workout history
- [ ] Mobile app
- [ ] Advanced AI models for better analysis
- [ ] Real-time video analysis
- [ ] Multi-language support
- [ ] Advanced rep counting algorithms
