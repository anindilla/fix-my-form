'use client'

import { useState } from 'react'
import VideoUploader from '../components/VideoUploader'
import LoadingAnalysis from '../components/LoadingAnalysis'
import { useRouter } from 'next/navigation'

export default function Home() {
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisId, setAnalysisId] = useState<string | null>(null)
  const router = useRouter()

  const handleAnalysisStart = (id: string) => {
    setAnalysisId(id)
    setIsAnalyzing(true)
  }

  const handleAnalysisComplete = () => {
    if (analysisId) {
      router.push(`/analysis/${analysisId}`)
    }
  }

  return (
    <div className="min-h-screen bg-white">
          {/* Hero Section with Gradient */}
          <section className="hero-gradient min-h-screen flex items-center justify-center relative overflow-hidden pt-20 pb-16">
            {/* Background Pattern */}
            <div className="absolute inset-0 bg-black/5"></div>
            <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent"></div>

            <div className="relative z-10 max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
              <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-bold text-gray-900 mb-6 sm:mb-8 tracking-tight">
                Fix My Form
              </h1>
              <p className="text-lg sm:text-xl md:text-2xl text-gray-800 mb-12 sm:mb-16 max-w-3xl mx-auto leading-relaxed font-medium px-4">
                Upload your workout video and get AI-powered feedback to improve your deadlift & squat.
              </p>

              {isAnalyzing ? (
                <LoadingAnalysis
                  analysisId={analysisId!}
                  onComplete={handleAnalysisComplete}
                />
              ) : (
                <VideoUploader onAnalysisStart={handleAnalysisStart} />
              )}
            </div>

          </section>

      {/* Spacing for smooth transition */}
      <div className="h-24 bg-gradient-to-b from-transparent via-white/50 to-gray-50"></div>

      {/* How It Works Section */}
      <section className="py-16 sm:py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12 sm:mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
              How It Works
            </h2>
            <p className="text-lg sm:text-xl text-gray-600 max-w-2xl mx-auto px-4">
              Get personalized feedback on your workout form in three simple steps
            </p>
          </div>
          
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8 sm:gap-12">
                  <div className="text-center group">
                    <div className="bg-blue-600 w-16 h-16 sm:w-20 sm:h-20 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                      <svg className="w-8 h-8 sm:w-10 sm:h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                      </svg>
                    </div>
                    <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-3 sm:mb-4">1. Upload Video</h3>
                    <p className="text-gray-600 text-base sm:text-lg leading-relaxed px-2">
                      Upload your workout video in any format. We support iPhone videos and all common formats.
                    </p>
                  </div>
                  
                  <div className="text-center group">
                    <div className="bg-blue-600 w-16 h-16 sm:w-20 sm:h-20 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                      <svg className="w-8 h-8 sm:w-10 sm:h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                      </svg>
                    </div>
                    <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-3 sm:mb-4">2. AI Analysis</h3>
                    <p className="text-gray-600 text-base sm:text-lg leading-relaxed px-2">
                      Our AI analyzes your form using pose detection to identify areas for improvement.
                    </p>
                  </div>
                  
                  <div className="text-center group">
                    <div className="bg-blue-600 w-16 h-16 sm:w-20 sm:h-20 rounded-2xl flex items-center justify-center mx-auto mb-4 sm:mb-6 group-hover:scale-110 transition-transform duration-300 shadow-lg">
                      <svg className="w-8 h-8 sm:w-10 sm:h-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeWidth={2.5}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-3 sm:mb-4">3. Get Feedback</h3>
                    <p className="text-gray-600 text-base sm:text-lg leading-relaxed px-2">
                      Receive detailed feedback with visual highlights showing exactly what to improve.
                    </p>
                  </div>
                </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400 text-lg">
            Vibe-coded by{' '}
            <a 
              href="https://anindilla.com" 
              target="_blank" 
              rel="noopener noreferrer"
              className="text-white hover:text-blue-300 transition-colors duration-200 font-semibold"
            >
              dilleuh
            </a>
          </p>
        </div>
      </footer>
    </div>
  )
}
