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
    })
    return response.data
  } catch (error) {
    if (axios.isAxiosError(error)) {
      throw new Error(error.response?.data?.detail || 'Upload failed')
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
