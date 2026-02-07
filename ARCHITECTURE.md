# Screen to Song - Technical Architecture

## System Overview

Screen to Song is a full-stack application that transforms screen activity into personalized music videos through AI-powered analysis and content generation.

## Technology Stack

### Frontend
- **Framework**: Next.js 14 (React)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **APIs**: Screen Capture API, Fetch API
- **State Management**: React Hooks

### Backend
- **Framework**: FastAPI (Python)
- **AI Models**: 
  - Claude Sonnet 4 (Vision + Text)
  - GPT-4o (Alternative)
- **Image Processing**: Pillow, imagehash
- **API Libraries**: Anthropic SDK, OpenAI SDK

### Video & Music Processing
- **Video Generation**: FFmpeg
- **Music Metadata**: Custom Python module
- **Format Support**: MP4, SRT, JSON

## Data Flow

```
┌─────────────────────────────────────────────────────────────┐
│                        FRONTEND                              │
│  (Next.js + React + TypeScript)                             │
│                                                              │
│  1. Screen Capture (Browser API)                            │
│     - getDisplayMedia()                                      │
│     - Canvas API for frame extraction                        │
│                                                              │
│  2. Frame Sampling                                           │
│     - Capture every 5 seconds                               │
│     - Convert to PNG blob                                   │
│                                                              │
│  3. UI Components                                           │
│     - Control panel                                         │
│     - Scene context display                                 │
│     - Live lyrics feed                                      │
│     - Audio visualizer                                      │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP POST /api/analyze-frame
                       │ (multipart/form-data)
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                        BACKEND                               │
│  (FastAPI + Python)                                         │
│                                                              │
│  4. Frame Analysis                                          │
│     - Perceptual hashing (dhash)                            │
│     - Cache check (avoid duplicate analysis)                │
│     - Base64 encoding                                       │
│                                                              │
│  5. Vision AI Processing                                    │
│     - Claude Vision or GPT-4o                               │
│     - Extract: mood, activity, objects, genre, energy       │
│     - Return structured JSON                                │
│                                                              │
│  6. Lyric Generation                                        │
│     - Context-aware prompting                               │
│     - Claude Sonnet 4 text generation                       │
│     - Avoid repetition using history                        │
│     - Genre-specific styling                                │
│                                                              │
│  7. Response Caching                                        │
│     - In-memory frame cache                                 │
│     - Lyric history management                              │
└──────────────────────┬──────────────────────────────────────┘
                       │ JSON Response
                       │ { context, lyrics, cached }
                       ▼
┌─────────────────────────────────────────────────────────────┐
│                   OFFLINE PROCESSING                         │
│  (Python Scripts)                                           │
│                                                              │
│  8. Music Generation                                        │
│     - Genre-based loop selection                            │
│     - BPM and key matching                                  │
│     - Crossfade planning                                    │
│     - Metadata export (JSON)                                │
│                                                              │
│  9. Video Assembly                                          │
│     - FFmpeg pipeline                                       │
│     - Gradient background generation                        │
│     - SRT subtitle creation                                 │
│     - Overlay lyrics with timing                            │
│     - Final MP4 export                                      │
└─────────────────────────────────────────────────────────────┘
```

## Component Architecture

### 1. Frontend Components

#### Main Page (`app/page.tsx`)
- Screen capture management
- Frame capture and upload
- Real-time UI updates
- State management

**Key Functions:**
```typescript
startCapture()       // Initialize screen capture
stopCapture()        // End capture session
captureAndAnalyze()  // Grab frame and send to API
generateLyrics()     // Request lyric generation
exportLyrics()       // Download lyrics as text
```

**State:**
```typescript
- isCapturing: boolean
- currentContext: SceneContext | null
- allLyrics: LyricSet[]
- status: string
- error: string | null
```

### 2. Backend API

#### Main Server (`backend/main.py`)

**Endpoints:**
- `POST /api/analyze-frame` - Vision analysis
- `POST /api/generate-lyrics` - Lyric generation
- `GET /api/lyrics-history` - Retrieve history
- `POST /api/clear-cache` - Reset state
- `GET /api/health` - Health check

**Core Functions:**
```python
analyze_with_claude()    # Claude Vision analysis
analyze_with_gpt4()      # GPT-4 Vision analysis
generate_lyrics()        # Claude text generation
should_analyze_frame()   # Cache decision logic
get_image_hash()         # Perceptual hashing
```

**Data Models:**
```python
SceneContext:
  - mood: str
  - activity: str
  - objects: List[str]
  - suggested_genre: str
  - energy_level: int (1-5)
  - description: str

LyricResponse:
  - lyrics: List[str]
  - timestamp: float
  - genre: str
```

### 3. Processing Scripts

#### Music Generator (`scripts/music_generator.py`)

**Purpose:** Generate music metadata and loop selection

