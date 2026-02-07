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

  // Update lyric count whenever lyrics change
  useEffect(() => {
    setLyricCount(allLyrics.flatMap(set => set.lyrics).length)
  }, [allLyrics])

  // Start screen capture
  const startCapture = async () => {
    try {
      setError(null)
      setStatus('Requesting screen access...')
      
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
      
      intervalRef.current = setInterval(() => {
        captureAndAnalyze()
      }, 5000)
      
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
      
      const analyzeResponse = await axios.post(
        `${API_URL}/api/analyze-frame`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' }
        }
      )
      
      const context: SceneContext = analyzeResponse.data.context
      setCurrentContext(context)
      
      setStatus(`Scene: ${context.activity}`)
      
      if (!analyzeResponse.data.cached) {
        await generateLyrics(context)
      }
      
    } catch (err: any) {
      console.error('Analysis error:', err)
      setStatus('Analysis failed - retrying...')
    }
  }

  // Generate lyrics
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
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center shadow-lg shadow-purple-500/30">
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

          {/* Current Scene Card */}
          {currentContext && (
            <div className="rounded-3xl bg-[#252839]/60 backdrop-blur-xl border border-white/5 p-5">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-pink-500 to-purple-500 flex items-center justify-center shadow-lg shadow-pink-500/30">
                  <Flame className="w-5 h-5 text-white" />
                </div>
                <div className="flex-1">
                  <h3 className="text-white font-semibold text-sm">Current Vibe</h3>
                  <p className="text-gray-400 text-xs line-clamp-1">{currentContext.description}</p>
                </div>
                <span className="px-3 py-1 rounded-full bg-purple-500/20 text-purple-300 text-xs font-medium border border-purple-500/30">
                  {currentContext.suggested_genre}
                </span>
              </div>
              
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-white/5 rounded-2xl p-3 border border-white/5">
                  <p className="text-gray-400 text-xs mb-1">Mood</p>
                  <p className="text-white font-semibold capitalize text-sm">{currentContext.mood}</p>
                </div>
                <div className="bg-white/5 rounded-2xl p-3 border border-white/5">
                  <p className="text-gray-400 text-xs mb-1">Activity</p>
                  <p className="text-white font-semibold capitalize text-sm">{currentContext.activity}</p>
                </div>
              </div>
              
              {/* Energy meter */}
              <div className="mt-3">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-xs text-gray-400">Energy Level</span>
                  <span className="text-xs text-white font-medium">{currentContext.energy_level}/5</span>
                </div>
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map(level => (
                    <div
                      key={level}
                      className={`h-1.5 flex-1 rounded-full transition-all ${
                        level <= currentContext.energy_level
                          ? 'bg-gradient-to-r from-green-400 to-cyan-400'
                          : 'bg-white/10'
                      }`}
                    />
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Status Card */}
          <div className="rounded-3xl bg-[#252839]/40 backdrop-blur-xl border border-white/5 p-4">
            <div className="flex items-center gap-3">
              <div className={`w-2 h-2 rounded-full ${
                isCapturing ? 'bg-green-400 animate-pulse' : 'bg-gray-500'
              }`}></div>
              <p className="text-sm text-gray-300">{status}</p>
            </div>
            {error && (
              <div className="mt-2 text-xs text-red-400 bg-red-500/10 rounded-lg p-2 border border-red-500/20">
                {error}
              </div>
            )}
          </div>

          {/* Lyrics Feed */}
          <div className="space-y-3">
            {allLyrics.length === 0 ? (
              <div className="rounded-3xl bg-[#252839]/30 backdrop-blur-xl border border-white/5 p-8 text-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center mx-auto mb-4">
                  <Music className="w-8 h-8 text-purple-400 opacity-50" />
                </div>
                <p className="text-gray-400 text-sm mb-1">No lyrics yet</p>
                <p className="text-gray-500 text-xs">Start capturing to generate your soundtrack</p>
              </div>
            ) : (
              <>
                <div className="flex items-center justify-between px-1">
                  <h2 className="text-sm font-semibold text-white">Generated Lyrics</h2>
                  <button
                    onClick={clearLyrics}
                    className="text-xs text-gray-400 hover:text-white flex items-center gap-1 transition-colors"
                  >
                    <Trash2 className="w-3 h-3" />
                    Clear
                  </button>
                </div>

                {allLyrics.slice().reverse().map((set, index) => (
                  <div
                    key={index}
                    className="rounded-3xl bg-[#252839]/40 backdrop-blur-xl border border-white/5 p-4 hover:bg-[#252839]/60 transition-colors"
                  >
                    <div className="flex items-center justify-between mb-3">
                      <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${
                          index === 0 ? 'bg-pink-400' : 'bg-purple-400'
                        }`}></div>
                        <span className="text-xs font-medium text-gray-400">
                          Verse {allLyrics.length - index}
                        </span>
                      </div>
                      <span className="px-2 py-0.5 rounded-full bg-purple-500/20 text-purple-300 text-[10px] font-medium border border-purple-500/30">
                        {set.genre}
                      </span>
                    </div>
                    <div className="space-y-2">
                      {set.lyrics.map((line, lineIndex) => (
                        <p
                          key={lineIndex}
                          className="text-sm leading-relaxed text-gray-200"
                        >
                          {line}
                        </p>
                      ))}
                    </div>
                  </div>
                ))}
              </>
            )}
          </div>

        </main>
      </div>

      {/* Hidden elements */}
      <video ref={videoRef} className="hidden" />
      <canvas ref={canvasRef} className="hidden" />
    </div>
  )
}
