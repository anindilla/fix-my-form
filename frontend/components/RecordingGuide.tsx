'use client'

import { 
  Camera, 
  CheckCircle, 
  XCircle, 
  AlertTriangle
} from 'lucide-react'

export default function RecordingGuide() {
  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="font-heading text-3xl sm:text-4xl font-bold text-neutral-900 mb-4">
          📹 Recording Guidelines
        </h2>
        <p className="text-lg text-neutral-700">
          Simple tips for the best analysis results
        </p>
      </div>

      {/* Single column stack */}
      <div className="space-y-6">
        
        {/* Section 1: Camera Setup */}
        <div className="bg-white rounded-xl p-6 shadow-card border border-neutral-200">
          <h3 className="font-semibold text-xl text-neutral-900 mb-4 flex items-center gap-3">
            <Camera className="w-5 h-5 text-primary-600" />
            Camera Setup
          </h3>
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <div className="w-1.5 h-1.5 bg-primary-500 rounded-full mt-2 flex-shrink-0" />
              <span className="text-sm text-neutral-700">
                <span className="font-medium">Side view (90°)</span> - captures depth and form perfectly
              </span>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-1.5 h-1.5 bg-primary-500 rounded-full mt-2 flex-shrink-0" />
              <span className="text-sm text-neutral-700">
                <span className="font-medium">6-10 feet</span> from camera
              </span>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-1.5 h-1.5 bg-primary-500 rounded-full mt-2 flex-shrink-0" />
              <span className="text-sm text-neutral-700">
                <span className="font-medium">Full body visible</span> (head to feet)
              </span>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-1.5 h-1.5 bg-primary-500 rounded-full mt-2 flex-shrink-0" />
              <span className="text-sm text-neutral-700">
                <span className="font-medium">Good lighting</span> (natural or bright indoor)
              </span>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-1.5 h-1.5 bg-primary-500 rounded-full mt-2 flex-shrink-0" />
              <span className="text-sm text-neutral-700">
                <span className="font-medium">5-15 seconds</span>, 1-5 reps maximum
              </span>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-1.5 h-1.5 bg-primary-500 rounded-full mt-2 flex-shrink-0" />
              <span className="text-sm text-neutral-700">
                <span className="font-medium">720p minimum</span>, 30fps recommended
              </span>
            </div>
          </div>
        </div>

        {/* Section 2: Do's and Don'ts */}
        <div className="bg-white rounded-xl p-6 shadow-card border border-neutral-200">
          <h3 className="font-semibold text-xl text-neutral-900 mb-4 flex items-center gap-3">
            <CheckCircle className="w-5 h-5 text-primary-600" />
            Do's and Don'ts
          </h3>
          
          {/* Desktop: Two columns, Mobile: Single column */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            
            {/* Do's Column */}
            <div>
              <h4 className="font-medium text-success-700 mb-3 flex items-center gap-2">
                <CheckCircle className="w-4 h-4" />
                Do's
              </h4>
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-4 h-4 text-success-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-neutral-700">Record from side angle</span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-4 h-4 text-success-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-neutral-700">Use good lighting</span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-4 h-4 text-success-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-neutral-700">Wear fitted clothing</span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-4 h-4 text-success-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-neutral-700">Keep video short (5-15s)</span>
                </div>
                <div className="flex items-start gap-3">
                  <CheckCircle className="w-4 h-4 text-success-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-neutral-700">Ensure full body visible</span>
                </div>
              </div>
            </div>

            {/* Don'ts Column */}
            <div>
              <h4 className="font-medium text-error-700 mb-3 flex items-center gap-2">
                <XCircle className="w-4 h-4" />
                Don'ts
              </h4>
              <div className="space-y-3">
                <div className="flex items-start gap-3">
                  <XCircle className="w-4 h-4 text-error-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-neutral-700">Don't record from front/back</span>
                </div>
                <div className="flex items-start gap-3">
                  <XCircle className="w-4 h-4 text-error-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-neutral-700">Don't use busy backgrounds</span>
                </div>
                <div className="flex items-start gap-3">
                  <XCircle className="w-4 h-4 text-error-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-neutral-700">Don't wear baggy clothing</span>
                </div>
                <div className="flex items-start gap-3">
                  <XCircle className="w-4 h-4 text-error-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-neutral-700">Don't film in dim lighting</span>
                </div>
                <div className="flex items-start gap-3">
                  <XCircle className="w-4 h-4 text-error-600 mt-0.5 flex-shrink-0" />
                  <span className="text-sm text-neutral-700">Don't record too many reps</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Section 3: Model Limitations */}
        <div className="bg-warm-50 rounded-xl p-6 border border-warm-200">
          <h3 className="font-semibold text-xl text-neutral-900 mb-4 flex items-center gap-3">
            <AlertTriangle className="w-5 h-5 text-warm-600" />
            Model Limitations
          </h3>
          <div className="space-y-3">
            <div className="flex items-start gap-3">
              <div className="w-1.5 h-1.5 bg-warm-500 rounded-full mt-2 flex-shrink-0" />
              <span className="text-sm text-neutral-700">Cannot analyze bar weight or speed</span>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-1.5 h-1.5 bg-warm-500 rounded-full mt-2 flex-shrink-0" />
              <span className="text-sm text-neutral-700">Cannot detect subtle joint positions</span>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-1.5 h-1.5 bg-warm-500 rounded-full mt-2 flex-shrink-0" />
              <span className="text-sm text-neutral-700">Requires clear view of body landmarks</span>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-1.5 h-1.5 bg-warm-500 rounded-full mt-2 flex-shrink-0" />
              <span className="text-sm text-neutral-700">Best for form analysis, not performance</span>
            </div>
            <div className="flex items-start gap-3">
              <div className="w-1.5 h-1.5 bg-warm-500 rounded-full mt-2 flex-shrink-0" />
              <span className="text-sm text-neutral-700">Limited to 2D analysis from one angle</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}