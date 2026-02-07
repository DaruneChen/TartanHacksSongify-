"""
Screen to Song - Complete Pipeline
End-to-end integration of screen capture → analysis → lyrics → music → video
"""

import os
import sys
import json
import time
from pathlib import Path
from typing import List, Dict, Optional
import argparse

# Add scripts directory to path
sys.path.append(str(Path(__file__).parent))

from music_generator import MusicGenerator, generate_music_for_scene
from video_assembler import VideoAssembler, create_video_from_lyrics


class ScreenToSongPipeline:
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.music_generator = MusicGenerator(str(self.output_dir / "music"))
        self.video_assembler = VideoAssembler(str(self.output_dir / "video"))
        
        self.session_data = {
            "start_time": time.time(),
            "scenes": [],
            "lyrics": [],
            "music_metadata": {},
            "video_path": None
        }
    
    def add_scene(self, context: Dict, lyrics: List[str]):
        """
        Add a scene with context and lyrics
        
        Args:
            context: Scene context dictionary (mood, activity, genre, etc.)
            lyrics: List of lyric lines for this scene
        """
        scene = {
            "timestamp": time.time(),
            "context": context,
            "lyrics": lyrics,
            "genre": context.get("suggested_genre", "lo-fi"),
            "energy_level": context.get("energy_level", 3)
        }
        
        self.session_data["scenes"].append(scene)
        self.session_data["lyrics"].extend(lyrics)
        
        print(f"✓ Scene added: {context.get('activity', 'unknown')} ({context.get('mood', 'neutral')})")
    
    def generate_music(self) -> Dict:
        """
        Generate music metadata for all scenes
        
        Returns:
            Music sequence metadata
        """
        print("\n🎵 Generating music sequence...")
        
        scenes_for_music = [
            {
                "genre": scene["genre"],
                "energy_level": scene["energy_level"],
                "duration": 30  # 30 seconds per scene
            }
            for scene in self.session_data["scenes"]
        ]
        
        sequence = self.music_generator.create_music_sequence(scenes_for_music)
        self.session_data["music_metadata"] = sequence
        
        # Export metadata
        metadata_path = self.music_generator.export_metadata(
            sequence,
            "session_music.json"
        )
        
        print(f"✓ Music metadata generated: {metadata_path}")
        print(f"  Total duration: {sequence['total_duration']}s")
        print(f"  Scenes: {sequence['scene_count']}")
        
        return sequence
    
    def create_video(self, output_filename: str = "screen_to_song_final.mp4") -> Optional[str]:
        """
        Create final lyric video
        
        Args:
            output_filename: Name for output video file
        
        Returns:
            Path to video file or None if failed
        """
        if not self.session_data["lyrics"]:
            print("⚠ No lyrics to create video")
            return None
        
        print("\n🎬 Creating lyric video...")
        
        # Determine predominant genre
        genres = [scene["genre"] for scene in self.session_data["scenes"]]
        predominant_genre = max(set(genres), key=genres.count)
        
        try:
            video_path = self.video_assembler.create_lyric_video(
                self.session_data["lyrics"],
                duration_per_line=5.0,
                genre=predominant_genre,
                output_file=output_filename
            )
            
            self.session_data["video_path"] = video_path
            print(f"✓ Video created: {video_path}")
            return video_path
            
        except Exception as e:
            print(f"✗ Video creation failed: {e}")
            return None
    
    def export_session_data(self, filename: str = "session_data.json") -> str:
        """
        Export complete session data
        
        Args:
            filename: Output filename
        
        Returns:
            Path to exported file
        """
        filepath = self.output_dir / filename
        
        export_data = {
            **self.session_data,
            "end_time": time.time(),
            "duration": time.time() - self.session_data["start_time"],
            "total_scenes": len(self.session_data["scenes"]),
            "total_lyrics": len(self.session_data["lyrics"])
        }
        
        with open(filepath, 'w') as f:
            json.dump(export_data, f, indent=2)
        
        print(f"\n✓ Session data exported: {filepath}")
        return str(filepath)
    
    def print_summary(self):
        """Print session summary"""
        print("\n" + "="*60)
        print("SESSION SUMMARY")
        print("="*60)
        print(f"Total Scenes: {len(self.session_data['scenes'])}")
        print(f"Total Lyrics: {len(self.session_data['lyrics'])} lines")
        print(f"Duration: {time.time() - self.session_data['start_time']:.1f}s")
        
        if self.session_data["scenes"]:
            print("\nScenes:")
            for i, scene in enumerate(self.session_data["scenes"], 1):
                ctx = scene["context"]
                print(f"  {i}. {ctx.get('activity', 'Unknown')} - "
                      f"{ctx.get('mood', 'neutral')} - "
                      f"{scene['genre']}")
        
        print("\nGenerated Files:")
        if self.session_data.get("music_metadata"):
            print(f"  - Music metadata")
        if self.session_data.get("video_path"):
            print(f"  - Video: {self.session_data['video_path']}")
        
        print("="*60 + "\n")


