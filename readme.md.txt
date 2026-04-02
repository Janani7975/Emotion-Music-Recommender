# 🎧 Emotion → Music Recommender

An AI-powered full-stack application that detects human emotions 
from **face images**, **webcam**, or **text** and recommends 
Spotify songs matching your mood.

---

## 🚀 Features

- 😊 **Face emotion detection** using MobileNetV2 CNN
- 💬 **Text emotion detection** using BERT transformer
- 🎥 **Live webcam** emotion capture
- 🎵 **30-second Spotify previews** built into the UI
- 📊 **Mood history chart** tracking your emotions over time
- 🎸 **Genre filter** for personalized recommendations
- 🎚️ **Adjustable playlist size** (3–15 songs)
- 🔄 **Uplift mode** — play happy songs when you're sad

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | Streamlit, Custom CSS |
| Backend | FastAPI, Uvicorn |
| Face Model | MobileNetV2 (Keras/TensorFlow) |
| Text Model | BERT (HuggingFace Transformers) |
| CV | OpenCV |
| Data | Pandas, Spotify Audio Features CSV |
| Language | Python 3.11 |

---

## 📁 Project Structure
```
Emotion-Music-Recommender/
├── backend/
│   ├── main.py          # FastAPI server
│   ├── image_models.py  # CNN emotion detection
│   ├── text_models.py   # BERT emotion detection
│   └── recommender.py   # Music recommendation logic
├── models/
│   └── mobilenetv2.keras  # (download separately)
├── data/
│   └── Music Info.csv
├── frontend/
│   └── app.py           # Streamlit UI
└── requirements.txt
```

---

## ⚙️ How to Run

### 1. Clone the repository
```bash
git clone https://github.com/YOUR_USERNAME/Emotion-Music-Recommender.git
cd Emotion-Music-Recommender
```

### 2. Create virtual environment
```bash
python -m venv venv
venv\Scripts\activate   # Windows
source venv/bin/activate  # Mac/Linux
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Download the model
Place `mobilenetv2.keras` in the `models/` folder.

### 5. Run backend
```bash
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

### 6. Run frontend (new terminal)
```bash
streamlit run frontend/app.py
```

Open browser at `http://localhost:8501`

---

## 🧠 How It Works

1. User inputs face image / webcam / text
2. AI model detects emotion (angry/happy/sad/surprise/neutral)
3. System filters Spotify dataset by valence & energy
4. Top N songs returned with 30-sec previews

---

## 👩‍💻 Built By

**Janani.G** 