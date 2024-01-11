from pygame import mixer
import os
import random

def playMusic(play=False):
    try:
        song_files = [f for f in os.listdir("data/music") if f.endswith(".mp3")]
        if song_files and play:
            x = random.choice(song_files)
            random_song = os.path.join("data/music", x)
            mixer.music.load(random_song)
            mixer.music.play(-1,)  # -1 makes the music loop indefinitely
            mixer.music.set_volume(0.5)
            print(f"Now playing: '{x}'")
    except Exception as e:
        print(f"Error while loading music:\n {e}")

def stopMusic():
    mixer.music.pause()