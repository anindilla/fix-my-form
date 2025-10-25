# Fix My Form - Workout Form Analyzer

An AI-powered workout form analysis app that helps users improve their exercise technique. Upload your workout video and get personalized feedback with visual highlights.

## Features

- **Video Upload**: Support for all common video formats including iPhone videos (MOV, MP4, HEVC)
- **AI Analysis**: MediaPipe pose detection with form analysis for Back Squat and Deadlift
- **Visual Feedback**: 3 annotated screenshots highlighting form issues
- **Detailed Reports**: Comprehensive feedback with scores and improvement suggestions
- **Modern UI**: Responsive design with drag-and-drop upload

## Tech Stack

### Backend
- **FastAPI**: Python web framework
- **MediaPipe**: Pose detection and analysis
- **OpenCV**: Video processing
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

### Back Squat
- **Depth**: Hip crease below knee level
- **Knee Tracking**: Knees over toes, no valgus collapse
- **Back Position**: Neutral spine, minimal forward lean
- **Bar Path**: Vertical over mid-foot

### Deadlift
- **Setup**: Shoulders over bar, hips higher than knees
- **Back Position**: Neutral spine throughout
- **Bar Path**: Vertical, close to body
- **Hip Hinge**: Proper hip drive, not squat motion

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
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
   - Environment: Python 3.11
3. **Add environment variables**:
   - `R2_ENDPOINT_URL`
   - `R2_ACCESS_KEY_ID`
   - `R2_SECRET_ACCESS_KEY`
   - `R2_BUCKET_NAME`

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
  "filename": "video.mp4"
}

Response:
{
  "file_id": "uuid",
  "exercise_type": "squat",
  "feedback": {
    "overall_score": 85,
    "strengths": ["Good depth"],
    "areas_for_improvement": ["Knee tracking"],
    "specific_cues": ["Push knees out"],
    "exercise_breakdown": {...}
  },
  "screenshots": ["https://..."],
  "metrics": {...}
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
│   │   └── storage.py
│   ├── models/                 # Data models
│   │   └── schemas.py
│   └── utils/                  # Utilities
│       ├── angle_calculator.py
│       └── screenshot_annotator.py
├── frontend/
│   ├── app/                    # Next.js app directory
│   │   ├── page.tsx           # Home page
│   │   ├── analysis/[id]/     # Analysis results
│   │   └── globals.css
│   ├── components/             # React components
│   │   ├── VideoUploader.tsx
│   │   ├── AnalysisResults.tsx
│   │   └── AnnotatedScreenshots.tsx
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

## Roadmap

- [ ] Add more exercises (bench press, overhead press)
- [ ] Real-time video analysis
- [ ] User accounts and history
- [ ] Mobile app
- [ ] Advanced AI models for better analysis
- [ ] Social features and sharing
