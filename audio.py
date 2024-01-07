from pygame import mixer
import os
import random
def playMusic():
    song_files = [f for f in os.listdir("data/music") if f.endswith(".mp3")]
    if song_files:
        random_song = os.path.join("data/music", random.choice(song_files))
        mixer.music.load(random_song)
        mixer.music.play(-1,)  # -1 makes the music loop indefinitely
        mixer.music.set_volume(0.5)