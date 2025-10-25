'use client'

import { useState } from 'react'
import { TrendingUp, AlertTriangle, CheckCircle, Target, BarChart3 } from 'lucide-react'

interface AnalysisResultsProps {
  analysis: {
    file_id: string
    exercise_type: string
    feedback: {
      overall_score: number
      strengths: string[]
      areas_for_improvement: string[]
      specific_cues: string[]
      exercise_breakdown: {
        [key: string]: {
          score: number
          feedback: string
        }
      }
    }
    metrics: {
      [key: string]: number
    }
  }
}

export default function AnalysisResults({ analysis }: AnalysisResultsProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'breakdown'>('overview')

  const getExerciseTitle = (exerciseType: string) => {
    const titleMap: { [key: string]: string } = {
      'front-squat': 'Front Squat',
      'back-squat': 'Back Squat',
      'conventional-deadlift': 'Conventional Deadlift',
      'sumo-deadlift': 'Sumo Deadlift',
      // Legacy support
      'squat': 'Back Squat',
      'deadlift': 'Conventional Deadlift'
    }
    return titleMap[exerciseType] || 'Exercise'
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-success-600'
    if (score >= 60) return 'text-warm-600'
    return 'text-error-600'
  }

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'score-excellent'
    if (score >= 60) return 'score-good'
    return 'score-poor'
  }

  const getScoreGradient = (score: number) => {
    if (score >= 80) return 'bg-gradient-to-r from-success-500 to-success-600'
    if (score >= 60) return 'bg-gradient-to-r from-warm-500 to-warm-600'
    return 'bg-gradient-to-r from-error-500 to-error-600'
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header - Strava style data display */}
      <div className="text-center mb-8 sm:mb-12">
        <h1 className="font-heading text-3xl sm:text-4xl lg:text-5xl font-bold text-neutral-900 mb-4">
          {getExerciseTitle(analysis.exercise_type)} Analysis
        </h1>
        
        {/* Large score display - Strava style */}
        <div className="inline-flex flex-col items-center space-y-4">
          <div className={`relative ${getScoreBg(analysis.feedback.overall_score)} px-8 py-6 rounded-3xl shadow-strava-lg border-2`}>
            <div className="text-center">
              <div className={`text-6xl sm:text-7xl lg:text-8xl font-bold font-heading ${getScoreColor(analysis.feedback.overall_score)} mb-2`}>
                {analysis.feedback.overall_score}
              </div>
              <div className="text-neutral-600 text-lg sm:text-xl font-semibold">Overall Score</div>
            </div>
            {/* Progress ring */}
            <div className="absolute inset-0 rounded-3xl overflow-hidden">
              <div 
                className={`h-1 ${getScoreGradient(analysis.feedback.overall_score)} transition-all duration-1000 ease-out`}
                style={{ width: `${analysis.feedback.overall_score}%` }}
              />
            </div>
          </div>
          
          {/* Score interpretation */}
          <div className="text-center">
            <p className="text-neutral-600 text-lg font-medium">
              {analysis.feedback.overall_score >= 80 ? 'Excellent form!' : 
               analysis.feedback.overall_score >= 60 ? 'Good form with room for improvement' : 
               'Focus on fundamentals'}
            </p>
          </div>
        </div>
      </div>

      {/* Tabs - Strava style */}
      <div className="border-b border-neutral-200 mb-8">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'overview', label: 'Overview', icon: TrendingUp },
            { id: 'breakdown', label: 'Breakdown', icon: BarChart3 }
          ].map((tab) => {
            const Icon = tab.icon
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center py-3 px-4 border-b-2 font-semibold text-sm transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600 bg-primary-50'
                    : 'border-transparent text-neutral-500 hover:text-neutral-700 hover:border-neutral-300 hover:bg-neutral-50'
                }`}
                aria-label={`Switch to ${tab.label} tab`}
              >
                <Icon className="w-5 h-5 mr-2" />
                {tab.label}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-6 sm:space-y-8">
          {/* Strengths */}
          {analysis.feedback.strengths.length > 0 && (
            <div className="card">
              <h3 className="font-heading text-xl font-semibold text-neutral-900 mb-6 flex items-center">
                <div className="w-8 h-8 bg-success-100 rounded-full flex items-center justify-center mr-3 success-bounce">
                  <CheckCircle className="w-5 h-5 text-success-600" />
                </div>
                What You're Doing Well
              </h3>
              <ul className="space-y-3">
                {analysis.feedback.strengths.map((strength, index) => (
                  <li key={index} className="flex items-start">
                    <div className="w-3 h-3 bg-success-500 rounded-full mt-2 mr-4 flex-shrink-0" />
                    <span className="text-neutral-700 text-base leading-relaxed">{strength}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Areas for Improvement */}
          {analysis.feedback.areas_for_improvement.length > 0 && (
            <div className="card">
              <h3 className="font-heading text-xl font-semibold text-neutral-900 mb-6 flex items-center">
                <div className="w-8 h-8 bg-warning-100 rounded-full flex items-center justify-center mr-3">
                  <AlertTriangle className="w-5 h-5 text-warning-600" />
                </div>
                Areas for Improvement
              </h3>
              <ul className="space-y-3">
                {analysis.feedback.areas_for_improvement.map((area, index) => (
                  <li key={index} className="flex items-start">
                    <div className="w-3 h-3 bg-warning-500 rounded-full mt-2 mr-4 flex-shrink-0" />
                    <span className="text-neutral-700 text-base leading-relaxed">{area}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Specific Cues */}
          {analysis.feedback.specific_cues.length > 0 && (
            <div className="card">
              <h3 className="font-heading text-xl font-semibold text-neutral-900 mb-6 flex items-center">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center mr-3">
                  <Target className="w-5 h-5 text-primary-600" />
                </div>
                Key Cues to Remember
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                {analysis.feedback.specific_cues.map((cue, index) => (
                  <div key={index} className="bg-gradient-to-r from-primary-50 to-primary-100 p-4 rounded-xl border border-primary-200 hover:shadow-card transition-shadow duration-200">
                    <p className="text-primary-800 font-medium text-base leading-relaxed">{cue}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'breakdown' && (
        <div className="space-y-6 sm:space-y-8">
          {Object.entries(analysis.feedback.exercise_breakdown).map(([key, breakdown]) => (
            <div key={key} className="card hover:shadow-card-hover transition-all duration-300">
              <div className="flex flex-col sm:flex-row sm:items-center justify-between mb-4 sm:mb-6">
                <h3 className="font-heading text-lg sm:text-xl font-semibold text-neutral-900 capitalize mb-2 sm:mb-0">
                  {key.replace('_', ' ')}
                </h3>
                <div className="flex items-center space-x-4">
                  {/* Score display */}
                  <div className={`px-4 py-2 rounded-xl ${getScoreBg(breakdown.score)} border-2`}>
                    <span className={`font-bold text-lg sm:text-xl ${getScoreColor(breakdown.score)}`}>
                      {breakdown.score}
                    </span>
                    <span className="text-neutral-600 text-sm ml-1">/100</span>
                  </div>
                  
                  {/* Progress bar */}
                  <div className="hidden sm:block w-24 h-2 bg-neutral-200 rounded-full overflow-hidden">
                    <div 
                      className={`h-full ${getScoreGradient(breakdown.score)} transition-all duration-1000 ease-out`}
                      style={{ width: `${breakdown.score}%` }}
                    />
                  </div>
                </div>
              </div>
              
              {/* Feedback text */}
              <div className="bg-neutral-50 p-4 rounded-xl border border-neutral-200">
                <p className="text-neutral-700 text-base leading-relaxed">{breakdown.feedback}</p>
              </div>
              
              {/* Mobile progress bar */}
              <div className="sm:hidden mt-4">
                <div className="w-full h-3 bg-neutral-200 rounded-full overflow-hidden">
                  <div 
                    className={`h-full ${getScoreGradient(breakdown.score)} transition-all duration-1000 ease-out`}
                    style={{ width: `${breakdown.score}%` }}
                  />
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

    </div>
  )
}
