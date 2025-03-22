import os
import json
import sqlite3
import yt_dlp
from pathlib import Path
import time
import shutil
import base64

DB_PATH = "hot100.db"

def ensure_default_image_exists():
    """Create a default image if it doesn't exist."""
    default_img_path = Path("assets/default.jpg")
    
    if not default_img_path.exists():
        print("Creating default image file...")
        # Create the assets directory if it doesn't exist
        os.makedirs("assets", exist_ok=True)
        
        try:
            # Simple base64 encoded default album art (a plain gray square with music note)
            default_img_base64 = """
            /9j/4AAQSkZJRgABAQEAYABgAAD/4QBoRXhpZgAATU0AKgAAAAgABAEaAAUAAAABAAAAPgEbAAUA
            AAABAAAARgEoAAMAAAABAAIAAAExAAIAAAARAAAATgAAAAAAAABgAAAAAQAAAGAAAAABcGFpbnQu
            bmV0IDQuMy4xMgAA/9sAQwAEAgMDAwIEAwMDBAQEBAUJBgUFBQULCAgGCQ0LDQ0NCwwMDhAUEQ4P
            Ew8MDBIYEhMVFhcXFw4RGRsZFhoUFhcW/9sAQwEEBAQFBQUKBgYKFg8MDxYWFhYWFhYWFhYWFhYW
            FhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYWFhYW/8AAEQgAyADIAwEiAAIRAQMRAf/E
            AB8AAAEFAQEBAQEBAAAAAAAAAAABAgMEBQYHCAkKC//EALUQAAIBAwMCBAMFBQQEAAABfQECAwAE
            EQUSITFBBhNRYQcicRQygZGhCCNCscEVUtHwJDNicoIJChYXGBkaJSYnKCkqNDU2Nzg5OkNERUZH
            SElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6g4SFhoeIiYqSk5SVlpeYmZqio6Slpqeoqaqys7S1
            tre4ubrCw8TFxsfIycrS09TV1tfY2drh4uPk5ebn6Onq8fLz9PX29/j5+v/EAB8BAAMBAQEBAQEB
            AQEAAAAAAAABAgMEBQYHCAkKC//EALURAAIBAgQEAwQHBQQEAAECdwABAgMRBAUhMQYSQVEHYXET
            IjKBCBRCkaGxwQkjM1LwFWJy0QoWJDThJfEXGBkaJicoKSo1Njc4OTpDREVGR0hJSlNUVVZXWFla
            Y2RlZmdoaWpzdHV2d3h5eoKDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXG
            x8jJytLT1NXW19jZ2uLj5OXm5+jp6vLz9PX29/j5+v/aAAwDAQACEQMRAD8A9KooooAKKKKACiii
            gAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKA
            CiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK
            KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoo
            ooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiii
            gAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKA
            CiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK
            KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoo
            ooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiii
            gAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKA
            CiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAK
            KKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAoo
            ooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiii
            gAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKA
            CiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooAKKKKACiiigAooooA//9k=
            """
            
            # Write base64 encoded default image to file
            img_data = base64.b64decode(default_img_base64)
            with open(default_img_path, 'wb') as f:
                f.write(img_data)
                
            print(f"Created default image at {default_img_path}")
        except Exception as e:
            print(f"Error creating default image: {e}")
            
            # As a fallback, create an empty file
            try:
                with open(default_img_path, 'wb') as f:
                    # Create a simple colored square as fallback
                    f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc0\x00\x11\x08\x00(\x00(\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xfe\xfe(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00(\xa2\x8a\x00')
                print("Created simple fallback image")
            except Exception:
                print("Failed to create even a simple default image")

def fetch_songs_from_db():
    """Retrieve artist and song names from the database."""
    if not os.path.exists(DB_PATH):
        print("Database not found.")
        return []

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute("SELECT id, artist, song, youtube_url FROM hot100")  
        songs = cursor.fetchall()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        songs = []
    finally:
        conn.close()
    
    return songs  # Returns a list of tuples (id, artist, song, youtube_url)

def song_file_exists(song_id):
    """Check if the song file already exists in assets/music."""
    mp3_path = Path(f"assets/music/{song_id}.mp3")
    return mp3_path.exists()

def metadata_needs_update(song_id, youtube_url):
    """Check if the metadata needs to be updated."""
    # If no youtube_url exists, metadata needs updating
    if not youtube_url:
        return True
        
    # Check if the JSON metadata file exists and has complete info
    json_path = Path(f"assets/meta/{song_id}.json")
    if not json_path.exists():
        return True
        
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
            
        # Check if key metadata fields exist and are not empty
        required_fields = ["youtube_url", "duration", "views"]
        for field in required_fields:
            if field not in metadata or not metadata[field]:
                return True
                
        # Check if metadata is older than 7 days (604800 seconds)
        if "last_updated" in metadata:
            last_updated = metadata["last_updated"]
            current_time = int(time.time())
            if current_time - last_updated > 604800:  # Update metadata weekly
                return True
    except Exception:
        return True
        
    return False

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
            "last_updated": int(time.time())  # Add timestamp for tracking updates
        }
        return metadata

    return None

def cleanup_failed_download(song_id):
    """
    Clean up any assets and database entries for a song that failed to download.
    This removes:
    - Song entry from hot100 database
    - Metadata JSON file from assets/meta
    - Artwork image from assets/imgs
    - Any partially downloaded audio files from assets/music
    """
    print(f"Cleaning up assets for failed download with ID: {song_id}")
    
    # Remove any partial MP3 downloads
    partial_files = list(Path("assets/music").glob(f"{song_id}.*"))
    for file_path in partial_files:
        try:
            file_path.unlink()
            print(f"Deleted partial audio file: {file_path}")
        except Exception as e:
            print(f"Error deleting partial audio file: {e}")
    
    # Remove metadata JSON
    json_path = Path(f"assets/meta/{song_id}.json")
    if json_path.exists():
        try:
            json_path.unlink()
            print(f"Deleted metadata file: {json_path}")
        except Exception as e:
            print(f"Error deleting metadata file: {e}")
    
    # Remove artwork image
    img_path = Path(f"assets/imgs/{song_id}.jpg")
    if img_path.exists():
        try:
            img_path.unlink()
            print(f"Deleted image file: {img_path}")
        except Exception as e:
            print(f"Error deleting image file: {e}")
    
    # Remove database entry
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM hot100 WHERE id = ?", (song_id,))
        conn.commit()
        if cursor.rowcount > 0:
            print(f"Removed database entry for ID: {song_id}")
        else:
            print(f"No database entry found for ID: {song_id}")
    except sqlite3.Error as e:
        print(f"Database error during cleanup: {e}")
    finally:
        conn.close()

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

    success = False
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        expected_file = Path(f"{output_filename}.mp3")
        if expected_file.exists():
            success = True
            return f"Downloaded: {expected_file}"
    
    except Exception as e:
        print(f"Error downloading: {e}")
    
    if not success:
        # Clean up if download failed
        cleanup_failed_download(song_id)
        return "Failed to download. All assets have been cleaned up."

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
        "description": "",
        "last_updated": int(time.time())
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
        "description": "TEXT",  # Added description column
        "last_updated": "INTEGER"  # Add timestamp column
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
            release_date = ?, thumbnail = ?, tags = ?, description = ?, last_updated = ?
        WHERE id = ?
        """
        cursor.execute(query, (
            metadata["url"], metadata["uploader"], metadata["duration"], metadata["views"],
            metadata["like_count"], metadata["release_date"], metadata["thumbnails"],
            json.dumps(metadata["tags"]), metadata.get("description", ""), 
            metadata["last_updated"], song_id
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
            "description": metadata.get("description", ""),
            "last_updated": metadata["last_updated"]
        })
        
        # Write updated JSON back to file
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=4)
        
        print(f"Updated metadata JSON file: {json_path}")
    except Exception as e:
        print(f"Error updating JSON metadata file: {e}")


def process_songs():
    """Fetch songs from the database and process only those that need updating."""
    songs = fetch_songs_from_db()
    
    if not songs:
        print("No songs found in the database.")
        return
    
    results = []
    downloaded_count = 0
    updated_metadata_count = 0
    skipped_count = 0
    failed_count = 0
    
    for song_data in songs:
        song_id = song_data[0]
        artist_name = song_data[1]
        song_name = song_data[2]
        youtube_url = song_data[3] if len(song_data) > 3 else None
        
        print(f"\nProcessing: {artist_name} - {song_name} (ID: {song_id})")
        
        # Check if MP3 already exists
        if song_file_exists(song_id):
            print(f"Audio file already exists for: {artist_name} - {song_name}")
            
            # Check if metadata needs updating
            if metadata_needs_update(song_id, youtube_url):
                print(f"Updating metadata for: {artist_name} - {song_name}")
                metadata_updated = False
                
                if youtube_url:
                    # Use existing URL to fetch fresh metadata
                    try:
                        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
                            info = ydl.extract_info(youtube_url, download=False)
                            metadata = {
                                "url": info.get("webpage_url"),
                                "title": info.get("title"),
                                "uploader": info.get("uploader"),
                                "duration": info.get("duration"),
                                "views": info.get("view_count"),
                                "like_count": info.get("like_count"),
                                "release_date": info.get("release_date"),
                                "thumbnails": info.get("thumbnail"),
                                "tags": info.get("tags"),
                                "description": info.get("description"),
                                "last_updated": int(time.time())
                            }
                            save_metadata(song_id=song_id, metadata=metadata)
                            updated_metadata_count += 1
                            metadata_updated = True
                    except Exception as e:
                        print(f"Error updating metadata from existing URL: {e}")
                
                if not metadata_updated:
                    # Search for the video if no URL exists or prior attempt failed
                    metadata = search_youtube(artist_name, song_name)
                    if metadata:
                        save_metadata(song_id=song_id, metadata=metadata)
                        updated_metadata_count += 1
                    else:
                        print(f"Failed to find metadata for: {artist_name} - {song_name}")
            else:
                print(f"Metadata is up to date for: {artist_name} - {song_name}")
                skipped_count += 1
                
            results.append(f"ID: {song_id} | {artist_name} - {song_name} | Status: Existing audio file")
            continue
            
        # Need to search and download
        print(f"Searching for: {artist_name} - {song_name}")
        metadata = search_youtube(artist_name, song_name)
        
        if not metadata or not metadata["url"]:
            results.append(f"No results found for {artist_name} - {song_name}")
            continue
            
        video_url = metadata["url"]
        print(f"Found video: {video_url}")
        
        # Download the audio
        result = download_audio(video_url, song_id)
        
        if "Failed to download" in result:
            failed_count += 1
            results.append(f"ID: {song_id} | {artist_name} - {song_name}\n{result}\n")
            continue
        
        # If download was successful
        downloaded_count += 1
        
        # Save metadata
        print("Saving metadata")
        try:
            save_metadata(song_id=song_id, metadata=metadata)
            updated_metadata_count += 1
        except Exception as e:
            print(f"Error saving metadata: {e}")
            # Clean up if metadata saving fails
            cleanup_failed_download(song_id)
            failed_count += 1
            results.append(f"ID: {song_id} | {artist_name} - {song_name}\nFailed to save metadata. Assets cleaned up.\n")
            continue
        
        results.append(f"ID: {song_id} | {artist_name} - {song_name}\n{result}\n")
    
    summary = f"\nSummary:\n"
    summary += f"  - Processed {len(songs)} songs\n"
    summary += f"  - Downloaded {downloaded_count} new songs\n"
    summary += f"  - Updated metadata for {updated_metadata_count} songs\n"
    summary += f"  - Skipped {skipped_count} songs (already up to date)\n"
    summary += f"  - Failed and cleaned up {failed_count} songs\n"
    
    return "\n".join(results) + summary

def main():
    print("Starting YouTube to MP3 downloader...")
    
    # Ensure directories exist
    os.makedirs("assets/music", exist_ok=True)
    os.makedirs("assets/meta", exist_ok=True)
    os.makedirs("assets/imgs", exist_ok=True)
    
    # Ensure default image exists
    ensure_default_image_exists()
    
    print("Fetching songs from the database...")
    results = process_songs()
    print(results)

if __name__ == "__main__":
    main()
