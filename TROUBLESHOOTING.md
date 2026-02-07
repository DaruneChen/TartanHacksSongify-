# 🔧 Quick Fix Guide

## Your Error: Cannot import 'generate' from 'elevenlabs'

### Problem
You're trying to run a backend file that has elevenlabs imports, but:
1. The backend I provided doesn't use elevenlabs
2. You might be in the wrong directory

### Solution

#### Option 1: Use the Correct Project (Recommended)

```bash
# Navigate to the screen-to-song project
cd /path/to/screen-to-song

# Go to backend
cd backend

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Mac/Linux
# or
.\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Add your API key to .env
echo "ANTHROPIC_API_KEY=your-key-here" > .env

# Run the server
python main.py
```

#### Option 2: Fix Your Current File

If you want to keep your existing `song/Backend/main.py`, remove the elevenlabs import:

```python
# Remove this line:
from elevenlabs import generate, Voice

# Or install elevenlabs:
pip install elevenlabs
```

### Why This Happened

The backend I built for you **does NOT require elevenlabs**. It only needs:
- fastapi
- anthropic (or openai)
- pillow
- imagehash

All specified in `requirements.txt`.

### Quick Test

To verify you're using the right backend:

```bash
# Check if you're in the right directory
pwd
# Should show: .../screen-to-song/backend

# Check the imports in main.py
head -20 main.py
# Should NOT show elevenlabs

# Check requirements.txt
cat requirements.txt
# Should NOT include elevenlabs
```

### Start Fresh (Easiest)

```bash
# 1. Navigate to Downloads or Desktop
cd ~/Desktop  # or wherever you extracted the project

# 2. Make sure you have the screen-to-song folder
ls screen-to-song

# 3. Go into it
cd screen-to-song

# 4. Run the automated setup
./setup.sh

# 5. Follow the prompts
```

### If You Want AI Singing

If you DO want to add AI singing (elevenlabs), I can add that feature! But the basic app works without it. The current implementation:
- ✅ Captures screen
- ✅ Analyzes with AI vision
- ✅ Generates lyrics
- ❌ Does NOT generate singing voice (by design for speed)

---

## TL;DR

You're in the wrong directory. Use the `screen-to-song` project I created, not `song/Backend`.

```bash
cd /path/to/screen-to-song/backend
python main.py
```
