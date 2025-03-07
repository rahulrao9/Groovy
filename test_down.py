import os
import json
import sqlite3
import yt_dlp
from pathlib import Path

DB_PATH = "hot100.db"

def fetch_songs_from_db():
    """Retrieve artist and song names from the database."""
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, artist, song FROM hot100")  
        songs = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        songs = []
    finally:
        conn.close()
    
    return songs  # Returns a list of tuples (id, artist, song)

def search_youtube(artist_name, song_name):
    """Use yt-dlp to find the first video URL from YouTube search."""
    search_query = f"ytsearch1:{artist_name} {song_name} official music video"
    
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,  # Get only video links, no downloading
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)

    if "entries" in info and info["entries"]:
        return info["entries"][0]["url"]

    return None

def download_audio(video_url, song_id):
    """Download audio from YouTube using yt-dlp and save in assets/music folder."""
    os.makedirs("assets/music", exist_ok=True)
    
    output_filename = f"assets/music/{song_id}"  # Use database ID as filename

    ydl_opts = {
        "format": "bestaudio/best",
        "postprocessors": [{"key": "FFmpegExtractAudio", "preferredcodec": "mp3", "preferredquality": "192"}],
        "outtmpl": f"{output_filename}.%(ext)s",
        "quiet": False,
        "nocheckcertificate": True,  # Skip SSL verification
        "retries": 5,
        "geo_bypass": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        expected_file = Path(f"{output_filename}.mp3")
        if expected_file.exists():
            return f"Downloaded: {expected_file}"
    
    except Exception as e:
        print(f"Error downloading: {e}")
    
    return "Failed to download."

def process_songs():
    """Fetch songs from the database and process them."""
    songs = fetch_songs_from_db()
    
    if not songs:
        print("No songs found in the database.")
        return
    
    results = []
    for song_id, artist_name, song_name in songs:
        print(f"\nSearching for: {artist_name} - {song_name}")
        
        video_url = search_youtube(artist_name, song_name)
        if not video_url:
            results.append(f"No results found for {artist_name} - {song_name}")
            continue
        
        print(f"Found video: {video_url}")
        result = download_audio(video_url, song_id)
        results.append(f"ID: {song_id} | {artist_name} - {song_name}\n{result}\n")
    
    return "\n".join(results)

def main():
    print("Starting YouTube to MP3 downloader...")
    print("Fetching songs from the database...")
    results = process_songs()
    print(results)

if __name__ == "__main__":
    main()
