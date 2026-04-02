import pandas as pd
import numpy as np
import os
 
# ======================================================
# Load Dataset
# ======================================================
DATA_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'Music Info.csv')
 
if not os.path.exists(DATA_PATH):
    raise FileNotFoundError(f"Dataset not found at {DATA_PATH}.")
 
music_df = pd.read_csv(DATA_PATH)
 
# Clean up
music_df['genre'] = music_df['genre'].fillna('Unknown')
music_df['tags'] = music_df['tags'].fillna('')
music_df['year'] = pd.to_numeric(music_df['year'], errors='coerce').fillna(0).astype(int)
music_df['spotify_preview_url'] = music_df['spotify_preview_url'].fillna('')
 
def track_id_to_spotify_url(track_id):
    return f"https://open.spotify.com/track/{track_id}"
 
music_df["spotify_url"] = music_df["spotify_id"].apply(track_id_to_spotify_url)
 
# ======================================================
# Get available genres
# ======================================================
def get_available_genres():
    genres = music_df['genre'].dropna().unique().tolist()
    genres = [g for g in genres if g and g != 'Unknown']
    return sorted(genres)
 
# ======================================================
# Core Recommendation Function
# ======================================================
def recommend_songs_by_emotion(emotion: str, n: int = 5, uplift: bool = False, genre: str = None):
    emotion = emotion.lower().strip()
 
    # Mood-Matching Mode
    if not uplift:
        if emotion == "sad":
            recs = music_df[(music_df["valence"] < 0.4) & (music_df["energy"] < 0.5)]
        elif emotion == "happy":
            recs = music_df[(music_df["valence"] > 0.6) & (music_df["energy"] > 0.5)]
        elif emotion == "angry":
            recs = music_df[(music_df["valence"] < 0.4) & (music_df["energy"] > 0.7)]
        elif emotion in ["surprised", "surprise"]:
            recs = music_df[(music_df["valence"].between(0.4, 0.7)) & (music_df["energy"] > 0.6)]
        elif emotion == "fearful":
            recs = music_df[(music_df["valence"] < 0.4) & (music_df["energy"].between(0.6, 1.0))]
        else:
            recs = music_df[(music_df["valence"].between(0.4, 0.6)) & (music_df["energy"].between(0.4, 0.6))]
 
    # Mood-Uplifting Mode
    else:
        if emotion == "sad":
            recs = music_df[(music_df["valence"] > 0.6) & (music_df["energy"].between(0.4, 0.7))]
        elif emotion == "angry":
            recs = music_df[(music_df["valence"] > 0.5) & (music_df["energy"] < 0.5)]
        elif emotion == "fearful":
            recs = music_df[(music_df["valence"] > 0.6) & (music_df["energy"].between(0.3, 0.6))]
        elif emotion == "happy":
            recs = music_df[(music_df["valence"] > 0.6) & (music_df["energy"] > 0.5)]
        elif emotion in ["surprised", "surprise"]:
            recs = music_df[(music_df["valence"].between(0.5, 0.8)) & (music_df["energy"] > 0.6)]
        else:
            recs = music_df[(music_df["valence"].between(0.4, 0.6)) & (music_df["energy"].between(0.4, 0.6))]
 
    # Apply genre filter if specified
    if genre and genre != "All Genres" and not recs.empty:
        genre_filtered = recs[recs['tags'].str.contains(genre.lower(), case=False, na=False) |
                              recs['genre'].str.contains(genre.lower(), case=False, na=False)]
        if not genre_filtered.empty:
            recs = genre_filtered
 
    # Fallback
    if recs.empty:
        recs = music_df.sample(min(n, len(music_df)))
 
    recs_sampled = recs.sample(min(n, len(recs)))
 
    results = []
    for _, row in recs_sampled.iterrows():
        results.append({
            "name": row["name"],
            "artist": row["artist"],
            "link": row["spotify_url"],
            "preview_url": row.get("spotify_preview_url", ""),
            "year": int(row.get("year", 0)),
            "danceability": round(float(row.get("danceability", 0)), 2),
            "energy": round(float(row.get("energy", 0)), 2),
            "valence": round(float(row.get("valence", 0)), 2),
            "tempo": round(float(row.get("tempo", 0)), 1),
        })
 
    return results