"""
Music Generation Module
Handles music generation and loop management
"""

import os
import random
from pathlib import Path
from typing import Dict, List
import json

# Genre-based music loops metadata
# In production, these would be actual audio files
MUSIC_LIBRARY = {
    "lo-fi": {
        "loops": [
            {"id": "lofi_1", "bpm": 70, "key": "C", "mood": "chill"},
            {"id": "lofi_2", "bpm": 75, "key": "Am", "mood": "relaxed"},
            {"id": "lofi_3", "bpm": 80, "key": "Dm", "mood": "focused"},
        ],
        "description": "Chill beats for coding and studying"
    },
    "edm": {
        "loops": [
            {"id": "edm_1", "bpm": 128, "key": "Em", "mood": "energetic"},
            {"id": "edm_2", "bpm": 130, "key": "Am", "mood": "intense"},
            {"id": "edm_3", "bpm": 126, "key": "Gm", "mood": "euphoric"},
        ],
        "description": "High energy electronic beats"
    },
    "pop": {
        "loops": [
            {"id": "pop_1", "bpm": 120, "key": "C", "mood": "upbeat"},
            {"id": "pop_2", "bpm": 115, "key": "G", "mood": "happy"},
            {"id": "pop_3", "bpm": 125, "key": "D", "mood": "catchy"},
        ],
        "description": "Catchy pop melodies"
    },
    "classical": {
        "loops": [
            {"id": "classical_1", "bpm": 60, "key": "C", "mood": "elegant"},
            {"id": "classical_2", "bpm": 65, "key": "Am", "mood": "contemplative"},
            {"id": "classical_3", "bpm": 55, "key": "F", "mood": "serene"},
        ],
        "description": "Classical orchestral pieces"
    },
    "jazz": {
        "loops": [
            {"id": "jazz_1", "bpm": 90, "key": "Bb", "mood": "smooth"},
            {"id": "jazz_2", "bpm": 95, "key": "F", "mood": "sophisticated"},
            {"id": "jazz_3", "bpm": 85, "key": "Eb", "mood": "mellow"},
        ],
        "description": "Smooth jazz vibes"
    },
    "ambient": {
        "loops": [
            {"id": "ambient_1", "bpm": 50, "key": "C", "mood": "atmospheric"},
            {"id": "ambient_2", "bpm": 55, "key": "Am", "mood": "dreamy"},
            {"id": "ambient_3", "bpm": 45, "key": "Em", "mood": "spacey"},
        ],
        "description": "Atmospheric soundscapes"
    }
}

