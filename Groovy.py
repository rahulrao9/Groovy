import os
import json
import streamlit as st
from PIL import Image

# Paths for assets
META_DIR = "assets/meta"
IMG_DIR = "assets/imgs"
MUSIC_DIR = "assets/music"

# Load music metadata and match with images/audio files
def load_music_data():
    records = []
    
    if not os.path.exists(META_DIR):
        print("Meta directory not found!")
        return records

    for file in os.listdir(META_DIR):
        if file.endswith(".json"):
            meta_path = os.path.join(META_DIR, file)
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
                song_name = data.get("song")
                artist_name = data.get("artist")
                song_id = file.split(".")[0]  # Unique ID from filename

                image_path = os.path.join(IMG_DIR, f"{song_id}.jpg")
                music_path = os.path.join(MUSIC_DIR, f"{song_id}.mp3")

                if os.path.exists(music_path):  # Ensure at least the music file exists
                    records.append({
                        "id": song_id,
                        "title": song_name,
                        "artist": artist_name,
                        "image": image_path if os.path.exists(image_path) else "assets/default.jpg",  # Fallback image
                        "audio": music_path
                    })

    return records

# Load music records
music_records = load_music_data()

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
        margin-bottom: 30px; /* Increased gap between rows */
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
        color: #636363;
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
        color: white; /* Ensures text color remains white */
    }

    .now-playing {
        text-align: center;
        font-weight: bold;
        font-size: 18px;
        color: #ff8a00;
    }

</style>
""", unsafe_allow_html=True)

st.title("🎵 Groovy")

# Use session state to track currently playing audio
if "current_audio" not in st.session_state:
    st.session_state.current_audio = None

# Function to select a song
def select_song(song_id):
    for record in music_records:
        if record["id"] == song_id:
            st.session_state.current_audio = record
            break  # Stop after finding the matching song

# Display music records in a structured row format
num_cols = 5  # Number of columns per row
for i in range(0, len(music_records), num_cols):
    row_records = music_records[i:i + num_cols]
    
    with st.container():  # Ensure consistent row layout
        cols = st.columns(num_cols)
        for col, record in zip(cols, row_records):
            with col:
                with st.container():
                    st.markdown(f'<div class="album-container">', unsafe_allow_html=True)
                    st.image(record["image"], use_container_width=True)  # Updated here!
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
