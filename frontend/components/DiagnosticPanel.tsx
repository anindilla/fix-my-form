'use client'

import { AlertCircle, Camera, Lightbulb, Users, Clock } from 'lucide-react'

interface DiagnosticPanelProps {
  diagnostic: {
    total_frames?: number
    frames_with_pose?: number
    success_rate?: number
    avg_visible_landmarks?: number
    issues?: string[]
    recommendations?: string[]
    quality_issues?: string[]
    quality_score?: number
    metadata?: {
      width?: number
      height?: number
      duration?: number
      fps?: number
    }
  }
}

export default function DiagnosticPanel({ diagnostic }: DiagnosticPanelProps) {
  const {
    total_frames,
    frames_with_pose,
    success_rate,
    avg_visible_landmarks,
    issues = [],
    recommendations = [],
    quality_issues = [],
    quality_score,
    metadata
  } = diagnostic

  const isQualityIssue = quality_issues.length > 0
  const isPoseIssue = issues.length > 0

  return (
    <div className="bg-red-50 border border-red-200 rounded-xl p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center gap-3">
        <div className="p-2 bg-red-100 rounded-lg">
          <AlertCircle className="w-6 h-6 text-red-600" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-red-900">Analysis Failed</h3>
          <p className="text-sm text-red-700">
            {isQualityIssue ? 'Video quality issues detected' : 'Pose detection failed'}
          </p>
        </div>
      </div>

      {/* Quality Issues */}
      {isQualityIssue && (
        <div className="space-y-4">
          <h4 className="font-medium text-red-900 flex items-center gap-2">
            <Camera className="w-4 h-4" />
            Video Quality Issues
          </h4>
          <div className="space-y-2">
            {quality_issues.map((issue, index) => (
              <div key={index} className="flex items-start gap-2 text-sm text-red-800">
                <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2 flex-shrink-0" />
                <span>{issue}</span>
              </div>
            ))}
          </div>
          {quality_score !== undefined && (
            <div className="text-sm text-red-700">
              Quality Score: {quality_score}/100
            </div>
          )}
        </div>
      )}

      {/* Pose Detection Issues */}
      {isPoseIssue && (
        <div className="space-y-4">
          <h4 className="font-medium text-red-900 flex items-center gap-2">
            <Users className="w-4 h-4" />
            Pose Detection Issues
          </h4>
          <div className="space-y-2">
            {issues.map((issue, index) => (
              <div key={index} className="flex items-start gap-2 text-sm text-red-800">
                <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2 flex-shrink-0" />
                <span>{issue}</span>
              </div>
            ))}
          </div>
          
          {/* Technical Details */}
          {(total_frames || success_rate !== undefined) && (
            <div className="bg-red-100 rounded-lg p-4 space-y-2">
              <h5 className="font-medium text-red-900 text-sm">Technical Details</h5>
              <div className="grid grid-cols-2 gap-2 text-xs text-red-800">
                {total_frames && (
                  <div>
                    <span className="font-medium">Total Frames:</span> {total_frames}
                  </div>
                )}
                {frames_with_pose !== undefined && (
                  <div>
                    <span className="font-medium">Pose Detected:</span> {frames_with_pose}
                  </div>
                )}
                {success_rate !== undefined && (
                  <div>
                    <span className="font-medium">Success Rate:</span> {success_rate}%
                  </div>
                )}
                {avg_visible_landmarks !== undefined && (
                  <div>
                    <span className="font-medium">Avg Landmarks:</span> {avg_visible_landmarks}/33
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Recommendations */}
      {recommendations.length > 0 && (
        <div className="space-y-4">
          <h4 className="font-medium text-red-900 flex items-center gap-2">
            <Lightbulb className="w-4 h-4" />
            How to Fix This
          </h4>
          <div className="space-y-3">
            {recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-white rounded-lg border border-red-200">
                <div className="w-6 h-6 bg-red-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <span className="text-xs font-medium text-red-700">{index + 1}</span>
                </div>
                <p className="text-sm text-red-800">{recommendation}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Video Metadata */}
      {metadata && (
        <div className="space-y-4">
          <h4 className="font-medium text-red-900 flex items-center gap-2">
            <Clock className="w-4 h-4" />
            Video Information
          </h4>
          <div className="grid grid-cols-2 gap-3 text-sm">
            {metadata.width && metadata.height && (
              <div className="bg-white rounded-lg p-3 border border-red-200">
                <div className="font-medium text-red-900">Resolution</div>
                <div className="text-red-700">{metadata.width} × {metadata.height}</div>
              </div>
            )}
            {metadata.duration && (
              <div className="bg-white rounded-lg p-3 border border-red-200">
                <div className="font-medium text-red-900">Duration</div>
                <div className="text-red-700">{metadata.duration.toFixed(1)}s</div>
              </div>
            )}
            {metadata.fps && (
              <div className="bg-white rounded-lg p-3 border border-red-200">
                <div className="font-medium text-red-900">Frame Rate</div>
                <div className="text-red-700">{metadata.fps.toFixed(1)} fps</div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Recording Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="font-medium text-blue-900 mb-2">💡 Recording Tips</h4>
        <div className="space-y-2 text-sm text-blue-800">
          <div>• Record from 6-10 feet away with your full body visible</div>
          <div>• Use good lighting (natural light or bright indoor lighting)</div>
          <div>• Film from a side angle (90° to your movement)</div>
          <div>• Avoid busy backgrounds and wear contrasting colors</div>
          <div>• Keep videos between 2-60 seconds for best results</div>
        </div>
      </div>
    </div>
  )
}
