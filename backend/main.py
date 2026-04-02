from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
import tempfile
 
from backend.image_models import predict_emotion_image, predict_emotion_webcam
from backend.text_models import TEXT_CLASSIFIER, EMOTION_MAPPING
from backend.recommender import recommend_songs_by_emotion, get_available_genres
 
app = FastAPI(title="Emotion-Based Music Recommender API", version="2.0")
 
class TextInput(BaseModel):
    text: str
 
class MusicInput(BaseModel):
    emotion: str
    uplift: Optional[bool] = False
    genre: Optional[str] = "All Genres"
    n: Optional[int] = 5
 
@app.post("/predict/text")
async def predict_text_emotion(input: TextInput):
    try:
        results = TEXT_CLASSIFIER(input.text)
        raw_emotion = results[0]['label'].lower()
        mapped_emotion = EMOTION_MAPPING.get(raw_emotion, 'Neutral')
        
        # Get all scores if available
        all_scores = {}
        if isinstance(results, list) and len(results) > 0:
            if isinstance(results[0], list):
                all_scores = {r['label']: round(r['score'], 3) for r in results[0]}
        
        return {
            "detected_text_emotion": raw_emotion,
            "mapped_emotion": mapped_emotion,
            "all_scores": all_scores
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Text emotion prediction failed: {str(e)}")
 
@app.post("/predict/face-image")
async def predict_face_from_image(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
            tmp.write(contents)
            tmp_path = tmp.name
        emotion = predict_emotion_image(tmp_path)
        return {"emotion": emotion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Face image prediction failed: {str(e)}")
 
@app.get("/predict/face-webcam")
def predict_face_from_webcam():
    try:
        emotion = predict_emotion_webcam()
        return {"emotion": emotion}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webcam emotion prediction failed: {str(e)}")
 
@app.post("/recommend")
async def recommend_music(input_data: MusicInput):
    try:
        recs = recommend_songs_by_emotion(
            emotion=input_data.emotion,
            uplift=input_data.uplift,
            genre=input_data.genre,
            n=input_data.n
        )
        return recs
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Music recommendation failed: {str(e)}")
 
@app.get("/genres")
def get_genres():
    try:
        genres = get_available_genres()
        return {"genres": ["All Genres"] + genres}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
 
@app.get("/")
def home():
    return {"message": "Emotion-Based Music Recommender API v2.0 🎵"}
 