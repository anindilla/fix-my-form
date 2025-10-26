import axios from 'axios'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000, // 30 seconds for video processing
})

export interface UploadResponse {
  file_id: string
  filename: string
  upload_url: string
  message: string
}

export interface AnalysisResponse {
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
  status: string
}

export async function uploadVideo(file: File): Promise<UploadResponse> {
  const formData = new FormData()
  formData.append('file', file)

  try {
    const response = await api.post('/api/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      timeout: 60000, // 60 seconds for large files
    })
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      const status = error.response?.status
      const detail = error.response?.data?.detail || error.message
      
      // Categorize errors for better retry logic
      if (status === 413) {
        throw new Error(`File too large: ${detail}`)
      } else if (status === 400) {
        throw new Error(`Invalid file: ${detail}`)
      } else if (status === 503) {
        throw new Error(`Service unavailable: ${detail}`)
      } else if (status === 504) {
        throw new Error(`Upload timeout: ${detail}`)
      } else if (error.code === 'ECONNABORTED') {
        throw new Error('Upload timeout - please try again')
      } else if (error.code === 'NETWORK_ERROR') {
        throw new Error('Network error - check your connection')
      } else {
        throw new Error(detail || 'Upload failed')
      }
    }
    throw new Error('Upload failed')
  }
}

export async function analyzeVideo(fileId: string, filename: string, exerciseType: string = 'squat'): Promise<AnalysisResponse> {
  try {
    const response = await api.post('/api/analyze', {
      file_id: fileId,
      filename: filename,
      exercise_type: exerciseType,
    }, {
      timeout: 300000, // 5 minutes for analysis (matches backend timeout)
    })
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'Analysis failed')
    }
    throw new Error('Analysis failed')
  }
}

export async function getAnalysis(analysisId: string): Promise<AnalysisResponse> {
  try {
    const response = await api.get(`/api/analysis/${analysisId}`)
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch analysis')
    }
    throw new Error('Failed to fetch analysis')
  }
}