class MusicGenerator:
    def __init__(self, output_dir: str = "./music_output"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.current_genre = None
        self.current_loop = None
        
    def get_available_genres(self) -> List[str]:
        """Get list of available music genres"""
        return list(MUSIC_LIBRARY.keys())
    
    def select_loop(self, genre: str, energy_level: int = 3) -> Dict:
        """
        Select appropriate music loop based on genre and energy level
        
        Args:
            genre: Music genre (lo-fi, edm, pop, etc.)
            energy_level: Energy level 1-5
        
        Returns:
            Loop metadata dictionary
        """
        # Normalize genre
        genre = genre.lower().replace("-", "").replace(" ", "")
        
        # Find closest matching genre
        matched_genre = None
        for g in MUSIC_LIBRARY.keys():
            if g.replace("-", "") in genre or genre in g.replace("-", ""):
                matched_genre = g
                break
        
        if not matched_genre:
            matched_genre = "lo-fi"  # Default
        
        loops = MUSIC_LIBRARY[matched_genre]["loops"]
        
        # Select loop based on energy level
        # Higher energy = higher BPM
        sorted_loops = sorted(loops, key=lambda x: x["bpm"])
        
        if energy_level <= 2:
            selected = sorted_loops[0]
        elif energy_level >= 4:
            selected = sorted_loops[-1]
        else:
            selected = sorted_loops[len(sorted_loops) // 2]
        
        self.current_genre = matched_genre
        self.current_loop = selected
        
        return {
            "genre": matched_genre,
            "loop": selected,
            "description": MUSIC_LIBRARY[matched_genre]["description"]
        }
    
    def generate_music_metadata(self, genre: str, energy_level: int, duration: int = 30) -> Dict:
        """
        Generate music metadata for a given genre and energy level
        
        Args:
            genre: Music genre
            energy_level: Energy level 1-5
            duration: Duration in seconds
        
        Returns:
            Music metadata dictionary
        """
        loop_info = self.select_loop(genre, energy_level)
        
        # Calculate number of bars based on BPM and duration
        bpm = loop_info["loop"]["bpm"]
        bars_per_minute = bpm / 4  # Assuming 4/4 time
        total_bars = int((duration / 60) * bars_per_minute)
        
        metadata = {
            "genre": loop_info["genre"],
            "loop_id": loop_info["loop"]["id"],
            "bpm": bpm,
            "key": loop_info["loop"]["key"],
            "mood": loop_info["loop"]["mood"],
            "duration": duration,
            "total_bars": total_bars,
            "energy_level": energy_level,
            "description": loop_info["description"]
        }
        
        return metadata
    
    def create_music_sequence(self, scenes: List[Dict]) -> Dict:
        """
        Create a music sequence from multiple scenes
        
        Args:
            scenes: List of scene dictionaries with genre and energy_level
        
        Returns:
            Music sequence metadata
        """
        sequence = []
        total_duration = 0
        
        for i, scene in enumerate(scenes):
            genre = scene.get("genre", "lo-fi")
            energy = scene.get("energy_level", 3)
            duration = scene.get("duration", 30)
            
            metadata = self.generate_music_metadata(genre, energy, duration)
            metadata["scene_index"] = i
            metadata["start_time"] = total_duration
            
            sequence.append(metadata)
            total_duration += duration
        
        return {
            "total_duration": total_duration,
            "scene_count": len(scenes),
            "sequence": sequence
        }
    
    def export_metadata(self, metadata: Dict, filename: str = "music_sequence.json"):
        """Export music metadata to JSON file"""
        filepath = self.output_dir / filename
        with open(filepath, 'w') as f:
            json.dump(metadata, f, indent=2)
        return str(filepath)


# Example usage and API functions
def generate_music_for_scene(genre: str, energy_level: int = 3, duration: int = 30) -> Dict:
    """
    Generate music metadata for a single scene
    
    Args:
        genre: Music genre
        energy_level: Energy level 1-5
        duration: Duration in seconds
    
    Returns:
        Music metadata
    """
    generator = MusicGenerator()
    return generator.generate_music_metadata(genre, energy_level, duration)


def create_soundtrack(scenes: List[Dict], output_file: str = "soundtrack.json") -> str:
    """
    Create a complete soundtrack from multiple scenes
    
    Args:
        scenes: List of scene dictionaries
        output_file: Output filename
    
    Returns:
        Path to exported metadata file
    """
    generator = MusicGenerator()
    sequence = generator.create_music_sequence(scenes)
    return generator.export_metadata(sequence, output_file)


if __name__ == "__main__":
    # Example: Generate music for different scenes
    print("Screen to Song - Music Generator\n")
    
    # Example scenes
    example_scenes = [
        {"genre": "lo-fi", "energy_level": 2, "duration": 30},
        {"genre": "edm", "energy_level": 5, "duration": 30},
        {"genre": "jazz", "energy_level": 3, "duration": 30},
    ]
    
    generator = MusicGenerator()
    
    print("Available genres:", generator.get_available_genres())
    print()
    
    # Generate music for each scene
    for i, scene in enumerate(example_scenes):
        print(f"Scene {i + 1}:")
        metadata = generator.generate_music_metadata(
            scene["genre"],
            scene["energy_level"],
            scene["duration"]
        )
        print(json.dumps(metadata, indent=2))
        print()
    
    # Create full sequence
    print("Creating full soundtrack sequence...")
    sequence = generator.create_music_sequence(example_scenes)
    filepath = generator.export_metadata(sequence, "example_soundtrack.json")
    print(f"Exported to: {filepath}")
