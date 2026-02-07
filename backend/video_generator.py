"""
Video generator for Screen-to-Song.
Assembles images + lyrics text + audio into music videos.
Adapted from hackathon project video.py.
"""

import os
import numpy as np
from PIL import Image
from pathlib import Path

# MoviePy imports
from moviepy import (
    ImageClip, TextClip, CompositeVideoClip,
    concatenate_videoclips, AudioFileClip,
)


def apply_ken_burns_effect(clip, zoom_ratio=0.08):
    """Apply gradual zoom-in effect to an image clip."""
    w, h = clip.size

    def make_frame(get_frame, t):
        frame = get_frame(t)
        progress = t / clip.duration
        zoom = 1.0 + (zoom_ratio * progress)
        new_w = int(w * zoom)
        new_h = int(h * zoom)

        img = Image.fromarray(frame)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        x_off = (new_w - w) // 2
        y_off = (new_h - h) // 2
        cropped = np.array(img)[y_off:y_off + h, x_off:x_off + w]
        return cropped

    return clip.transform(make_frame)


def create_text_with_fade(text, duration=3.5, fade_duration=0.4):
    """Create a text clip with fade in/out effect."""
    txt = TextClip(
        text=text,
        font_size=48,
        color="white",
        stroke_color="black",
        stroke_width=2,
    )

    def make_frame(get_frame, t):
        frame = get_frame(0)
        if t < fade_duration:
            alpha = t / fade_duration
        elif t > duration - fade_duration:
            alpha = (duration - t) / fade_duration
        else:
            alpha = 1.0
        return (frame * max(0, min(1, alpha))).astype(np.uint8)

    return txt.transform(make_frame).with_duration(duration)


def assemble_music_video(
    scene_images: list[str],
    lyrics_list: list[list[str]],
    audio_path: str,
    output_path: str,
    scene_durations: list[float] | None = None,
) -> str:
    """
    Assemble a music video from images, lyrics, and audio.

    Args:
        scene_images: List of image file paths
        lyrics_list: List of lyric line lists (one per scene)
        audio_path: Path to the audio file
        output_path: Path for the output MP4
        scene_durations: Optional list of durations per scene (seconds)

    Returns:
        Path to the output video file
    """
    clips = []

    # Calculate durations
    if scene_durations is None:
        # Distribute evenly based on audio duration or default 4s per scene
        if os.path.exists(audio_path):
            audio = AudioFileClip(audio_path)
            total = audio.duration
            per_scene = total / max(len(scene_images), 1)
            scene_durations = [per_scene] * len(scene_images)
        else:
            scene_durations = [4.0] * len(scene_images)

    for i, img_path in enumerate(scene_images):
        if not os.path.exists(img_path):
            continue

        duration = scene_durations[i] if i < len(scene_durations) else 4.0

        # Create image clip
        img_clip = ImageClip(img_path).with_duration(duration)

        # Apply Ken Burns zoom
        try:
            img_clip = apply_ken_burns_effect(img_clip, zoom_ratio=0.08)
        except Exception as e:
            print(f"Ken Burns failed for scene {i + 1}: {e}")

        # Add lyrics text overlay
        lyrics_text = ""
        if i < len(lyrics_list):
            lyrics_text = "\n".join(lyrics_list[i])

        if lyrics_text:
            try:
                txt_clip = create_text_with_fade(lyrics_text, duration=duration, fade_duration=0.5)
                txt_clip = txt_clip.with_position(("center", 0.78), relative=True)
                composite = CompositeVideoClip([img_clip, txt_clip]).resized((1280, 720))
            except Exception as e:
                print(f"Text overlay failed for scene {i + 1}: {e}")
                composite = img_clip.resized((1280, 720))
        else:
            composite = img_clip.resized((1280, 720))

        clips.append(composite)

    if not clips:
        raise ValueError("No valid scene clips to assemble")

    # Concatenate all scenes
    video = concatenate_videoclips(clips, method="compose")

    # Add audio
    if os.path.exists(audio_path):
        audio = AudioFileClip(audio_path)
        if audio.duration > video.duration:
            audio = audio.subclipped(0, video.duration)
        video = video.with_audio(audio)

    video.write_videofile(output_path, fps=24, codec="libx264", audio_codec="aac")
    return output_path
