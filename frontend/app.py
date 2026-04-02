import os
import requests
import streamlit as st
 
FASTAPI_URL = os.getenv("FASTAPI_URL", "http://localhost:8000")
 
st.set_page_config(
    page_title="Emotion → Music Recommender",
    page_icon="🎧",
    layout="wide"
)
 
# =====================
# CSS
# =====================
st.markdown("""
<style>
.stApp {
  background: linear-gradient(135deg, #0f0c29 0%, #302b63 45%, #24243e 100%);
  color: #F2F5F7 !important;
}
.block-container {
  padding-top: 1.2rem !important;
  padding-left: 2rem !important;
  padding-right: 2rem !important;
  max-width: 100% !important;
}
.music-card {
  background: rgba(255,255,255,0.06);
  border: 1px solid rgba(255,255,255,0.08);
  border-radius: 14px;
  padding: 0.9rem 1.1rem;
  margin-bottom: 1rem;
}
h1,h2,h3,h4,h5 { color: #F6F7FB !important; }
.stButton>button {
  background: #7c4dff !important;
  color: white !important;
  border-radius: 10px !important;
  border: 0 !important;
  padding: 0.5rem 1.2rem !important;
  font-size: 0.95rem !important;
  width: 100% !important;
}
.stButton>button:hover { background: #5f2eea !important; }
.stTabs [data-baseweb="tab-list"] {
  gap: 4px;
  background: rgba(255,255,255,0.05);
  border-radius: 10px;
  padding: 4px;
}
.stTabs [data-baseweb="tab"] {
  border-radius: 8px;
  padding: 8px 16px;
  color: #ccc !important;
  font-size: 0.9rem !important;
}
.stTabs [aria-selected="true"] {
  background: #7c4dff !important;
  color: white !important;
}
.song-card {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.1);
  padding: 1rem;
  border-radius: 12px;
  margin-bottom: 0.8rem;
}
.emotion-badge {
  display: inline-block;
  background: #7c4dff;
  color: white;
  padding: 0.3rem 1rem;
  border-radius: 20px;
  font-size: 1.1rem;
  font-weight: bold;
  margin: 0.5rem 0;
}
a.song-link { color: #9ad0ff !important; text-decoration: none; }
a.song-link:hover { text-decoration: underline; }
.divider {
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
  margin: 0.8rem 0 1rem 0;
}
.stTextArea textarea {
  background: #1a1a3e !important;
  color: #ffffff !important;
  border: 1.5px solid #7c4dff !important;
  border-radius: 10px !important;
  font-size: 1rem !important;
  caret-color: #ffffff !important;
}
.stTextArea label p { color: #e0e0ff !important; font-weight: 600 !important; }
.stCheckbox { 
  background: rgba(124,77,255,0.15) !important;
  border: 1px solid rgba(124,77,255,0.5) !important;
  border-radius: 10px !important;
  padding: 0.5rem 0.8rem !important;
  margin: 0.5rem 0 !important;
}
.stCheckbox label p, .stCheckbox label span {
  color: #ffffff !important;
  font-size: 1rem !important;
  font-weight: 600 !important;
}
.stSlider label p { color: #e0e0ff !important; font-weight: 600 !important; }
.stSelectbox label p { color: #e0e0ff !important; font-weight: 600 !important; }
 
/* Sidebar - force all text visible */
section[data-testid="stSidebar"] {
  background: #1a1040 !important;
  border-right: 1px solid rgba(124,77,255,0.3) !important;
}
section[data-testid="stSidebar"] * {
  color: #ffffff !important;
}
section[data-testid="stSidebar"] h1,
section[data-testid="stSidebar"] h2,
section[data-testid="stSidebar"] h3,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
  color: #ffffff !important;
  opacity: 1 !important;
  visibility: visible !important;
}
section[data-testid="stSidebar"] .stSlider label p,
section[data-testid="stSidebar"] .stSlider span {
  color: #ffffff !important;
  font-weight: 700 !important;
  font-size: 1rem !important;
}
section[data-testid="stSidebar"] .stSelectbox label p {
  color: #ffffff !important;
  font-weight: 700 !important;
  font-size: 1rem !important;
}
section[data-testid="stSidebar"] .stSelectbox div {
  background: #2a1a5e !important;
  color: #ffffff !important;
  border: 1px solid rgba(124,77,255,0.5) !important;
}
/* Slider track and value */
section[data-testid="stSidebar"] .stSlider [data-testid="stTickBar"] {
  color: #ffffff !important;
}
section[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
  color: #ffffff !important;
  font-size: 0.95rem !important;
}
.stat-pill {
  display: inline-block;
  background: rgba(124,77,255,0.2);
  border: 1px solid rgba(124,77,255,0.4);
  border-radius: 20px;
  padding: 2px 10px;
  font-size: 0.78rem;
  color: #ccc;
  margin-right: 4px;
}
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
 
# =====================
# Session state init
# =====================
for key, val in [
    ("last_emotion", None),
    ("last_recs", []),
    ("mood_history", []),
    ("camera_enabled", False)
]:
    if key not in st.session_state:
        st.session_state[key] = val
 
# =====================
# Emotion emoji map
# =====================
EMOTION_EMOJI = {
    "happy": "😊", "sad": "😢", "angry": "😠",
    "surprise": "😲", "surprised": "😲",
    "neutral": "😐", "fearful": "😨",
    "no face detected": "🚫"
}
 
# =====================
# Helpers
# =====================
def post_text_emotion(text):
    r = requests.post(f"{FASTAPI_URL}/predict/text", json={"text": text}, timeout=60)
    r.raise_for_status()
    j = r.json()
    return j.get("mapped_emotion") or j.get("detected_text_emotion"), j.get("all_scores", {})
 
def post_face_emotion(image_bytes):
    r = requests.post(f"{FASTAPI_URL}/predict/face-image",
                      files={"file": ("face.jpg", image_bytes, "image/jpeg")}, timeout=60)
    r.raise_for_status()
    return r.json().get("emotion")
 
def post_webcam_emotion():
    r = requests.get(f"{FASTAPI_URL}/predict/face-webcam", timeout=180)
    r.raise_for_status()
    return r.json().get("emotion")
 
def post_recommendations(emotion, uplift, genre, n):
    r = requests.post(f"{FASTAPI_URL}/recommend",
                      json={"emotion": emotion, "uplift": uplift, "genre": genre, "n": n},
                      timeout=60)
    r.raise_for_status()
    return r.json()
 
def get_genres():
    try:
        r = requests.get(f"{FASTAPI_URL}/genres", timeout=10)
        return r.json().get("genres", ["All Genres"])
    except:
        return ["All Genres", "rock", "pop", "indie", "alternative", "electronic", "jazz", "classical"]
 
def render_emotion_result(emotion):
    emoji = EMOTION_EMOJI.get(emotion.lower(), "🎭")
    st.markdown(f"""
    <div style="text-align:center; padding: 1rem 0;">
      <div style="font-size: 3rem;">{emoji}</div>
      <div class="emotion-badge">{emotion.upper()}</div>
    </div>
    """, unsafe_allow_html=True)
    # Save to mood history
    st.session_state.mood_history.append(emotion.lower())
 
def render_confidence_bars(scores: dict):
    if not scores:
        return
    st.markdown("**Emotion confidence scores:**")
    emotion_emojis = {"joy":"😊","love":"😊","sadness":"😢","anger":"😠",
                      "fear":"😨","surprise":"😲","happy":"😊","sad":"😢",
                      "angry":"😠","neutral":"😐"}
    for label, score in sorted(scores.items(), key=lambda x: x[1], reverse=True):
        emoji = emotion_emojis.get(label.lower(), "🎭")
        pct = int(score * 100)
        st.markdown(f"{emoji} **{label.capitalize()}**")
        st.progress(score)
        st.markdown(f"<p style='color:#aaa;font-size:0.8rem;margin-top:-10px'>{pct}%</p>",
                    unsafe_allow_html=True)
 
def render_songs(recs):
    if not recs:
        st.info("No songs found.")
        return
    for i, item in enumerate(recs, 1):
        name = item.get("name", "Unknown")
        artist = item.get("artist", "Unknown")
        link = item.get("link", "")
        preview = item.get("preview_url", "")
        year = item.get("year", "")
        energy = item.get("energy", 0)
        valence = item.get("valence", 0)
        tempo = item.get("tempo", 0)
        danceability = item.get("danceability", 0)
 
        with st.container():
            st.markdown(f"""
            <div class="song-card">
              <div style="font-size:1rem;font-weight:700;color:#fff;">
                {i}. 🎵 {name}
              </div>
              <div style="color:#bbb;font-size:0.9rem;margin:2px 0 6px 0;">
                by <em>{artist}</em>{f" · {year}" if year else ""}
              </div>
              <span class="stat-pill">⚡ Energy {int(energy*100)}%</span>
              <span class="stat-pill">💛 Mood {int(valence*100)}%</span>
              <span class="stat-pill">💃 Dance {int(danceability*100)}%</span>
              <span class="stat-pill">🎵 {tempo} BPM</span>
              <br><br>
              <a class="song-link" href="{link}" target="_blank">▶ Open on Spotify</a>
            </div>
            """, unsafe_allow_html=True)
 
            # 30-second preview player
            if preview and preview.startswith("http"):
                st.audio(preview, format="audio/mp3")
 
def render_mood_chart():
    history = st.session_state.mood_history
    if len(history) < 2:
        st.info("Detect at least 2 emotions to see your mood history chart.")
        return
    from collections import Counter
    counts = Counter(history)
    emotions = list(counts.keys())
    values = list(counts.values())
    import matplotlib.pyplot as plt
    fig, ax = plt.subplots(figsize=(8, 3))
    fig.patch.set_facecolor('#1a1a3e')
    ax.set_facecolor('#1a1a3e')
    colors = ['#7c4dff','#00e5ff','#ff6b6b','#ffd166','#06d6a0','#ff9f1c']
    bars = ax.bar(emotions, values, color=colors[:len(emotions)], edgecolor='none', width=0.5)
    ax.set_xlabel("Emotion", color='white', fontsize=11)
    ax.set_ylabel("Times Detected", color='white', fontsize=11)
    ax.tick_params(colors='white')
    ax.spines['bottom'].set_color('#444')
    ax.spines['left'].set_color('#444')
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                str(val), ha='center', color='white', fontsize=10)
    plt.tight_layout()
    st.pyplot(fig)
    plt.close()
 
# =====================
# Header
# =====================
st.markdown("## 🎧 Emotion → Music Recommender")
st.markdown(
    "<div class='music-card'>Detect your emotion from your <b>face</b>, <b>camera</b>, "
    "or <b>text</b> — and get a personalized playlist with 30-second previews! 🎵✨</div>",
    unsafe_allow_html=True
)
 
# =====================
# Sidebar — controls
# =====================
with st.sidebar:
    st.markdown("<h2 style='color:white;font-size:1.3rem;'>🎛️ Settings</h2>", unsafe_allow_html=True)
    st.markdown("<hr style='border-color:rgba(124,77,255,0.4);'>", unsafe_allow_html=True)
 
    st.markdown("<p style='color:#ffffff;font-weight:700;font-size:1rem;margin-bottom:4px;'>🎵 Number of songs</p>", unsafe_allow_html=True)
    n_songs = st.slider("Number of songs", min_value=3, max_value=15, value=5, step=1, label_visibility="collapsed")
 
    st.markdown("<p style='color:#ffffff;font-weight:700;font-size:1rem;margin-bottom:4px;'>🎸 Filter by genre</p>", unsafe_allow_html=True)
    genres = get_genres()
    selected_genre = st.selectbox("Filter by genre", genres, label_visibility="collapsed")
 
    st.markdown("<hr style='border-color:rgba(124,77,255,0.4);'>", unsafe_allow_html=True)
    st.markdown("<h3 style='color:white;font-size:1.1rem;'>📊 Mood History</h3>", unsafe_allow_html=True)
    render_mood_chart()
 
    if st.button("🗑️ Clear History"):
        st.session_state.mood_history = []
        st.rerun()
 
    st.markdown("<hr style='border-color:rgba(124,77,255,0.4);'>", unsafe_allow_html=True)
    if st.session_state.last_emotion:
        st.markdown(
            f"<p style='color:#ffffff;font-weight:600;'>Last emotion: "
            f"{EMOTION_EMOJI.get(st.session_state.last_emotion.lower(),'')} "
            f"<span style='background:#7c4dff;padding:2px 10px;border-radius:10px;'>"
            f"{st.session_state.last_emotion.upper()}</span></p>",
            unsafe_allow_html=True
        )
 
# =====================
# Main tabs
# =====================
tab_face, tab_webcam, tab_text = st.tabs(
    ["📷 Face / Camera", "🎥 Webcam", "💬 Text"]
)
 
# -------------------------
# Tab 1: Face
# -------------------------
with tab_face:
    st.markdown("### 📷 Detect Emotion from Face")
    st.markdown(
        "<div class='music-card'>Upload a face photo or use your camera. "
        "The CNN model detects your emotion and recommends songs with previews.</div>",
        unsafe_allow_html=True
    )
    c1, c2 = st.columns(2)
 
    with c1:
        st.markdown("**📤 Upload a photo**")
        uploaded = st.file_uploader("Choose face image", type=["jpg","jpeg","png"],
                                    label_visibility="collapsed")
        if uploaded:
            st.image(uploaded, caption="Your photo", use_column_width=True)
 
    with c2:
        st.markdown("**📸 Or use camera**")
        if not st.session_state.camera_enabled:
            if st.button("🎥 Enable Camera", key="en_cam"):
                st.session_state.camera_enabled = True
                st.rerun()
        else:
            camera_image = st.camera_input("Take a picture")
            if camera_image:
                st.image(camera_image, use_column_width=True)
            if st.button("❌ Close Camera", key="cl_cam"):
                st.session_state.camera_enabled = False
                st.rerun()
 
    uplift1 = st.checkbox("🎶 Cheer me up instead of matching my mood", key="up1")
 
    if st.button("🔍 Analyze & Recommend", key="go_face"):
        try:
            img_bytes = None
            if uploaded:
                img_bytes = uploaded.read()
            elif st.session_state.camera_enabled and "camera_image" in locals() and camera_image:
                img_bytes = camera_image.getvalue()
 
            if not img_bytes:
                st.warning("Please upload or capture an image first.")
            else:
                with st.spinner("🤖 Detecting emotion from face..."):
                    emo = post_face_emotion(img_bytes)
                st.session_state.last_emotion = emo
                render_emotion_result(emo)
 
                with st.spinner("🎵 Finding perfect songs..."):
                    recs = post_recommendations(emo, uplift1, selected_genre, n_songs)
                st.session_state.last_recs = recs
                st.markdown(f"### 🎧 Your Playlist ({len(recs)} songs)")
                render_songs(recs)
 
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot reach backend. Is Terminal 1 running?")
        except Exception as e:
            st.error(f"Error: {e}")
 
# -------------------------
# Tab 2: Webcam
# -------------------------
with tab_webcam:
    st.markdown("### 🎥 Live Webcam Detection")
    st.markdown(
        "<div class='music-card'>Captures 30 frames from your webcam and detects "
        "your dominant emotion. Sit in front of your camera before clicking!</div>",
        unsafe_allow_html=True
    )
    st.info("💡 Make sure you are well-lit and facing the camera directly.")
    uplift2 = st.checkbox("🎶 Cheer me up instead of matching my mood", key="up2")
 
    if st.button("🎥 Start Webcam Analysis", key="go_webcam"):
        try:
            with st.spinner("📸 Capturing from webcam (5–10 seconds)..."):
                emo = post_webcam_emotion()
            st.session_state.last_emotion = emo
            render_emotion_result(emo)
 
            with st.spinner("🎵 Finding perfect songs..."):
                recs = post_recommendations(emo, uplift2, selected_genre, n_songs)
            st.session_state.last_recs = recs
            st.markdown(f"### 🎧 Your Playlist ({len(recs)} songs)")
            render_songs(recs)
 
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot reach backend. Is Terminal 1 running?")
        except Exception as e:
            st.error(f"Error: {e}")
 
# -------------------------
# Tab 3: Text
# -------------------------
with tab_text:
    st.markdown("### 💬 Detect Emotion from Text")
    st.markdown(
        "<div class='music-card'>Type how you're feeling. BERT model analyzes your "
        "text and recommends matching songs with confidence scores.</div>",
        unsafe_allow_html=True
    )
    user_text = st.text_area("How are you feeling today?",
                              "I am feeling very happy and excited today!", height=120)
    uplift3 = st.checkbox("🎶 Cheer me up instead of matching my mood", key="up3")
 
    if st.button("🔍 Analyze & Recommend", key="go_text"):
        try:
            if not user_text.strip():
                st.warning("Please type something first.")
            else:
                with st.spinner("🤖 Analyzing your text with BERT..."):
                    emo, scores = post_text_emotion(user_text)
                st.session_state.last_emotion = emo
                render_emotion_result(emo)
 
                if scores:
                    with st.expander("📊 See all emotion scores"):
                        render_confidence_bars(scores)
 
                with st.spinner("🎵 Finding perfect songs..."):
                    recs = post_recommendations(emo, uplift3, selected_genre, n_songs)
                st.session_state.last_recs = recs
                st.markdown(f"### 🎧 Your Playlist ({len(recs)} songs)")
                render_songs(recs)
 
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot reach backend. Is Terminal 1 running?")
        except Exception as e:
            st.error(f"Error: {e}")
 
# =====================
# Footer
# =====================
st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
with st.expander("📋 Last session results"):
    if st.session_state.last_emotion:
        render_emotion_result(st.session_state.last_emotion)
    render_songs(st.session_state.last_recs)