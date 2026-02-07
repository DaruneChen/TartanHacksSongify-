from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from pydantic import BaseModel
from typing import Optional, List
import base64
import io
import os
import json
import hashlib
import time
from pathlib import Path
import anthropic
import openai
from PIL import Image
import imagehash
from dotenv import load_dotenv
from elevenlabs import ElevenLabs

from audio_processor import (
    apply_vocal_effects, generate_background_music,
    mix_and_master, get_tempo_for_genre,
)
from video_generator import assemble_music_video
from pipeline import run_pipeline

load_dotenv()

app = FastAPI(title="Screen to Song API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
UDIO_API_KEY = os.getenv("UDIO_API_KEY", "")

anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY) if ANTHROPIC_API_KEY else None
openai_client = openai.OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None
elevenlabs_client = ElevenLabs(api_key=ELEVENLABS_API_KEY) if ELEVENLABS_API_KEY else None

# In-memory cache for frame analysis
frame_cache = {}
lyric_history = []

# Paths
OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Models
class SceneContext(BaseModel):
    mood: str
    activity: str
    objects: List[str]
    suggested_genre: str
    energy_level: int  # 1-5
    description: str
    screen_text: Optional[str] = None  # Extracted text content from screen for study lyrics

class LyricRequest(BaseModel):
    scene_context: SceneContext
    previous_lyrics: Optional[List[str]] = None

class LyricResponse(BaseModel):
    lyrics: List[str]
    timestamp: float
    genre: str

# Helper Functions
def image_to_base64(image_bytes: bytes) -> str:
    """Convert image bytes to base64 string"""
    return base64.b64encode(image_bytes).decode('utf-8')

def get_image_hash(image_bytes: bytes) -> str:
    """Get perceptual hash of image"""
    img = Image.open(io.BytesIO(image_bytes))
    return str(imagehash.dhash(img))

def should_analyze_frame(image_bytes: bytes) -> bool:
    """Check if frame is different enough to analyze"""
    img_hash = get_image_hash(image_bytes)
    
    # Check if we've seen this frame recently (within last 10 frames)
    recent_hashes = list(frame_cache.keys())[-10:]
    if img_hash in recent_hashes:
        return False
    
    return True

async def analyze_with_claude(image_base64: str) -> SceneContext:
    """Analyze screen capture using Claude Vision"""
    if not anthropic_client:
        raise HTTPException(status_code=500, detail="Anthropic API key not configured")
    
    try:
        message = anthropic_client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=1024,
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/png",
                                "data": image_base64,
                            },
                        },
                        {
                            "type": "text",
                            "text": """Analyze this screen capture and return a JSON object with:
{
  "mood": "one word mood (e.g., focused, relaxed, energetic, creative)",
  "activity": "main activity (e.g., coding, gaming, browsing, video-editing, studying)",
  "objects": ["list", "of", "visible", "objects"],
  "suggested_genre": "music genre that fits (e.g., lo-fi, edm, pop, classical, jazz)",
  "energy_level": 1-5 (1=calm, 5=intense),
  "description": "brief 1-sentence description",
  "screen_text": "Extract the KEY educational/informational content visible on screen. Include main headings, definitions, key facts, code snippets, or study material. This will be turned into song lyrics to help the user memorize/study the content. If no educational content, write null."
}

Only respond with valid JSON, no other text."""
                        }
                    ],
                }
            ],
        )
        
        # Extract JSON from response
        response_text = message.content[0].text
        # Try to find JSON in the response
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = response_text[start_idx:end_idx]
            data = json.loads(json_str)
            return SceneContext(**data)
        else:
            raise ValueError("No JSON found in response")
            
    except Exception as e:
        print(f"Claude analysis error: {e}")
        # Fallback response
        return SceneContext(
            mood="neutral",
            activity="working",
            objects=["screen"],
            suggested_genre="lo-fi",
            energy_level=3,
            description="User working on computer"
        )

