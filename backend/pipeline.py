"""
Complex AI Agent Pipeline for Screen-to-Song.
Multi-step orchestration with self-critique, retry logic, caching, and error recovery.
Follows the hackathon agent.py pattern with proper agentic behavior.
"""

import hashlib
import json
import os
import time
from pathlib import Path
from typing import Optional, Callable


OUTPUT_DIR = Path(__file__).parent / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)
CACHE_DIR = Path(__file__).parent / "cache"
CACHE_DIR.mkdir(exist_ok=True)


class PipelineStep:
    """Tracks a single step in the pipeline with timing and status."""
    def __init__(self, name: str):
        self.name = name
        self.status = "pending"
        self.start_time = None
        self.end_time = None
        self.duration_ms = None
        self.error = None
        self.attempt = 0

    def start(self):
        self.status = "running"
        self.start_time = time.time()
        self.attempt += 1

    def complete(self):
        self.status = "completed"
        self.end_time = time.time()
        self.duration_ms = int((self.end_time - self.start_time) * 1000)

    def fail(self, error: str):
        self.status = "failed"
        self.end_time = time.time()
        self.duration_ms = int((self.end_time - self.start_time) * 1000)
        self.error = error

    def to_dict(self):
        return {
            "name": self.name,
            "status": self.status,
            "attempt": self.attempt,
            "duration_ms": self.duration_ms,
            "error": self.error,
        }


def _critique_lyrics(lyrics: list, context, critique_fn) -> dict:
    """
    Self-critique loop: evaluate generated lyrics quality.
    Mirrors the hackathon's critique_storyboard + improve_storyboard pattern.
    """
    if not critique_fn:
        return {"score": 8, "needs_improvement": False}

    try:
        critique_prompt = f"""You are a music critic and study aid expert.

Evaluate these song lyrics meant to help someone study/memorize content:

Lyrics:
{chr(10).join(lyrics)}

Context - the user is: {context.activity}
Screen content: {context.screen_text or context.description}
Genre: {context.suggested_genre}

Rate on these criteria:
1. Singability (1-10) - Do the lyrics flow and rhyme naturally?
2. Content accuracy (1-10) - Do they capture the key study material?
3. Memorability (1-10) - Are they catchy enough to stick in memory?
4. Genre fit (1-10) - Do they match the {context.suggested_genre} style?

Return JSON: {{"score": <average 1-10>, "needs_improvement": true/false, "issues": ["issue1", ...], "strengths": ["str1", ...]}}
Only JSON, no other text."""

        result = critique_fn(critique_prompt)
        text = result if isinstance(result, str) else str(result)
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end > start:
            return json.loads(text[start:end])
    except Exception as e:
        print(f"Critique failed: {e}")

    return {"score": 7, "needs_improvement": False}


