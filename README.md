
## 🚀 Quick Start

### Prerequisites

- **Python 3.8+** (for backend)
- **Node.js 18+** (for frontend)
- **FFmpeg** (for video generation)
- **Anthropic API Key** or **OpenAI API Key**

### Installation

#### 1. Clone the repository

```bash
git clone <repository-url>
cd screen-to-song
```

#### 2. Set up Backend

```bash
cd backend
pip install -r requirements.txt

# Copy and configure environment variables
cp ../.env.example .env
# Edit .env and add your API keys
```

#### 3. Set up Frontend

```bash
cd frontend
npm install

# Create .env.local
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local
```

#### 4. Install FFmpeg

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**macOS:**
```bash
brew install ffmpeg
```

**Windows:**
Download from [ffmpeg.org](https://ffmpeg.org/download.html)

### Running the Application

#### Terminal 1 - Start Backend

```bash
cd backend
python main.py
```

Backend runs on `http://localhost:8000`

#### Terminal 2 - Start Frontend

```bash
cd frontend
npm run dev
```

Frontend runs on `http://localhost:3000`

### Usage

1. **Open** `http://localhost:3000` in your browser
2. **Click** "Start Capturing"
3. **Select** your screen or window to capture
4. **Watch** as the AI analyzes your activity and generates lyrics in real-time
5. **Export** lyrics or create a video when done

## 🎯 API Endpoints

### Backend API (`http://localhost:8000`)

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/analyze-frame` | POST | Analyze screen capture |
| `/api/generate-lyrics` | POST | Generate lyrics from context |
| `/api/lyrics-history` | GET | Get lyrics history |
| `/api/clear-cache` | POST | Clear cache |
| `/api/health` | GET | Health check |

### Example API Call

```python
import requests

# Analyze a frame
with open('screenshot.png', 'rb') as f:
    response = requests.post(
        'http://localhost:8000/api/analyze-frame',
        files={'file': f}
    )
    context = response.json()['context']
    print(context)
```

## 🛠️ Scripts

### Music Generator

Generate music metadata for scenes:

```bash
cd scripts
python music_generator.py
```

### Video Assembler

Create lyric videos:

```bash
cd scripts
python video_assembler.py
```

### Complete Pipeline

Run end-to-end demo:

```bash
cd scripts
python pipeline.py --demo
```

Process existing session:

```bash
python pipeline.py --session-file session.json --output-dir ./output
```

## 🎨 Customization

### Adding Music Genres

Edit `scripts/music_generator.py` and add to `MUSIC_LIBRARY`:

```python
MUSIC_LIBRARY = {
    "your-genre": {
        "loops": [
            {"id": "genre_1", "bpm": 120, "key": "C", "mood": "happy"}
        ],
        "description": "Your genre description"
    }
}
```

### Changing Color Schemes

Edit `scripts/video_assembler.py`:

```python
color_schemes = {
    "your-genre": ("#HEX1", "#HEX2")
}
```

### Customizing Lyrics Style

Modify the prompt in `backend/main.py` in the `generate_lyrics()` function.

## 📊 Project Structure

```
screen-to-song/
├── backend/              # FastAPI backend
│   ├── main.py          # Main API server
│   ├── requirements.txt
│   └── outputs/         # Generated files
├── frontend/            # Next.js frontend
│   ├── app/
│   │   ├── page.tsx    # Main UI
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── package.json
│   └── next.config.js
├── scripts/             # Utility scripts
│   ├── music_generator.py
│   ├── video_assembler.py
│   └── pipeline.py      # End-to-end pipeline
└── README.md
```

## 🎪 Hackathon Tips

### MVP Checklist (Day 1)

- [x] Screen capture working
- [x] Vision API integration
- [x] Basic lyric generation
- [x] Simple UI
- [x] Export functionality

### Stretch Goals (Day 2)

- [ ] Real music generation (MusicGen API)
- [ ] Beat-synced lyrics
- [ ] Multiple genre detection
- [ ] Social media export
- [ ] Real-time mode

### Demo Script

1. **Hook** (10s): "What if your screen had a soundtrack?"
2. **Demo** (60s): Show live capture → lyrics → video
3. **Use Cases** (20s): Coding, gaming, browsing
4. **Tech** (10s): Vision AI + LLMs + FFmpeg
5. **Close**: "Your digital life, now with a beat"

## 🔧 Troubleshooting

### Screen capture not working

- **Chrome**: Enable screen sharing permissions
- **Firefox**: Allow screen capture in browser settings
- **Safari**: Grant screen recording permission in System Preferences

### API errors

```bash
# Check if backend is running
curl http://localhost:8000/api/health

# Check API keys
cat backend/.env
```

### FFmpeg not found

```bash
# Verify installation
ffmpeg -version

# Install if missing (Ubuntu)
sudo apt-get install ffmpeg
```

### CORS errors

Make sure backend CORS is configured for your frontend URL in `main.py`:

```python
allow_origins=["http://localhost:3000"]
```

## 🎯 Performance Optimization

### Frame Analysis

- Adjust capture interval in `frontend/app/page.tsx`:
```typescript
intervalRef.current = setInterval(() => {
    captureAndAnalyze()
}, 5000) // Change to 3000 for more frequent captures
```

### Caching

- Frame hashing prevents redundant API calls
- Lyric history prevents repetition
- Clear cache with `/api/clear-cache` endpoint

## 🚢 Deployment

### Backend (Railway/Render)

```bash
# Install production dependencies
pip install gunicorn

# Run with gunicorn
gunicorn main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker
```

### Frontend (Vercel)

```bash
npm run build
# Deploy to Vercel
vercel deploy
```

## 📝 License

MIT License - feel free to use for hackathons and projects!

## 🙏 Acknowledgments

- **Anthropic Claude** - Vision and lyric generation
- **OpenAI GPT-4** - Alternative vision model
- **FFmpeg** - Video processing
- **Next.js** - Frontend framework
- **FastAPI** - Backend framework

## 🎵 Made with ❤️ for Hackathons

Built to help you create something amazing in 24 hours. Good luck! 🚀

---

**Questions?** Open an issue or reach out!

**Demo Video:** [Coming soon]