async def analyze_with_gpt4(image_base64: str) -> SceneContext:
    """Analyze screen capture using GPT-4 Vision"""
    if not openai_client:
        raise HTTPException(status_code=500, detail="OpenAI API key not configured")
    
    try:
        response = openai_client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analyze this screen capture and return ONLY a JSON object with:
{
  "mood": "one word mood",
  "activity": "main activity (e.g., coding, studying, browsing, gaming)",
  "objects": ["list of objects"],
  "suggested_genre": "music genre",
  "energy_level": 1-5,
  "description": "brief description",
  "screen_text": "Extract KEY educational/informational content visible on screen - headings, definitions, key facts, code, study material. This becomes song lyrics. null if no educational content."
}"""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ],
                }
            ],
            max_tokens=500,
        )
        
        response_text = response.choices[0].message.content
        # Extract JSON
        start_idx = response_text.find('{')
        end_idx = response_text.rfind('}') + 1
        
        if start_idx != -1 and end_idx != 0:
            json_str = response_text[start_idx:end_idx]
            data = json.loads(json_str)
            return SceneContext(**data)
        else:
            raise ValueError("No JSON found")
            
    except Exception as e:
        print(f"GPT-4 analysis error: {e}")
        return SceneContext(
            mood="neutral",
            activity="working",
            objects=["screen"],
            suggested_genre="lo-fi",
            energy_level=3,
            description="User working on computer"
        )

async def generate_lyrics(context: SceneContext, previous_lyrics: List[str] = None) -> List[str]:
    """Generate lyrics based on scene context, using screen content for study material"""
    if not anthropic_client and not openai_client:
        raise HTTPException(status_code=500, detail="No API key configured")

    previous_text = ""
    if previous_lyrics:
        previous_text = f"\n\nPrevious lyrics to avoid repeating:\n" + "\n".join(previous_lyrics[-10:])

    # If screen has educational content, make study-focused lyrics
    screen_content = ""
    if context.screen_text:
        screen_content = f"""
IMPORTANT - The user is studying/reading this content on their screen:
\"\"\"{context.screen_text}\"\"\"

Your lyrics MUST incorporate the KEY FACTS, DEFINITIONS, or CONCEPTS from this content.
The goal is to help the user MEMORIZE and STUDY this material through catchy song lyrics.
Transform the educational content into memorable, singable lines.
"""

    prompt = f"""Write 4 lines of SONG LYRICS for a {context.suggested_genre} song.
{screen_content}
Context:
- Mood: {context.mood}
- Activity: {context.activity}
- Energy level: {context.energy_level}/5
- Scene: {context.description}

CRITICAL RULES for lyrics:
1. Write like a REAL SONG - use rhythm, rhyme, and poetic flow
2. Each line should be SHORT and SINGABLE (5-12 words max)
3. Use rhyme schemes (AABB or ABAB)
4. If study content is provided, weave the key facts INTO the lyrics naturally
5. Make it CATCHY and MEMORABLE - like something you'd actually sing
6. Fit the {context.suggested_genre} genre style
7. Think: "Would this sound good performed with music?"

BAD example (too dry): "Photosynthesis converts light to energy"
GOOD example: "Catching sunlight, turning it to green / The chloroplast machine, you know what I mean"

{previous_text}

