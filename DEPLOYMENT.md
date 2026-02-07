# 🚀 Deployment & Hackathon Checklist

## Pre-Hackathon Checklist

### ✅ Development Environment
- [ ] Python 3.8+ installed
- [ ] Node.js 18+ installed
- [ ] FFmpeg installed
- [ ] Git configured
- [ ] Code editor ready (VS Code recommended)

### ✅ API Keys Obtained
- [ ] Anthropic API key (https://console.anthropic.com/)
  - Or OpenAI API key (https://platform.openai.com/)
- [ ] Keys added to `backend/.env`
- [ ] Tested with health endpoint

### ✅ Local Testing
- [ ] Backend starts successfully (`./backend/start.sh`)
- [ ] Frontend starts successfully (`./frontend/start.sh`)
- [ ] Screen capture works in browser
- [ ] Vision API returns results
- [ ] Lyrics generation works
- [ ] Export functionality works

### ✅ Demo Preparation
- [ ] Record demo video (60-90 seconds)
- [ ] Prepare presentation slides
- [ ] Test on presentation laptop
- [ ] Backup demo data ready

## Hackathon Day Checklist

### Hour 0-2: Setup
- [ ] Clone repo on hackathon machine
- [ ] Run `./setup.sh`
- [ ] Test all components
- [ ] Fix any environment issues

### Hour 2-6: Core Features
- [ ] Screen capture working
- [ ] Basic UI functional
- [ ] Vision API integrated
- [ ] Lyric generation working

### Hour 6-12: Polish
- [ ] Improve UI/UX
- [ ] Add more genres
- [ ] Error handling
- [ ] Loading states

### Hour 12-18: Advanced Features
- [ ] Video generation
- [ ] Music metadata
- [ ] Export options
- [ ] Easter eggs

### Hour 18-22: Final Polish
- [ ] Test all features
- [ ] Fix critical bugs
- [ ] Prepare demo
- [ ] Create pitch

### Hour 22-24: Presentation
- [ ] Finalize demo
- [ ] Practice pitch
- [ ] Deploy (optional)
- [ ] Submit project

## Deployment Guide

### Option 1: Vercel (Frontend) + Railway (Backend)

#### Frontend (Vercel)
```bash
cd frontend
npm install -g vercel
vercel login
vercel deploy
```

#### Backend (Railway)
1. Create account at https://railway.app/
2. New Project → Deploy from GitHub
3. Add environment variables:
   - `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`
4. Deploy

**Update Frontend:**
```env
# frontend/.env.local
NEXT_PUBLIC_API_URL=https://your-backend.railway.app
```

### Option 2: Single Server (DigitalOcean/AWS)

#### Setup Script:
```bash
# Install dependencies
sudo apt update
sudo apt install python3 python3-pip nodejs npm ffmpeg nginx

# Clone and setup
git clone <your-repo>
cd screen-to-song
./setup.sh

# Start with PM2
npm install -g pm2

# Backend
cd backend
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name backend

# Frontend
cd ../frontend
npm run build
pm2 start "npm start" --name frontend

# Configure Nginx
sudo nano /etc/nginx/sites-available/screen-to-song
```

**Nginx Config:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
    }

    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

### Option 3: Docker (Advanced)

**Dockerfile (Backend):**
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

**docker-compose.yml:**
```yaml
version: '3.8'
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - ANTHROPIC_API_KEY=${ANTHROPIC_API_KEY}
  
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    environment:
      - NEXT_PUBLIC_API_URL=http://backend:8000
```

## Demo Best Practices

### 1. Prepare Fallbacks
- Pre-recorded demo video
- Screenshots of features
- Backup API keys
- Localhost demo if deployment fails

### 2. Demo Script (90 seconds)
```
0:00-0:10  Hook: "What if your screen had a soundtrack?"
0:10-0:30  Problem: Digital life is passive
0:30-1:00  Demo: Live screen capture → lyrics
1:00-1:20  Features: Multiple genres, real-time
1:20-1:30  Call to action: Try it yourself!
```

### 3. Common Demo Pitfalls
- ❌ Starting with long explanation
- ❌ Live coding during demo
- ❌ Apologizing for features
- ✅ Start with impact
- ✅ Show, don't tell
- ✅ Focus on working features

## Judging Criteria Prep

### Technical Complexity
**What to highlight:**
- Vision AI integration
- Real-time processing
- Multi-component architecture
- Efficient caching

**What to show:**
- Code quality
- System architecture diagram
- Performance optimizations

### Creativity
**What to highlight:**
- Novel use of screen capture
- Personal soundtrack concept
- Genre adaptation

**What to show:**
- Different activity detection
- Lyric quality
- Visual design

### Usefulness
**What to highlight:**
- Productivity tracking
- Content creation
- Social media
- Personal journaling

**What to show:**
- Real use cases
- Export features
- Sharing capabilities

### Polish
**What to highlight:**
- Clean UI
- Smooth UX
- Error handling
- Loading states

**What to show:**
- Live demo
- Responsive design
- Professional aesthetics

## Post-Hackathon

### If You Win
- [ ] Add to portfolio
- [ ] LinkedIn post
- [ ] GitHub showcase
- [ ] Blog post about building it

### If You Don't Win
- [ ] Still add to portfolio
- [ ] Share on social media
- [ ] Get user feedback
- [ ] Plan v2 features

### Next Steps
- [ ] Add tests
- [ ] Improve error handling
- [ ] Real music generation
- [ ] Mobile app version
- [ ] Open source it

## Resources

### Documentation
- [Anthropic Docs](https://docs.anthropic.com/)
- [OpenAI Docs](https://platform.openai.com/docs)
- [FFmpeg Docs](https://ffmpeg.org/documentation.html)
- [Next.js Docs](https://nextjs.org/docs)

### Inspiration
- Spotify Wrapped
- Year in Review apps
- Music visualization tools
- AI art generators

### Support
- GitHub Issues
- Discord communities
- Stack Overflow
- Claude.ai (for debugging!)

---

## 🎯 Final Reminders

1. **Start Simple**: Get MVP working first
2. **Test Early**: Don't wait until hour 23
3. **Document**: README matters for judges
4. **Have Fun**: Enjoy the process!

Good luck! 🚀
