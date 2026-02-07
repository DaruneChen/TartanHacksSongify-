"""
Audio processing pipeline for Screen-to-Song.
Transforms flat TTS output into singing-like vocals with background music.
Adapted from hackathon project audio.py.
"""

import numpy as np
import librosa
import soundfile as sf
from scipy.io import wavfile
from pedalboard import (
    Pedalboard, Reverb, Chorus, Compressor, Gain,
    HighpassFilter, LowpassFilter,
)
import io
import os

SAMPLE_RATE = 44100


def get_melody_freqs_for_mood(mood: str) -> tuple:
    """Return (base_freq, melody_freqs) pentatonic scale based on mood."""
    mood_lower = mood.lower() if isinstance(mood, str) else "neutral"

    if any(w in mood_lower for w in ["calm", "peaceful", "serene", "relaxed", "lo-fi"]):
        return 220, [220, 247, 277, 330, 370]  # A3 major pentatonic
    elif any(w in mood_lower for w in ["energetic", "exciting", "upbeat", "edm", "pop"]):
        return 440, [440, 494, 523, 587, 659]  # A4 major pentatonic
    elif any(w in mood_lower for w in ["dark", "mysterious", "ominous", "haunting"]):
        return 110, [110, 123, 131, 147, 165]  # A2 minor pentatonic
    elif any(w in mood_lower for w in ["cosmic", "ethereal", "dreamy", "ambient", "jazz"]):
        return 330, [330, 370, 415, 440, 494]  # E4 major pentatonic
    else:
        return 261.63, [262, 294, 330, 349, 392]  # C major pentatonic


def _apply_singing_timing(y: np.ndarray, sr: int) -> np.ndarray:
    """
    Apply variable timing to make speech sound more like singing.
    Randomly stretches and compresses segments to break the monotonous reading pace.
    """
    import random

    # Split into segments (~0.3s each)
    segment_len = int(0.3 * sr)
    segments = []
    for i in range(0, len(y), segment_len):
        segments.append(y[i:i + segment_len])

    # Apply random time-stretching to each segment
    processed = []
    for seg in segments:
        if len(seg) < 1000:
            processed.append(seg)
            continue
        # Random stretch factor: 0.75 (faster) to 1.3 (slower/drawn out)
        stretch = random.uniform(0.75, 1.3)
        stretched = librosa.effects.time_stretch(seg, rate=stretch)
        processed.append(stretched)

    return np.concatenate(processed)


def apply_vocal_effects(audio_path: str, mood: str = "neutral") -> bool:
    """
    Apply pitch shifting + professional vocal FX chain to TTS audio.
    Makes speech sound more like singing with higher pitch and varied timing.
    """
    try:
        y, sr = librosa.load(audio_path, sr=SAMPLE_RATE)

        # Step 1: Apply variable timing to break monotonous reading pace
        y = _apply_singing_timing(y, sr)

        # Step 2: Pitch shift UP to sound more like singing (higher, brighter voice)
        # Always shift up by 4-6 semitones for a brighter, more musical sound
        base_freq, melody_freqs = get_melody_freqs_for_mood(mood)
        target_freq = melody_freqs[len(melody_freqs) // 2]
        semitones = 12 * np.log2(target_freq / base_freq)
        # Minimum +4 semitones up, scaled by mood
        semitones_shift = max(4.0, semitones * 0.7 + 4.0)

        y_shifted = librosa.effects.pitch_shift(y, sr=sr, n_steps=semitones_shift)

        # Step 3: Add vibrato (pitch wobble) for singing quality
        t = np.arange(len(y_shifted)) / sr
        vibrato_rate = 5.5  # Hz - natural singing vibrato
        vibrato_depth = 0.3  # semitones
        vibrato = vibrato_depth * np.sin(2 * np.pi * vibrato_rate * t)
        # Apply vibrato as micro pitch shifts via phase modulation
        phase_mod = np.cumsum(vibrato / sr) * 2 * np.pi * 100
        y_vibrato = y_shifted * (1 + 0.02 * np.sin(phase_mod))

        # Step 4: Professional vocal effects chain
        vocal_board = Pedalboard([
            Compressor(threshold_db=-25, ratio=3, attack_ms=5, release_ms=50),
            Chorus(rate_hz=2.0, depth=0.5, centre_delay_ms=7, feedback=0.3, mix=0.45),
            Reverb(room_size=0.65, damping=0.4, wet_level=0.4, dry_level=0.75, width=0.9),
            Compressor(threshold_db=-18, ratio=4, attack_ms=10, release_ms=100),
            Gain(gain_db=3.0),
        ])

        y_effected = vocal_board(y_vibrato, sr)

        # Normalize
        y_effected = y_effected / (np.max(np.abs(y_effected)) + 0.01)

        sf.write(audio_path, y_effected, sr)
        return True

    except Exception as e:
        print(f"Vocal effects failed: {e}")
        return False


def _generate_instrument(freq: float, duration: float, sr: int,
                         instrument_type: str = "synth") -> np.ndarray:
    """Generate instrument sound with harmonics and ADSR envelope."""
    num_samples = int(sr * duration)
    t = np.linspace(0, duration, num_samples)

    if instrument_type == "synth":
        signal = (
            1.0 * np.sin(2 * np.pi * freq * t) +
            0.5 * np.sin(2 * np.pi * freq * 2 * t) +
            0.25 * np.sin(2 * np.pi * freq * 3 * t) +
            0.125 * np.sin(2 * np.pi * freq * 4 * t)
        )
    elif instrument_type == "bass":
        signal = (
            1.0 * np.sin(2 * np.pi * freq * t) +
            0.3 * np.sin(2 * np.pi * freq * 2 * t) +
            0.1 * np.sin(2 * np.pi * freq * 4 * t)
        )
    else:  # pad
        signal = (
            0.8 * np.sin(2 * np.pi * freq * t) +
            0.4 * np.sin(2 * np.pi * freq * 2 * t) +
            0.3 * np.sin(2 * np.pi * freq * 3 * t) +
            0.2 * np.sin(2 * np.pi * freq * 5 * t) +
            0.1 * np.sin(2 * np.pi * freq * 7 * t)
        )

    # ADSR envelope
    attack_samples = int(sr * 0.02)
    decay_samples = int(sr * 0.05)
    release_samples = int(sr * 0.1)
    sustain_level = 0.7

    envelope = np.ones_like(signal)
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    if decay_samples > 0 and attack_samples + decay_samples < len(envelope):
        envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain_level, decay_samples)
    sustain_start = attack_samples + decay_samples
    sustain_end = len(envelope) - release_samples
    if sustain_start < sustain_end:
        envelope[sustain_start:sustain_end] = sustain_level
    if release_samples > 0:
        envelope[-release_samples:] = np.linspace(sustain_level, 0, release_samples)

    return signal * envelope


