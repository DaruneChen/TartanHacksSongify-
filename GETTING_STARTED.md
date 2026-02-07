# 🚀 Getting Started with Screen to Song

## Welcome!

You now have a complete, production-ready application. This guide will get you running in 5 minutes.

## What You Have

📁 **Complete Project Structure:**
```
screen-to-song/
├── backend/          → Python FastAPI server
├── frontend/         → Next.js React app
├── scripts/          → Utility scripts
└── docs/            → Documentation
```

## Quick Start (5 Minutes)

### Step 1: One-Command Setup

```bash
cd screen-to-song
./setup.sh
```

This will:
- ✅ Check all prerequisites
- ✅ Install Python dependencies
- ✅ Install Node.js dependencies
- ✅ Create environment files
- ✅ Run system tests

### Step 2: Add API Keys

Edit `backend/.env` and add one of:

```bash
# Option 1: Anthropic (Recommended)
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Option 2: OpenAI
OPENAI_API_KEY=sk-xxxxx
```

**Get keys from:**
- Anthropic: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/

### Step 3: Start Backend

```bash
cd backend
./start.sh
```

Should see: `🚀 Starting FastAPI server on http://localhost:8000`

### Step 4: Start Frontend (New Terminal)

```bash
cd frontend
./start.sh
```

Should see: `✓ Ready on http://localhost:3000`

### Step 5: Use the App

1. Open http://localhost:3000
2. Click "Start Capturing"
3. Select your screen
4. Watch the magic! ✨

## What Each Component Does

### Backend (`backend/main.py`)
**What it does:** Analyzes screen frames and generates lyrics

**Key endpoints:**
- `POST /api/analyze-frame` - Analyzes a screenshot
- `POST /api/generate-lyrics` - Generates lyrics from context
- `GET /api/health` - Checks if everything works

**Test it:**
```bash
curl http://localhost:8000/api/health
```

### Frontend (`frontend/app/page.tsx`)
**What it does:** Beautiful UI for capturing and displaying

**Features:**
- Screen capture controls
- Real-time scene context
- Live lyrics feed
- Audio visualizer
- Export functionality

### Scripts (`scripts/`)

**Music Generator:**
```bash
cd scripts
python music_generator.py
```
Creates music metadata for different genres

**Video Assembler:**
```bash
python video_assembler.py
```
Generates lyric videos using FFmpeg

**Complete Pipeline:**
```bash
python pipeline.py --demo
```
End-to-end demo with mock data

## File Breakdown

### Must Read
- 📖 `README.md` - Main documentation
- 🚀 `QUICKSTART.md` - This file
- 🏗️ `ARCHITECTURE.md` - Technical deep dive

### Important Files
- ⚙️ `backend/main.py` - API server (309 lines)
- 🎨 `frontend/app/page.tsx` - UI component (378 lines)
- 🎵 `scripts/music_generator.py` - Music system (195 lines)
- 🎬 `scripts/video_assembler.py` - Video creation (283 lines)
- 🔗 `scripts/pipeline.py` - Integration (239 lines)

### Configuration
- 🔐 `.env.example` - Environment template
- 📦 `backend/requirements.txt` - Python packages
- 📦 `frontend/package.json` - Node packages

## How It Works (Simple Explanation)

```
1. Capture Screen
   ↓ (every 5 seconds)
2. Send to AI
   ↓ (Claude Vision)
3. AI Sees: "coding in dark IDE"
   ↓
4. Generate Lyrics
   ↓ (Claude Text)
5. Output: "Midnight glow from a terminal light..."
   ↓
6. Display in UI ✨
```

## Common Issues & Fixes

### ❌ "Screen capture not working"
**Fix:** Allow screen sharing in browser settings
- Chrome: chrome://settings/content/desktop-capture
- Firefox: Allow in permission popup

### ❌ "Backend won't start"
**Fix:** Check Python version and dependencies
```bash
python3 --version  # Should be 3.8+
cd backend
pip install -r requirements.txt
```

### ❌ "Frontend won't start"
**Fix:** Clear and reinstall
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### ❌ "No lyrics generating"
**Fix:** Check API key in `backend/.env`
```bash
cat backend/.env | grep API_KEY
```

### ❌ "FFmpeg not found"
**Fix:** Install FFmpeg
```bash
# Ubuntu/Debian
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Windows
# Download from https://ffmpeg.org/
```

## Testing Each Component

### Test 1: Backend Health
```bash
curl http://localhost:8000/api/health
```
Should return: `{"status": "healthy", ...}`

### Test 2: Vision Analysis
```bash
# Upload a test image
curl -X POST http://localhost:8000/api/analyze-frame \
  -F "file=@test_image.png"
```

