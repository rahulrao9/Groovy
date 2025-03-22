import sqlite3
import pandas as pd
import json
import re
import numpy as np

db_path = 'hot100.db'

table_name = 'hot100'

with sqlite3.connect(db_path) as conn:
    df = pd.read_sql(f"SELECT * FROM {table_name};", conn)

df.drop(['youtube_url', 'release_date','thumbnail','description'], axis=1, inplace=True)

# Function to split artist names
def process_artists(artist_str):
    # Split by common separators
    if isinstance(artist_str, str):
        # Replace "Featuring" and other variants
        artist_str = re.sub(r'Featuring|Feat\.|Feat|ft\.', '&', artist_str)
        # Split by & or "with" 
        artists = re.split(r'\s*&\s*|\s+with\s+', artist_str)
        # Strip whitespace
        return [artist.strip() for artist in artists]
    return []

# Function to process tags
def process_tags(tags_str):
    if isinstance(tags_str, str):
        try:
            # Parse JSON string
            tags = json.loads(tags_str)
            # Extract and clean tags
            return [tag.lower().strip() for tag in tags]
        except json.JSONDecodeError:
            return []
    return []

# Apply transformations to DataFrame
def cal_scores(df):
    df['artists_list'] = df['artist'].apply(process_artists)
    df['tags_list'] = df['tags'].apply(process_tags)

    # Create engagement metrics
    df['engagement_ratio'] = df['like_count'] / df['views'].apply(lambda x: max(x, 1))  # Avoid division by zero

    # Normalize popularity metrics (Min-Max scaling)
    df['views_normalized'] = (df['views'] - df['views'].min()) / (df['views'].max() - df['views'].min())
    df['likes_normalized'] = (df['like_count'] - df['like_count'].min()) / (df['like_count'].max() - df['like_count'].min())

    # Calculate a popularity score
    df['popularity_score'] = (df['views_normalized'] * 0.7) + (df['likes_normalized'] * 0.3)

# ------- Artist and Tag Affinity Calculation -------

def calculate_artist_affinity(df):
    """Calculate user affinity for artists based on play counts"""
    artist_play_counts = {}
    
    # Iterate through each row in the DataFrame
    for _, row in df.iterrows():
        play_count = row['count']
        if play_count > 0:  # Only consider songs that have been played
            for artist in row['artists_list']:
                if artist in artist_play_counts:
                    artist_play_counts[artist] += play_count
                else:
                    artist_play_counts[artist] = play_count
    
    # Normalize artist play counts
    total_plays = sum(artist_play_counts.values()) or 1  # Avoid division by zero
    artist_affinity = {artist: count/total_plays for artist, count in artist_play_counts.items()}
    
    return artist_affinity

def calculate_tag_affinity(df):
    """Calculate user affinity for music tags/genres based on play counts"""
    tag_play_counts = {}
    
    # Iterate through rows
    for _, row in df.iterrows():
        play_count = row['count']
        if play_count > 0:
            for tag in row['tags_list']:
                if tag in tag_play_counts:
                    tag_play_counts[tag] += play_count
                else:
                    tag_play_counts[tag] = play_count
    
    # Normalize
    total_plays = sum(tag_play_counts.values()) or 1
    tag_affinity = {tag: count/total_plays for tag, count in tag_play_counts.items()}
    
    return tag_affinity

def score_by_artist_affinity(row, artist_affinity):
    """Score songs based on user's artist preferences"""
    score = 0
    for artist in row['artists_list']:
        score += artist_affinity.get(artist, 0)
    return score

def score_by_tag_affinity(row, tag_affinity):
    """Score songs based on user's genre/tag preferences"""
    score = 0
    for tag in row['tags_list']:
        score += tag_affinity.get(tag, 0)
    return score

# ------- Collaborative Filtering Component -------

def calculate_song_similarity(df):
    """Calculate similarity between songs based on artists and tags"""
    n_songs = len(df)
    similarity_matrix = np.zeros((n_songs, n_songs))
    
    for i in range(n_songs):
        for j in range(i, n_songs):
            if i == j:
                similarity_matrix[i][j] = 1.0
                continue
                
            # Get artists and tags for both songs
            artists_i = set(df.iloc[i]['artists_list'])
            artists_j = set(df.iloc[j]['artists_list'])
            
            tags_i = set(df.iloc[i]['tags_list'])
            tags_j = set(df.iloc[j]['tags_list'])
            
            # Calculate Jaccard similarity for artists and tags
            if len(artists_i) == 0 or len(artists_j) == 0:
                artist_sim = 0
            else:
                artist_sim = len(artists_i & artists_j) / len(artists_i | artists_j)
                
            if len(tags_i) == 0 or len(tags_j) == 0:
                tag_sim = 0
            else:
                tag_sim = len(tags_i & tags_j) / len(tags_i | tags_j)
            
            # Weight artist similarity more heavily than tag similarity
            final_sim = (artist_sim * 0.7) + (tag_sim * 0.3)
            
            # Make matrix symmetric
            similarity_matrix[i][j] = final_sim
            similarity_matrix[j][i] = final_sim
    
    return similarity_matrix

