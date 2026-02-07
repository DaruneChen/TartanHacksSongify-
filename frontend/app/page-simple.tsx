'use client'

import { useState, useRef, useEffect } from 'react'
import { Play, Square, Music, Sparkles, Download, Trash2, Zap, TrendingUp, Settings } from 'lucide-react'
import axios from 'axios'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface SceneContext {
  mood: string
  activity: string
  objects: string[]
  suggested_genre: string
  energy_level: number
  description: string
}

interface LyricSet {
  lyrics: string[]
  timestamp: number
  genre: string
}

export default function Home() {
  const [isCapturing, setIsCapturing] = useState(false)
  const [currentContext, setCurrentContext] = useState<SceneContext | null>(null)
  const [allLyrics, setAllLyrics] = useState<LyricSet[]>([])
  const [status, setStatus] = useState('Ready')
  const [error, setError] = useState<string | null>(null)
  const [lyricCount, setLyricCount] = useState(0)
  
  const streamRef = useRef<MediaStream | null>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    setLyricCount(allLyrics.flatMap(set => set.lyrics).length)
  }, [allLyrics])

  const startCapture = async () => {
    try {
      setError(null)
      setStatus('Starting...')
      
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { cursor: 'never', displaySurface: 'monitor' }
      })
      
      streamRef.current = stream
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      }
      
      setIsCapturing(true)
      setStatus('Live')
      
      intervalRef.current = setInterval(() => captureAndAnalyze(), 5000)
      setTimeout(() => captureAndAnalyze(), 1000)
      
    } catch (err: any) {
      setError(`Failed: ${err.message}`)
      setStatus('Error')
    }
  }

  const stopCapture = () => {
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop())
      streamRef.current = null
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current)
      intervalRef.current = null
    }
    if (videoRef.current) {
      videoRef.current.srcObject = null
    }
    setIsCapturing(false)
    setStatus('Stopped')
  }

  const captureAndAnalyze = async () => {
    if (!videoRef.current || !canvasRef.current) return
    
    try {
      setStatus('Analyzing...')
      
      const canvas = canvasRef.current
      const video = videoRef.current
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      ctx.drawImage(video, 0, 0)
      
      const blob = await new Promise<Blob>((resolve) => {
        canvas.toBlob((b) => resolve(b!), 'image/png')
      })
      
      const formData = new FormData()
      formData.append('file', blob, 'screen.png')
      
      const analyzeResponse = await axios.post(`${API_URL}/api/analyze-frame`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      
      const context: SceneContext = analyzeResponse.data.context
      setCurrentContext(context)
      setStatus('Live')
      
      if (!analyzeResponse.data.cached) {
        await generateLyrics(context)
      }
    } catch (err: any) {
      console.error('Analysis error:', err)
      setStatus('Error')
    }
  }

  const generateLyrics = async (context: SceneContext) => {
    try {
      const previousLyrics = allLyrics.flatMap(set => set.lyrics)
      const response = await axios.post(`${API_URL}/api/generate-lyrics`, {
        scene_context: context,
        previous_lyrics: previousLyrics
      })
      
      const lyricSet: LyricSet = response.data
      setAllLyrics(prev => [...prev, lyricSet])
      setStatus('Live')
    } catch (err: any) {
      console.error('Lyric error:', err)
    }
  }

  const exportLyrics = () => {
    const text = allLyrics.map((set, i) => 
      `[Verse ${i + 1}] - ${set.genre}\n${set.lyrics.join('\n')}\n`
    ).join('\n')
    
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'lyrics.txt'
    a.click()
  }

  const clearLyrics = async () => {
    setAllLyrics([])
    try {
      await axios.post(`${API_URL}/api/clear-cache`)
    } catch (err) {
      console.error(err)
    }
  }

  useEffect(() => {
    return () => stopCapture()
  }, [])

  return (
    <div className="min-h-screen bg-[#2a2d42] text-white overflow-hidden">
      <div className="max-w-[420px] mx-auto min-h-screen bg-[#2a2d42] p-4 pt-6">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <button className="w-10 h-10 rounded-full bg-[#1f2233] flex items-center justify-center">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M12 5L7 10L12 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center">
            <Play className="w-5 h-5 text-white" fill="white" />
          </div>
        </div>

        {/* Main Balance Card with Mesh Gradient */}
        <div className="relative mb-4 rounded-[32px] overflow-hidden">
          {/* Mesh gradient background */}
          <div className="absolute inset-0 bg-gradient-to-br from-[#ff6b9d] via-[#ff8a80] to-[#4ade80] opacity-90"></div>
          <div className="absolute inset-0 bg-gradient-to-tl from-[#60efff] via-transparent to-transparent opacity-60"></div>
          <div className="absolute inset-0 bg-gradient-to-br from-[#a78bfa] via-transparent to-transparent opacity-40"></div>
          
          <div className="relative backdrop-blur-sm bg-black/20 p-6">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-white/80">Screen.song</span>
              <button className="w-8 h-8 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center">
                <Settings className="w-4 h-4 text-white" />
              </button>
            </div>
            
            <div className="mb-6">
              <p className="text-sm text-white/70 mb-1">Balance</p>
              <div className="flex items-baseline gap-2">
                <span className="text-6xl font-bold text-white tracking-tight">{lyricCount}</span>
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
                  <span className="text-lg font-bold text-white">L</span>
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <button
                onClick={isCapturing ? undefined : startCapture}
                disabled={isCapturing}
                className="flex-1 bg-black/40 backdrop-blur-sm rounded-full py-3 px-4 flex items-center justify-center gap-2 text-white text-sm font-medium disabled:opacity-50"
              >
                <Zap className="w-4 h-4" />
                Generate lyrics
              </button>
              <button
                onClick={exportLyrics}
                disabled={allLyrics.length === 0}
                className="flex-1 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full py-3 px-4 flex items-center justify-center gap-2 text-white text-sm font-semibold disabled:opacity-50 shadow-lg shadow-blue-500/30"
              >
                <Download className="w-4 h-4" />
                Export lyrics
              </button>
            </div>
          </div>
        </div>

        {/* Transaction-style cards */}
        {currentContext && (
          <div className="bg-[#1f2233] rounded-[28px] p-4 mb-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-pink-400 to-purple-500 flex items-center justify-center flex-shrink-0">
                <Music className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-purple-400 text-sm font-medium">+{currentContext.energy_level}</span>
                    <div className="w-5 h-5 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
                      <span className="text-[10px] font-bold text-white">L</span>
                    </div>
                  </div>
                  <span className="px-2.5 py-0.5 bg-orange-500 rounded-full text-white text-xs font-medium">
                    {isCapturing ? 'Live' : 'Ready'}
                  </span>
                </div>
                <h3 className="text-white font-medium text-base mb-1">
                  {currentContext.activity.charAt(0).toUpperCase() + currentContext.activity.slice(1)} detected
                </h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  {currentContext.description}
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Lyrics as transaction cards */}
        {allLyrics.slice().reverse().map((set, index) => (
          <div key={index} className="bg-[#1f2233] rounded-[28px] p-4 mb-4">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center flex-shrink-0">
                <Sparkles className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-purple-400 text-sm font-medium">-{set.lyrics.length}</span>
                    <div className="w-5 h-5 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center">
                      <span className="text-[10px] font-bold text-white">L</span>
                    </div>
                  </div>
                  <span className="px-2.5 py-0.5 bg-gray-600/60 rounded-full text-white text-xs font-medium">
                    {set.genre}
                  </span>
                </div>
                <h3 className="text-white font-medium text-base mb-2">
                  Verse {allLyrics.length - index}
                </h3>
                <div className="space-y-1">
                  {set.lyrics.map((line, i) => (
                    <p key={i} className="text-gray-400 text-sm leading-relaxed">
                      {line}
                    </p>
                  ))}
                </div>
              </div>
            </div>
          </div>
        ))}

        {/* Empty state */}
        {allLyrics.length === 0 && !currentContext && (
          <div className="bg-[#1f2233] rounded-[28px] p-8 text-center">
            <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center mx-auto mb-4">
              <Music className="w-8 h-8 text-purple-400 opacity-50" />
            </div>
            <h3 className="text-white font-medium text-base mb-1">No lyrics yet</h3>
            <p className="text-gray-400 text-sm">
              Start capturing to generate your personalized soundtrack
            </p>
          </div>
        )}

        {/* Status indicator */}
        {isCapturing && (
          <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-black/80 backdrop-blur-xl rounded-full px-4 py-2 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
            <span className="text-sm text-white">{status}</span>
          </div>
        )}
      </div>

      {/* Hidden elements */}
      <video ref={videoRef} className="hidden" />
      <canvas ref={canvasRef} className="hidden" />
    </div>
  )
}