Return ONLY the 4 lines of lyrics, no explanations or quotes."""

    try:
        if anthropic_client:
            message = anthropic_client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            lyrics_text = message.content[0].text.strip()
        else:
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                max_tokens=256,
                messages=[{"role": "user", "content": prompt}],
            )
            lyrics_text = response.choices[0].message.content.strip()

        lyrics = [line.strip() for line in lyrics_text.split('\n') if line.strip()]

        return lyrics[:4]  # Ensure we only return 4 lines

    except Exception as e:
        print(f"Lyric generation error: {e}")
        return [
            f"Living in the {context.mood} zone",
            f"Just {context.activity} all alone",
            f"Finding rhythm in the daily grind",
            "Making melodies inside my mind"
        ]

# API Endpoints

@app.get("/")
async def root():
    return {
        "message": "Screen to Song API",
        "version": "1.0.0",
        "endpoints": {
            "analyze": "/api/analyze-frame",
            "lyrics": "/api/generate-lyrics",
            "health": "/api/health"
        }
    }

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "anthropic_configured": anthropic_client is not None,
        "openai_configured": openai_client is not None,
        "elevenlabs_configured": elevenlabs_client is not None,
        "udio_configured": bool(UDIO_API_KEY),
    }

@app.post("/api/analyze-frame")
async def analyze_frame(file: UploadFile = File(...), use_gpt4: bool = False):
    """
    Analyze a screen capture frame
    Returns scene context including mood, activity, and suggested genre
    """
    try:
        # Read image
        image_bytes = await file.read()
        
        # Check if we should analyze this frame
        if not should_analyze_frame(image_bytes):
            # Return cached result
            img_hash = get_image_hash(image_bytes)
            if img_hash in frame_cache:
                return JSONResponse(content={
                    "cached": True,
                    "context": frame_cache[img_hash]
                })
        
        # Convert to base64
        image_base64 = image_to_base64(image_bytes)
        
        # Analyze with chosen model (fall back to GPT-4 if Anthropic not configured)
        if use_gpt4 or not anthropic_client:
            context = await analyze_with_gpt4(image_base64)
        else:
            context = await analyze_with_claude(image_base64)
        
        # Cache result
        img_hash = get_image_hash(image_bytes)
        frame_cache[img_hash] = context.model_dump()

        # Save screenshot for video generation
        screenshot_path = str(OUTPUT_DIR / f"capture_{int(time.time())}.png")
        with open(screenshot_path, "wb") as f:
            f.write(image_bytes)
        captured_screenshots.append(screenshot_path)
        # Keep only last 20 screenshots
        if len(captured_screenshots) > 20:
            captured_screenshots.pop(0)

        return JSONResponse(content={
            "cached": False,
            "context": context.model_dump()
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-lyrics")
async def generate_lyrics_endpoint(request: LyricRequest):
    """
    Generate lyrics based on scene context
    """
    try:
        lyrics = await generate_lyrics(
            request.scene_context,
            request.previous_lyrics
        )
        
        # Add to history
        lyric_history.extend(lyrics)
        
        return LyricResponse(
            lyrics=lyrics,
            timestamp=time.time(),
            genre=request.scene_context.suggested_genre
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/lyrics-history")
async def get_lyrics_history(limit: int = 50):
    """Get recent lyrics history"""
    return {
        "lyrics": lyric_history[-limit:],
        "count": len(lyric_history)
    }

class SingRequest(BaseModel):
    lyrics: List[str]
    genre: Optional[str] = "pop"
    mood: Optional[str] = "neutral"

@app.post("/api/sing")
async def sing_lyrics(request: SingRequest):
    """Generate singing audio: ElevenLabs TTS + vocal FX + background music + mastering"""
    if not elevenlabs_client:
        raise HTTPException(status_code=500, detail="ElevenLabs API key not configured")

    lyrics_text = "\n\n".join(request.lyrics)
    ts = int(time.time())

    try:
        # Step 1: Generate TTS vocals via ElevenLabs
        audio_iter = elevenlabs_client.text_to_speech.convert(
            text=lyrics_text,
            voice_id="EXAVITQu4vr4xnSDxMaL",  # "Bella" - expressive female voice
            model_id="eleven_multilingual_v2",
            voice_settings={
                "stability": 0.3,
                "similarity_boost": 0.75,
                "style": 1.0,
                "use_speaker_boost": True,
            },
        )
        tts_bytes = b"".join(audio_iter)

        # Save TTS as MP3, then convert to WAV for processing
        tts_mp3_path = OUTPUT_DIR / f"tts_{ts}.mp3"
        tts_mp3_path.write_bytes(tts_bytes)

        vocal_wav_path = str(OUTPUT_DIR / f"vocal_{ts}.wav")

        # Convert MP3 to WAV using ffmpeg
        import subprocess
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(tts_mp3_path), "-ar", "44100", "-ac", "1", vocal_wav_path],
            capture_output=True, check=True,
        )

        # Step 2: Apply vocal effects (pitch shift + chorus + reverb)
        mood = request.mood or request.genre or "neutral"
        apply_vocal_effects(vocal_wav_path, mood)

        # Step 3: Generate background music
        from scipy.io import wavfile
        sr, vocal_data = wavfile.read(vocal_wav_path)
        vocal_duration = len(vocal_data) / sr
        tempo = get_tempo_for_genre(request.genre or "pop")
        bg_music = generate_background_music(vocal_duration, tempo, mood)

        # Step 4: Mix and master (sidechain + EQ + mastering chain)
        final_wav_path = str(OUTPUT_DIR / f"mixed_{ts}.wav")
        mix_and_master(vocal_wav_path, bg_music, final_wav_path)

        # Step 5: Convert final WAV to MP3 for smaller file size
        final_mp3_path = str(OUTPUT_DIR / f"song_{ts}.mp3")
        subprocess.run(
            ["ffmpeg", "-y", "-i", final_wav_path, "-b:a", "192k", final_mp3_path],
            capture_output=True, check=True,
        )

        return FileResponse(
            path=final_mp3_path,
            media_type="audio/mpeg",
            filename=f"song_{ts}.mp3",
        )
    except Exception as e:
        print(f"Sing error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Store captured screenshots for video generation
captured_screenshots: List[str] = []


class VideoRequest(BaseModel):
    lyrics_sets: List[List[str]]
    genre: Optional[str] = "pop"
    mood: Optional[str] = "neutral"


@app.post("/api/generate-video")
async def generate_video(request: VideoRequest):
    """Generate a music video from lyrics + captured screenshots + audio"""
    if not elevenlabs_client:
        raise HTTPException(status_code=500, detail="ElevenLabs API key not configured")

    ts = int(time.time())

    try:
        # Step 1: Generate the full song audio first
        all_lyrics = [line for verse in request.lyrics_sets for line in verse]
        lyrics_text = "\n\n".join(all_lyrics)

        audio_iter = elevenlabs_client.text_to_speech.convert(
            text=lyrics_text,
            voice_id="EXAVITQu4vr4xnSDxMaL",
            model_id="eleven_multilingual_v2",
            voice_settings={
                "stability": 0.3,
                "similarity_boost": 0.75,
                "style": 1.0,
                "use_speaker_boost": True,
            },
        )
        tts_bytes = b"".join(audio_iter)

        tts_mp3 = OUTPUT_DIR / f"video_tts_{ts}.mp3"
        tts_mp3.write_bytes(tts_bytes)

        vocal_wav = str(OUTPUT_DIR / f"video_vocal_{ts}.wav")
        import subprocess
        subprocess.run(
            ["ffmpeg", "-y", "-i", str(tts_mp3), "-ar", "44100", "-ac", "1", vocal_wav],
            capture_output=True, check=True,
        )

        mood = request.mood or "neutral"
        apply_vocal_effects(vocal_wav, mood)

        from scipy.io import wavfile
        sr, vocal_data = wavfile.read(vocal_wav)
        vocal_duration = len(vocal_data) / sr
        tempo = get_tempo_for_genre(request.genre or "pop")
        bg_music = generate_background_music(vocal_duration, tempo, mood)

        audio_wav = str(OUTPUT_DIR / f"video_audio_{ts}.wav")
        mix_and_master(vocal_wav, bg_music, audio_wav)

        # Step 2: Use captured screenshots as scene images (or generate placeholders)
        scene_images = []
        for i in range(len(request.lyrics_sets)):
            if i < len(captured_screenshots) and os.path.exists(captured_screenshots[i]):
                scene_images.append(captured_screenshots[i])
            else:
                # Create a gradient placeholder image
                from PIL import Image as PILImage
                import numpy as np
                img = PILImage.new("RGB", (1280, 720))
                pixels = np.zeros((720, 1280, 3), dtype=np.uint8)
                for y in range(720):
                    r = int(100 + 80 * (y / 720))
                    g = int(50 + 100 * (1 - y / 720))
                    b = int(150 + 60 * (y / 720))
                    pixels[y, :] = [r, g, b]
                img = PILImage.fromarray(pixels)
                img_path = str(OUTPUT_DIR / f"scene_{ts}_{i}.png")
                img.save(img_path)
                scene_images.append(img_path)

        # Step 3: Assemble video
        video_path = str(OUTPUT_DIR / f"video_{ts}.mp4")
        assemble_music_video(scene_images, request.lyrics_sets, audio_wav, video_path)

        return FileResponse(
            path=video_path,
            media_type="video/mp4",
            filename=f"video_{ts}.mp4",
        )
    except Exception as e:
        print(f"Video generation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/pipeline")
async def pipeline_endpoint(file: UploadFile = File(...), genre: str = "pop", make_video: bool = False):
    """One-click pipeline: upload screenshot -> get audio (and optionally video)"""
    try:
        image_bytes = await file.read()

        # Save screenshot for potential video use
        ts = int(time.time())
        screenshot_path = str(OUTPUT_DIR / f"capture_{ts}.png")
        with open(screenshot_path, "wb") as f:
            f.write(image_bytes)
        captured_screenshots.append(screenshot_path)

        image_base64 = image_to_base64(image_bytes)

        # Define sync wrappers for the pipeline
        def analyze_fn(img_bytes):
            import asyncio
            loop = asyncio.get_event_loop()
            if not anthropic_client:
                return loop.run_until_complete(analyze_with_gpt4(image_to_base64(img_bytes)))
            return loop.run_until_complete(analyze_with_claude(image_to_base64(img_bytes)))

        def lyrics_fn(context, prev):
            import asyncio
            loop = asyncio.get_event_loop()
            return loop.run_until_complete(generate_lyrics(context, prev))

        def sing_fn(lyrics, g):
            lyrics_text = "\n\n".join(lyrics)
            audio_iter = elevenlabs_client.text_to_speech.convert(
                text=lyrics_text,
                voice_id="EXAVITQu4vr4xnSDxMaL",
                model_id="eleven_multilingual_v2",
                voice_settings={"stability": 0.3, "similarity_boost": 0.75, "style": 1.0, "use_speaker_boost": True},
            )
            tts_bytes = b"".join(audio_iter)
            wav_path = str(OUTPUT_DIR / f"pipe_vocal_{ts}.wav")
            mp3_path = str(OUTPUT_DIR / f"pipe_tts_{ts}.mp3")
            Path(mp3_path).write_bytes(tts_bytes)
            import subprocess
            subprocess.run(["ffmpeg", "-y", "-i", mp3_path, "-ar", "44100", "-ac", "1", wav_path], capture_output=True, check=True)
            apply_vocal_effects(wav_path, g)
            from scipy.io import wavfile
            sr, vd = wavfile.read(wav_path)
            bg = generate_background_music(len(vd) / sr, get_tempo_for_genre(g), g)
            out = str(OUTPUT_DIR / f"pipe_mixed_{ts}.wav")
            mix_and_master(wav_path, bg, out)
            return out

        # Critique function for self-improvement loop
        def critique_fn(prompt):
            if anthropic_client:
                msg = anthropic_client.messages.create(
                    model="claude-sonnet-4-20250514",
                    max_tokens=512,
                    messages=[{"role": "user", "content": prompt}],
                )
                return msg.content[0].text
            elif openai_client:
                resp = openai_client.chat.completions.create(
                    model="gpt-4o",
                    max_tokens=512,
                    messages=[{"role": "user", "content": prompt}],
                )
                return resp.choices[0].message.content
            return '{"score": 7, "needs_improvement": false}'

        result = run_pipeline(
            analyze_fn=analyze_fn,
            lyrics_fn=lyrics_fn,
            sing_fn=sing_fn,
            critique_fn=critique_fn,
            image_bytes=image_bytes,
            genre=genre,
            make_video=make_video,
        )

        return JSONResponse(content={
            "context": result.get("context"),
            "lyrics": result.get("lyrics"),
            "audio_path": result.get("audio_path"),
            "video_path": result.get("video_path"),
            "trace": result.get("trace", []),
            "errors": result.get("errors", []),
            "cached": result.get("cached", False),
        })
    except Exception as e:
        print(f"Pipeline error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/clear-cache")
async def clear_cache():
    """Clear frame cache and lyric history"""
    frame_cache.clear()
    lyric_history.clear()
    return {"message": "Cache cleared successfully"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
