import cv2
import numpy as np
import re
from typing import Dict, Any, List, Optional

def analyze_visuals(
    video_path: str,
    sentence_segments: Optional[List[Dict[str, Any]]] = None,
    max_samples: int = 600,
    genre_info: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Maximum Visual Dynamics Analysis using OpenCV:
    - Detects scene cuts using color histogram / pixel differences.
    - Measures Average Shot Length (ASL) and Visual Velocity Score (0-100).
    - Identifies Visual Boredom Windows (intervals > 3.0s without a cut or visual transition).
    - Generates 3 contextual B-roll search terms and an AI visual prompt for every static section.
    - Flags recommended dynamic punch-in zoom timestamps.
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return {
            "scene_cuts": [],
            "static_scenes": [],
            "boredom_windows": [],
            "suggested_zooms": [],
            "b_roll_prompts": [],
            "visual_velocity_score": 50,
            "visual_pace_rating": "Unknown",
            "average_shot_length": 0.0,
            "fps": 30.0,
            "width": 1920,
            "height": 1080,
            "duration": 0.0,
            "visual_cut_count": 0
        }

    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) or 1920)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) or 1080)
    duration = frame_count / fps if fps > 0 else 0.0

    # Adaptive sampling: For 4K/high-res (or long) videos, sample every 1.5s (max 60 frames)
    # for ultra-fast, responsive processing while preserving shot pacing accuracy
    if width > 1920 or height > 1080 or frame_count > 1500:
        step = max(1, int(fps * 1.5))
    else:
        step = max(1, int(fps / 2))
    
    prev_gray = None
    scene_cuts: List[float] = []
    static_segments: List[Dict[str, Any]] = []
    boredom_windows: List[Dict[str, Any]] = []
    
    last_transition_time = 0.0
    static_start = 0.0
    is_static = False

    current_frame_idx = 0

    while current_frame_idx < frame_count:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame_idx)
        ret, frame = cap.read()
        if not ret:
            break

        timestamp = round(current_frame_idx / fps, 2)
        small = cv2.resize(frame, (160, 90))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)

        if prev_gray is not None:
            diff = cv2.absdiff(gray, prev_gray)
            mean_diff = float(np.mean(diff))

            # Scene Cut Detection threshold (sudden large pixel change)
            if mean_diff > 35.0:
                scene_cuts.append(timestamp)
                
                # Check if the previous interval was a boredom window (>3.0s without a cut)
                gap_duration = timestamp - last_transition_time
                if gap_duration >= 3.2:
                    boredom_windows.append({
                        "start": round(last_transition_time, 2),
                        "end": round(timestamp, 2),
                        "duration": round(gap_duration, 2),
                        "severity": "high" if gap_duration >= 5.5 else "med"
                    })

                if is_static:
                    dur = timestamp - static_start
                    if dur >= 4.0:
                        static_segments.append({
                            "start": round(static_start, 2),
                            "end": round(timestamp, 2),
                            "duration": round(dur, 2)
                        })
                    is_static = False
                last_transition_time = timestamp

            # Static frame threshold (very low movement)
            elif mean_diff < 4.5:
                if not is_static:
                    is_static = True
                    static_start = timestamp
            else:
                if is_static:
                    dur = timestamp - static_start
                    if dur >= 4.0:
                        static_segments.append({
                            "start": round(static_start, 2),
                            "end": round(timestamp, 2),
                            "duration": round(dur, 2)
                        })
                    is_static = False

        prev_gray = gray
        current_frame_idx += step

    cap.release()

    # Final interval check
    final_gap = duration - last_transition_time
    if final_gap >= 3.2:
        boredom_windows.append({
            "start": round(last_transition_time, 2),
            "end": round(duration, 2),
            "duration": round(final_gap, 2),
            "severity": "high" if final_gap >= 5.5 else "med"
        })

    if is_static and duration - static_start >= 4.0:
        static_segments.append({
            "start": round(static_start, 2),
            "end": round(duration, 2),
            "duration": round(duration - static_start, 2)
        })

    # Calculate Average Shot Length (ASL)
    total_shots = len(scene_cuts) + 1
    asl = round(duration / total_shots, 2) if total_shots > 0 else duration

    # Compute Visual Velocity Score (0-100)
    # Modern short-form: ASL between 2.0s and 3.5s is optimal (100 pts)
    if asl <= 3.5:
        velocity_score = 95
        rating = "Elite Short-Form Pacing (Fast Cuts)"
    elif asl <= 5.0:
        velocity_score = 80
        rating = "Good Visual Pacing"
    elif asl <= 8.0:
        velocity_score = 62
        rating = "Moderate / Traditional YouTube Pacing"
    else:
        velocity_score = 45
        rating = "High Boredom Risk (Visual Stagnation)"

    # Penalize visual velocity if any severe static boredom window exists
    # Even if ASL is low, a single 8-10s static gap will cause viewers to swipe away
    max_boredom = max([w["duration"] for w in boredom_windows], default=0.0)
    if max_boredom >= 8.0:
        velocity_score = min(velocity_score, 45)
        rating = f"Severe Stagnation ({max_boredom:.1f}s static scene)"
    elif max_boredom >= 5.0:
        velocity_score = min(velocity_score, 60)
        rating = f"High Boredom Risk ({max_boredom:.1f}s static gap)"
    elif max_boredom >= 3.5:
        velocity_score = min(velocity_score, 75)
        rating = f"Moderate Visual Lull ({max_boredom:.1f}s gap)"

    # Suggest punch-in / zoom intervals
    suggested_zooms: List[Dict[str, Any]] = []
    for win in boredom_windows:
        punch_time = round(win["start"] + min(2.5, win["duration"] / 2.0), 2)
        suggested_zooms.append({
            "timestamp": punch_time,
            "type": "punch_in",
            "scale": 1.15,
            "duration": min(3.0, round(win["duration"] - 1.5, 2)),
            "reason": f"Break visual stagnation after {round(punch_time - win['start'], 1)}s without visual transition"
        })

    # Generate B-Roll & Visual Insert Prompts for each boredom window
    b_roll_prompts = generate_b_roll_suggestions(boredom_windows, sentence_segments, genre_info=genre_info)

    return {
        "scene_cuts": scene_cuts,
        "static_scenes": static_segments,
        "boredom_windows": boredom_windows,
        "suggested_zooms": suggested_zooms,
        "b_roll_prompts": b_roll_prompts,
        "visual_velocity_score": velocity_score,
        "visual_pace_rating": rating,
        "average_shot_length": asl,
        "fps": round(fps, 2),
        "width": width,
        "height": height,
        "duration": round(duration, 2),
        "visual_cut_count": len(scene_cuts)
    }


