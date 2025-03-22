import pandas as pd
import numpy as np
import json
import re
from sklearn.metrics.pairwise import cosine_similarity
import firebase_config as fb

# ------- Artist and Tag Affinity Calculation -------

def process_artists(artist_str):
    """Split artist names that contain featuring, with, &, etc."""
    if isinstance(artist_str, str):
        # Replace "Featuring" and other variants
        artist_str = re.sub(r'Featuring|Feat\.|Feat|ft\.', '&', artist_str)
        # Split by & or "with" 
        artists = re.split(r'\s*&\s*|\s+with\s+', artist_str)
        # Strip whitespace
        return [artist.strip() for artist in artists]
    return []

def process_tags(tags_str):
    """Process tags from JSON string to list."""
    if isinstance(tags_str, str):
        try:
            # Parse JSON string
            tags = json.loads(tags_str)
            # Extract and clean tags
            return [tag.lower().strip() for tag in tags]
        except json.JSONDecodeError:
            return []
    return []

def calculate_artist_affinity(df, user_plays=None):
    """Calculate user affinity for artists based on play counts."""
    if user_plays is None:
        # Use the count column from the dataframe (local DB)
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
    else:
        # Use user-specific play counts from Firebase
        artist_play_counts = {}
        for song_id, play_data in user_plays.items():
            if song_id == 'info':
                continue
                
            play_count = play_data.get('count', 0)
            if play_count > 0:
                artists = process_artists(play_data.get('artist', ''))
                for artist in artists:
                    if artist in artist_play_counts:
                        artist_play_counts[artist] += play_count
                    else:
                        artist_play_counts[artist] = play_count
    
    # Normalize artist play counts
    total_plays = sum(artist_play_counts.values()) or 1  # Avoid division by zero
    artist_affinity = {artist: count/total_plays for artist, count in artist_play_counts.items()}
    
    return artist_affinity

def calculate_tag_affinity(df, user_plays=None):
    """Calculate user affinity for music tags/genres based on play counts."""
    # This requires joining user plays with the full dataframe to get tags
    tag_play_counts = {}
    
    if user_plays is None:
        # Use the count column from the dataframe (local DB)
        for _, row in df.iterrows():
            play_count = row['count']
            if play_count > 0:
                for tag in row['tags_list']:
                    if tag in tag_play_counts:
                        tag_play_counts[tag] += play_count
                    else:
                        tag_play_counts[tag] = play_count
    else:
        # Use user-specific play counts from Firebase
        for song_id, play_data in user_plays.items():
            if song_id == 'info':
                continue
                
            play_count = play_data.get('count', 0)
            if play_count > 0:
                # Find this song in the dataframe to get its tags
                song_df = df[df['id'] == song_id]
                if not song_df.empty:
                    tags = song_df.iloc[0]['tags_list']
                    for tag in tags:
                        if tag in tag_play_counts:
                            tag_play_counts[tag] += play_count
                        else:
                            tag_play_counts[tag] = play_count
    
    # Normalize
    total_plays = sum(tag_play_counts.values()) or 1
    tag_affinity = {tag: count/total_plays for tag, count in tag_play_counts.items()}
    
    return tag_affinity

def score_by_artist_affinity(row, artist_affinity):
    """Score songs based on user's artist preferences."""
    score = 0
    for artist in row['artists_list']:
        score += artist_affinity.get(artist, 0)
    return score

def score_by_tag_affinity(row, tag_affinity):
    """Score songs based on user's genre/tag preferences."""
    score = 0
    for tag in row['tags_list']:
        score += tag_affinity.get(tag, 0)
    return score

# ------- Collaborative Filtering Component -------

