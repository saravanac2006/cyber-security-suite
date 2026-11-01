import cv2
import numpy as np
import tempfile
import os
from PIL import Image


class VideoProcessor:

    def __init__(self):
        self.face_cascade = None
        try:
            if hasattr(cv2, "CascadeClassifier") and hasattr(cv2, "data"):
                cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
                self.face_cascade = cv2.CascadeClassifier(cascade_path)
        except Exception:
            pass

    def extract_frames(self, video_path: str, max_frames: int = 30) -> list:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            return []

        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if total <= 0:
            cap.release()
            return []

        step = max(1, total // max_frames)
        frames = []
        idx = 0

        while len(frames) < max_frames:
            cap.set(cv2.CAP_PROP_POS_FRAMES, idx)
            ret, frame = cap.read()
            if not ret:
                break
            frames.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            idx += step

        cap.release()
        return frames

    def extract_frames_from_upload(self, uploaded_file, max_frames: int = 30) -> list:
        suffix = os.path.splitext(uploaded_file.name)[-1]
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        try:
            frames = self.extract_frames(tmp_path, max_frames)
        finally:
            os.unlink(tmp_path)
        return frames

    def detect_faces(self, frame: np.ndarray) -> list:
        if self.face_cascade is None:
            return []
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_RGB2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
            if len(faces) == 0:
                return []
            return [tuple(f) for f in faces]
        except Exception:
            return []

    def crop_face(self, frame: np.ndarray, face_rect: tuple, padding: int = 20) -> np.ndarray:
        x, y, w, h = face_rect
        h_img, w_img = frame.shape[:2]
        x1 = max(0, x - padding)
        y1 = max(0, y - padding)
        x2 = min(w_img, x + w + padding)
        y2 = min(h_img, y + h + padding)
        return frame[y1:y2, x1:x2]

    def frames_to_pil(self, frames: list) -> list:
        return [Image.fromarray(f) for f in frames]
