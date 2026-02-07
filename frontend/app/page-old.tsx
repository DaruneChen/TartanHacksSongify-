'use client'

import { useState, useRef, useEffect } from 'react'
import { Play, Square, Music, Sparkles, Download, Trash2, Zap, Flame } from 'lucide-react'
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
  const [status, setStatus] = useState('Ready to capture')
  const [error, setError] = useState<string | null>(null)
  const [lyricCount, setLyricCount] = useState(0)
  
  const streamRef = useRef<MediaStream | null>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  // Start screen capture
  const startCapture = async () => {
    try {
      setError(null)
      setStatus('Requesting screen access...')
      
      // Request screen capture
      const stream = await navigator.mediaDevices.getDisplayMedia({
        video: { 
          cursor: 'never',
          displaySurface: 'monitor'
        }
      })
      
      streamRef.current = stream
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream
        await videoRef.current.play()
      }
      
      setIsCapturing(true)
      setStatus('Capturing screen...')
      
      // Start analyzing frames every 5 seconds
      intervalRef.current = setInterval(() => {
        captureAndAnalyze()
      }, 5000)
      
      // Capture first frame immediately
      setTimeout(() => captureAndAnalyze(), 1000)
      
    } catch (err: any) {
      setError(`Failed to start capture: ${err.message}`)
      setStatus('Error')
      console.error(err)
    }
  }

  // Stop screen capture
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
    setStatus('Capture stopped')
  }

  // Capture frame and analyze
  const captureAndAnalyze = async () => {
    if (!videoRef.current || !canvasRef.current) return
    
    try {
      setStatus('Analyzing scene...')
      
      const canvas = canvasRef.current
      const video = videoRef.current
      
      // Set canvas size
      canvas.width = video.videoWidth
      canvas.height = video.videoHeight
      
      // Draw video frame to canvas
      const ctx = canvas.getContext('2d')
      if (!ctx) return
      
      ctx.drawImage(video, 0, 0)
      
      // Convert canvas to blob
      const blob = await new Promise<Blob>((resolve) => {
        canvas.toBlob((b) => resolve(b!), 'image/png')
      })
      
      // Send to backend for analysis
      const formData = new FormData()
      formData.append('file', blob, 'screen.png')
      
      const analyzeResponse = await axios.post(
        `${API_URL}/api/analyze-frame`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      )
      
      const context: SceneContext = analyzeResponse.data.context
      setCurrentContext(context)
      
      setStatus(`Scene: ${context.activity} (${context.mood})`)
      
      // Generate lyrics if scene changed
      if (!analyzeResponse.data.cached) {
        await generateLyrics(context)
      }
      
    } catch (err: any) {
      console.error('Analysis error:', err)
      setStatus('Analysis failed - retrying...')
    }
  }

  // Generate lyrics for current context
  const generateLyrics = async (context: SceneContext) => {
    try {
      setStatus('Generating lyrics...')
      
      const previousLyrics = allLyrics.flatMap(set => set.lyrics)
      
      const response = await axios.post(`${API_URL}/api/generate-lyrics`, {
        scene_context: context,
        previous_lyrics: previousLyrics
      })
      
      const lyricSet: LyricSet = response.data
      setAllLyrics(prev => [...prev, lyricSet])
      
      setStatus(`Generated ${context.suggested_genre} lyrics`)
      
    } catch (err: any) {
      console.error('Lyric generation error:', err)
      setStatus('Lyric generation failed')
    }
  }

  // Export lyrics
  const exportLyrics = () => {
    const text = allLyrics.map((set, i) => {
      return `[Verse ${i + 1}] - ${set.genre}\n${set.lyrics.join('\n')}\n`
    }).join('\n')
    
    const blob = new Blob([text], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'screen-to-song-lyrics.txt'
    a.click()
  }

  // Clear all lyrics
  const clearLyrics = async () => {
    setAllLyrics([])
    try {
      await axios.post(`${API_URL}/api/clear-cache`)
    } catch (err) {
      console.error('Clear cache error:', err)
    }
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCapture()
    }
  }, [])

  return (
    <div className="min-h-screen bg-[#1a1d2e] text-white overflow-hidden relative">
      {/* Animated gradient background */}
      <div className="absolute inset-0 bg-gradient-to-br from-[#ff6b9d] via-[#c084fc] to-[#60efff] opacity-20 blur-3xl"></div>
      <div className="absolute inset-0 bg-[#1a1d2e]/90"></div>
      
      {/* Floating orbs */}
      <div className="absolute top-20 right-20 w-64 h-64 bg-pink-500 rounded-full blur-3xl opacity-20 animate-pulse-slow"></div>
      <div className="absolute bottom-20 left-20 w-80 h-80 bg-cyan-500 rounded-full blur-3xl opacity-20 animate-pulse-slow" style={{animationDelay: '1s'}}></div>
      
      <div className="relative z-10">
        {/* Header */}
        <header className="px-6 py-6">
          <div className="flex items-center justify-between max-w-md mx-auto">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center">
                <Music className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Screen.song</h1>
                <p className="text-xs text-gray-400">AI Soundtrack Generator</p>
              </div>
            </div>
            <div className={`px-3 py-1.5 rounded-full text-xs font-medium backdrop-blur-xl ${
              isCapturing 
                ? 'bg-green-500/20 text-green-400 border border-green-500/30' 
                : 'bg-gray-800/40 text-gray-400 border border-gray-700/30'
            }`}>
              {isCapturing ? '● Live' : 'Offline'}
            </div>
          </div>
        </header>

        {/* Main Content */}
        <main className="px-6 pb-8 max-w-md mx-auto space-y-4">
          
          {/* Balance Card - Maps.me style */}
          <div className="relative overflow-hidden rounded-3xl bg-gradient-to-br from-pink-500/80 via-purple-500/80 to-cyan-500/80 p-[1px]">
            <div className="rounded-3xl bg-[#1a1d2e]/95 backdrop-blur-xl p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm text-gray-400">Lyrics Generated</span>
                <button className="w-8 h-8 rounded-full bg-white/10 backdrop-blur-sm flex items-center justify-center hover:bg-white/20 transition-colors">
                  <Sparkles className="w-4 h-4 text-white" />
                </button>
              </div>
              <div className="flex items-baseline gap-2 mb-6">
                <span className="text-5xl font-bold text-white">{lyricCount}</span>
                <span className="w-8 h-8 rounded-full bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center text-sm font-bold">
                  L
                </span>
              </div>
              
              <div className="flex gap-2">
                <button
                  onClick={isCapturing ? stopCapture : startCapture}
                  className={`flex-1 py-3 px-4 rounded-2xl font-semibold text-sm flex items-center justify-center gap-2 transition-all ${
                    isCapturing
                      ? 'bg-red-500/20 text-red-400 border border-red-500/30 backdrop-blur-sm'
                      : 'bg-gradient-to-r from-purple-500 to-pink-500 text-white shadow-lg shadow-purple-500/50 hover:shadow-purple-500/70'
                  }`}
                >
                  <Zap className="w-4 h-4" />
                  {isCapturing ? 'Stop' : 'Start Capture'}
                </button>
                <button
                  onClick={exportLyrics}
                  disabled={allLyrics.length === 0}
                  className="py-3 px-4 rounded-2xl bg-gradient-to-r from-blue-500 to-cyan-500 text-white font-semibold text-sm disabled:opacity-30 disabled:cursor-not-allowed hover:shadow-lg hover:shadow-blue-500/50 transition-all"
                >
                  <Download className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
          
          {/* Left Column - Controls & Scene */}
          <div className="space-y-6">
            
            {/* Control Panel */}
            <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700">
              <h2 className="text-xl font-semibold mb-4 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-yellow-400" />
                Capture Control
              </h2>
              
              <div className="space-y-4">
                {!isCapturing ? (
                  <button
                    onClick={startCapture}
                    className="w-full bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold py-4 px-6 rounded-xl flex items-center justify-center gap-2 transition-all transform hover:scale-105"
                  >
                    <Play className="w-5 h-5" />
                    Start Capturing
                  </button>
                ) : (
                  <button
                    onClick={stopCapture}
                    className="w-full bg-red-500 hover:bg-red-600 text-white font-semibold py-4 px-6 rounded-xl flex items-center justify-center gap-2 transition-all"
                  >
                    <Square className="w-5 h-5" />
                    Stop Capturing
                  </button>
                )}
                
                <div className="flex gap-2">
                  <button
                    onClick={exportLyrics}
                    disabled={allLyrics.length === 0}
                    className="flex-1 bg-blue-500 hover:bg-blue-600 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all"
                  >
                    <Download className="w-4 h-4" />
                    Export
                  </button>
                  <button
                    onClick={clearLyrics}
                    disabled={allLyrics.length === 0}
                    className="flex-1 bg-gray-600 hover:bg-gray-700 disabled:bg-gray-800 disabled:cursor-not-allowed text-white font-semibold py-3 px-4 rounded-xl flex items-center justify-center gap-2 transition-all"
                  >
                    <Trash2 className="w-4 h-4" />
                    Clear
                  </button>
                </div>
              </div>

              {error && (
                <div className="mt-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-300 text-sm">
                  {error}
                </div>
              )}
            </div>

            {/* Current Scene Context */}
            {currentContext && (
              <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700">
                <h2 className="text-xl font-semibold mb-4">Current Scene</h2>
                
                <div className="space-y-3">
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Mood</span>
                    <span className="text-purple-400 font-semibold capitalize">{currentContext.mood}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Activity</span>
                    <span className="text-pink-400 font-semibold capitalize">{currentContext.activity}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Genre</span>
                    <span className="text-blue-400 font-semibold capitalize">{currentContext.suggested_genre}</span>
                  </div>
                  <div className="flex justify-between items-center">
                    <span className="text-gray-400">Energy</span>
                    <div className="flex gap-1">
                      {[1, 2, 3, 4, 5].map(level => (
                        <div
                          key={level}
                          className={`w-6 h-2 rounded-full ${
                            level <= currentContext.energy_level
                              ? 'bg-gradient-to-r from-green-400 to-yellow-400'
                              : 'bg-gray-600'
                          }`}
                        />
                      ))}
                    </div>
                  </div>
                  <div className="pt-2 border-t border-gray-700">
                    <p className="text-gray-300 text-sm italic">{currentContext.description}</p>
                  </div>
                </div>
              </div>
            )}

            {/* Audio Visualizer Placeholder */}
            <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700">
              <h2 className="text-xl font-semibold mb-4">Audio Visualizer</h2>
              <div className="flex items-end justify-center gap-1 h-32">
                {[...Array(20)].map((_, i) => (
                  <div
                    key={i}
                    className="visualizer-bar bg-gradient-to-t from-purple-500 to-pink-500 w-3 rounded-t"
                    style={{
                      animationDelay: `${i * 0.1}s`,
                      height: `${Math.random() * 60 + 20}%`
                    }}
                  />
                ))}
              </div>
            </div>
          </div>

          {/* Right Column - Lyrics Display */}
          <div className="bg-gray-800/50 backdrop-blur-lg rounded-2xl p-6 border border-gray-700 h-[calc(100vh-12rem)] overflow-y-auto">
            <h2 className="text-xl font-semibold mb-6 sticky top-0 bg-gray-800/90 backdrop-blur-lg py-2 -mx-6 px-6">
              Generated Lyrics
            </h2>
            
            {allLyrics.length === 0 ? (
              <div className="text-center py-12 text-gray-500">
                <Music className="w-16 h-16 mx-auto mb-4 opacity-50" />
                <p>Start capturing to generate lyrics</p>
              </div>
            ) : (
              <div className="space-y-8">
                {allLyrics.map((set, index) => (
                  <div key={index} className="lyric-line">
                    <div className="flex items-center justify-between mb-2">
                      <span className="text-sm font-semibold text-purple-400">
                        Verse {index + 1}
                      </span>
                      <span className="text-xs text-gray-500 uppercase">
                        {set.genre}
                      </span>
                    </div>
                    <div className="space-y-2">
                      {set.lyrics.map((line, lineIndex) => (
                        <p
                          key={lineIndex}
                          className="text-lg leading-relaxed text-gray-200"
                          style={{ animationDelay: `${lineIndex * 0.1}s` }}
                        >
                          {line}
                        </p>
                      ))}
                    </div>
                    {index < allLyrics.length - 1 && (
                      <div className="mt-6 border-b border-gray-700" />
                    )}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Hidden elements */}
      <video ref={videoRef} className="hidden" />
      <canvas ref={canvasRef} className="hidden" />
    </div>
  )
}
