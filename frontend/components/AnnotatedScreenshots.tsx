'use client'

import { useState } from 'react'
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, RotateCcw, AlertCircle } from 'lucide-react'

interface AnnotatedScreenshotsProps {
  screenshots: string[]
}

export default function AnnotatedScreenshots({ screenshots }: AnnotatedScreenshotsProps) {
  const [currentIndex, setCurrentIndex] = useState(0)
  const [zoom, setZoom] = useState(1)
  const [rotation, setRotation] = useState(0)

  const nextImage = () => {
    setCurrentIndex((prev) => (prev + 1) % screenshots.length)
  }

  const prevImage = () => {
    setCurrentIndex((prev) => (prev - 1 + screenshots.length) % screenshots.length)
  }

  const resetView = () => {
    setZoom(1)
    setRotation(0)
  }

  if (screenshots.length === 0) {
    return (
      <div className="card text-center py-12">
        <AlertCircle className="w-12 h-12 text-yellow-500 mx-auto mb-4" />
        <p className="text-gray-700 font-semibold mb-2">Visual Analysis Temporarily Disabled</p>
        <p className="text-gray-500 text-sm">
          Visual form analysis is currently disabled. You'll still receive detailed written feedback 
          on your workout form and technique.
        </p>
      </div>
    )
  }

        return (
          <div className="space-y-6">
            <div className="text-center">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">Visual Form Analysis</h3>
              <p className="text-gray-600">
                This screenshot highlights the most crucial improvement point from your workout
              </p>
            </div>

      {/* Image Viewer */}
      <div className="card">
        <div className="relative bg-gray-100 rounded-lg overflow-hidden">
          {/* Image */}
          <div className="relative overflow-hidden" style={{ height: '500px' }}>
            <img
              src={screenshots[currentIndex]}
              alt={`Form analysis ${currentIndex + 1}`}
              className="w-full h-full object-contain transition-transform duration-200"
              style={{
                transform: `scale(${zoom}) rotate(${rotation}deg)`,
                transformOrigin: 'center'
              }}
            />
          </div>

          {/* Navigation */}
          {screenshots.length > 1 && (
            <>
              <button
                onClick={prevImage}
                className="absolute left-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition-opacity"
              >
                <ChevronLeft className="w-6 h-6" />
              </button>
              <button
                onClick={nextImage}
                className="absolute right-4 top-1/2 transform -translate-y-1/2 bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition-opacity"
              >
                <ChevronRight className="w-6 h-6" />
              </button>
            </>
          )}

          {/* Controls */}
          <div className="absolute top-4 right-4 flex space-x-2">
            <button
              onClick={() => setZoom(prev => Math.min(prev + 0.25, 3))}
              className="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition-opacity"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
            <button
              onClick={() => setZoom(prev => Math.max(prev - 0.25, 0.5))}
              className="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition-opacity"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <button
              onClick={() => setRotation(prev => prev + 90)}
              className="bg-black bg-opacity-50 text-white p-2 rounded-full hover:bg-opacity-75 transition-opacity"
            >
              <RotateCcw className="w-4 h-4" />
            </button>
            <button
              onClick={resetView}
              className="bg-black bg-opacity-50 text-white px-3 py-2 rounded-full hover:bg-opacity-75 transition-opacity text-sm"
            >
              Reset
            </button>
          </div>

          {/* Image Counter */}
          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 bg-black bg-opacity-50 text-white px-3 py-1 rounded-full text-sm">
            {currentIndex + 1} of {screenshots.length}
          </div>
        </div>

        {/* Thumbnails */}
        {screenshots.length > 1 && (
          <div className="mt-4 flex justify-center space-x-2">
            {screenshots.map((screenshot, index) => (
              <button
                key={index}
                onClick={() => setCurrentIndex(index)}
                className={`w-16 h-16 rounded-lg overflow-hidden border-2 transition-colors ${
                  index === currentIndex
                    ? 'border-primary-500'
                    : 'border-gray-300 hover:border-gray-400'
                }`}
              >
                <img
                  src={screenshot}
                  alt={`Thumbnail ${index + 1}`}
                  className="w-full h-full object-cover"
                />
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Analysis Notes */}
      <div className="card">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">What to Look For</h4>
        <div className="grid md:grid-cols-3 gap-4">
          <div className="bg-red-50 p-4 rounded-lg">
            <div className="flex items-center mb-2">
              <div className="w-3 h-3 bg-red-500 rounded-full mr-2" />
              <span className="font-medium text-red-800">Red Arrows</span>
            </div>
            <p className="text-sm text-red-700">Critical form issues that need immediate attention</p>
          </div>
          <div className="bg-yellow-50 p-4 rounded-lg">
            <div className="flex items-center mb-2">
              <div className="w-3 h-3 bg-yellow-500 rounded-full mr-2" />
              <span className="font-medium text-yellow-800">Yellow Arrows</span>
            </div>
            <p className="text-sm text-yellow-700">Areas for improvement to optimize your form</p>
          </div>
          <div className="bg-blue-50 p-4 rounded-lg">
            <div className="flex items-center mb-2">
              <div className="w-3 h-3 bg-blue-500 rounded-full mr-2" />
              <span className="font-medium text-blue-800">Blue Arrows</span>
            </div>
            <p className="text-sm text-blue-700">Technical points to focus on during your next workout</p>
          </div>
        </div>
      </div>
    </div>
  )
}
