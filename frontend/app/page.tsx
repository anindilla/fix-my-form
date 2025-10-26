'use client'

import { useState } from 'react'
import VideoUploader from '../components/VideoUploader'
import LoadingAnalysis from '../components/LoadingAnalysis'
import RecordingGuide from '../components/RecordingGuide'
import { useRouter } from 'next/navigation'

export default function Home() {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisId, setAnalysisId] = useState<string | null>(null)
  const [exerciseType, setExerciseType] = useState<string>('back-squat')
  const [filename, setFilename] = useState<string | null>(null)
  const router = useRouter()

  const handleAnalysisStart = (id: string, exercise: string, file: string) => {
    setAnalysisId(id)
    setExerciseType(exercise)
    setFilename(file)
    setIsAnalyzing(true)
  }

  const handleAnalysisComplete = () => {
    if (analysisId) {
      router.push(`/analysis/${analysisId}`)
    }
  }

  return (
    <div className="min-h-screen bg-neutral-50">
          {/* Hero Section with Strava-inspired Design */}
          <section className="hero-gradient min-h-screen flex items-center justify-center relative overflow-hidden pt-20 pb-16">
            {/* Background Pattern - Strava style */}
            <div className="absolute inset-0 bg-gradient-to-br from-primary-50/30 to-transparent"></div>
            <div className="absolute inset-0 bg-gradient-to-tl from-warm-50/20 to-transparent"></div>
            
            {/* Subtle grid pattern */}
            <div className="absolute inset-0 opacity-5">
              <div className="absolute inset-0" style={{
                backgroundImage: `radial-gradient(circle at 1px 1px, #ff9800 1px, transparent 0)`,
                backgroundSize: '20px 20px'
              }}></div>
            </div>

            <div className="relative z-10 max-w-6xl mx-auto container-spacing text-center">
              {/* Main heading with Space Grotesk */}
              <h1 className="font-heading text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold text-neutral-900 mb-6 sm:mb-8 tracking-tight">
                <span className="text-gradient">Fix My Form</span>
              </h1>
              
              {/* Subtitle with better typography */}
              <p className="text-body-lg mb-8 sm:mb-12 max-w-4xl mx-auto px-4">
                Upload your workout video and get <span className="font-semibold text-primary-600">AI-powered feedback</span> to improve your deadlift & squat form.
              </p>

              {isAnalyzing ? (
                <LoadingAnalysis
                  analysisId={analysisId!}
                  exerciseType={exerciseType}
                  filename={filename!}
                  onComplete={handleAnalysisComplete}
                />
              ) : (
                <>
                  <VideoUploader onAnalysisStart={handleAnalysisStart} />
                  
                  {/* Recording Guidelines Section */}
                  <div className="mt-8 sm:mt-10">
                    <RecordingGuide />
                  </div>
                </>
              )}
            </div>

          </section>

      {/* How It Works Section - Strava style */}
      <section className="py-8 sm:py-12 bg-neutral-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="font-heading text-3xl sm:text-4xl font-bold text-neutral-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg sm:text-xl text-neutral-600 max-w-2xl mx-auto px-4">
              Get personalized feedback on your workout form in three simple steps
            </p>
          </div>
          
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 sm:gap-12">
            <div className="text-center group">
              <div className="bg-gradient-orange w-20 h-20 sm:w-24 sm:h-24 rounded-2xl flex items-center justify-center mx-auto mb-6 sm:mb-8 group-hover:scale-110 transition-transform duration-300 shadow-strava">
                <svg className="w-10 h-10 sm:w-12 sm:h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                </svg>
              </div>
              <h3 className="font-heading text-xl sm:text-2xl font-bold text-neutral-900 mb-3 sm:mb-4">1. Upload Video</h3>
              <p className="text-neutral-600 text-base sm:text-lg leading-relaxed px-2">
                Upload your workout video in any format. We support iPhone videos and all common formats.
              </p>
            </div>
            
            <div className="text-center group">
              <div className="bg-gradient-warm w-20 h-20 sm:w-24 sm:h-24 rounded-2xl flex items-center justify-center mx-auto mb-6 sm:mb-8 group-hover:scale-110 transition-transform duration-300 shadow-strava">
                <svg className="w-10 h-10 sm:w-12 sm:h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <h3 className="font-heading text-xl sm:text-2xl font-bold text-neutral-900 mb-3 sm:mb-4">2. AI Analysis</h3>
              <p className="text-neutral-600 text-base sm:text-lg leading-relaxed px-2">
                Our AI analyzes your form using pose detection to identify areas for improvement.
              </p>
            </div>
            
            <div className="text-center group">
              <div className="bg-gradient-to-r from-accent-500 to-accent-700 w-20 h-20 sm:w-24 sm:h-24 rounded-2xl flex items-center justify-center mx-auto mb-6 sm:mb-8 group-hover:scale-110 transition-transform duration-300 shadow-strava">
                <svg className="w-10 h-10 sm:w-12 sm:h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <h3 className="font-heading text-xl sm:text-2xl font-bold text-neutral-900 mb-3 sm:mb-4">3. Get Feedback</h3>
              <p className="text-neutral-600 text-base sm:text-lg leading-relaxed px-2">
                Receive detailed feedback with visual highlights showing exactly what to improve.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Footer - Strava style */}
      <footer className="bg-gradient-to-r from-neutral-900 to-neutral-800 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="mb-6">
            <h3 className="font-heading text-2xl font-bold text-white mb-2">Fix My Form</h3>
            <p className="text-neutral-400 text-lg">AI-powered form analysis for better workouts</p>
          </div>
          <p className="text-neutral-400 text-lg">
            Built with ❤️ by{' '}
            <a 
              href="https://anindilla.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-primary-400 hover:text-primary-300 transition-colors duration-200 font-semibold"
            >
              dilleuh
            </a>
          </p>
        </div>
      </footer>
    </div>
  )
}
