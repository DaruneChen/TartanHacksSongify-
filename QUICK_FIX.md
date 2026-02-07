# 🚀 Quick Start - Screen to Song

## You're Seeing Import Errors?

**You're in the wrong directory!**

The project I built for you is called `screen-to-song` and is in the folder you downloaded.

## Correct Setup (3 Steps)

### 1️⃣ Navigate to the Project

```bash
# Find where you extracted the project
# It should be named: screen-to-song

cd ~/Desktop/screen-to-song
# or
cd ~/Downloads/screen-to-song
```

### 2️⃣ Run Setup

```bash
./setup.sh
```

This will:
- ✅ Install all dependencies
- ✅ Create virtual environment
- ✅ Set up .env file

### 3️⃣ Add API Key

Edit `backend/.env`:

```bash
# Use Anthropic (recommended)
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxx

# OR use OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxxx
```

Get keys:
- Anthropic: https://console.anthropic.com/
- OpenAI: https://platform.openai.com/

### 4️⃣ Start Backend

```bash
cd backend
./start.sh
```

Should see:
```
✓ Python detected
✓ Virtual environment activated
🚀 Starting FastAPI server on http://localhost:8000
```

### 5️⃣ Start Frontend (New Terminal)

```bash
cd frontend
./start.sh
```

Should see:
```
✓ Node detected
🚀 Starting Next.js
Ready on http://localhost:3000
```

## Common Errors & Fixes

### ❌ "cannot import 'generate' from 'elevenlabs'"
**Problem:** You're running the wrong backend file
**Fix:** Use the `screen-to-song/backend/main.py` file

### ❌ "No such file or directory"
**Problem:** Wrong directory
**Fix:** `cd` to the correct `screen-to-song` folder

### ❌ "ANTHROPIC_API_KEY not configured"
**Problem:** Missing API key
**Fix:** Add key to `backend/.env`

### ❌ "ModuleNotFoundError: No module named 'fastapi'"
**Problem:** Dependencies not installed
**Fix:** 
```bash
cd backend
pip install -r requirements.txt
```

## What The Backend DOES Use

- ✅ FastAPI (web server)
- ✅ Anthropic Claude (vision + text)
- ✅ OpenAI GPT-4 (alternative)
- ✅ Pillow (image processing)
- ✅ imagehash (caching)

## What The Backend DOES NOT Use

- ❌ elevenlabs (not included)
- ❌ singing voice generation
- ❌ actual music generation

These were intentionally excluded to keep the demo fast and simple.

## File Structure

```
screen-to-song/          ← YOU SHOULD BE HERE
├── backend/
│   ├── main.py         ← CORRECT BACKEND
│   ├── requirements.txt
│   ├── start.sh
│   └── .env            ← ADD YOUR API KEY HERE
├── frontend/
│   ├── app/
│   ├── start.sh
│   └── package.json
├── setup.sh            ← RUN THIS FIRST
└── README.md
```

## If You're In `/Desktop/song/Backend`

That's a DIFFERENT project! Either:

1. **Switch to screen-to-song** (recommended)
2. **Remove elevenlabs from your song/Backend/main.py**
3. **Install elevenlabs:** `pip install elevenlabs`

## Still Stuck?

Run the system test:
```bash
cd screen-to-song
python3 scripts/test_system.py
```

This will tell you exactly what's wrong.

---

## TL;DR

```bash
cd screen-to-song          # ← Use this project
./setup.sh                 # ← Run setup
# Add API key to backend/.env
cd backend && ./start.sh   # ← Start backend
# New terminal:
cd frontend && ./start.sh  # ← Start frontend
```

**Open http://localhost:3000** 🎉
