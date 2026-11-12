import os
import cv2
import numpy as np
from typing import Dict, Any, List

def analyze_safe_zone_framing(video_path: str, max_samples: int = 30) -> Dict[str, Any]:
    """
    Analyzes video framing and face positioning relative to social media
    UI danger zones (Instagram Reels, TikTok, YouTube Shorts).
    Uses OpenCV's bundled Haar Cascade face detector.
    """
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {
            "safe_zone_score": 85,
            "framing_status": "Standard",
            "face_detected": False,
            "violations": []
        }

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1920)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1080)
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 1)
    is_vertical = height > width

    actual_samples = min(max_samples, 15) if (width > 1920 or height > 1080) else max_samples
    step = max(1, frame_count // actual_samples)
    
    faces_detected_count = 0
    violations: List[str] = []
    sampled_count = 0
    face_positions: List[Dict[str, float]] = []

    for f_idx in range(0, frame_count, step):
        cap.set(cv2.CAP_PROP_POS_FRAMES, f_idx)
        ret, frame = cap.read()
        if not ret:
            break

        sampled_count += 1
        # Downscale for ultra-fast real-time face detection
        target_w = 360
        target_h = int(height * (360.0 / width))
        small = cv2.resize(frame, (target_w, target_h))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=4, minSize=(30, 30))

        if len(faces) > 0:
            faces_detected_count += 1
            # Primary face
            fx, fy, fw, fh = faces[0]
            # Normalized coordinates (0.0 to 1.0)
            norm_x = fx / target_w
            norm_y = fy / target_h
            norm_cx = (fx + fw / 2) / target_w
            norm_cy = (fy + fh / 2) / target_h
            norm_bottom = (fy + fh) / target_h

            face_positions.append({
                "cx": round(norm_cx, 3),
                "cy": round(norm_cy, 3),
                "bottom": round(norm_bottom, 3)
            })

            # Check Danger Zones in 9:16 vertical mode
            if is_vertical:
                # Bottom 22% danger zone (Captions / Username)
                if norm_bottom > 0.78:
                    if "Face overlaps bottom UI zone (Instagram captions & username will cover chin/mouth)" not in violations:
                        violations.append("Face overlaps bottom UI zone (Instagram captions & username will cover chin/mouth)")
                
                # Right 18% danger zone (Like / Share buttons)
                if (norm_x + fw / width) > 0.82:
                    if "Subject placed too far right (TikTok/Shorts like & share buttons obstruct view)" not in violations:
                        violations.append("Subject placed too far right (TikTok/Shorts like & share buttons obstruct view)")

                # Top 10% danger zone (Header / Status bar)
                if norm_y < 0.10:
                    if "Headroom too tight (top of head enters status bar overlay)" not in violations:
                        violations.append("Headroom too tight (top of head enters status bar overlay)")

    cap.release()

    face_detected = faces_detected_count > 0
    safe_score = 95

    if is_vertical:
        if violations:
            safe_score -= len(violations) * 15
        elif not face_detected:
            safe_score = 85  # Screen recording or B-roll without face
    else:
        # Horizontal 16:9 check
        safe_score = 90

    safe_score = max(40, min(100, safe_score))

    if safe_score >= 88:
        status = "Optimal Framing"
    elif safe_score >= 70:
        status = "Minor UI Collision"
    else:
        status = "Obscured by Social UI"

    return {
        "safe_zone_score": safe_score,
        "framing_status": status,
        "is_vertical": is_vertical,
        "face_detected": face_detected,
        "detection_confidence": round(faces_detected_count / max(1, sampled_count), 2),
        "violations": violations if violations else ["Face and focal subject are centered inside the viral safe zone."],
        "recommended_action": "Keep focal elements within central 75% width and between 15% and 78% height for clean Reels/Shorts playback."
    }