def run_pipeline(
    analyze_fn: Callable,
    lyrics_fn: Callable,
    sing_fn: Callable,
    video_fn: Callable = None,
    image_fn: Callable = None,
    critique_fn: Callable = None,
    image_bytes: bytes = None,
    mood: str = None,
    genre: str = None,
    make_video: bool = False,
    max_retries: int = 3,
) -> dict:
    """
    Complex AI agent pipeline with:
    - Step-by-step tracking with timing
    - Self-critique loop for lyrics quality
    - Retry logic with exponential backoff
    - MD5-based caching
    - Error recovery with fallbacks
    - Detailed trace logging

    Pipeline steps:
    1. Analyze frame (vision AI)
    2. Generate lyrics (LLM)
    3. Self-critique lyrics (agentic loop)
    4. Generate audio (TTS + FX + music)
    5. Generate images (optional, for video)
    6. Assemble video (optional)
    """
    pipeline_start = time.time()

    # Cache key from image hash + genre
    cache_key = hashlib.md5(
        (image_bytes[:2048] if image_bytes else b"empty") + (genre or "pop").encode()
    ).hexdigest()[:12]
    cache_path = CACHE_DIR / f"pipeline_{cache_key}.json"

    # Check cache
    if cache_path.exists():
        try:
            cached = json.loads(cache_path.read_text())
            if cached.get("audio_path") and os.path.exists(cached["audio_path"]):
                cached["cached"] = True
                print(f"Pipeline cache hit: {cache_key}")
                return cached
        except Exception:
            pass

    # Initialize pipeline tracking
    steps = {
        "analyze": PipelineStep("analyze_frame"),
        "lyrics": PipelineStep("generate_lyrics"),
        "critique": PipelineStep("self_critique"),
        "audio": PipelineStep("generate_audio"),
        "images": PipelineStep("generate_images"),
        "video": PipelineStep("assemble_video"),
    }
    errors = []
    result = {"cached": False, "errors": errors}

    # ── Step 1: Analyze frame ──
    context = None
    steps["analyze"].start()
    for attempt in range(max_retries):
        try:
            context = analyze_fn(image_bytes)
            steps["analyze"].complete()
            print(f"  Step 1/6: Frame analyzed ({steps['analyze'].duration_ms}ms)")
            break
        except Exception as e:
            err = f"analyze_attempt_{attempt + 1}: {str(e)}"
            errors.append(err)
            if attempt == max_retries - 1:
                steps["analyze"].fail(str(e))
                result["error"] = "Failed to analyze frame"
                result["trace"] = [s.to_dict() for s in steps.values()]
                return result
            time.sleep(0.5 * (attempt + 1))

    if context is None:
        result["error"] = "No context produced"
        result["trace"] = [s.to_dict() for s in steps.values()]
        return result

    # Apply overrides
    if mood:
        context.mood = mood
    if genre:
        context.suggested_genre = genre

    result["context"] = context.model_dump() if hasattr(context, "model_dump") else context

    # ── Step 2: Generate lyrics ──
    lyrics = None
    steps["lyrics"].start()
    for attempt in range(max_retries):
        try:
            lyrics = lyrics_fn(context, None)
            steps["lyrics"].complete()
            print(f"  Step 2/6: Lyrics generated ({steps['lyrics'].duration_ms}ms)")
            break
        except Exception as e:
            err = f"lyrics_attempt_{attempt + 1}: {str(e)}"
            errors.append(err)
            if attempt == max_retries - 1:
                lyrics = [
                    f"Living in the {context.mood} zone",
                    f"Just {context.activity} all alone",
                    "Finding rhythm in the daily grind",
                    "Making melodies inside my mind",
                ]
                steps["lyrics"].fail("fallback_used")
            time.sleep(0.5 * (attempt + 1))

    result["lyrics"] = lyrics

    # ── Step 3: Self-critique (agentic behavior) ──
    steps["critique"].start()
    if critique_fn and lyrics:
        try:
            critique = _critique_lyrics(lyrics, context, critique_fn)
            score = critique.get("score", 10)
            print(f"  Step 3/6: Self-critique score: {score}/10")

            # If score is low, regenerate lyrics with feedback
            if score < 6 or critique.get("needs_improvement", False):
                print(f"    Score too low ({score}/10), regenerating...")
                issues = critique.get("issues", [])

                for attempt in range(2):
                    try:
                        original_desc = context.description
                        context.description += f" (Fix these issues: {', '.join(issues[:3])})"
                        lyrics = lyrics_fn(context, lyrics)
                        context.description = original_desc

                        new_critique = _critique_lyrics(lyrics, context, critique_fn)
                        new_score = new_critique.get("score", 10)
                        print(f"    Improved score: {new_score}/10")
                        if new_score >= 6:
                            break
                    except Exception:
                        context.description = original_desc

                result["lyrics"] = lyrics

            steps["critique"].complete()
        except Exception as e:
            steps["critique"].fail(str(e))
            errors.append(f"critique: {str(e)}")
    else:
        steps["critique"].status = "skipped"
        steps["critique"].duration_ms = 0
        print(f"  Step 3/6: Self-critique skipped")

    # ── Step 4: Generate audio ──
    audio_path = None
    steps["audio"].start()
    for attempt in range(max_retries):
        try:
            audio_path = sing_fn(lyrics, context.suggested_genre)
            steps["audio"].complete()
            print(f"  Step 4/6: Audio generated ({steps['audio'].duration_ms}ms)")
            break
        except Exception as e:
            err = f"audio_attempt_{attempt + 1}: {str(e)}"
            errors.append(err)
            if attempt == max_retries - 1:
                steps["audio"].fail(str(e))
            time.sleep(0.5 * (attempt + 1))

    result["audio_path"] = audio_path

    # ── Step 5: Generate images (for video) ──
    image_paths = []
    if make_video and image_fn:
        steps["images"].start()
        try:
            prompt = f"{context.suggested_genre} aesthetic, {context.mood} mood: {context.description}"
            img_path = str(OUTPUT_DIR / f"scene_{cache_key}_0.png")
            if not os.path.exists(img_path):
                image_fn(img_path, prompt)
            image_paths.append(img_path)
            steps["images"].complete()
            print(f"  Step 5/6: Images generated ({steps['images'].duration_ms}ms)")
        except Exception as e:
            steps["images"].fail(str(e))
            errors.append(f"images: {str(e)}")
    else:
        steps["images"].status = "skipped"

    result["image_paths"] = image_paths

    # ── Step 6: Assemble video ──
    if make_video and video_fn and audio_path:
        steps["video"].start()
        for attempt in range(max_retries):
            try:
                video_path = video_fn(lyrics, audio_path, image_paths)
                result["video_path"] = video_path
                steps["video"].complete()
                print(f"  Step 6/6: Video assembled ({steps['video'].duration_ms}ms)")
                break
            except Exception as e:
                err = f"video_attempt_{attempt + 1}: {str(e)}"
                errors.append(err)
                if attempt == max_retries - 1:
                    steps["video"].fail(str(e))
                time.sleep(0.5 * (attempt + 1))
    else:
        steps["video"].status = "skipped"

    # Build trace
    result["trace"] = [s.to_dict() for s in steps.values()]
    total_ms = int((time.time() - pipeline_start) * 1000)
    result["total_duration_ms"] = total_ms

    # Cache result
    try:
        cacheable = {k: v for k, v in result.items() if isinstance(v, (str, list, dict, bool, int, float, type(None)))}
        cache_path.write_text(json.dumps(cacheable, indent=2))
    except Exception:
        pass

    completed = sum(1 for s in steps.values() if s.status == "completed")
    total = sum(1 for s in steps.values() if s.status != "skipped")
    print(f"Pipeline complete: {completed}/{total} steps in {total_ms}ms ({len(errors)} errors)")

    return result
