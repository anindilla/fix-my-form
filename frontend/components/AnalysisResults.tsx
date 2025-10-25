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

  const getScoreColor = (score: number) => {
    if (score >= 80) return 'text-success-600'
    if (score >= 60) return 'text-warning-600'
    return 'text-error-600'
  }

  const getScoreBg = (score: number) => {
    if (score >= 80) return 'bg-success-100'
    if (score >= 60) return 'bg-warning-100'
    return 'bg-error-100'
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          {analysis.exercise_type === 'squat' ? 'Back Squat' : 'Deadlift'} Analysis
        </h1>
        <div className={`inline-flex items-center px-4 py-2 rounded-full ${getScoreBg(analysis.feedback.overall_score)}`}>
          <span className={`text-2xl font-bold ${getScoreColor(analysis.feedback.overall_score)}`}>
            {analysis.feedback.overall_score}/100
          </span>
          <span className="ml-2 text-gray-600">Overall Score</span>
        </div>
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200 mb-8">
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
                className={`flex items-center py-2 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <Icon className="w-4 h-4 mr-2" />
                {tab.label}
              </button>
            )
          })}
        </nav>
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="space-y-8">
          {/* Strengths */}
          {analysis.feedback.strengths.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <CheckCircle className="w-5 h-5 text-success-600 mr-2" />
                What You're Doing Well
              </h3>
              <ul className="space-y-2">
                {analysis.feedback.strengths.map((strength, index) => (
                  <li key={index} className="flex items-start">
                    <div className="w-2 h-2 bg-success-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                    <span className="text-gray-700">{strength}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Areas for Improvement */}
          {analysis.feedback.areas_for_improvement.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <AlertTriangle className="w-5 h-5 text-warning-600 mr-2" />
                Areas for Improvement
              </h3>
              <ul className="space-y-2">
                {analysis.feedback.areas_for_improvement.map((area, index) => (
                  <li key={index} className="flex items-start">
                    <div className="w-2 h-2 bg-warning-500 rounded-full mt-2 mr-3 flex-shrink-0" />
                    <span className="text-gray-700">{area}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Specific Cues */}
          {analysis.feedback.specific_cues.length > 0 && (
            <div className="card">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                <Target className="w-5 h-5 text-primary-600 mr-2" />
                Key Cues to Remember
              </h3>
              <div className="grid md:grid-cols-2 gap-4">
                {analysis.feedback.specific_cues.map((cue, index) => (
                  <div key={index} className="bg-primary-50 p-4 rounded-lg">
                    <p className="text-primary-800 font-medium">{cue}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {activeTab === 'breakdown' && (
        <div className="space-y-6">
          {Object.entries(analysis.feedback.exercise_breakdown).map(([key, breakdown]) => (
            <div key={key} className="card">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900 capitalize">
                  {key.replace('_', ' ')}
                </h3>
                <div className={`px-3 py-1 rounded-full ${getScoreBg(breakdown.score)}`}>
                  <span className={`font-semibold ${getScoreColor(breakdown.score)}`}>
                    {breakdown.score}/100
                  </span>
                </div>
              </div>
              <p className="text-gray-700">{breakdown.feedback}</p>
            </div>
          ))}

        </div>
      )}

    </div>
  )
}