# ------- Main Recommendation System -------

def build_recommendation_model(df):
    """Build the complete recommendation model"""
    
    # 1. Create normalized count (handling zero division case)
    max_count = df['count'].max()
    min_count = df['count'].min()
    if max_count > min_count:
        df['count_normalized'] = (df['count'] - min_count) / (max_count - min_count)
    else:
        df['count_normalized'] = df['count'].apply(lambda x: 1.0 if x > 0 else 0.0)
    
    # 2. Calculate recency factor (more weight to recently played songs)
    df['recency_factor'] = df['count_normalized'] * 1.5  # Boost recent plays
    
    # 3. Calculate artist and tag affinity
    artist_affinity = calculate_artist_affinity(df)
    tag_affinity = calculate_tag_affinity(df)
    
    # 4. Apply the affinity scores
    df['artist_affinity_score'] = df.apply(lambda row: score_by_artist_affinity(row, artist_affinity), axis=1)
    df['tag_affinity_score'] = df.apply(lambda row: score_by_tag_affinity(row, tag_affinity), axis=1)
    
    # 5. Calculate song similarity matrix for collaborative filtering
    similarity_matrix = calculate_song_similarity(df)
    
    # 6. Collaborative filtering score - similar to what user has played
    def collaborative_score(idx):
        if df.loc[idx, 'count'] > 0:
            # If song is already played, collaborative score doesn't matter as much
            return 0.0
        
        # Find similarity with played songs
        collab_score = 0
        played_songs = df[df['count'] > 0].index
        
        if len(played_songs) == 0:
            return 0.0
        
        # Get similarities with played songs, weighted by play count
        for played_idx in played_songs:
            sim = similarity_matrix[idx][played_idx]
            play_count = df.loc[played_idx, 'count']
            collab_score += sim * play_count
        
        # Normalize by number of played songs
        return collab_score / len(played_songs)
    
    # Apply collaborative filtering
    df['collaborative_score'] = df.index.map(collaborative_score)
    
    # 7. Final blended recommendation score
    df['recommendation_score'] = (
        # Direct user interaction signals (50%)
        df['count_normalized'] * 0.4 +             # Play count is very important
        df['engagement_ratio'] * 0.1 +             # How engaging the content is
        
        # Personalization signals (35%)
        df['artist_affinity_score'] * 0.2 +        # Artist preference
        df['tag_affinity_score'] * 0.15 +          # Genre preference
        
        # Collaborative filtering (5%)
        df['collaborative_score'] * 0.05 +
        
        # Global popularity (10%)
        df['popularity_score'] * 0.1               # General popularity
    ) * (1 + df['recency_factor'] * 0.5)           # Recency boost
    
    # 8. Handle cold start (no user history)
    if df[df['count'] > 0].empty:
        # If no songs have been played, use popularity & engagement
        df['recommendation_score'] = (
            df['popularity_score'] * 0.7 +
            df['engagement_ratio'] * 0.3
        )
    
    # Store the dataframe for future predictions
    return df.sort_values('recommendation_score', ascending=False)

# ------- User Recommendation Functions -------

def get_recommendations(df, n=5, exclude_played=False):
    """Get top N song recommendations"""
    model_df = build_recommendation_model(df)
    
    if exclude_played:
        model_df = model_df[model_df['count'] == 0]
    
    # Get top N recommendations
    recommendations = model_df.head(n)
    
    # Format output as a user-friendly list
    result = []
    for i, (_, song) in enumerate(recommendations.iterrows()):
        result.append({
            'rank': i+1,
            'song': song['song'],
            'artist': song['artist'],
            'recommendation_score': song['recommendation_score'],
            'id': song['id']
        })
    
    return result

def get_recommendations_by_artist(df, artist, n=3):
    """Get top N song recommendations by a specific artist"""
    model_df = build_recommendation_model(df)
    
    # Filter by artist (case insensitive partial match)
    artist_df = model_df[model_df['artist'].str.lower().str.contains(artist.lower())]
    
    # Sort by recommendation score and return top N
    return artist_df.head(n)[['artist', 'song', 'recommendation_score']]

def get_recommendations_by_tag(df, tag, n=3):
    """Get top N song recommendations with a specific tag/genre"""
    model_df = build_recommendation_model(df)
    
    # Filter songs that have this tag
    tag_matches = model_df[model_df['tags_list'].apply(lambda tags: any(tag.lower() in t.lower() for t in tags))]
    
    # Sort by recommendation score and return top N
    return tag_matches.head(n)[['artist', 'song', 'recommendation_score']]

