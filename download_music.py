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
    """Use yt-dlp to find the first video URL from YouTube search and extract metadata."""
    search_query = f"ytsearch1:{artist_name} {song_name} official music video"
    
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": False,  # Allow full metadata extraction
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(search_query, download=False)

    if "entries" in info and info["entries"]:
        video_info = info["entries"][0]
        metadata = {
            "url": video_info.get("webpage_url"),
            "title": video_info.get("title"),
            "uploader": video_info.get("uploader"),
            "duration": video_info.get("duration"),
            "views": video_info.get("view_count"),
            "like_count": video_info.get("like_count"),
            "release_date": video_info.get("release_date"),
            "thumbnails": video_info.get("thumbnail"),
            "tags": video_info.get("tags"),
            "description": video_info.get("description"),
        }
        return metadata

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

def save_metadata(song_id, metadata):
    """Create missing columns if necessary and save metadata to the database and JSON file."""
    # Set default values for metadata to handle errors
    default_metadata = {
        "url": "",
        "uploader": "",
        "duration": 0,
        "views": 0,
        "like_count": 0,
        "release_date": "",
        "thumbnails": "",
        "tags": [],
        "description": ""
    }
    
    # Use default values for any missing keys in metadata
    for key, default_value in default_metadata.items():
        if key not in metadata or metadata[key] is None:
            metadata[key] = default_value
    
    # Update database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Ensure necessary columns exist
    columns_to_add = {
        "youtube_url": "TEXT",
        "uploader": "TEXT",
        "duration": "INTEGER",
        "views": "INTEGER",
        "like_count": "INTEGER",
        "release_date": "TEXT",
        "thumbnail": "TEXT",
        "tags": "TEXT",
        "description": "TEXT"  # Added description column
    }

    # Check and add missing columns
    try:
        cursor.execute("PRAGMA table_info(hot100)")
        existing_columns = {col[1] for col in cursor.fetchall()}

        for column, col_type in columns_to_add.items():
            if column not in existing_columns:
                cursor.execute(f"ALTER TABLE hot100 ADD COLUMN {column} {col_type}")
                print(f"Added column: {column}")

        # Update metadata in the table
        query = """
        UPDATE hot100
        SET youtube_url = ?, uploader = ?, duration = ?, views = ?, like_count = ?, 
            release_date = ?, thumbnail = ?, tags = ?, description = ?
        WHERE id = ?
        """
        cursor.execute(query, (
            metadata["url"], metadata["uploader"], metadata["duration"], metadata["views"],
            metadata["like_count"], metadata["release_date"], metadata["thumbnails"],
            json.dumps(metadata["tags"]), metadata.get("description", ""), song_id
        ))

        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()
    
    # Update JSON metadata file
    json_path = os.path.join("assets", "meta", f"{song_id}.json")
    try:
        # Read existing JSON file if it exists
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)
        else:
            # Create new JSON data if file doesn't exist
            json_data = {"id": song_id}
            
        # Update JSON with new metadata
        json_data.update({
            "youtube_url": metadata["url"],
            "uploader": metadata["uploader"],
            "duration": metadata["duration"],
            "views": metadata["views"],
            "like_count": metadata["like_count"],
            "release_date": metadata["release_date"],
            "thumbnail": metadata["thumbnails"],
            "tags": metadata["tags"],
            "description": metadata.get("description", "")
        })
        
        # Write updated JSON back to file
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4)
        
        print(f"Updated metadata JSON file: {json_path}")
    except Exception as e:
        print(f"Error updating JSON metadata file: {e}")


def process_songs():
    """Fetch songs from the database and process them."""
    songs = fetch_songs_from_db()
    
    if not songs:
        print("No songs found in the database.")
        return
    
    results = []
    for song_id, artist_name, song_name in songs:
        print(f"\nSearching for: {artist_name} - {song_name}")
        
        metadata = search_youtube(artist_name, song_name)
        video_url = metadata["url"]
        if not video_url:
            results.append(f"No results found for {artist_name} - {song_name}")
            continue
        
        print(f"Found video: {video_url}")
        result = download_audio(video_url, song_id)
        results.append(f"ID: {song_id} | {artist_name} - {song_name}\n{result}\n")
        print("Saving metadata")
        save_metadata(song_id=song_id, metadata=metadata)
    
    return "\n".join(results)

def main():
    print("Starting YouTube to MP3 downloader...")
    print("Fetching songs from the database...")
    results = process_songs()
    print(results)

if __name__ == "__main__":
    main()