def generate_background_music(duration_s: float, tempo_bpm: int, mood: str) -> np.ndarray:
    """Generate procedural background music with melody, pads, bass, and drums."""
    sr = SAMPLE_RATE
    num_samples = int(sr * duration_s)
    t = np.linspace(0, duration_s, num_samples)
    beat_duration_s = 60.0 / tempo_bpm

    base_freq, melody_freqs = get_melody_freqs_for_mood(mood)

    # Melody
    melody = np.zeros(num_samples)
    note_duration = 2.0
    for i, freq in enumerate(melody_freqs * int(np.ceil(duration_s / (len(melody_freqs) * note_duration)))):
        if i * note_duration * sr >= num_samples:
            break
        note = _generate_instrument(freq, note_duration, sr, "synth")
        start = int(i * note_duration * sr)
        end = min(start + len(note), num_samples)
        if end - start > 0:
            melody[start:end] += note[:end - start] * 0.08

    # Chord pads
    pad = np.zeros(num_samples)
    chord_duration = 4.0
    for i in range(int(np.ceil(duration_s / chord_duration))):
        if i * chord_duration * sr >= num_samples:
            break
        root = melody_freqs[i % len(melody_freqs)]
        third = melody_freqs[(i + 2) % len(melody_freqs)]
        chord = (
            _generate_instrument(root, chord_duration, sr, "pad") +
            _generate_instrument(third, chord_duration, sr, "pad")
        ) * 0.5
        start = int(i * chord_duration * sr)
        end = min(start + len(chord), num_samples)
        if end - start > 0:
            pad[start:end] += chord[:end - start] * 0.05

    # Bass
    bass = np.zeros(num_samples)
    bass_note_dur = beat_duration_s * 2
    for i in range(int(np.ceil(duration_s / bass_note_dur))):
        if i * bass_note_dur * sr >= num_samples:
            break
        bass_note = _generate_instrument(base_freq * 0.5, bass_note_dur, sr, "bass")
        start = int(i * bass_note_dur * sr)
        end = min(start + len(bass_note), num_samples)
        if end - start > 0:
            bass[start:end] += bass_note[:end - start] * 0.12

    # Drums
    kick = np.zeros(num_samples)
    snare = np.zeros(num_samples)
    hihat = np.zeros(num_samples)
    beat_times = np.arange(0, duration_s, beat_duration_s)

    for i, bt in enumerate(beat_times):
        bs = int(bt * sr)
        # Kick on every beat
        kd = int(0.15 * sr)
        ke = min(bs + kd, num_samples)
        if bs < num_samples:
            kt = np.linspace(0, 0.15, ke - bs)
            kick[bs:ke] += (
                0.15 * np.exp(-15 * kt) * np.sin(2 * np.pi * (60 + 40 * np.exp(-20 * kt)) * kt) +
                0.02 * np.random.randn(len(kt))
            )
        # Snare on beats 2 and 4
        if i % 2 == 1 and bs < num_samples:
            sd = int(0.12 * sr)
            se = min(bs + sd, num_samples)
            st = np.linspace(0, 0.12, se - bs)
            snare[bs:se] += (
                0.1 * np.exp(-20 * st) * np.sin(2 * np.pi * 200 * st) +
                0.08 * np.exp(-15 * st) * np.random.randn(len(st))
            )
        # Hi-hat on every half beat
        for j in range(2):
            ht = bt + j * beat_duration_s / 2
            hs = int(ht * sr)
            if hs < num_samples:
                hd = int(0.05 * sr)
                he = min(hs + hd, num_samples)
                hht = np.linspace(0, 0.05, he - hs)
                hihat[hs:he] += 0.03 * np.exp(-40 * hht) * np.random.randn(len(hht))

    music = melody + pad + bass + kick + snare + hihat

    # Apply EQ and compression to music
    music_board = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=80),
        Compressor(threshold_db=-20, ratio=2, attack_ms=20, release_ms=200),
        Gain(gain_db=-2.0),
    ])
    music = music_board(music, sr)

    # Fade in/out
    fade_samples = int(sr * 1.5)
    if len(music) > 2 * fade_samples:
        music[:fade_samples] *= np.linspace(0, 1, fade_samples)
        music[-fade_samples:] *= np.linspace(1, 0, fade_samples)

    return music


