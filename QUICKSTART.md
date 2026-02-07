# 🚀 Quick Start Guide - Screen to Song

## 5-Minute Setup

### 1. Prerequisites Check

Run the system test:
```bash
cd scripts
python3 test_system.py
```

This will verify you have:
- Python 3.8+
- Node.js 18+
- FFmpeg
- Required packages

### 2. Configure API Keys

```bash
# Copy environment template
cp .env.example backend/.env

# Edit and add your API key (choose one)
# Get Anthropic key: https://console.anthropic.com/
# Get OpenAI key: https://platform.openai.com/
nano backend/.env
```

Add either:
```
ANTHROPIC_API_KEY=sk-ant-xxxxx
```
or
```
OPENAI_API_KEY=sk-xxxxx
```

### 3. Install Dependencies

**Backend:**
```bash
cd backend
pip install -r requirements.txt
```

**Frontend:**
```bash
cd frontend
npm install
```

### 4. Start the Application

**Terminal 1 - Backend:**
```bash
cd backend
./start.sh
```

**Terminal 2 - Frontend:**
```bash
cd frontend
./start.sh
```

### 5. Use the App

1. Open http://localhost:3000
2. Click "Start Capturing"
3. Select your screen/window
4. Watch the magic happen! ✨

## 🎯 What You'll See

1. **Screen Analysis**: AI detects your activity (coding, gaming, browsing)
2. **Real-time Lyrics**: Custom lyrics generated every 5 seconds
3. **Genre Matching**: Music style adapts to your activity
4. **Live Dashboard**: Beautiful UI showing context and lyrics

## 🎬 Creating Your First Video

1. Capture for 30-60 seconds
2. Click "Stop Capturing"
3. Click "Export" to download lyrics
4. Run video generator:
   ```bash
   cd scripts
   python pipeline.py --demo
   ```

## 📊 Testing Components Individually

**Test Vision Analysis:**
```bash
cd backend
python main.py
# Then in another terminal:
curl -X POST http://localhost:8000/api/health
```

**Test Music Generator:**
```bash
cd scripts
python music_generator.py
```

**Test Video Assembler:**
```bash
cd scripts
python video_assembler.py
```

**Test Complete Pipeline:**
```bash
cd scripts
python pipeline.py --demo
```

## 🐛 Troubleshooting

### Backend won't start
```bash
# Check Python packages
pip list | grep fastapi

# Reinstall if needed
pip install -r requirements.txt --force-reinstall
```

### Frontend won't start
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

### Screen capture not working
- **Chrome**: chrome://settings/content/desktop-capture
- **Firefox**: Allow in permission popup
- **Safari**: System Preferences → Security → Screen Recording

### No lyrics generating
- Check API key in `backend/.env`
- Check backend logs for errors
- Try the health endpoint: http://localhost:8000/api/health

### FFmpeg errors
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install ffmpeg

# macOS
brew install ffmpeg

# Verify
ffmpeg -version
```

## 🎪 Hackathon Tips

### 1. Start Simple
- Get screen capture working first
- Add AI vision second
- Polish UI last

### 2. Use Mock Data
```javascript
// In frontend, test with mock data:
const mockContext = {
  mood: "focused",
  activity: "coding",
  genre: "lo-fi"
}
```

### 3. Prepare Demo Video
Record a 60-second demo showing:
1. Starting capture
2. Switching activities (code → game → browse)
3. Generated lyrics
4. Final video

### 4. Have a Backup
If APIs fail during demo:
- Use pre-generated lyrics
- Show static examples
- Walk through the concept

## 🔗 Useful URLs

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/health

## 📱 Next Steps

Once basic app works:
1. ✅ Add more genres
2. ✅ Improve lyric quality
3. ✅ Add music generation
4. ✅ Create better visualizations
5. ✅ Deploy to cloud

## 🎉 You're Ready!

Everything should now be working. Start capturing and creating your soundtrack!

**Need help?** Check the main README.md or open an issue.

---

Happy hacking! 🚀
