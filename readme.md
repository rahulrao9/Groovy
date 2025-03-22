<div align="center">
  <img src="https://raw.githubusercontent.com/rahulrao9/Groovy/master/screenshots/logo.png" alt="Groovy App Banner" width="200"/>
  <p><i>Discover your next favorite track with Groovy</i></p>
</div>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-screenshots">Screenshots</a> •
  <a href="#-tech-stack">Tech Stack</a> •
  <a href="#-architecture">Architecture</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-how-it-works">How It Works</a> •
  <a href="#-license">License</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white" alt="Streamlit"/>
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas"/>
  <img src="https://img.shields.io/badge/scikit--learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white" alt="Scikit-learn"/>
  <img src="https://img.shields.io/badge/SQL-4479A1?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQL"/>
  <img src="https://img.shields.io/badge/Firebase-FFCA28?style=for-the-badge&logo=firebase&logoColor=black" alt="Firebase"/>
</p>

## 🚀 Features

- **Personal Music Library** - Browse and play Billboard's top tracks
- **AI-Powered Recommendations** - Personalized song suggestions that improve as you listen
- **User Authentication** - Create an account and sign in to access your personalized content
- **Cross-Device Sync** - Your listening history and preferences follow you across devices
- **Federated Learning** - Your listening data is securely stored and processed
- **Billboard Hot 100 Integration** - Automatically fetch the latest chart-toppers
- **YouTube Integration** - Download high-quality audio from official music videos
- **Beautiful UI/UX** - Modern, responsive design with intuitive controls

## 📸 Screenshots

<div align="center">
  <img src="https://raw.githubusercontent.com/rahulrao9/Groovy/master/screenshots/firebase.png" alt="Groovy App Main Screen" width="800"/>
  <p><i>Groovy's login page</i></p>

  <img src="https://raw.githubusercontent.com/rahulrao9/Groovy/master/screenshots/1.png" alt="Groovy App Main Screen" width="800"/>
  <p><i>Groovy's main interface with album cover display and music player</i></p>
  
  <img src="https://raw.githubusercontent.com/rahulrao9/Groovy/master/screenshots/2.png" alt="Groovy App Recommendations" width="800"/>
  <p><i>Personalized recommendations improve as you listen to more music</i></p>
</div>

## 🏗 Architecture

```
🎵 Groovy
│
├── 📂 assets/                 # Assets directory
│   ├── 📂 imgs/              # Album artwork images
│   ├── 📂 meta/              # Song metadata JSON files
│   └── 📂 music/             # MP3 audio files
│
├── 📄 Groovy.py               # Main application UI
├── 📄 login.py                # Authentication interface
├── 📄 firebase_config.py      # Firebase configuration
├── 📄 rec.py                  # Recommendation system
├── 📄 fetch_hot_100.py        # Billboard scraper
├── 📄 download_music.py       # YouTube downloader
├── 📄 clear_db_assets.py      # Utility to reset app
├── 📄 run_groovy.py           # Application launcher
├── 📄 .env.example            # Environment variables template
└── 📄 requirements.txt        # Dependencies
```

## 📦 Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/rahulrao9/Groovy.git
   cd groovy
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   Edit the `.env` file with your Firebase credentials and other configuration

4. **Fetch Billboard Hot 100 data**
   ```bash
   python fetch_hot_100.py
   ```

5. **Download music from YouTube**
   ```bash
   python download_music.py
   ```

6. **Launch the app**
   ```bash
   python run_groovy.py
   ```
   or
   ```bash
   streamlit run Groovy.py
   ```

7. **Open the app in your browser**
   ```
   http://localhost:8501
   ```

## 🎮 How It Works

### Federated Learning Music Recommendation System

Groovy uses a sophisticated recommendation engine that combines multiple approaches:

1. **Content-Based Filtering**
   - Analyzes artists, song features, and tags
   - Creates embeddings to find similar music

2. **Play Count Analysis**
   - Tracks which songs you play most frequently
   - Builds an understanding of your explicit preferences

3. **Artist Affinity Modeling**
   - Calculates your preference for specific artists
   - Recommends new songs from artists you enjoy

4. **Genre/Tag Preference Learning**
   - Identifies music genres you prefer
   - Suggests similar music in your favorite styles

5. **Hybrid Scoring**
   - Combines all these signals with global popularity metrics
   - Produces personalized recommendations that improve over time

The recommendation model updates every 10 plays, adapting to your changing preferences.

### User Authentication and Data Sync

Groovy uses Firebase Authentication to:
- Allow users to create accounts and sign in
- Securely store and sync listening history across devices
- Provide personalized recommendations that follow users wherever they go

### Data Privacy

User data is securely stored in Firebase and processed according to best practices. Authentication ensures that your listening habits are private and only accessible to you.

## 🧠 Machine Learning Details

The recommendation system works by:

1. **Preprocessing**
   - Artist name normalization and splitting
   - Tag extraction and processing
   - Numerical feature normalization

2. **Vectorization**
   - Transforms musical attributes into mathematical spaces
   - Calculates similarities between songs

3. **Multi-factor Scoring**
   ```python
   recommendation_score = (
       count_normalized * 0.35 +          # Play count
       engagement_ratio * 0.1 +           # How engaging the content is
       artist_affinity_score * 0.15 +     # Artist preference 
       tag_affinity_score * 0.15 +        # Genre/tag preference
       collaborative_score * 0.15 +       # Similar users' preferences
       popularity_score * 0.1             # Global popularity
   ) * (1 + recency_factor * 0.5)         # Recency boost
   ```

## 📋 Todo List & Future Improvements

- [x] User accounts and profiles
- [x] Multi-device sync
- [ ] Social sharing features
- [ ] Advanced visualization of listening habits
- [ ] Voice-activated controls
- [ ] Expanded music metadata

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

<p align="center">
  Made with ❤️ by Rahul Rao
</p>

<p align="center">
  <a href="https://github.com/rahulrao9">GitHub</a> •
  <a href="https://www.kaggle.com/rahulrrao">Kaggle</a> •
  <a href="https://www.linkedin.com/in/rahul-rao-305337288/">LinkedIn</a>
</p>