def _apply_sidechain(music: np.ndarray, vocals: np.ndarray, sr: int = SAMPLE_RATE) -> np.ndarray:
    """Sidechain compression: duck music when vocals are active."""
    window_size = int(0.05 * sr)
    vocal_envelope = np.zeros_like(vocals)

    for i in range(0, len(vocals) - window_size, window_size // 2):
        rms = np.sqrt(np.mean(vocals[i:i + window_size] ** 2))
        vocal_envelope[i:i + window_size] = max(vocal_envelope[i], rms)

    duck_amount = 0.4
    ducking = np.ones_like(music)
    active = vocal_envelope > 0.01

    for i in range(len(ducking)):
        target = duck_amount if active[i] else 1.0
        if i > 0:
            rate = 0.95 if active[i] else 0.99
            ducking[i] = ducking[i - 1] * rate + target * (1 - rate)
        else:
            ducking[i] = target

    return music * ducking


def mix_and_master(vocal_path: str, background_music: np.ndarray, output_path: str) -> str:
    """
    Mix vocals with background music using sidechain compression and mastering.
    Returns path to the final mixed audio file.
    """
    sr = SAMPLE_RATE

    # Load vocals
    if os.path.exists(vocal_path):
        narr_rate, vocals = wavfile.read(vocal_path)
        if vocals.dtype == np.int16:
            vocals = vocals.astype(np.float32) / 32767.0
        # Handle stereo
        if len(vocals.shape) > 1:
            vocals = vocals.mean(axis=1)
    else:
        vocals = np.zeros_like(background_music)

    # Match lengths
    if len(vocals) < len(background_music):
        vocals = np.pad(vocals, (0, len(background_music) - len(vocals)))
    elif len(vocals) > len(background_music):
        background_music = np.pad(background_music, (0, len(vocals) - len(background_music)))

    # Sidechain compression
    ducked_music = _apply_sidechain(background_music, vocals, sr)

    # EQ separation
    music_eq = Pedalboard([
        HighpassFilter(cutoff_frequency_hz=120),
        LowpassFilter(cutoff_frequency_hz=12000),
    ])
    ducked_music = music_eq(ducked_music, sr)

    # Mix
    mixed = (vocals * 1.0) + (ducked_music * 0.35)

    # Mastering chain
    mastering = Pedalboard([
        Compressor(threshold_db=-12, ratio=3, attack_ms=15, release_ms=150),
        Compressor(threshold_db=-6, ratio=10, attack_ms=1, release_ms=50),
        Gain(gain_db=3.5),
    ])
    mixed = mastering(mixed, sr)

    # Normalize
    peak = np.max(np.abs(mixed))
    if peak > 0:
        mixed = mixed / peak * 0.95
    mixed = np.clip(mixed, -1.0, 1.0)
    mixed = np.int16(mixed * 32767)

    wavfile.write(output_path, sr, mixed)
    return output_path


def get_tempo_for_genre(genre: str) -> int:
    """Map genre to appropriate BPM."""
    genre_lower = genre.lower() if genre else "pop"
    tempos = {
        "lo-fi": 85, "jazz": 100, "classical": 90, "pop": 120,
        "edm": 128, "rock": 130, "hip-hop": 90, "r&b": 95,
        "ambient": 70, "funk": 110,
    }
    for key, bpm in tempos.items():
        if key in genre_lower:
            return bpm
    return 120
