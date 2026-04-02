import cv2
import numpy as np
from keras.models import load_model
from collections import Counter
import os
 
# Load model globally once
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'models', 'mobilenetv2.keras')
model = load_model(MODEL_PATH)
emotion_labels = ['angry', 'happy', 'sad', 'surprise', 'neutral']
detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
 
# ============================================================
# NEUTRAL BIAS FIX:
# If model predicts "neutral" but confidence < this threshold,
# pick the next best non-neutral emotion instead.
# Raise this value (e.g. 0.75) to make it even less biased.
# ============================================================
NEUTRAL_CONFIDENCE_THRESHOLD = 0.70
 
def smart_predict(pred):
    """
    Applies anti-neutral-bias logic:
    - If top prediction is neutral AND confidence < threshold → pick 2nd best
    - Otherwise return top prediction normally
    """
    scores = pred[0]
    sorted_indices = np.argsort(scores)[::-1]  # descending order
 
    top_idx = sorted_indices[0]
    top_label = emotion_labels[top_idx]
    top_conf = scores[top_idx]
 
    print(f"[DEBUG] Raw scores: {dict(zip(emotion_labels, scores.tolist()))}")
    print(f"[DEBUG] Top prediction: {top_label} ({top_conf:.2f})")
 
    # If neutral wins but not confidently → use 2nd best non-neutral
    if top_label == 'neutral' and top_conf < NEUTRAL_CONFIDENCE_THRESHOLD:
        for idx in sorted_indices[1:]:
            if emotion_labels[idx] != 'neutral':
                second_label = emotion_labels[idx]
                second_conf = scores[idx]
                print(f"[DEBUG] Neutral not confident ({top_conf:.2f} < {NEUTRAL_CONFIDENCE_THRESHOLD})")
                print(f"[DEBUG] Using 2nd best: {second_label} ({second_conf:.2f})")
                return second_label
 
    print(f"[DEBUG] Final emotion: {top_label}")
    return top_label
 
 
def predict_emotion_image(img_path):
    image = cv2.imread(img_path)
    if image is None:
        return "Could not read image"
 
    rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
 
    # Try with relaxed parameters first
    faces = detector.detectMultiScale(rgb, scaleFactor=1.05, minNeighbors=3, minSize=(30, 30))
 
    # Fallback: try grayscale if RGB detection fails
    if len(faces) == 0:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, scaleFactor=1.05, minNeighbors=2, minSize=(20, 20))
        print("[DEBUG] Used grayscale fallback for detection")
 
    if len(faces) == 0:
        print("[DEBUG] No face detected in image")
        return "No Face Detected"
 
    for (x, y, w, h) in faces:
        # Add 10% padding around face for better context
        pad_w = int(0.1 * w)
        pad_h = int(0.1 * h)
        x1 = max(0, x - pad_w)
        y1 = max(0, y - pad_h)
        x2 = min(rgb.shape[1], x + w + pad_w)
        y2 = min(rgb.shape[0], y + h + pad_h)
 
        face_crop = rgb[y1:y2, x1:x2]
        face_resized = cv2.resize(face_crop, (128, 128))
        face_input = np.expand_dims(face_resized, axis=0) / 255.0
        pred = model.predict(face_input, verbose=0)
 
        return smart_predict(pred)
 
    return "No Face Detected"
 
 
def predict_emotion_webcam():
    cap = cv2.VideoCapture(0)
 
    if not cap.isOpened():
        return "Camera not accessible"
 
    emotions_detected = []
    total_frames = 30
    frame_count = 0
 
    while frame_count < total_frames:
        ret, frame = cap.read()
        if not ret:
            break
 
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        faces = detector.detectMultiScale(rgb, scaleFactor=1.05, minNeighbors=3, minSize=(30, 30))
 
        for (x, y, w, h) in faces:
            face_crop = rgb[y:y+h, x:x+w]
            face_resized = cv2.resize(face_crop, (128, 128))
            face_input = np.expand_dims(face_resized, axis=0) / 255.0
            pred = model.predict(face_input, verbose=0)
            emotions_detected.append(smart_predict(pred))
 
        frame_count += 1
 
    cap.release()
 
    if emotions_detected:
        # Filter out any stray neutrals using majority vote
        non_neutral = [e for e in emotions_detected if e != 'neutral']
        if non_neutral:
            majority = Counter(non_neutral).most_common(1)[0][0]
        else:
            majority = Counter(emotions_detected).most_common(1)[0][0]
        print(f"[DEBUG] All webcam emotions: {emotions_detected}")
        print(f"[DEBUG] Final majority: {majority}")
        return majority
 
    return "No Face Detected"
 