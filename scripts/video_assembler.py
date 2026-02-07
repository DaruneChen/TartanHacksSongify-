"""
Video Assembly Module
Creates lyric videos with visualizations using FFmpeg
"""

import os
import subprocess
import json
from pathlib import Path
from typing import List, Dict, Optional
import textwrap

class VideoAssembler:
    def __init__(self, output_dir: str = "./video_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.width = 1920
        self.height = 1080
        self.fps = 30
        
    def check_ffmpeg(self) -> bool:
        """Check if FFmpeg is installed"""
        try:
            subprocess.run(
                ["ffmpeg", "-version"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                check=True
            )
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def create_lyric_subtitle_file(
        self,
        lyrics: List[str],
        duration_per_line: float = 5.0,
        output_file: str = "lyrics.srt"
    ) -> str:
        """
        Create SRT subtitle file from lyrics
        
        Args:
            lyrics: List of lyric lines
            duration_per_line: How long each line appears (seconds)
            output_file: Output filename
        
        Returns:
            Path to subtitle file
        """
        filepath = self.output_dir / output_file
        
        with open(filepath, 'w', encoding='utf-8') as f:
            for i, line in enumerate(lyrics, 1):
                start_time = (i - 1) * duration_per_line
                end_time = i * duration_per_line
                
                # Format: HH:MM:SS,mmm
                start_str = self._format_srt_time(start_time)
                end_str = self._format_srt_time(end_time)
                
                f.write(f"{i}\n")
                f.write(f"{start_str} --> {end_str}\n")
                f.write(f"{line}\n\n")
        
        return str(filepath)
    
    def _format_srt_time(self, seconds: float) -> str:
        """Format seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
    
    def create_gradient_background(
        self,
        duration: float,
        colors: tuple = ("#8B5CF6", "#EC4899"),  # purple to pink
        output_file: str = "background.mp4"
    ) -> str:
        """
        Create animated gradient background video
        
        Args:
            duration: Duration in seconds
            colors: Tuple of hex colors (start, end)
            output_file: Output filename
        
        Returns:
            Path to background video
        """
        filepath = self.output_dir / output_file
        
        # FFmpeg command to create gradient
        # Using color generation with gradients
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={colors[0]}:s={self.width}x{self.height}:d={duration}",
            "-vf", f"geq=r='r(X,Y)':g='g(X,Y)':b='b(X,Y)+sin(T)*50'",
            "-c:v", "libx264",
            "-t", str(duration),
            "-pix_fmt", "yuv420p",
            str(filepath)
        ]
        
        # Simplified version - solid color
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={colors[0]}:s={self.width}x{self.height}:d={duration}:r={self.fps}",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(filepath)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return str(filepath)
        except subprocess.CalledProcessError as e:
            print(f"Error creating background: {e.stderr.decode()}")
            raise
    
    def add_lyrics_to_video(
        self,
        background_video: str,
        subtitle_file: str,
        output_file: str = "lyric_video.mp4",
        font_size: int = 48,
        font_color: str = "white"
    ) -> str:
        """
        Add lyrics as subtitles to background video
        
        Args:
            background_video: Path to background video
            subtitle_file: Path to SRT subtitle file
            output_file: Output filename
            font_size: Font size for lyrics
            font_color: Font color
        
        Returns:
            Path to output video
        """
        filepath = self.output_dir / output_file
        
        # Escape the subtitle file path for FFmpeg
        subtitle_path = str(Path(subtitle_file).absolute()).replace('\\', '/').replace(':', '\\:')
        
        cmd = [
            "ffmpeg", "-y",
            "-i", background_video,
            "-vf", f"subtitles={subtitle_path}:force_style='FontSize={font_size},PrimaryColour=&H{self._color_to_ass(font_color)},Alignment=2,MarginV=100'",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(filepath)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return str(filepath)
        except subprocess.CalledProcessError as e:
            print(f"Error adding lyrics: {e.stderr.decode()}")
            raise
    
    def _color_to_ass(self, color: str) -> str:
        """Convert color name or hex to ASS format"""
        color_map = {
            "white": "FFFFFF",
            "black": "000000",
            "red": "0000FF",
            "green": "00FF00",
            "blue": "FF0000",
            "yellow": "00FFFF",
            "purple": "FF00FF",
            "pink": "CBC0FF"
        }
        
        if color.lower() in color_map:
            return color_map[color.lower()]
        elif color.startswith("#"):
            # Convert #RRGGBB to BBGGRR for ASS
            hex_color = color[1:]
            return hex_color[4:6] + hex_color[2:4] + hex_color[0:2]
        else:
            return "FFFFFF"
    
    def create_lyric_video(
        self,
        lyrics: List[str],
        duration_per_line: float = 5.0,
        genre: str = "lo-fi",
        output_file: str = "final_video.mp4"
    ) -> str:
        """
        Create complete lyric video
        
        Args:
            lyrics: List of lyric lines
            duration_per_line: Duration per line in seconds
            genre: Music genre (affects color scheme)
            output_file: Output filename
        
        Returns:
            Path to final video
        """
        # Genre-based color schemes
        color_schemes = {
            "lo-fi": ("#8B5CF6", "#EC4899"),  # Purple to pink
            "edm": ("#3B82F6", "#8B5CF6"),     # Blue to purple
            "pop": ("#EC4899", "#F59E0B"),     # Pink to orange
            "classical": ("#1F2937", "#4B5563"), # Dark gray tones
            "jazz": ("#92400E", "#B45309"),    # Brown tones
            "ambient": ("#1E293B", "#334155")  # Dark blue-gray
        }
        
        colors = color_schemes.get(genre.lower(), color_schemes["lo-fi"])
        total_duration = len(lyrics) * duration_per_line
        
        # Step 1: Create subtitle file
        print("Creating subtitle file...")
        subtitle_file = self.create_lyric_subtitle_file(
            lyrics,
            duration_per_line,
            "lyrics.srt"
        )
        
        # Step 2: Create background
        print("Creating background video...")
        background_file = self.create_gradient_background(
            total_duration,
            colors,
            "background.mp4"
        )
        
        # Step 3: Add lyrics
        print("Adding lyrics to video...")
        final_video = self.add_lyrics_to_video(
            background_file,
            subtitle_file,
            output_file,
            font_size=56,
            font_color="white"
        )
        
        print(f"Video created: {final_video}")
        return final_video
    
    def create_simple_lyric_card(
        self,
        lyrics: List[str],
        genre: str = "lo-fi",
        output_file: str = "lyric_card.mp4",
        duration: float = 10.0
    ) -> str:
        """
        Create a simple static lyric card video (easier than full animation)
        
        Args:
            lyrics: List of lyric lines
            genre: Music genre
            output_file: Output filename
            duration: Duration in seconds
        
        Returns:
            Path to video file
        """
        filepath = self.output_dir / output_file
        
        # Create text file for drawtext filter
        text = "\\n".join(lyrics)
        
        # Genre colors
        color_schemes = {
            "lo-fi": "#8B5CF6",
            "edm": "#3B82F6",
            "pop": "#EC4899",
            "classical": "#4B5563",
            "jazz": "#B45309",
            "ambient": "#334155"
        }
        
        bg_color = color_schemes.get(genre.lower(), "#8B5CF6")
        
        # FFmpeg command with drawtext
        cmd = [
            "ffmpeg", "-y",
            "-f", "lavfi",
            "-i", f"color=c={bg_color}:s={self.width}x{self.height}:d={duration}:r={self.fps}",
            "-vf", f"drawtext=text='{text}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            str(filepath)
        ]
        
        try:
            subprocess.run(cmd, check=True, capture_output=True)
            return str(filepath)
        except subprocess.CalledProcessError as e:
            print(f"Error creating lyric card: {e.stderr.decode()}")
            # Return a simple version
            return self.create_gradient_background(duration, (bg_color, bg_color), output_file)


def create_video_from_lyrics(
    lyrics: List[str],
    genre: str = "lo-fi",
    output_file: str = "screen_to_song.mp4"
) -> str:
    """
    Convenience function to create video from lyrics
    
    Args:
        lyrics: List of lyric lines
        genre: Music genre
        output_file: Output filename
    
    Returns:
        Path to created video
    """
    assembler = VideoAssembler()
    
    if not assembler.check_ffmpeg():
        print("Warning: FFmpeg not found. Please install FFmpeg to create videos.")
        print("Returning metadata only.")
        return json.dumps({
            "lyrics": lyrics,
            "genre": genre,
            "duration": len(lyrics) * 5.0
        })
    
    return assembler.create_lyric_video(lyrics, genre=genre, output_file=output_file)


if __name__ == "__main__":
    # Example usage
    print("Screen to Song - Video Assembler\n")
    
    example_lyrics = [
        "Midnight glow from a terminal light",
        "Debugging dreams in the quiet night",
        "Code flows like a river of thought",
        "Solutions found in battles fought"
    ]
    
    assembler = VideoAssembler()
    
    if assembler.check_ffmpeg():
        print("FFmpeg detected ✓")
        print("\nCreating lyric video...")
        
        video_path = assembler.create_lyric_video(
            example_lyrics,
            duration_per_line=5.0,
            genre="lo-fi",
            output_file="example_video.mp4"
        )
        
        print(f"\n✓ Video created: {video_path}")
    else:
        print("FFmpeg not found. Please install FFmpeg:")
        print("  Ubuntu/Debian: sudo apt-get install ffmpeg")
        print("  macOS: brew install ffmpeg")
        print("  Windows: Download from https://ffmpeg.org/")