def calculate_user_similarity(target_user_plays, all_user_plays):
    """Calculate similarity between target user and other users."""
    if not target_user_plays:
        return {}  # No user data to compare
        
    user_similarities = {}
    
    for user_id, plays in all_user_plays.items():
        if user_id == 'target_user':
            continue  # Skip comparing with self
            
        # Count songs in common and calculate play count similarity
        common_songs = set(target_user_plays.keys()) & set(plays.keys())
        if not common_songs:
            user_similarities[user_id] = 0
            continue
            
        # Calculate similarity based on play counts for common songs
        similarity = 0
        for song_id in common_songs:
            target_count = target_user_plays[song_id].get('count', 0)
            other_count = plays[song_id].get('count', 0)
            # Add simple count similarity
            similarity += min(target_count, other_count) / max(target_count, other_count)
            
        # Normalize by number of common songs
        user_similarities[user_id] = similarity / len(common_songs)
    
    return user_similarities

def get_collaborative_recommendations(user_id, df, top_n=10):
    """Get recommendations based on similar users' preferences."""
    if not user_id:
        return {}  # No user ID provided
        
    # Get target user's play data
    target_user_plays = fb.get_user_play_counts(user_id)
    if not target_user_plays:
        return {}  # No play data for this user
        
    # Get all other users' play data
    all_user_plays = fb.get_all_users_play_data(limit=50)
    if user_id in all_user_plays:
        del all_user_plays[user_id]  # Remove target user
        
    # Calculate user similarities
    user_similarities = calculate_user_similarity(target_user_plays, all_user_plays)
    
    # Get recommendations from similar users
    song_scores = {}
    
    for other_user_id, similarity in sorted(user_similarities.items(), key=lambda x: x[1], reverse=True)[:10]:
        # Only consider the top 10 most similar users
        other_user_plays = all_user_plays[other_user_id]
        
        for song_id, play_data in other_user_plays.items():
            if song_id in target_user_plays:
                continue  # Skip songs the user has already played
                
            play_count = play_data.get('count', 0)
            if song_id in song_scores:
                song_scores[song_id] += similarity * play_count
            else:
                song_scores[song_id] = similarity * play_count
    
    # Sort songs by score
    return {k: v for k, v in sorted(song_scores.items(), key=lambda x: x[1], reverse=True)[:top_n]}

# ------- Main Recommendation System -------

