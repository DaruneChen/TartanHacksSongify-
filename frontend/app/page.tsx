'use client'

import { useState, useRef, useEffect } from 'react'
import { Play, Square, Music, Sparkles, Download, Trash2, Zap, TrendingUp, Settings, Mic2, Activity, Volume2, Loader2, Video, Film } from 'lucide-react'
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
  const [isGenerating, setIsGenerating] = useState(false)
  const [audioWave, setAudioWave] = useState<number[]>(Array(20).fill(0))
  const [singingIndex, setSingingIndex] = useState<number | null>(null)
  const [audioUrl, setAudioUrl] = useState<string | null>(null)
  const [isGeneratingVideo, setIsGeneratingVideo] = useState(false)

  const streamRef = useRef<MediaStream | null>(null)
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const intervalRef = useRef<NodeJS.Timeout | null>(null)

  useEffect(() => {
    setLyricCount(allLyrics.flatMap(set => set.lyrics).length)
  }, [allLyrics])

  // Animate audio wave
  useEffect(() => {
    if (isCapturing || isGenerating) {
      const interval = setInterval(() => {
        setAudioWave(prev => prev.map(() => Math.random() * 100))
      }, 100)
      return () => clearInterval(interval)
    } else {
      setAudioWave(Array(20).fill(0))
    }
  }, [isCapturing, isGenerating])

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
      setIsGenerating(true)
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
    } finally {
      setIsGenerating(false)
    }
  }

  const generateLyrics = async (context: SceneContext) => {
    try {
      setStatus('Writing lyrics...')
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

  const singLyrics = async (lyrics: string[], index: number, genre: string) => {
    try {
      setSingingIndex(index)
      if (audioRef.current) {
        audioRef.current.pause()
      }
      if (audioUrl) {
        URL.revokeObjectURL(audioUrl)
      }

      const mood = currentContext?.mood || 'neutral'
      const response = await axios.post(`${API_URL}/api/sing`, { lyrics, genre, mood }, {
        responseType: 'blob',
        timeout: 120000,  // Music generation can take a while
      })

      const url = URL.createObjectURL(response.data)
      setAudioUrl(url)
      const audio = new Audio(url)
      audioRef.current = audio
      audio.onended = () => setSingingIndex(null)
      await audio.play()
    } catch (err: any) {
      console.error('Sing error:', err)
      setError('Failed to generate audio')
      setSingingIndex(null)
    }
  }

  const generateVideo = async () => {
    if (allLyrics.length === 0) return
    try {
      setIsGeneratingVideo(true)
      setError(null)

      const lyricsSets = allLyrics.map(set => set.lyrics)
      const genre = allLyrics[0]?.genre || 'pop'
      const mood = currentContext?.mood || 'neutral'

      const response = await axios.post(`${API_URL}/api/generate-video`, {
        lyrics_sets: lyricsSets,
        genre,
        mood,
      }, {
        responseType: 'blob',
        timeout: 300000, // 5 min - video generation takes time
      })

      const url = URL.createObjectURL(response.data)
      const a = document.createElement('a')
      a.href = url
      a.download = `screen-to-song-${Date.now()}.mp4`
      a.click()
      URL.revokeObjectURL(url)
    } catch (err: any) {
      console.error('Video generation error:', err)
      setError('Failed to generate video')
    } finally {
      setIsGeneratingVideo(false)
    }
  }

  useEffect(() => {
    return () => stopCapture()
  }, [])

  return (
    <div className="min-h-screen bg-[#2a2d42] text-white overflow-hidden relative">
      {/* Animated background particles */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-white/20 rounded-full animate-float"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 5}s`,
              animationDuration: `${5 + Math.random() * 10}s`,
            }}
          />
        ))}
      </div>

      <div className="max-w-[420px] mx-auto min-h-screen bg-[#2a2d42] p-4 pt-6 relative z-10">
        
        {/* Header with slide-in animation */}
        <div className="flex items-center justify-between mb-6 animate-slide-down">
          <button className="w-10 h-10 rounded-full bg-[#1f2233] flex items-center justify-center hover:bg-[#252839] transition-all hover:scale-110 active:scale-95">
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M12 5L7 10L12 15" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-purple-500 flex items-center justify-center shadow-lg shadow-blue-500/30 animate-pulse-glow">
            <Play className="w-5 h-5 text-white" fill="white" />
          </div>
        </div>

        {/* Main Balance Card with enhanced animations */}
        <div className="relative mb-4 rounded-[32px] overflow-hidden animate-scale-in">
          {/* Animated mesh gradient */}
          <div className="absolute inset-0 animate-gradient-shift">
            <div className="absolute inset-0 bg-gradient-to-br from-[#ff6b9d] via-[#ff8a80] to-[#4ade80] opacity-90"></div>
            <div className="absolute inset-0 bg-gradient-to-tl from-[#60efff] via-transparent to-transparent opacity-60"></div>
            <div className="absolute inset-0 bg-gradient-to-br from-[#a78bfa] via-transparent to-transparent opacity-40"></div>
          </div>
          
          {/* Animated sparkles */}
          {isGenerating && (
            <div className="absolute inset-0">
              {[...Array(10)].map((_, i) => (
                <div
                  key={i}
                  className="absolute animate-sparkle"
                  style={{
                    left: `${Math.random() * 100}%`,
                    top: `${Math.random() * 100}%`,
                    animationDelay: `${Math.random() * 2}s`,
                  }}
                >
                  <Sparkles className="w-3 h-3 text-white" />
                </div>
              ))}
            </div>
          )}
          
          <div className="relative backdrop-blur-sm bg-black/20 p-6">
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-white/80 animate-fade-in">Screen.song</span>
              <button className="w-8 h-8 rounded-full bg-white/20 backdrop-blur-sm flex items-center justify-center hover:bg-white/30 transition-all hover:rotate-90 duration-300">
                <Settings className="w-4 h-4 text-white" />
              </button>
            </div>
            
            <div className="mb-6">
              <p className="text-sm text-white/70 mb-1">Balance</p>
              <div className="flex items-baseline gap-2">
                <span className="text-6xl font-bold text-white tracking-tight animate-count-up">{lyricCount}</span>
                <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center animate-bounce-slow">
                  <span className="text-lg font-bold text-white">L</span>
                </div>
              </div>
            </div>

            {/* Audio wave visualization */}
            <div className="flex items-end justify-center gap-1 h-12 mb-4">
              {audioWave.map((height, i) => (
                <div
                  key={i}
                  className="w-1 bg-white/40 rounded-full transition-all duration-100"
                  style={{ height: `${Math.max(20, height)}%` }}
                />
              ))}
            </div>

            <div className="flex gap-3">
              <button
                onClick={isCapturing ? stopCapture : startCapture}
                className={`flex-1 rounded-full py-3 px-4 flex items-center justify-center gap-2 text-white text-sm font-medium transition-all transform hover:scale-105 active:scale-95 ${
                  isCapturing 
                    ? 'bg-red-500/40 backdrop-blur-sm hover:bg-red-500/60' 
                    : 'bg-black/40 backdrop-blur-sm hover:bg-black/60'
                }`}
              >
                {isCapturing ? (
                  <>
                    <Square className="w-4 h-4 animate-pulse" />
                    Stop capture
                  </>
                ) : (
                  <>
                    <Zap className="w-4 h-4" />
                    Start capture
                  </>
                )}
              </button>
              <button
                onClick={exportLyrics}
                disabled={allLyrics.length === 0}
                className="flex-1 bg-gradient-to-r from-blue-500 to-purple-500 rounded-full py-3 px-4 flex items-center justify-center gap-2 text-white text-sm font-semibold disabled:opacity-50 shadow-lg shadow-blue-500/30 hover:shadow-blue-500/50 transition-all transform hover:scale-105 active:scale-95"
              >
                <Download className="w-4 h-4" />
                Export
              </button>
            </div>
            <div className="flex gap-3 mt-3">
              <button
                onClick={generateVideo}
                disabled={allLyrics.length === 0 || isGeneratingVideo}
                className="flex-1 bg-gradient-to-r from-pink-500 to-orange-500 rounded-full py-3 px-4 flex items-center justify-center gap-2 text-white text-sm font-semibold disabled:opacity-50 shadow-lg shadow-pink-500/30 hover:shadow-pink-500/50 transition-all transform hover:scale-105 active:scale-95"
              >
                {isGeneratingVideo ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin" />
                    Creating video...
                  </>
                ) : (
                  <>
                    <Film className="w-4 h-4" />
                    Create Video
                  </>
                )}
              </button>
            </div>
          </div>
        </div>

        {/* Current context card with slide animation */}
        {currentContext && (
          <div className="bg-[#1f2233] rounded-[28px] p-4 mb-4 animate-slide-up hover:bg-[#252839] transition-colors">
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-pink-400 to-purple-500 flex items-center justify-center flex-shrink-0 animate-pulse-glow">
                <Activity className="w-5 h-5 text-white" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-start justify-between gap-2 mb-1">
                  <div className="flex items-center gap-2">
                    <span className="text-purple-400 text-sm font-medium animate-fade-in">+{currentContext.energy_level}</span>
                    <div className="w-5 h-5 rounded-full bg-gradient-to-br from-blue-400 to-blue-600 flex items-center justify-center animate-spin-slow">
                      <span className="text-[10px] font-bold text-white">L</span>
                    </div>
                  </div>
                  <span className={`px-2.5 py-0.5 rounded-full text-white text-xs font-medium animate-pulse ${
                    isCapturing ? 'bg-green-500' : 'bg-orange-500'
                  }`}>
                    {isCapturing ? 'Live' : 'Ready'}
                  </span>
                </div>
                <h3 className="text-white font-medium text-base mb-1 animate-fade-in">
                  {currentContext.activity.charAt(0).toUpperCase() + currentContext.activity.slice(1)} detected
                </h3>
                <p className="text-gray-400 text-sm leading-relaxed animate-fade-in-delay">
                  {currentContext.description}
                </p>
                
                {/* Genre badge with animation */}
                <div className="mt-2 flex items-center gap-2">
                  <Mic2 className="w-3 h-3 text-purple-400" />
                  <span className="text-xs text-purple-400 font-medium animate-fade-in-delay">
                    {currentContext.suggested_genre}
                  </span>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Lyrics with staggered animations */}
        {allLyrics.slice().reverse().map((set, index) => (
          <div 
            key={index} 
            className="bg-[#1f2233] rounded-[28px] p-4 mb-4 hover:bg-[#252839] transition-all transform hover:scale-[1.02] hover:shadow-lg hover:shadow-purple-500/20"
            style={{
              animation: `slideUp 0.5s ease-out ${index * 0.1}s both`
            }}
          >
            <div className="flex items-start gap-3">
              <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-purple-400 to-pink-500 flex items-center justify-center flex-shrink-0 animate-pulse-glow">
                <Sparkles className="w-5 h-5 text-white animate-sparkle-rotate" />
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
                    <p
                      key={i}
                      className="text-gray-400 text-sm leading-relaxed animate-fade-in"
                      style={{ animationDelay: `${i * 0.1}s` }}
                    >
                      {line}
                    </p>
                  ))}
                </div>
                <button
                  onClick={() => singLyrics(set.lyrics, allLyrics.length - 1 - index, set.genre)}
                  disabled={singingIndex !== null}
                  className="mt-3 flex items-center gap-1.5 text-xs text-purple-400 hover:text-purple-300 transition-colors disabled:opacity-50"
                >
                  {singingIndex === allLyrics.length - 1 - index ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin" />
                      Singing...
                    </>
                  ) : (
                    <>
                      <Volume2 className="w-3.5 h-3.5" />
                      Sing it
                    </>
                  )}
                </button>
              </div>
            </div>
          </div>
        ))}

        {/* Enhanced empty state */}
        {allLyrics.length === 0 && !currentContext && (
          <div className="bg-[#1f2233] rounded-[28px] p-8 text-center animate-scale-in">
            <div className="relative w-20 h-20 mx-auto mb-4">
              <div className="absolute inset-0 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-full animate-ping"></div>
              <div className="relative w-20 h-20 rounded-full bg-gradient-to-br from-purple-500/20 to-pink-500/20 flex items-center justify-center">
                <Music className="w-10 h-10 text-purple-400 opacity-50 animate-pulse" />
              </div>
            </div>
            <h3 className="text-white font-medium text-base mb-1">No lyrics yet</h3>
            <p className="text-gray-400 text-sm">
              Start capturing to generate your personalized soundtrack
            </p>
          </div>
        )}

        {/* Floating status indicator */}
        {(isCapturing || isGenerating) && (
          <div className="fixed bottom-6 left-1/2 -translate-x-1/2 bg-black/80 backdrop-blur-xl rounded-full px-4 py-2 flex items-center gap-2 animate-slide-up shadow-lg shadow-black/50">
            <div className="relative">
              <div className="w-2 h-2 rounded-full bg-green-400 animate-pulse"></div>
              <div className="absolute inset-0 w-2 h-2 rounded-full bg-green-400 animate-ping"></div>
            </div>
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
