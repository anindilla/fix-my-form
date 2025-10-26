# Fix My Form - AI-Powered Workout Form Analyzer
- **Live App**: https://fix-my-form.vercel.app

Fix My Form is an AI-powered workout form analysis app that helps users improve their exercise technique using Google Gemini 2.0 Flash Vision. Upload your workout video and get personalized feedback to improve your form.

## Features

- **Video Upload**: Support for common video formats (MP4, MOV, AVI) with 50MB size limit
- **Exercise Selection**: Choose between Back Squat, Front Squat, Conventional Deadlift, and Sumo Deadlift
- **AI Analysis**: Google Gemini 2.0 Flash Vision for advanced form analysis
- **Intelligent Scoring**: Detailed scoring system with exercise-specific breakdowns
- **Detailed Reports**: Comprehensive written feedback with scores and improvement suggestions
- **Modern UI**: Clean, accessible design with consistent typography and spacing
- **Real-time Processing**: Fast analysis with immediate feedback
- **Mobile Optimized**: Responsive design with proper touch targets

## Tech Stack

### Backend
- **FastAPI**: Python web framework
- **Google Gemini 2.0 Flash**: AI-powered video analysis
- **Cloudflare R2**: Video storage
- **Render**: Free tier deployment

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type safety
- **Tailwind CSS**: Styling with custom design system
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
         │              │ Google Gemini   │
         │              │ 2.0 Flash      │
         │              │ (AI Analysis)   │
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
- **AI-Powered Analysis**: Google Gemini 2.0 Flash Vision for comprehensive form analysis
- **Exercise-Specific Scoring**: Detailed breakdowns for each exercise type
- **Form Analysis**: Depth, knee tracking, back position, bar path analysis
- **Improvement Cues**: Specific actionable feedback for each exercise
- **Exercise Breakdown**: Detailed analysis of key movement components
- **Real-time Processing**: Fast analysis with timeout protection

## Local Development

### Prerequisites
- Python 3.11+
- Node.js 18+
- Cloudflare R2 account (free tier)
- Google AI API key (free tier)

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
   
   Edit `.env` with your credentials:
   ```
   R2_ENDPOINT_URL=your-r2-endpoint
   R2_ACCESS_KEY_ID=your-access-key
   R2_SECRET_ACCESS_KEY=your-secret-key
   R2_BUCKET_NAME=your-bucket-name
   GOOGLE_AI_API_KEY=your-google-ai-api-key
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
   - `GOOGLE_AI_API_KEY`

### Frontend (Vercel)

1. **Connect your GitHub repository to Vercel**
2. **Set environment variables**:
   - `NEXT_PUBLIC_API_URL`: Your Render backend URL
3. **Deploy automatically**

### Cloudflare R2 Setup

1. **Create R2 bucket** and configure storage
2. **Get API credentials** for your bucket

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
│   │   ├── llm_analyzer.py    # Google Gemini integration
│   │   ├── video_processor.py # Video validation and optimization
│   │   └── storage.py         # Cloudflare R2 integration
│   ├── models/                 # Data models
│   │   └── schemas.py
│   └── utils/                  # Utilities
│       └── screenshot_annotator.py
├── frontend/
│   ├── app/                    # Next.js app directory
│   │   ├── page.tsx           # Home page
│   │   ├── analysis/[id]/     # Analysis results
│   │   └── globals.css
│   ├── components/             # React components
│   │   ├── VideoUploader.tsx
│   │   ├── AnalysisResults.tsx
│   │   ├── LoadingAnalysis.tsx
│   │   └── RecordingGuide.tsx
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

### ✅ **AI Analysis Overhaul (Latest)**
- **Google Gemini 2.0 Flash**: Replaced MediaPipe with advanced AI vision model
- **Video Preprocessing**: Added video validation and optimization pipeline
- **Async Processing**: Proper async handling with timeout protection
- **Error Handling**: Comprehensive error handling and user-friendly messages
- **Filename Fix**: Resolved critical filename mismatch between upload and analysis

### ✅ **Frontend UI Enhancements**
- **Typography Standardization**: Implemented 4-core font size system
- **Consistent Design**: Removed emoji inconsistencies, unified visual language
- **Sticky Footer**: Updated footer with "Vibe-coded by dilleuh" copy
- **Accessibility**: Added skip-to-content links and improved focus indicators
- **Mobile Optimization**: Better touch targets and responsive spacing
- **Card Spacing**: Fixed massive UI spacing issues in analysis results

### ✅ **Storage & Upload System**
- **R2 Integration**: Enhanced Cloudflare R2 storage with retry logic
- **Upload Verification**: HeadObject verification after upload
- **Debug Tools**: Added R2 contents debugging endpoint
- **Error Messages**: User-friendly error messages for storage failures
- **File Validation**: Comprehensive video file validation

### ✅ **Analysis Pipeline**
- **Exercise Support**: Back Squat, Front Squat, Conventional Deadlift, Sumo Deadlift
- **Detailed Feedback**: Comprehensive form analysis with specific cues
- **Scoring System**: Exercise-specific scoring with breakdown categories
- **Real-time Processing**: Fast analysis with proper timeout handling

## Current Status

✅ **Fully Working Features:**
- Video upload and processing with Google Gemini 2.0 Flash analysis
- Exercise selection (4 exercise types: Back Squat, Front Squat, Conventional Deadlift, Sumo Deadlift)
- AI-powered form analysis with detailed feedback
- Comprehensive scoring system with exercise breakdowns
- Modern, accessible UI with consistent typography
- Mobile-optimized responsive design
- Production deployment (Vercel + Render)
- Cloudflare R2 video storage with retry logic
- Real-time analysis with timeout protection

🚧 **Future Enhancements:**
- Visual form analysis (screenshots with annotations)
- Additional exercise types (bench press, overhead press)
- User accounts and workout history
- Mobile app development
- Advanced AI models for enhanced analysis

## Technical Improvements

### **AI Analysis System**
- **Google Gemini 2.0 Flash**: Advanced vision model for comprehensive form analysis
- **Video Preprocessing**: File validation, format checking, and optimization
- **Async Processing**: Proper async/await patterns with timeout protection
- **Error Handling**: Graceful fallbacks and user-friendly error messages
- **Exercise-Specific Prompts**: Tailored analysis prompts for each exercise type

### **Storage & Upload System**
- **Cloudflare R2**: Reliable object storage with retry logic
- **Upload Verification**: HeadObject checks to ensure successful uploads
- **File Validation**: Comprehensive video format and size validation
- **Debug Tools**: Storage debugging for troubleshooting
- **Error Recovery**: Automatic retry with exponential backoff

### **Frontend Architecture**
- **Design System**: Consistent 4-core typography hierarchy
- **Accessibility**: Skip-to-content links, focus indicators, keyboard navigation
- **Mobile Optimization**: Proper touch targets and responsive spacing
- **Component Architecture**: Modular, reusable React components
- **Error Boundaries**: Graceful error handling throughout the UI

## Roadmap

- [ ] Re-enable visual form analysis with improved R2 integration
- [ ] Add more exercises (bench press, overhead press)
- [ ] User accounts and workout history
- [ ] Mobile app
- [ ] Advanced AI models for better analysis
- [ ] Real-time video analysis
- [ ] Multi-language support
- [ ] Advanced rep counting algorithms
