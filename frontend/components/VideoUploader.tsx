'use client'

import { useCallback, useState } from 'react'
import { useDropzone } from 'react-dropzone'
import { Upload, Video, AlertCircle, CheckCircle, Dumbbell, Weight } from 'lucide-react'
import { uploadVideo, analyzeVideo } from '../lib/api'

interface VideoUploaderProps {
  onAnalysisStart: (analysisId: string) => void
}

const exerciseOptions = [
  {
    id: 'front-squat',
    name: 'Front Squat',
    description: 'Squat with barbell in front position',
    icon: Dumbbell,
    color: 'from-blue-500 to-cyan-500'
  },
  {
    id: 'back-squat',
    name: 'Back Squat',
    description: 'Traditional squat with barbell on back',
    icon: Dumbbell,
    color: 'from-purple-500 to-pink-500'
  },
  {
    id: 'conventional-deadlift',
    name: 'Conventional Deadlift',
    description: 'Standard deadlift with narrow stance',
    icon: Weight,
    color: 'from-green-500 to-emerald-500'
  },
  {
    id: 'sumo-deadlift',
    name: 'Sumo Deadlift',
    description: 'Wide stance deadlift variation',
    icon: Weight,
    color: 'from-orange-500 to-red-500'
  }
]

export default function VideoUploader({ onAnalysisStart }: VideoUploaderProps) {
  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)
  const [selectedExercise, setSelectedExercise] = useState<string>('')
  const [retryCount, setRetryCount] = useState(0)
  const [maxRetries] = useState(3)

  const uploadWithRetry = useCallback(async (file: File, attempt: number = 1): Promise<void> => {
    try {
      // Simulate upload progress
      const progressInterval = setInterval(() => {
        setUploadProgress(prev => {
          if (prev >= 90) {
            clearInterval(progressInterval)
            return 90
          }
          return prev + 10
        })
      }, 200)

      // Upload video
      const uploadResult = await uploadVideo(file)
      setUploadProgress(100)
      clearInterval(progressInterval)

      // Start analysis with selected exercise
      const analysisResult = await analyzeVideo(uploadResult.file_id, uploadResult.filename, selectedExercise)
      
      setSuccess(true)
      setRetryCount(0) // Reset retry count on success
      onAnalysisStart(analysisResult.file_id)

    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Upload failed'
      
      // Check if we should retry
      if (attempt < maxRetries && (
        errorMessage.includes('timeout') || 
        errorMessage.includes('network') || 
        errorMessage.includes('connection') ||
        errorMessage.includes('503') ||
        errorMessage.includes('504')
      )) {
        setRetryCount(attempt)
        setError(`${errorMessage} (Attempt ${attempt}/${maxRetries})`)
        
        // Exponential backoff: wait 2^attempt seconds
        const delay = Math.pow(2, attempt) * 1000
        setTimeout(() => {
          setError(null)
          uploadWithRetry(file, attempt + 1)
        }, delay)
      } else {
        setError(errorMessage)
        setUploading(false)
        setRetryCount(0)
      }
    }
  }, [onAnalysisStart, selectedExercise, maxRetries])

  const onDrop = useCallback(async (acceptedFiles: File[]) => {
    const file = acceptedFiles[0]
    if (!file) return

    if (!selectedExercise) {
      setError('Please select an exercise type first')
      return
    }

    setUploading(true)
    setError(null)
    setSuccess(false)
    setUploadProgress(0)
    setRetryCount(0)

    await uploadWithRetry(file)
  }, [uploadWithRetry, selectedExercise])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'video/*': ['.mp4', '.mov', '.avi', '.mkv', '.webm']
    },
    maxFiles: 1,
    disabled: uploading
  })

  return (
    <div className="max-w-4xl mx-auto">
      {/* Exercise Selection */}
      <div className="mb-12 sm:mb-16">
        <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-6 sm:mb-8 text-center">Choose Your Exercise</h3>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4">
          {exerciseOptions.map((exercise) => {
            const Icon = exercise.icon
            const isSelected = selectedExercise === exercise.id
            return (
              <button
                key={exercise.id}
                onClick={() => setSelectedExercise(exercise.id)}
                className={`
                  p-4 sm:p-6 rounded-2xl border-2 transition-all duration-300 backdrop-blur-sm
                  ${isSelected 
                    ? 'border-blue-400 bg-blue-100 shadow-xl' 
                    : 'border-gray-400 bg-white/90 hover:border-blue-300 hover:bg-blue-50 hover:shadow-lg'
                  }
                `}
              >
                <div className="flex items-center space-x-3">
                  <div className={`w-10 h-10 sm:w-12 sm:h-12 rounded-xl bg-gradient-to-r ${exercise.color} flex items-center justify-center flex-shrink-0`}>
                    <Icon className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
                  </div>
                  <div className="text-left min-w-0 flex-1">
                    <h4 className="text-gray-900 font-semibold text-base sm:text-lg">{exercise.name}</h4>
                    <p className="text-gray-700 text-xs sm:text-sm font-medium">{exercise.description}</p>
                  </div>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Video Upload Area */}
      <div
        {...getRootProps()}
        className={`
          border-2 border-dashed rounded-2xl p-8 sm:p-12 lg:p-16 text-center cursor-pointer transition-all duration-300 backdrop-blur-sm
          ${isDragActive ? 'border-blue-400 bg-blue-100' : 'border-gray-400 bg-white/95'}
          ${uploading ? 'cursor-not-allowed opacity-50' : 'hover:border-blue-300 hover:bg-blue-50'}
        `}
      >
        <input {...getInputProps()} />
        
        {uploading ? (
            <div className="space-y-4 sm:space-y-6">
              <div className="w-16 h-16 sm:w-20 sm:h-20 mx-auto bg-blue-100 rounded-2xl flex items-center justify-center">
                <Upload className="w-8 h-8 sm:w-10 sm:h-10 text-blue-600 animate-pulse" />
              </div>
              <div>
                <h3 className="text-xl sm:text-2xl font-bold text-gray-900 mb-3 sm:mb-4">Uploading...</h3>
                <div className="w-full bg-gray-300 rounded-full h-2 sm:h-3 mb-3 sm:mb-4">
                  <div 
                    className="bg-blue-500 h-2 sm:h-3 rounded-full transition-all duration-300 shadow-lg"
                    style={{ width: `${uploadProgress}%` }}
                  />
                </div>
                <p className="text-gray-700 text-base sm:text-lg font-medium">{uploadProgress}% complete</p>
              </div>
            </div>
        ) : success ? (
          <div className="space-y-4 sm:space-y-6">
            <div className="w-16 h-16 sm:w-20 sm:h-20 mx-auto bg-green-100 rounded-2xl flex items-center justify-center">
              <CheckCircle className="w-8 h-8 sm:w-10 sm:h-10 text-green-600" />
            </div>
            <h3 className="text-xl sm:text-2xl font-bold text-gray-900">Upload Successful!</h3>
            <p className="text-gray-700 text-base sm:text-lg font-medium">Starting analysis...</p>
          </div>
        ) : (
          <div className="space-y-4 sm:space-y-6">
            <div className="w-16 h-16 sm:w-20 sm:h-20 mx-auto bg-gray-200 rounded-2xl flex items-center justify-center">
              <Video className="w-8 h-8 sm:w-10 sm:h-10 text-gray-700" />
            </div>
            <div>
              <h3 className="text-lg sm:text-xl lg:text-2xl font-bold text-gray-900 mb-3 sm:mb-4">
                {isDragActive ? 'Drop your video here' : selectedExercise ? `Upload your ${exerciseOptions.find(e => e.id === selectedExercise)?.name} video` : 'Upload your workout video'}
              </h3>
              <p className="text-gray-700 text-base sm:text-lg mb-4 sm:mb-6 font-medium px-2">
                {selectedExercise ? `Ready to analyze your ${exerciseOptions.find(e => e.id === selectedExercise)?.name.toLowerCase()}` : 'Select an exercise above, then drag and drop your video file here, or click to browse'}
              </p>
              <div className="text-gray-600 text-xs sm:text-sm space-y-1 font-medium">
                <p>Supported formats: MP4, MOV, AVI, MKV, WebM</p>
                <p>Max file size: 50MB</p>
              </div>
            </div>
          </div>
        )}
      </div>

      {error && (
        <div className="mt-6 sm:mt-8 p-4 sm:p-6 bg-red-100 border border-red-300 rounded-2xl">
          <div className="flex items-center mb-3">
            <AlertCircle className="w-5 h-5 sm:w-6 sm:h-6 text-red-600 mr-3 sm:mr-4 flex-shrink-0" />
            <p className="text-red-800 text-base sm:text-lg font-medium">{error}</p>
          </div>
          {retryCount > 0 && retryCount < maxRetries && (
            <div className="text-sm text-red-700">
              Retrying automatically in a few seconds...
            </div>
          )}
          {retryCount >= maxRetries && (
            <button
              onClick={() => {
                setError(null)
                setRetryCount(0)
                setUploading(false)
              }}
              className="mt-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors text-sm font-medium"
            >
              Try Again
            </button>
          )}
        </div>
      )}
    </div>
  )
}
