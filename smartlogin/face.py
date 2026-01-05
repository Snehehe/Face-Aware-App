import numpy as np
import cv2
from deepface import DeepFace

MODEL_NAME = "Facenet512"

def extract_embedding(bgr_frame):
    """
    Returns (embedding, quality_score) for the largest detected face in the frame,
    or (None, None) if no face found.
    """
    # DeepFace expects RGB
    rgb = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)

    try:
        reps = DeepFace.represent(
            img_path=rgb,
            model_name=MODEL_NAME,
            detector_backend="opencv",  
            enforce_detection=False
        )
    except Exception:
        return None, None

    if not reps:
        return None, None

    if isinstance(reps, dict):
        reps = [reps]

    # Choose largest face if facial_area available; else take first
    best = reps[0]
    best_area = -1

    for r in reps:
        area = -1
        fa = r.get("facial_area")
        if fa and all(k in fa for k in ("w", "h")):
            area = fa["w"] * fa["h"]
        if area > best_area:
            best_area = area
            best = r

    emb = np.array(best["embedding"], dtype=np.float32)
    emb /= (np.linalg.norm(emb) + 1e-12)

    quality = float(best_area if best_area > 0 else 0.0)
    return emb, quality

def cosine_sim(a, b):
    return float(np.dot(a, b))
