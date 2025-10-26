'use client'

import { useState, useEffect } from 'react'
import { useParams } from 'next/navigation'
import AnalysisResults from '../../../components/AnalysisResults'
import { getAnalysis } from '../../../lib/api'
import { ArrowLeft, RefreshCw, AlertCircle } from 'lucide-react'
import Link from 'next/link'

export default function AnalysisPage() {
  const params = useParams()
  const analysisId = params.id as string
  
  const [analysis, setAnalysis] = useState<any>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchAnalysis = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Simulate polling for analysis completion
        const pollAnalysis = async () => {
          try {
            const result = await getAnalysis(analysisId)
            setAnalysis(result)
            setLoading(false)
          } catch (err) {
            // If analysis is still processing, continue polling
            if (err instanceof Error && err.message.includes('not found')) {
              setTimeout(pollAnalysis, 2000) // Poll every 2 seconds
            } else {
              throw err
            }
          }
        }
        
        await pollAnalysis()
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load analysis')
        setLoading(false)
      }
    }

    fetchAnalysis()
  }, [analysisId])

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <div className="w-16 h-16 mx-auto bg-primary-100 rounded-full flex items-center justify-center mb-4">
              <RefreshCw className="w-8 h-8 text-primary-600 animate-spin" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Loading Analysis...</h2>
            <p className="text-gray-600">This may take a few moments</p>
          </div>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <div className="w-16 h-16 mx-auto bg-error-100 rounded-full flex items-center justify-center mb-4">
              <AlertCircle className="w-8 h-8 text-error-600" />
            </div>
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Analysis Not Found</h2>
            <p className="text-gray-600 mb-6">{error}</p>
            <div className="space-x-4">
              <Link href="/" className="btn-primary">
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back to Home
              </Link>
              <button 
                onClick={() => window.location.reload()} 
                className="btn-secondary"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (!analysis) {
    return (
      <div className="min-h-screen bg-gray-50">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">No Analysis Data</h2>
            <p className="text-gray-600 mb-6">Unable to load analysis results</p>
            <Link href="/" className="btn-primary">
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Home
            </Link>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col">
      {/* Header */}
      <header className="bg-white shadow-sm border-b flex-shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <div className="flex items-center">
              <Link href="/" className="flex items-center text-gray-600 hover:text-gray-900">
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back to Home
              </Link>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="flex-1 py-8 sm:py-12">
        <AnalysisResults analysis={analysis} />
      </main>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-6 sm:py-8 flex-shrink-0">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-gray-400 text-sm sm:text-base">
            Share this analysis with your trainer or save for future reference
          </p>
        </div>
      </footer>
    </div>
  )
}