**Key Classes:**
```python
class MusicGenerator:
  - select_loop()                 # Choose appropriate loop
  - generate_music_metadata()     # Create metadata
  - create_music_sequence()       # Multi-scene sequences
  - export_metadata()             # Save to JSON
```

**Music Library Structure:**
```python
MUSIC_LIBRARY = {
  "genre": {
    "loops": [
      {
        "id": "unique_id",
        "bpm": 120,
        "key": "C",
        "mood": "happy"
      }
    ],
    "description": "Genre description"
  }
}
```

#### Video Assembler (`scripts/video_assembler.py`)

**Purpose:** Create lyric videos using FFmpeg

**Key Classes:**
```python
class VideoAssembler:
  - create_lyric_subtitle_file()   # Generate SRT
  - create_gradient_background()   # Background video
  - add_lyrics_to_video()          # Overlay subtitles
  - create_lyric_video()           # Complete pipeline
```

**FFmpeg Pipeline:**
```
1. Color background → color filter
2. Gradient effect → geq filter
3. Subtitle overlay → subtitles filter
4. H.264 encoding → libx264 codec
5. MP4 container → yuv420p pixel format
```

#### Complete Pipeline (`scripts/pipeline.py`)

**Purpose:** End-to-end integration

**Key Classes:**
```python
class ScreenToSongPipeline:
  - add_scene()           # Add analyzed scene
  - generate_music()      # Create music sequence
  - create_video()        # Generate final video
  - export_session_data() # Save session JSON
  - print_summary()       # Display stats
```

## Performance Optimizations

### 1. Frame Analysis Caching

**Problem:** Redundant API calls for similar frames
**Solution:** Perceptual hashing with dhash

```python
# Only analyze if frame changed significantly
if imagehash.dhash(current) != imagehash.dhash(previous):
    analyze_frame()
```

**Benefit:** ~70% reduction in API calls

### 2. Lyric Deduplication

**Problem:** Repetitive lyrics
**Solution:** Context-aware history

```python
# Include previous lyrics in prompt
previous_text = "\n".join(lyric_history[-10:])
prompt = f"... avoid repeating: {previous_text}"
```

**Benefit:** Better lyric variety

### 3. Batch Processing

**Problem:** Sequential processing is slow
**Solution:** Pipeline architecture

```
Frame → [Queue] → Batch Analysis → [Queue] → Lyric Gen
```

**Benefit:** Can process multiple scenes concurrently

## Security Considerations

### API Key Management
- Environment variables only
- Never commit to git
- Separate dev/prod keys

### CORS Configuration
```python
allow_origins=["http://localhost:3000"]  # Dev
allow_origins=["https://yourdomain.com"] # Prod
```

### Input Validation
- File size limits (10MB max)
- Image format validation
- Rate limiting on endpoints

## Scalability

### Current Limitations
- In-memory caching (not distributed)
- Single-instance backend
- No persistent storage

### Scale-Up Path
1. **Add Redis** for distributed caching
2. **Add PostgreSQL** for session persistence
3. **Add Queue System** (Celery + RabbitMQ)
4. **Horizontal Scaling** with load balancer
5. **CDN** for video delivery

## Deployment Architecture

### Development
```
Frontend: http://localhost:3000
Backend:  http://localhost:8000
```

### Production (Recommended)

**Frontend:**
- Vercel / Netlify
- Static site generation
- CDN distribution

**Backend:**
- Railway / Render / Fly.io
- Auto-scaling workers
- Environment variables

**Storage:**
- AWS S3 for videos
- CloudFront for delivery

## Monitoring & Observability

### Metrics to Track
- API response times
- Frame analysis duration
- Lyric generation success rate
- Cache hit ratio
- Error rates by endpoint

### Logging
```python
# Structured logging
logger.info("Frame analyzed", {
    "hash": frame_hash,
    "cached": is_cached,
    "genre": context.genre,
    "duration_ms": duration
})
```

## Future Enhancements

### Short-term (Hackathon++)
- [ ] Real music generation (MusicGen API)
- [ ] Beat-synced lyrics
- [ ] Social media export (TikTok format)
- [ ] Mobile app (React Native)

### Long-term
- [ ] Multi-user sessions
- [ ] Collaborative playlists
- [ ] Live streaming mode
- [ ] Professional music library
- [ ] AI voice synthesis for singing
- [ ] 3D visualizations

## Development Guidelines

### Code Style
- Python: PEP 8
- TypeScript: Airbnb style guide
- Auto-format with Black/Prettier

### Testing
```bash
# Unit tests
pytest backend/tests/

# Integration tests
npm test

# E2E tests
playwright test
```

### Git Workflow
```
main → dev → feature/xyz
```

## License & Attribution

**License:** MIT

**Core Dependencies:**
- Anthropic Claude API
- OpenAI GPT-4 API
- FFmpeg (GPL/LGPL)
- Next.js (MIT)
- FastAPI (MIT)

---

**Last Updated:** 2024
**Architecture Version:** 1.0