def cal_scores(df, user_id=None):
    """Calculate recommendation scores for songs."""
    # Process data for recommendation
    df['artists_list'] = df['artist'].apply(process_artists)
    df['tags_list'] = df['tags'].apply(process_tags)
    
    # Get user-specific play counts if a user ID is provided
    user_plays = None
    if user_id:
        user_plays = fb.get_user_play_counts(user_id)
    
    # Calculate normalized counts and engagement metrics
    max_count = df['count'].max()
    min_count = df['count'].min()
    
    # If using Firebase, replace the count normalization with user-specific counts
    if user_id and user_plays:
        # Create a map of song_id to user-specific count
        user_count_map = {song_id: play_data.get('count', 0) for song_id, play_data in user_plays.items()}
        
        # Apply user-specific counts to the dataframe
        df['user_count'] = df['id'].apply(lambda x: user_count_map.get(x, 0))
        max_user_count = max(user_count_map.values()) if user_count_map else 0
        
        # Normalize user counts
        if max_user_count > 0:
            df['count_normalized'] = df['user_count'] / max_user_count
        else:
            df['count_normalized'] = 0
    else:
        # Use local DB counts
        if max_count > min_count:
            df['count_normalized'] = (df['count'] - min_count) / (max_count - min_count)
        else:
            df['count_normalized'] = df['count'].apply(lambda x: 1.0 if x > 0 else 0.0)
    
    # Calculate engagement metrics if available
    if 'views' in df.columns and 'like_count' in df.columns:
        df['engagement_ratio'] = df.apply(
            lambda row: row['like_count'] / max(row['views'], 1) if pd.notnull(row['views']) and pd.notnull(row['like_count']) else 0, 
            axis=1
        )
    else:
        df['engagement_ratio'] = 0
    
    # Calculate recency factor
    df['recency_factor'] = df['count_normalized'] * 1.5  # Boost recent plays
    
    # Calculate artist and tag affinity
    artist_affinity = calculate_artist_affinity(df, user_plays)
    tag_affinity = calculate_tag_affinity(df, user_plays)
    
    # Apply the affinity scores
    df['artist_affinity_score'] = df.apply(lambda row: score_by_artist_affinity(row, artist_affinity), axis=1)
    df['tag_affinity_score'] = df.apply(lambda row: score_by_tag_affinity(row, tag_affinity), axis=1)
    
    # Calculate collaborative filtering score if user is logged in
    if user_id:
        # Get collaborative recommendations
        collab_recs = get_collaborative_recommendations(user_id, df)
        
        # Add collaborative scores to dataframe
        df['collaborative_score'] = df['id'].apply(lambda x: collab_recs.get(x, 0))
    else:
        df['collaborative_score'] = 0
    
    # Calculate popularity score (normalize views and likes if available)
    if 'views' in df.columns and 'like_count' in df.columns:
        max_views = df['views'].max() or 1
        max_likes = df['like_count'].max() or 1
        
        df['views_normalized'] = df['views'] / max_views
        df['likes_normalized'] = df['like_count'] / max_likes
        
        df['popularity_score'] = (df['views_normalized'] * 0.7) + (df['likes_normalized'] * 0.3)
    else:
        df['popularity_score'] = 0
    
    # Final blended recommendation score
    df['recommendation_score'] = (
        # Direct user interaction signals (45%)
        df['count_normalized'] * 0.35 +             # Play count is very important
        df['engagement_ratio'] * 0.1 +              # How engaging the content is
        
        # Personalization signals (30%)
        df['artist_affinity_score'] * 0.15 +        # Artist preference
        df['tag_affinity_score'] * 0.15 +           # Genre preference
        
        # Collaborative filtering (15%)
        df['collaborative_score'] * 0.15 +
        
        # Global popularity (10%)
        df['popularity_score'] * 0.1                # General popularity
    ) * (1 + df['recency_factor'] * 0.5)            # Recency boost
    
    # Handle cold start for new users (no play history)
    if (user_id and not user_plays) or (not user_id and df[df['count'] > 0].empty):
        # If no songs have been played, use popularity & engagement
        df['recommendation_score'] = (
            df['popularity_score'] * 0.7 +
            df['engagement_ratio'] * 0.3
        )
    
    return df

def get_recommendations(df, n=5, exclude_played=False, user_id=None):
    """Get top N song recommendations."""
    # Calculate scores with user data if available
    df = cal_scores(df, user_id)
    
    # Filter out played songs if requested
    if exclude_played:
        if user_id:
            # Get user's play history
            user_plays = fb.get_user_play_counts(user_id)
            played_songs = list(user_plays.keys())
            
            # Filter dataframe
            df_filtered = df[~df['id'].isin(played_songs)]
        else:
            # Use local count column
            df_filtered = df[df['count'] == 0]
    else:
        df_filtered = df
    
    # Sort by recommendation score
    df_sorted = df_filtered.sort_values('recommendation_score', ascending=False)
    
    # Get top N recommendations
    recommendations = df_sorted.head(n)
    
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
    model_df = cal_scores(df)
    
    # Filter by artist (case insensitive partial match)
    artist_df = model_df[model_df['artist'].str.lower().str.contains(artist.lower())]
    
    # Sort by recommendation score and return top N
    return artist_df.head(n)[['artist', 'song', 'recommendation_score']]

def get_recommendations_by_tag(df, tag, n=3):
    """Get top N song recommendations with a specific tag/genre"""
    model_df = cal_scores(df)
    
    # Filter songs that have this tag
    tag_matches = model_df[model_df['tags_list'].apply(lambda tags: any(tag.lower() in t.lower() for t in tags))]
    
    # Sort by recommendation score and return top N
    return tag_matches.head(n)[['artist', 'song', 'recommendation_score']] 