def demo_pipeline():
    """
    Demo of the complete pipeline with mock data
    """
    print("🎸 Screen to Song - Complete Pipeline Demo\n")
    
    # Initialize pipeline
    pipeline = ScreenToSongPipeline("./demo_output")
    
    # Mock scenes
    demo_scenes = [
        {
            "context": {
                "mood": "focused",
                "activity": "coding",
                "objects": ["laptop", "coffee", "code editor"],
                "suggested_genre": "lo-fi",
                "energy_level": 3,
                "description": "Developer coding in a dark IDE"
            },
            "lyrics": [
                "Midnight glow from a terminal light",
                "Debugging dreams in the quiet night",
                "Code flows like a river of thought",
                "Solutions found in battles fought"
            ]
        },
        {
            "context": {
                "mood": "energetic",
                "activity": "gaming",
                "objects": ["monitor", "keyboard", "headset"],
                "suggested_genre": "edm",
                "energy_level": 5,
                "description": "Intense gaming session"
            },
            "lyrics": [
                "Pixels dance across the screen",
                "Victory's the sweetest thing I've seen",
                "Adrenaline pumping through my veins",
                "Level up, breaking all the chains"
            ]
        },
        {
            "context": {
                "mood": "relaxed",
                "activity": "browsing",
                "objects": ["browser", "social media", "coffee"],
                "suggested_genre": "pop",
                "energy_level": 2,
                "description": "Casual social media browsing"
            },
            "lyrics": [
                "Scrolling through the endless feed",
                "Finding stories that I need",
                "Connections made in digital space",
                "Every click a new embrace"
            ]
        }
    ]
    
    # Add scenes
    print("📝 Adding scenes...\n")
    for scene in demo_scenes:
        pipeline.add_scene(scene["context"], scene["lyrics"])
        time.sleep(0.5)  # Simulate time between captures
    
    # Generate music
    pipeline.generate_music()
    
    # Create video
    pipeline.create_video("demo_final.mp4")
    
    # Export session data
    pipeline.export_session_data("demo_session.json")
    
    # Print summary
    pipeline.print_summary()
    
    print("✨ Demo complete! Check the ./demo_output directory for results.\n")


def main():
    parser = argparse.ArgumentParser(
        description="Screen to Song - Complete Pipeline"
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Run demo with mock data"
    )
    parser.add_argument(
        "--session-file",
        type=str,
        help="Load session from JSON file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./output",
        help="Output directory"
    )
    
    args = parser.parse_args()
    
    if args.demo:
        demo_pipeline()
    elif args.session_file:
        # Load and process existing session
        with open(args.session_file, 'r') as f:
            session_data = json.load(f)
        
        pipeline = ScreenToSongPipeline(args.output_dir)
        
        # Add scenes from file
        for scene in session_data.get("scenes", []):
            pipeline.add_scene(scene["context"], scene["lyrics"])
        
        # Generate outputs
        pipeline.generate_music()
        pipeline.create_video()
        pipeline.export_session_data()
        pipeline.print_summary()
    else:
        print("Screen to Song Pipeline")
        print("\nUsage:")
        print("  --demo              Run demo with mock data")
        print("  --session-file FILE Load and process session file")
        print("  --output-dir DIR    Set output directory")
        print("\nExample:")
        print("  python pipeline.py --demo")


if __name__ == "__main__":
    main()
