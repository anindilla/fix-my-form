'use client'

import { useState } from 'react'
import { 
  Camera, 
  CheckCircle, 
  XCircle, 
  Clock, 
  Video, 
  Users, 
  Lightbulb,
  AlertTriangle,
  Target,
  Zap
} from 'lucide-react'

interface RecordingGuideProps {
  selectedExercise?: string
}

const exerciseTabs = [
  { id: 'front-squat', name: 'Front Squat', icon: '🏋️' },
  { id: 'back-squat', name: 'Back Squat', icon: '🏋️' },
  { id: 'conventional-deadlift', name: 'Conventional Deadlift', icon: '🏋️' },
  { id: 'sumo-deadlift', name: 'Sumo Deadlift', icon: '🏋️' }
]

const generalRequirements = [
  { icon: Clock, text: 'Duration: 2-60 seconds (optimal: 5-15 seconds)' },
  { icon: Target, text: 'Max reps: 1-5 reps recommended' },
  { icon: Video, text: 'Resolution: Minimum 480x360 (720p+ recommended)' },
  { icon: Video, text: 'File size: Maximum 50MB' },
  { icon: Video, text: 'Frame rate: Minimum 15fps (30fps recommended)' },
  { icon: Lightbulb, text: 'Lighting: Good natural or bright indoor lighting' },
  { icon: Users, text: 'Background: Clear, uncluttered' }
]

const cameraAngles = [
  { angle: 'Side view (90°)', quality: 'BEST', description: 'Captures depth and form perfectly', icon: '📐' },
  { angle: '3/4 angle (45°)', quality: 'GOOD', description: 'Shows stance and tracking well', icon: '📐' },
  { angle: 'Front view (0°)', quality: 'AVOID', description: "Can't see depth or bar path", icon: '❌' },
  { angle: 'Back view (180°)', quality: 'AVOID', description: 'Obscures key landmarks', icon: '❌' }
]

const dos = [
  'Record 1-5 reps maximum',
  'Keep video under 60 seconds',
  'Use good lighting (natural or bright indoor)',
  'Wear fitted clothing for clear landmark detection',
  'Film from 6-10 feet away',
  'Ensure full body is visible (head to feet)',
  'Use a clear, uncluttered background',
  'Record from side angle for best results'
]

const donts = [
  "Don't record from front or back view",
  "Don't use busy or distracting backgrounds",
  "Don't wear very baggy or loose clothing",
  "Don't film in dim or poor lighting",
  "Don't record too many reps (over 5)",
  "Don't stand too close or too far from camera",
  "Don't use low resolution (under 480x360)",
  "Don't exceed 50MB file size"
]

const exerciseSpecificTips = {
  'front-squat': {
    title: 'Front Squat Tips',
    tips: [
      'Film from side to capture hip depth clearly',
      'Ensure bar position is visible',
      'Focus on torso angle and knee tracking',
      'Critical angles: Hip depth, knee angle, torso position'
    ]
  },
  'back-squat': {
    title: 'Back Squat Tips',
    tips: [
      'Side view essential for depth assessment',
      'Make sure bar path is visible',
      'Focus on hip crease below knee level',
      'Critical angles: Hip depth, knee tracking, bar path'
    ]
  },
  'conventional-deadlift': {
    title: 'Conventional Deadlift Tips',
    tips: [
      'Side view crucial for back angle assessment',
      'Ensure bar is visible throughout movement',
      'Focus on hip hinge and neutral spine',
      'Critical angles: Back angle, hip hinge, bar path'
    ]
  },
  'sumo-deadlift': {
    title: 'Sumo Deadlift Tips',
    tips: [
      'Side view shows stance width and hip position',
      'Ensure wide stance is clearly visible',
      'Focus on upright torso and hip positioning',
      'Critical angles: Stance width, hip angle, torso position'
    ]
  }
}

const modelLimitations = [
  'Cannot analyze bar weight, speed, or power output',
  'Requires clear view of body landmarks (shoulders, hips, knees, ankles)',
  'Best for form analysis, not performance metrics',
  'Struggles with very baggy clothing, poor lighting, busy backgrounds',
  'Cannot detect internal rotation or subtle joint positions',
  'Limited to 2D analysis from single camera angle'
]

