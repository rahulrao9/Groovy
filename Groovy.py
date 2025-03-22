import os
import json
import sqlite3
import streamlit as st
from PIL import Image
import pandas as pd
# Import the recommendation functions
from rec import get_recommendations, cal_scores
# Import Firebase configuration and login page
import firebase_config as fb
from login import auth_page

DB_PATH = "hot100.db"
META_DIR = "assets/meta"
IMG_DIR = "assets/imgs"
MUSIC_DIR = "assets/music"
DEFAULT_IMG = "assets/default.jpg"

# Initialize session states for authentication
if 'user_id' not in st.session_state:
    st.session_state.user_id = None
if 'username' not in st.session_state:
    st.session_state.username = None
if 'auth_status' not in st.session_state:
    st.session_state.auth_status = None
if 'page' not in st.session_state:
    st.session_state.page = "login"  # Default page is login

# Check if logged in, if not, show login page
if st.session_state.user_id is None:
    auth_page()
    st.stop()  # Stop execution here if not logged in

# If we got here, user is logged in
# Get user info
if st.session_state.username is None and st.session_state.user_id is not None:
    user_info = fb.get_user_info(st.session_state.user_id)
    if user_info:
        st.session_state.username = user_info.get('username', 'User')

# Custom CSS for styling (fonts & colors)
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600&display=swap');
    
    html, body, [class*="st-"] {
        font-family: 'Poppins', sans-serif;
    }
    
    h1, h2, h3 {
        text-align: center;
        font-weight: 600;
        background: -webkit-linear-gradient(45deg, #ff8a00, #e52e71);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    .album-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
        gap: 10px;
        margin-bottom: 30px;
    }
    
    .album-container img {
        border-radius: 100%;
        width: 170px;
        height: 170px;
        object-fit: cover;
        border: 3px solid #ff8a00;
        transition: transform 0.2s ease-in-out;
    }
    
    .album-container img:hover {
        transform: scale(1.1);
        border-color: #e52e71;
    }
    
    .album-caption {
        font-size: 13px;
        font-weight: bold;
        color: #7d7c7c;
    }

    .stButton > button {
        width: 100px;
        height: 30px;
        font-size: 13px;
        font-weight: bold;
        color: white;
        background: linear-gradient(45deg, #ff8a00, #e52e71);
        border: none;
        border-radius: 20px;
        transition: 0.3s ease-in-out;
    }

    .stButton > button:hover {
        background: linear-gradient(45deg, #e52e71, #ff8a00);
        transform: scale(1.05);
        color: white;
    }

    .now-playing {
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        color: #ff8a00;
    }
    
    .user-info {
        padding: 10px;
        border-radius: 10px;
        background-color: rgba(255,138,0,0.1);
        margin-bottom: 20px;
    }
    
    .logout-btn {
        color: #e52e71;
        font-weight: bold;
        cursor: pointer;
    }
</style>
""", unsafe_allow_html=True)

# Initialize additional session state
if "total_plays" not in st.session_state:
    st.session_state.total_plays = 0
if "recommendations" not in st.session_state:
    st.session_state.recommendations = []
if "current_audio" not in st.session_state:
    st.session_state.current_audio = None
if "last_recommendation_update" not in st.session_state:
    st.session_state.last_recommendation_update = 0
if "needs_rerun" not in st.session_state:
    st.session_state.needs_rerun = False

# Ensure the default image exists
def ensure_assets_exist():
    """Ensure all required directories and default files exist."""
    # Create necessary directories
    os.makedirs(META_DIR, exist_ok=True)
    os.makedirs(IMG_DIR, exist_ok=True)
    os.makedirs(MUSIC_DIR, exist_ok=True)
    
    # Check if default image exists, create a simple one if not
    if not os.path.exists(DEFAULT_IMG):
        try:
            # Create a simple colored square as fallback
            with open(DEFAULT_IMG, 'wb') as f:
                f.write(b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00\xff\xdb\x00C\x00\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xc0\x00\x11\x08\x00(\x00(\x03\x01"\x00\x02\x11\x01\x03\x11\x01\xff\xc4\x00\x1f\x00\x00\x01\x05\x01\x01\x01\x01\x01\x01\x00\x00\x00\x00\x00\x00\x00\x00\x01\x02\x03\x04\x05\x06\x07\x08\t\n\x0b\xff\xc4\x00\xb5\x10\x00\x02\x01\x03\x03\x02\x04\x03\x05\x05\x04\x04\x00\x00\x01}\x01\x02\x03\x00\x04\x11\x05\x12!1A\x06\x13Qa\x07"q\x142\x81\x91\xa1\x08#B\xb1\xc1\x15R\xd1\xf0$3br\x82\t\n\x16\x17\x18\x19\x1a%&\'()*456789:CDEFGHIJSTUVWXYZcdefghijstuvwxyz\x83\x84\x85\x86\x87\x88\x89\x8a\x92\x93\x94\x95\x96\x97\x98\x99\x9a\xa2\xa3\xa4\xa5\xa6\xa7\xa8\xa9\xaa\xb2\xb3\xb4\xb5\xb6\xb7\xb8\xb9\xba\xc2\xc3\xc4\xc5\xc6\xc7\xc8\xc9\xca\xd2\xd3\xd4\xd5\xd6\xd7\xd8\xd9\xda\xe1\xe2\xe3\xe4\xe5\xe6\xe7\xe8\xe9\xea\xf1\xf2\xf3\xf4\xf5\xf6\xf7\xf8\xf9\xfa\xff\xda\x00\x0c\x03\x01\x00\x02\x11\x03\x11\x00?\x00\xfe\xfe(\xa2\x8a\x00')
                print(f"Created default image at {DEFAULT_IMG}")
        except Exception as e:
            print(f"Error creating default image: {e}")

# Run initialization at startup
ensure_assets_exist()

# Load music data
def load_music_data():
    records = []
    if not os.path.exists(META_DIR):
        return records
    for file in os.listdir(META_DIR):
        if file.endswith(".json"):
            try:
                meta_path = os.path.join(META_DIR, file)
                with open(meta_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    song_id = file.split(".")[0]
                    image_path = os.path.join(IMG_DIR, f"{song_id}.jpg")
                    music_path = os.path.join(MUSIC_DIR, f"{song_id}.mp3")
                    
                    # Use default image if the specific one doesn't exist
                    if not os.path.exists(image_path):
                        image_path = DEFAULT_IMG
                        
                    if os.path.exists(music_path):
                        records.append({
                            "id": song_id,
                            "title": data.get("song"),
                            "artist": data.get("artist"),
                            "image": image_path,
                            "audio": music_path
                        })
            except Exception as e:
                print(f"Error loading song metadata for {file}: {e}")
    return records

# Fetch recommendations using the recommendation model
def fetch_recommendations():
    # Load the database into a DataFrame
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql(f"SELECT * FROM hot100;", conn)
    
    # Drop unnecessary columns 
    df.drop(['youtube_url', 'release_date', 'thumbnail', 'description'], axis=1, inplace=True)
    
    # Calculate scores and get recommendations with user-specific data
    user_id = st.session_state.user_id if st.session_state.user_id else None
    recommendations_list = get_recommendations(df, n=5, exclude_played=True, user_id=user_id)
    
    # Convert recommendations to the format used by the UI
    recommendations = []
    for rec in recommendations_list:
        song_id = rec['id']
        image_path = os.path.join(IMG_DIR, f"{song_id}.jpg")
        music_path = os.path.join(MUSIC_DIR, f"{song_id}.mp3")
        
        # Use default image if specific one doesn't exist
        if not os.path.exists(image_path):
            image_path = DEFAULT_IMG
            
        if os.path.exists(music_path):
            recommendations.append({
                "id": song_id,
                "title": rec['song'],
                "artist": rec['artist'],
                "image": image_path,
                "audio": music_path
            })
    return recommendations

# Load music records
music_records = load_music_data()

# Function to handle logout
def logout():
    """Clear session state and log user out."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# Main UI
st.title("🎵 Groovy")

# User Info and Logout
col1, col2 = st.columns([3, 1])
with col1:
    st.markdown(f"<div class='user-info'>👋 Welcome, <b>{st.session_state.username}</b>!</div>", unsafe_allow_html=True)
with col2:
    if st.button("Logout"):
        logout()

# Function to select a song and update play count
def select_song(song_id):
    # Find the song info
    for record in music_records:
        if record["id"] == song_id:
            st.session_state.current_audio = record
            song_info = record
            break
    
    # Update play count in local database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE hot100 SET count = count + 1 WHERE id = ?", (song_id,))
    conn.commit()
    conn.close()
    
    # Update play count in Firebase for the specific user
    if st.session_state.user_id:
        fb.update_play_count(
            st.session_state.user_id, 
            song_id, 
            song_info["artist"], 
            song_info["title"]
        )

    # Increment session play count
    st.session_state.total_plays += 1
    
    # Update recommendations every 10 plays
    if st.session_state.total_plays % 10 == 0 and st.session_state.total_plays > st.session_state.last_recommendation_update:
        st.session_state.recommendations = fetch_recommendations()
        st.session_state.last_recommendation_update = st.session_state.total_plays
        st.session_state.needs_rerun = True  # Set a flag instead of directly calling rerun

# Check if we need to rerun the app (outside of callbacks)
if st.session_state.needs_rerun:
    st.session_state.needs_rerun = False  # Reset the flag
    st.rerun()  # Now this is not inside a callback

# Initial recommendations if needed
if not st.session_state.recommendations and st.session_state.total_plays >= 10:
    st.session_state.recommendations = fetch_recommendations()
    st.session_state.last_recommendation_update = st.session_state.total_plays

# Recommendations Section
if st.session_state.total_plays >= 10 and st.session_state.recommendations:
    st.markdown("### Recommendations For You")
    rec_cols = st.columns(5)
    for col, rec in zip(rec_cols, st.session_state.recommendations):
        with col:
            with st.container():
                st.markdown(f'<div class="album-container">', unsafe_allow_html=True)
                st.image(rec["image"], use_container_width=True)
                st.button("▶ Play", key=f"rec_btn_{rec['id']}", on_click=select_song, args=(rec["id"],))
                st.markdown(f'<div class="album-caption">{rec["title"]}<br>{rec["artist"]}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")

# Library Section
st.markdown("### Music Library")
num_cols = 5  # Number of columns per row
for i in range(0, len(music_records), num_cols):
    row_records = music_records[i:i + num_cols]
    
    with st.container():  # Ensure consistent row layout
        cols = st.columns(num_cols)
        for col, record in zip(cols, row_records):
            with col:
                with st.container():
                    st.markdown(f'<div class="album-container">', unsafe_allow_html=True)
                    st.image(record["image"], use_container_width=True)
                    st.button("▶ Play", key=f"btn_{record['id']}", on_click=select_song, args=(record["id"],))
                    st.markdown(f'<div class="album-caption">{record["title"]}<br>{record["artist"]}</div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

# Now Playing Section
if st.session_state.current_audio:
    audio_player = st.session_state.current_audio
    st.markdown("---")
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image(audio_player["image"], width=200)
    with col2:
        st.markdown(f"### {audio_player['title']}")
        st.markdown(f"**{audio_player['artist']}**")
        st.audio(audio_player["audio"])
        
# Display play count for debugging (can be removed in production)
with st.sidebar:
    st.write(f"Total plays: {st.session_state.total_plays}")
    st.write(f"Last recommendation update: {st.session_state.last_recommendation_update}")
    
    # Show user stats
    if st.session_state.user_id:
        user_info = fb.get_user_info(st.session_state.user_id)
        if user_info:
            st.markdown("### Your Stats")
            st.write(f"Username: {user_info.get('username', 'N/A')}")
            st.write(f"Total plays: {user_info.get('total_plays', 0)}")
            st.markdown("---")
            
            # Get user's top played songs
            user_plays = fb.get_user_play_counts(st.session_state.user_id)
            if user_plays:
                st.markdown("### Your Top Songs")
                # Convert to list, sort by count
                top_songs = sorted(
                    [(song_id, data) for song_id, data in user_plays.items() if song_id != 'info'],
                    key=lambda x: x[1].get('count', 0),
                    reverse=True
                )[:5]  # Top 5
                
                for i, (song_id, data) in enumerate(top_songs):
                    st.write(f"{i+1}. {data.get('song', 'Unknown')} - {data.get('count', 0)} plays")