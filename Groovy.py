import os
import json
import sqlite3
import streamlit as st
from PIL import Image
import pandas as pd
# Import the recommendation functions
from reco import get_recommendations, cal_scores    

DB_PATH = "hot100.db"
META_DIR = "assets/meta"
IMG_DIR = "assets/imgs"
MUSIC_DIR = "assets/music"

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
</style>
""", unsafe_allow_html=True)

# Initialize session state
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

# Load music data
def load_music_data():
    records = []
    if not os.path.exists(META_DIR):
        return records
    for file in os.listdir(META_DIR):
        if file.endswith(".json"):
            meta_path = os.path.join(META_DIR, file)
            with open(meta_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                song_id = file.split(".")[0]
                image_path = os.path.join(IMG_DIR, f"{song_id}.jpg")
                music_path = os.path.join(MUSIC_DIR, f"{song_id}.mp3")
                if os.path.exists(music_path):
                    records.append({
                        "id": song_id,
                        "title": data.get("song"),
                        "artist": data.get("artist"),
                        "image": image_path if os.path.exists(image_path) else "assets/default.jpg",
                        "audio": music_path
                    })
    return records

# Fetch recommendations using the recommendation model
def fetch_recommendations():
    # Load the database into a DataFrame
    with sqlite3.connect(DB_PATH) as conn:
        df = pd.read_sql(f"SELECT * FROM hot100;", conn)
    
    # Drop unnecessary columns 
    df.drop(['youtube_url', 'release_date', 'thumbnail', 'description'], axis=1, inplace=True)
    
    # Calculate scores and get recommendations
    cal_scores(df)
    recommendations_list = get_recommendations(df)
    
    # Convert recommendations to the format used by the UI
    recommendations = []
    for rec in recommendations_list:
        song_id = rec['id']
        image_path = os.path.join(IMG_DIR, f"{song_id}.jpg")
        music_path = os.path.join(MUSIC_DIR, f"{song_id}.mp3")
        if os.path.exists(music_path):
            recommendations.append({
                "id": song_id,
                "title": rec['song'],
                "artist": rec['artist'],
                "image": image_path if os.path.exists(image_path) else "assets/default.jpg",
                "audio": music_path
            })
    return recommendations

# Load music records
music_records = load_music_data()

# Main UI
st.title("🎵 Groovy")

# Function to select a song and update play count
def select_song(song_id):
    for record in music_records:
        if record["id"] == song_id:
            st.session_state.current_audio = record
            break
    
    # Update play count in database
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("UPDATE hot100 SET count = count + 1 WHERE id = ?", (song_id,))
    conn.commit()
    conn.close()

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
st.sidebar.write(f"Total plays: {st.session_state.total_plays}")
st.sidebar.write(f"Last recommendation update: {st.session_state.last_recommendation_update}")