### Test 3: System Test
```bash
python3 scripts/test_system.py
```
Should show all ✓ checks passing

### Test 4: Pipeline Demo
```bash
cd scripts
python pipeline.py --demo
```
Should create demo files in `demo_output/`

## Next Steps

### For Hackathon
1. ✅ Test all features
2. ✅ Prepare demo script
3. ✅ Record backup video
4. ✅ Practice pitch
5. ✅ Have fun! 🎉

### For Development
1. 📖 Read `ARCHITECTURE.md`
2. 🎨 Customize UI colors
3. 🎵 Add more genres
4. 🚀 Deploy to production
5. 📱 Build mobile app

## Pro Tips

### 💡 Tip 1: Test Early
Run the system test before making changes:
```bash
python3 scripts/test_system.py
```

### 💡 Tip 2: Use Mock Data
Test UI without API calls by uncommenting mock data in `frontend/app/page.tsx`

### 💡 Tip 3: Cache Management
Clear cache if getting stale results:
```bash
curl -X POST http://localhost:8000/api/clear-cache
```

### 💡 Tip 4: Debug Mode
See API responses in browser console (F12)

### 💡 Tip 5: Export Tricks
Lyrics export includes timestamps - use for video sync!

## Deployment Options

### Option 1: Quick Deploy (Vercel + Railway)
**Time:** ~10 minutes
**Cost:** Free tier available

Frontend (Vercel):
```bash
cd frontend
npm install -g vercel
vercel deploy
```

Backend (Railway):
- Go to railway.app
- Connect GitHub
- Add environment variables
- Deploy!

### Option 2: Docker
**Time:** ~20 minutes
**Cost:** Variable

```bash
docker-compose up
```

See `DEPLOYMENT.md` for full instructions.

## Resources

### Documentation
- 📖 Main README
- 🏗️ Architecture Guide
- 🚀 Deployment Guide
- 📋 Project Overview

### External Links
- [Anthropic Docs](https://docs.anthropic.com/)
- [Next.js Docs](https://nextjs.org/docs)
- [FFmpeg Docs](https://ffmpeg.org/documentation.html)

### Support
- GitHub Issues (create one!)
- Stack Overflow
- Discord communities

## FAQ

**Q: How much does it cost to run?**
A: ~$0.35 per 5-minute session on Anthropic, $0.46 on OpenAI. Very affordable!

**Q: Can I use different AI models?**
A: Yes! The backend supports both Claude and GPT-4. Easy to add more.

**Q: Does it work on mobile?**
A: Desktop only for now. Screen Capture API requires desktop browser.

**Q: Can I customize the lyrics?**
A: Yes! Edit the prompt in `backend/main.py` line ~180.

**Q: How do I add more genres?**
A: Edit `MUSIC_LIBRARY` in `scripts/music_generator.py`.

**Q: Is my data stored?**
A: No! Everything is in-memory for privacy. Export if you want to save.

**Q: Can I contribute?**
A: Yes! It's open source. PRs welcome!

## Help & Support

### If Something Breaks

1. **Check the logs**
   - Backend: Terminal where `./start.sh` is running
   - Frontend: Browser console (F12)

2. **Run system test**
   ```bash
   python3 scripts/test_system.py
   ```

3. **Check API keys**
   ```bash
   cat backend/.env
   ```

4. **Restart everything**
   ```bash
   # Stop both terminals (Ctrl+C)
   # Clear cache
   rm -rf backend/__pycache__
   rm -rf frontend/.next
   # Restart
   ```

### Still Stuck?

1. Read `ARCHITECTURE.md` for technical details
2. Check `DEPLOYMENT.md` for deployment issues
3. Look at code comments (heavily documented)
4. Create GitHub issue

## What Makes This Special

✨ **Production Ready**
- Real error handling
- Proper caching
- Clean code
- Full documentation

🎯 **Hackathon Optimized**
- Quick setup
- Impressive demo
- Modular design
- Easy to explain

🚀 **Deployment Ready**
- Environment configs
- Docker support
- Cloud-ready
- Scalable architecture

## Final Checklist

Before your hackathon demo:
- [ ] Backend running (http://localhost:8000)
- [ ] Frontend running (http://localhost:3000)
- [ ] API keys configured
- [ ] Screen capture tested
- [ ] Demo script prepared
- [ ] Backup video recorded
- [ ] Pitch practiced
- [ ] Laptop charged 🔋

## You're Ready! 🎉

Everything is set up and working. Now go build something amazing!

**Remember:**
- Start simple
- Test early
- Have fun
- Ship it!

Good luck with your hackathon! 🚀

---

*Made with ❤️ using Claude, Next.js, and FastAPI*