export default function RecordingGuide({ selectedExercise }: RecordingGuideProps) {
  const [activeTab, setActiveTab] = useState(selectedExercise || 'front-squat')

  return (
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="font-heading text-3xl sm:text-4xl font-bold text-neutral-900 mb-4">
          📹 Recording Guidelines
        </h2>
        <p className="text-lg text-neutral-700 max-w-2xl mx-auto">
          Follow these tips to get the best analysis results from your workout videos
        </p>
      </div>

      {/* Exercise Tabs */}
      <div className="flex flex-wrap justify-center gap-2 mb-8">
        {exerciseTabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`
              px-4 py-2 rounded-lg font-medium transition-all duration-200
              ${activeTab === tab.id
                ? 'bg-primary-600 text-white shadow-strava'
                : 'bg-white text-neutral-700 border border-neutral-300 hover:border-primary-300 hover:bg-primary-50'
              }
            `}
          >
            <span className="mr-2">{tab.icon}</span>
            {tab.name}
          </button>
        ))}
      </div>

      {/* Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Left Column */}
        <div className="space-y-6">
          
          {/* Camera Setup */}
          <div className="bg-white rounded-xl p-6 shadow-card border border-neutral-200">
            <h3 className="font-semibold text-lg text-neutral-900 mb-4 flex items-center gap-2">
              <Camera className="w-5 h-5 text-primary-600" />
              Camera Setup
            </h3>
            <div className="space-y-3">
              {cameraAngles.map((angle, index) => (
                <div key={index} className="flex items-start gap-3">
                  <span className="text-lg">{angle.icon}</span>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-neutral-900">{angle.angle}</span>
                      <span className={`
                        px-2 py-1 rounded-full text-xs font-medium
                        ${angle.quality === 'BEST' ? 'bg-success-100 text-success-700' :
                          angle.quality === 'GOOD' ? 'bg-warm-100 text-warm-700' :
                          'bg-error-100 text-error-700'}
                      `}>
                        {angle.quality}
                      </span>
                    </div>
                    <p className="text-sm text-neutral-600">{angle.description}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Do's */}
          <div className="bg-white rounded-xl p-6 shadow-card border border-neutral-200">
            <h3 className="font-semibold text-lg text-neutral-900 mb-4 flex items-center gap-2">
              <CheckCircle className="w-5 h-5 text-success-600" />
              Do's
            </h3>
            <div className="space-y-2">
              {dos.map((item, index) => (
                <div key={index} className="flex items-start gap-3">
                  <CheckCircle className="w-4 h-4 text-success-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-neutral-700">{item}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Exercise-Specific Tips */}
          <div className="bg-white rounded-xl p-6 shadow-card border border-neutral-200">
            <h3 className="font-semibold text-lg text-neutral-900 mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-primary-600" />
              {exerciseSpecificTips[activeTab as keyof typeof exerciseSpecificTips]?.title}
            </h3>
            <div className="space-y-2">
              {exerciseSpecificTips[activeTab as keyof typeof exerciseSpecificTips]?.tips.map((tip, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-primary-500 rounded-full mt-2 flex-shrink-0" />
                  <span className="text-sm text-neutral-700">{tip}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          
          {/* Technical Requirements */}
          <div className="bg-white rounded-xl p-6 shadow-card border border-neutral-200">
            <h3 className="font-semibold text-lg text-neutral-900 mb-4 flex items-center gap-2">
              <Video className="w-5 h-5 text-primary-600" />
              Technical Requirements
            </h3>
            <div className="space-y-3">
              {generalRequirements.map((req, index) => (
                <div key={index} className="flex items-start gap-3">
                  <req.icon className="w-4 h-4 text-primary-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-neutral-700">{req.text}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Don'ts */}
          <div className="bg-white rounded-xl p-6 shadow-card border border-neutral-200">
            <h3 className="font-semibold text-lg text-neutral-900 mb-4 flex items-center gap-2">
              <XCircle className="w-5 h-5 text-error-600" />
              Don'ts
            </h3>
            <div className="space-y-2">
              {donts.map((item, index) => (
                <div key={index} className="flex items-start gap-3">
                  <XCircle className="w-4 h-4 text-error-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-neutral-700">{item}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Model Limitations */}
          <div className="bg-warm-50 rounded-xl p-6 border border-warm-200">
            <h3 className="font-semibold text-lg text-neutral-900 mb-4 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-warm-600" />
              Model Limitations
            </h3>
            <div className="space-y-2">
              {modelLimitations.map((limitation, index) => (
                <div key={index} className="flex items-start gap-3">
                  <div className="w-1.5 h-1.5 bg-warm-500 rounded-full mt-2 flex-shrink-0" />
                  <span className="text-sm text-neutral-700">{limitation}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Bottom CTA */}
      <div className="mt-8 text-center">
        <div className="bg-primary-50 rounded-xl p-6 border border-primary-200">
          <h3 className="font-semibold text-lg text-primary-900 mb-2 flex items-center justify-center gap-2">
            <Zap className="w-5 h-5" />
            Ready to Record?
          </h3>
          <p className="text-primary-700 mb-4">
            Follow these guidelines for the best analysis results. Our AI will provide detailed feedback on your form!
          </p>
          <div className="text-sm text-primary-600">
            💡 Tip: Record a test video first to check your setup before your main workout
          </div>
        </div>
      </div>
    </div>
  )
}
