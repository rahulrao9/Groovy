import os
import json
import requests
import uuid
import sqlite3
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Database setup from environment variables
DB_PATH = os.getenv("DB_PATH", "hot100.db")

def init_db():
    """Initialize SQLite database and create table if it doesn't exist."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Create the table with the new 'count' column
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hot100 (
            id TEXT PRIMARY KEY,
            artist TEXT,
            song TEXT,
            count INTEGER DEFAULT 0,  -- New column to track occurrences
            UNIQUE(artist, song)  -- Ensure no duplicate artist+song
        )
    """)

    # Ensure 'count' column exists for older versions of the database
    cursor.execute("PRAGMA table_info(hot100)")
    columns = [col[1] for col in cursor.fetchall()]
    if "count" not in columns:
        cursor.execute("ALTER TABLE hot100 ADD COLUMN count INTEGER DEFAULT 0")
    
    conn.commit()
    conn.close()

def song_exists(artist, song):
    """Check if the song is already in the database and update its counter."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id, count FROM hot100 WHERE artist = ? AND song = ?", (artist, song))
    result = cursor.fetchone()
    
    if result:
        # Increment the count for existing songs
        song_id, current_count = result
        cursor.execute("UPDATE hot100 SET count = ? WHERE id = ?", (current_count + 1, song_id))
        conn.commit()
    
    conn.close()
    return result[0] if result else None  # Returns song_id if exists, None otherwise

def save_to_db(unique_id, artist, song):
    """Save a new entry to the database."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO hot100 (id, artist, song, count) VALUES (?, ?, ?, ?)", (unique_id, artist, song, 0))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Skip duplicates
    finally:
        conn.close()

def fetch_hot_100(limit=10):
    url = "https://www.billboard.com/charts/hot-100/"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print("Failed to retrieve data")
        return
    
    soup = BeautifulSoup(response.text, "html.parser")
    chart_items = soup.find_all("div", class_="o-chart-results-list-row-container")
    
    os.makedirs("assets/meta", exist_ok=True)
    os.makedirs("assets/imgs", exist_ok=True)
    
    count = 0
    new_songs = 0
    updated_songs = 0
    
    for item in chart_items:
        # if count >= limit:
        #     break
        
        # Locate the correct li tag containing song and artist info
        details_tag = item.find("li", class_="o-chart-results-list__item // lrv-u-flex-grow-1 lrv-u-flex lrv-u-flex-direction-column lrv-u-justify-content-center lrv-u-border-b-1 u-border-b-0@mobile-max lrv-u-border-color-grey-light lrv-u-padding-l-050 lrv-u-padding-l-1@mobile-max")
        
        if details_tag:
            # Extract song title
            song_tag = details_tag.find("h3")
            song_name = song_tag.text.strip() if song_tag else None
            
            # Extract artist name
            artist_tag = details_tag.find("span")
            artist_name = artist_tag.text.strip() if artist_tag else None
        else:
            song_name = None
            artist_name = None
        
        # Skip entries with missing data
        if not song_name or not artist_name:
            continue
        
        # Check if the song already exists in the database
        existing_song_id = song_exists(artist_name, song_name)
        if existing_song_id:
            print(f"Song already exists: {artist_name} - {song_name} (ID: {existing_song_id})")
            updated_songs += 1
            count += 1
            continue
        
        # Extract image URL
        img_tag = item.find("img", class_="c-lazy-image__img")
        img_url = img_tag["src"] if img_tag else None
        
        # Generate unique UUID
        unique_id = str(uuid.uuid4())  # Generate a unique identifier
        
        # Save metadata with UUID
        meta_path = f"assets/meta/{unique_id}.json"
        meta_data = {"id": unique_id, "artist": artist_name, "song": song_name}
        with open(meta_path, "w", encoding="utf-8") as f:
            json.dump(meta_data, f, indent=4)
        print(f"Saved metadata: {meta_path}")
        
        # Save image with UUID
        if img_url:
            img_path = f"assets/imgs/{unique_id}.jpg"
            img_response = requests.get(img_url, headers=headers)
            if img_response.status_code == 200:
                with open(img_path, "wb") as img_file:
                    img_file.write(img_response.content)
                print(f"Saved image: {img_path}")
        
        # Save to database
        save_to_db(unique_id, artist_name, song_name)
        new_songs += 1
        count += 1
    
    print(f"\nSummary: Found {count} songs in Hot 100")
    print(f"  - {new_songs} new songs added to database")
    print(f"  - {updated_songs} existing songs updated")

if __name__ == "__main__":
    init_db()  # Initialize the database
    fetch_hot_100(limit=20)
