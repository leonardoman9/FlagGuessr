from pygame import mixer
import os
import random
from scripts import resource_path

# Music directory
music_dir = resource_path("data/music")

# Global variables for music state
current_song = None
music_paused = False
music_volume = 0.5

def init_mixer():
    """Initialize pygame mixer"""
    try:
        mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
        print("Audio mixer initialized successfully")
        return True
    except Exception as e:
        print(f"Error initializing audio mixer: {e}")
        return False

def get_available_songs():
    """Get list of available music files"""
    try:
        song_files = [f for f in os.listdir(music_dir) if f.endswith(".mp3")]
        return song_files
    except Exception as e:
        print(f"Error loading song list: {e}")
        return []

def get_song_names():
    """Get cleaned song names for display"""
    songs = get_available_songs()
    # Clean up filenames for display (remove extension, clean up names)
    display_names = []
    for song in songs:
        name = os.path.splitext(song)[0]  # Remove .mp3
        # Clean up common patterns
        name = name.replace("OST - ", "").replace("OST_ ", "")
        name = name.replace("_ ", " - ").replace("__", " - ")
        display_names.append(name)
    return display_names

def playMusic(song_name=None, random_song=False):
    """Play music - either specific song or random"""
    global current_song, music_paused
    try:
        song_files = get_available_songs()
        if not song_files:
            print("No music files found!")
            return False
            
        if random_song or song_name is None:
            selected_song = random.choice(song_files)
        else:
            # Find song by name (either filename or display name)
            selected_song = None
            song_names = get_song_names()
            
            for i, display_name in enumerate(song_names):
                if song_name.lower() in display_name.lower() or song_name == song_files[i]:
                    selected_song = song_files[i]
                    break
            
            if not selected_song:
                print(f"Song '{song_name}' not found, playing random song")
                selected_song = random.choice(song_files)
        
        song_path = os.path.join(music_dir, selected_song)
        mixer.music.load(song_path)
        mixer.music.play(-1)  # -1 makes the music loop indefinitely
        mixer.music.set_volume(music_volume)
        current_song = selected_song
        music_paused = False
        
        # Get display name
        display_name = os.path.splitext(selected_song)[0]
        display_name = display_name.replace("OST - ", "").replace("OST_ ", "")
        display_name = display_name.replace("_ ", " - ").replace("__", " - ")
        
        print(f"Now playing: '{display_name}'")
        return True
        
    except Exception as e:
        print(f"Error while loading music: {e}")
        return False

def pauseMusic():
    """Pause/unpause music"""
    global music_paused
    try:
        if mixer.music.get_busy() and not music_paused:
            mixer.music.pause()
            music_paused = True
            print("Music paused")
        elif music_paused:
            mixer.music.unpause()
            music_paused = False
            print("Music resumed")
    except Exception as e:
        print(f"Error pausing/resuming music: {e}")

def stopMusic():
    """Stop music completely"""
    global current_song, music_paused
    try:
        mixer.music.stop()
        current_song = None
        music_paused = False
        print("Music stopped")
    except Exception as e:
        print(f"Error stopping music: {e}")

def setVolume(volume):
    """Set music volume (0.0 to 1.0)"""
    global music_volume
    try:
        music_volume = max(0.0, min(1.0, volume))
        mixer.music.set_volume(music_volume)
        print(f"Volume set to {int(music_volume * 100)}%")
    except Exception as e:
        print(f"Error setting volume: {e}")

def is_playing():
    """Check if music is currently playing"""
    return mixer.music.get_busy() and not music_paused

def is_paused():
    """Check if music is paused"""
    return music_paused

def get_current_song():
    """Get currently playing song"""
    return current_song