def generate_b_roll_suggestions(
    boredom_windows: List[Dict[str, Any]],
    sentence_segments: Optional[List[Dict[str, Any]]],
    genre_info: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Extracts spoken context for each visual boredom interval and produces
    3 actionable, professional B-Roll search terms and 1 Midjourney/DALL-E prompt
    tailored to the video's genre and visual aesthetic.
    """
    suggestions = []
    genre_type = (genre_info.get("genre") if genre_info else "general") or "general"
    subject_title = (genre_info.get("subject") if genre_info else "Visual Insert") or "Visual Insert"

    stop_words = {
        "the", "this", "that", "with", "from", "your", "have", "will", "what", "video",
        "about", "there", "when", "here", "late", "time", "over", "just", "really", "then",
        "soon", "some", "only", "also", "back", "more", "much", "very", "every", "look",
        "take", "give", "make", "said", "were", "been", "come", "into", "their", "them",
        "which", "where", "after", "before", "right", "down", "well", "even"
    }

    for win in boredom_windows[:5]:
        w_start = win["start"]
        w_end = win["end"]

        # Find spoken sentences in this interval
        context_words = []
        if sentence_segments:
            for seg in sentence_segments:
                if not (seg.get("end", 0) < w_start or seg.get("start", 0) > w_end):
                    words = re.findall(r"\b[a-zA-Z]{4,}\b", seg.get("text", "").lower())
                    context_words.extend([w for w in words if w not in stop_words])

        if genre_type == "anime_edit":
            subject_str = f"{subject_title} Action Transition"
            search_terms = [
                f"{subject_title.lower()} anime 4k 60fps high speed slash VFX",
                "cinematic glowing particle overlay VFX 60fps",
                "stylized dark anime character aesthetic close up 4k"
            ]
            ai_prompt = (
                f"Cinematic dark anime protagonist {subject_title} surrounded by vibrant purple glowing energy aura, "
                "dramatic rim lighting, photorealistic 8k octane render, vertical 9:16 high visual impact."
            )
        elif genre_type == "gaming":
            subject_str = f"{subject_title} Clutch VFX"
            search_terms = [
                f"{subject_title.lower()} fast paced clutch motion graphic 4k",
                "neon glitch impact transition overlay 60fps",
                "3D gaming particle shockwave visual insert"
            ]
            ai_prompt = (
                f"Hyper-detailed 3D render of {subject_title} legendary mythical ability with electric lightning VFX, "
                "volumetric lighting, Unreal Engine 5 render, vertical 9:16."
            )
        elif genre_type == "podcast":
            p_sub = context_words[0].capitalize() if context_words else "Mindset"
            s_sub = context_words[1].capitalize() if len(context_words) > 1 else "Focus"
            subject_str = f"{p_sub} {s_sub}".strip()
            search_terms = [
                f"cinematic 4k footage of {p_sub.lower()} neural activity",
                f"high-tech animated 3D infographic explaining {p_sub.lower()}",
                "modern studio documentary macro close up 4k"
            ]
            ai_prompt = (
                f"Photorealistic cinematic visualization of {p_sub.lower()} and {s_sub.lower()} neural pathways in human brain, "
                "glowing bioluminescent synapses, 8k macro photography, vertical 9:16 ratio."
            )
        else:
            p_sub = context_words[0].capitalize() if context_words else "Dynamic"
            s_sub = context_words[1].capitalize() if len(context_words) > 1 else "Action"
            subject_str = f"{p_sub} {s_sub}".strip()
            search_terms = [
                f"cinematic 4k slow motion visual of {p_sub.lower()}",
                f"clean modern 3D motion graphic {p_sub.lower()} {s_sub.lower()}",
                f"dynamic visual transition insert 60fps {p_sub.lower()}"
            ]
            ai_prompt = (
                f"Commercial-grade hyper-realistic cinematic 3D render of {p_sub.lower()} {s_sub.lower()}, "
                "volumetric studio lighting, 8k resolution, modern aesthetic, vertical 9:16 aspect ratio."
            )

        suggestions.append({
            "timestamp_range": f"{w_start:.1f}s - {w_end:.1f}s",
            "duration": win["duration"],
            "subject": subject_str,
            "stock_search_terms": search_terms,
            "ai_image_prompt": ai_prompt
        })

    return suggestions
