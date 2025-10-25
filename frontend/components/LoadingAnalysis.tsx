'use client'

import { useState, useEffect } from 'react'
import { Brain, Zap, Target, CheckCircle } from 'lucide-react'

interface LoadingAnalysisProps {
  analysisId: string
  onComplete: () => void
}

export default function LoadingAnalysis({ analysisId, onComplete }: LoadingAnalysisProps) {
  const [currentStep, setCurrentStep] = useState(0)
  const [progress, setProgress] = useState(0)

  const steps = [
    { icon: Brain, title: 'Processing Video', description: 'Extracting frames and detecting poses' },
    { icon: Zap, title: 'Analyzing Form', description: 'Calculating angles and identifying issues' },
    { icon: Target, title: 'Generating Feedback', description: 'Creating personalized recommendations' },
    { icon: CheckCircle, title: 'Creating Screenshots', description: 'Highlighting key form points' }
  ]

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval)
          setTimeout(onComplete, 1000)
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
  }, [onComplete])

  return (
    <div className="max-w-2xl mx-auto">
      <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-8 border border-gray-200 shadow-lg">
        <div className="text-center mb-8">
          <div className="w-20 h-20 mx-auto bg-blue-100 rounded-2xl flex items-center justify-center mb-6">
            <Brain className="w-10 h-10 text-blue-600 animate-pulse" />
          </div>
          <h2 className="text-3xl font-bold text-gray-800 mb-4">Analyzing Your Form</h2>
          <p className="text-gray-600 text-lg">This usually takes 30-60 seconds...</p>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex justify-between text-gray-600 mb-3">
            <span className="font-semibold">Progress</span>
            <span className="font-semibold">{progress}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-blue-500 h-3 rounded-full transition-all duration-300 shadow-lg"
              style={{ width: `${progress}%` }}
            />
          </div>
        </div>

        {/* Steps */}
        <div className="space-y-4">
          {steps.map((step, index) => {
            const Icon = step.icon
            const isActive = index === currentStep
            const isCompleted = index < currentStep
            
            return (
            <div 
              key={index}
              className={`flex items-center p-4 rounded-xl transition-all duration-300 ${
                isActive ? 'bg-blue-50 border-blue-200' : 
                isCompleted ? 'bg-green-50 border-green-200' : 
                'bg-gray-50 border-gray-200'
              } border`}
            >
              <div className={`w-12 h-12 rounded-xl flex items-center justify-center mr-4 ${
                isActive ? 'bg-blue-500 text-white' :
                isCompleted ? 'bg-green-500 text-white' :
                'bg-gray-300 text-gray-600'
              }`}>
                <Icon className="w-6 h-6" />
              </div>
              <div className="flex-1">
                <h3 className={`font-bold text-lg ${
                  isActive ? 'text-gray-800' : 
                  isCompleted ? 'text-gray-800' : 
                  'text-gray-600'
                }`}>
                  {step.title}
                </h3>
                <p className={`${
                  isActive ? 'text-gray-600' : 
                  isCompleted ? 'text-gray-600' : 
                  'text-gray-500'
                }`}>
                  {step.description}
                </p>
              </div>
              {isCompleted && (
                <CheckCircle className="w-6 h-6 text-green-500" />
              )}
            </div>
            )
          })}
        </div>

        <div className="mt-8 text-center">
          <p className="text-gray-500">
            Analysis ID: <code className="bg-gray-100 px-3 py-1 rounded-lg text-gray-700 font-mono">{analysisId}</code>
          </p>
        </div>
      </div>
    </div>
  )
}
