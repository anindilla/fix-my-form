'use client'

import { useState, useEffect } from 'react'
import { Brain, Zap, Target, CheckCircle, AlertCircle } from 'lucide-react'
import { analyzeVideo } from '../lib/api'

interface LoadingAnalysisProps {
  analysisId: string
  exerciseType: string
  filename: string
  onComplete: () => void
}

export default function LoadingAnalysis({ analysisId, exerciseType, filename, onComplete }: LoadingAnalysisProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)

  const steps = [
    { icon: Brain, title: 'Processing Video', description: 'Extracting frames and detecting poses' },
    { icon: Zap, title: 'Analyzing Form', description: 'Calculating angles and identifying issues' },
    { icon: Target, title: 'Generating Feedback', description: 'Creating personalized recommendations' }
  ]

  useEffect(() => {
    const startAnalysis = async () => {
      try {
        console.log('Starting analysis:', { analysisId, exerciseType, filename })
        // Start the actual analysis
        await analyzeVideo(analysisId, filename, exerciseType)
        
        // Analysis completed successfully
        setTimeout(() => {
          onComplete()
        }, 1000)
      } catch (err) {
        console.error('Analysis error:', err)
        console.error('Error details:', {
          message: err instanceof Error ? err.message : 'Unknown error',
          stack: err instanceof Error ? err.stack : undefined
        })
        setError(err instanceof Error ? err.message : 'Analysis failed')
      }
    }

    startAnalysis()
  }, [analysisId, exerciseType, onComplete])

  useEffect(() => {
    if (error) return // Don't run progress if there's an error

    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          return 100
        }
        return prev + 2
      })
    }, 100)

    const stepInterval = setInterval(() => {
      setCurrentStep(prev => {
        if (prev >= steps.length - 1) {
          clearInterval(stepInterval)
          return prev
        }
        return prev + 1
      })
    }, 2000)

    return () => {
      clearInterval(interval)
      clearInterval(stepInterval)
    }
  }, [error])

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white/95 backdrop-blur-sm rounded-2xl p-8 border border-neutral-200 shadow-strava-lg">
        {error ? (
          // Error state
          <div className="text-center">
            <div className="w-20 h-20 mx-auto bg-error-100 rounded-2xl flex items-center justify-center mb-6">
              <AlertCircle className="w-10 h-10 text-error-600" />
            </div>
            <h2 className="font-heading text-3xl font-bold text-neutral-900 mb-4">Analysis Failed</h2>
            <p className="text-neutral-600 text-lg mb-6">{error}</p>
            <div className="text-sm text-neutral-500 mb-6">
              If this persists, try:
              <ul className="list-disc list-inside mt-2">
                <li>Recording from a side angle</li>
                <li>Ensuring good lighting</li>
                <li>Keeping the full body in frame</li>
              </ul>
            </div>
            <button 
              onClick={() => window.location.reload()}
              className="btn-primary"
            >
              Try Again
            </button>
          </div>
        ) : (
          // Loading state
          <>
            <div className="text-center mb-8">
              <div className="w-20 h-20 mx-auto bg-gradient-orange rounded-2xl flex items-center justify-center mb-6 shadow-strava">
                <Brain className="w-10 h-10 text-white animate-pulse" />
              </div>
              <h2 className="font-heading text-3xl font-bold text-neutral-900 mb-4">Analyzing Your Form</h2>
              <p className="text-neutral-600 text-lg">This usually takes 30-60 seconds...</p>
            </div>

            {/* Progress Bar - Strava style */}
            <div className="mb-8">
              <div className="flex justify-between text-neutral-600 mb-3">
                <span className="font-semibold text-lg">Progress</span>
                <span className="font-bold text-lg text-primary-600">{progress}%</span>
              </div>
              <div className="w-full bg-neutral-200 rounded-full h-4 overflow-hidden">
                <div 
                  className="bg-gradient-orange h-4 rounded-full transition-all duration-300 shadow-strava"
                  style={{ width: `${progress}%` }}
                />
              </div>
            </div>

            {/* Steps - Strava style */}
            <div className="space-y-4">
              {steps.map((step, index) => {
                const Icon = step.icon
                const isActive = index === currentStep
                const isCompleted = index < currentStep
                
                return (
                  <div 
                    key={index}
                    className={`flex items-center p-5 rounded-xl transition-all duration-300 ${
                      isActive ? 'bg-primary-50 border-primary-200 shadow-strava' : 
                      isCompleted ? 'bg-success-50 border-success-200' : 
                      'bg-neutral-50 border-neutral-200'
                    } border-2`}
                  >
                    <div className={`w-14 h-14 rounded-xl flex items-center justify-center mr-4 shadow-strava ${
                      isActive ? 'bg-gradient-orange text-white animate-pulse' :
                      isCompleted ? 'bg-gradient-to-r from-success-500 to-success-600 text-white' :
                      'bg-neutral-300 text-neutral-600'
                    }`}>
                      <Icon className="w-7 h-7" />
                    </div>
                    <div className="flex-1">
                      <h3 className={`font-heading font-bold text-lg ${
                        isActive ? 'text-primary-900' : 
                        isCompleted ? 'text-success-900' : 
                        'text-neutral-700'
                      }`}>
                        {step.title}
                      </h3>
                      <p className={`text-sm ${
                        isActive ? 'text-primary-700' : 
                        isCompleted ? 'text-success-700' : 
                        'text-neutral-600'
                      }`}>
                        {step.description}
                      </p>
                    </div>
                  </div>
                )
              })}
            </div>
          </>
        )}
      </div>
    </div>
  )
}