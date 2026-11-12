import os
from typing import Dict, Any, List, Optional
from .speech import analyze_speech
from .silence import detect_silence
from .hook import evaluate_hook
from .visual import analyze_visuals
from .vocal_dynamics import analyze_vocal_dynamics
from .safe_zone import analyze_safe_zone_framing
from .retention_curve import calculate_predicted_retention_curve
from .genre import detect_video_genre
from .virality import calculate_viral_potential, get_optimal_posting_times

def run_retention_audit(video_path: str, platform_metrics: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Executes the Maximum Multi-Dimensional Retention Audit:
    1. Speech Transcription & Word Timestamps (faster-whisper)
    2. Dead-air / Silence Detection (FFmpeg silencedetect)
    3. Visual Dynamics, ASL, Boredom Windows & AI B-Roll Prompts (OpenCV)
    4. Hook Score & 5 Alternative Hooks
    5. Vocal Dynamics, Monotone Detection & Pitch Inflection
    6. Social Media Safe Zone Framing & Face Tracking
    7. Second-by-Second Predicted Retention Risk Curve & Top Drop-offs
    8. Consolidated Retention-Risk Timeline
    9. Real Platform Metric Calibration (YouTube / TikTok views, likes, comments)
    """
    # 1. Speech Analysis
    speech_res = analyze_speech(video_path)
    word_timestamps = speech_res.get("word_timestamps", [])
    sentence_segments = speech_res.get("sentence_segments", [])
    transcript = speech_res.get("transcript_text", "")
    filler_words = speech_res.get("filler_words", [])
    wpm = speech_res.get("words_per_minute", 0.0)

    # 2. Silence Detection
    silence_res = detect_silence(video_path, noise_db=-32.0, min_silence_duration=0.55)
    silence_intervals = silence_res.get("silence_intervals", [])
    total_silence = silence_res.get("total_silence_duration", 0.0)

    # 3. Visual Dynamics & Pattern Interrupts (pass sentence_segments for contextual B-roll)
    visual_res = analyze_visuals(video_path, sentence_segments=sentence_segments)
    scene_cuts = visual_res.get("scene_cuts", [])
    static_scenes = visual_res.get("static_scenes", [])
    boredom_windows = visual_res.get("boredom_windows", [])
    duration = visual_res.get("duration", speech_res.get("audio_duration", 0.0))

    silence_pct = round((total_silence / duration * 100.0), 1) if duration > 0 else 0.0

    # 3b. Content Genre Intelligence (AMV / Anime Edit / Gaming / Talking-Head)
    filename = os.path.basename(video_path)
    genre_info = detect_video_genre(
        filename=filename,
        transcript=transcript,
        word_count=speech_res.get("word_count", 0),
        average_shot_length=visual_res.get("average_shot_length", 2.0),
        visual_cut_count=len(scene_cuts),
        duration=duration
    )
    visual_res["genre_info"] = genre_info

    # Re-generate B-roll suggestions with fully calibrated genre context
    from .visual import generate_b_roll_suggestions
    visual_res["b_roll_prompts"] = generate_b_roll_suggestions(boredom_windows, sentence_segments, genre_info=genre_info)

    # 4. Hook Analysis
    first_silence = silence_intervals[0]["duration"] if silence_intervals and silence_intervals[0]["start"] < 1.0 else 0.0
    hook_res = evaluate_hook(
        transcript=transcript,
        word_timestamps=word_timestamps,
        first_silence_duration=first_silence,
        video_duration=duration,
        genre_info=genre_info,
        scene_cuts=scene_cuts
    )

    # 5. Vocal Dynamics & Monotone Voice Detection
    vocal_res = analyze_vocal_dynamics(video_path)
    monotone_segments = vocal_res.get("monotone_segments", [])
    emphasis_peaks = vocal_res.get("emphasis_peaks", [])

    # 6. Social Media Safe Zone & Face Framing
    safe_zone_res = analyze_safe_zone_framing(video_path)

    # 7. Second-by-Second Predicted Retention Risk Curve
    retention_curve_res = calculate_predicted_retention_curve(
        duration=duration,
        hook_score=hook_res.get("hook_score", 70),
        first_word_latency=hook_res.get("first_word_latency", 0.0),
        silence_intervals=silence_intervals,
        monotone_segments=monotone_segments,
        boredom_windows=boredom_windows,
        scene_cuts=scene_cuts,
        emphasis_peaks=emphasis_peaks
    )

    # 8. Build Unified Retention-Risk Timeline
    timeline: List[Dict[str, Any]] = []

    # A. Hook Event
    timeline.append({
        "timestamp": 0.0,
        "type": "hook",
        "severity": "high" if hook_res["hook_score"] < 65 else ("med" if hook_res["hook_score"] < 80 else "low"),
        "title": f"Hook Assessment ({hook_res['hook_grade']} Grade - {hook_res['hook_score']}/100)",
        "description": hook_res["hook_explanation"],
        "actionable_fix": hook_res["hook_recommendations"][0] if hook_res.get("hook_recommendations") else ("Maintain high visual velocity to match the audio drops." if genre_info.get("is_music_edit") else "Start speaking immediately on frame 1.")
    })

    # B. Silence / Dead-Air Events
    for s in silence_intervals:
        severity = "high" if s["duration"] >= 1.5 else "med"
        timeline.append({
            "timestamp": s["start"],
            "end_timestamp": s["end"],
            "type": "silence",
            "severity": severity,
            "title": f"Dead-Air Pause ({s['duration']}s)",
            "description": f"Silent interval from {s['start']}s to {s['end']}s where viewer engagement drops.",
            "actionable_fix": f"Auto-Fixer can trim this {s['duration']}s gap seamlessly."
        })

    # C. Visual Boredom / Pattern Interrupt Gaps (>3.0s without transition)
    for bw in boredom_windows:
        timeline.append({
            "timestamp": bw["start"],
            "end_timestamp": bw["end"],
            "type": "static_scene",
            "severity": bw.get("severity", "med"),
            "title": f"Visual Boredom Window ({bw['duration']}s)",
            "description": f"No cut or camera motion for {bw['duration']}s (exceeds 3.0s short-form threshold).",
            "actionable_fix": "Insert punch-in zoom, animated caption, or B-roll overlay."
        })

    # D. Monotone Delivery Events
    for mono in monotone_segments:
        timeline.append({
            "timestamp": mono["start"],
            "end_timestamp": mono["end"],
            "type": "monotone",
            "severity": mono.get("severity", "med"),
            "title": f"Monotone Vocal Delivery ({mono['duration']}s)",
            "description": mono["description"],
            "actionable_fix": mono["recommendation"]
        })

    # E. Safe Zone Warning (if any)
    if safe_zone_res.get("violations") and safe_zone_res["safe_zone_score"] < 85:
        timeline.append({
            "timestamp": 0.5,
            "type": "safe_zone",
            "severity": "med",
            "title": "UI Safe Zone Warning",
            "description": safe_zone_res["violations"][0],
            "actionable_fix": "Re-center focal subject away from Instagram/TikTok overlay."
        })

    # F. Filler Words Events (limit to top 8 distinct occurrences)
    for fw in filler_words[:8]:
        timeline.append({
            "timestamp": fw["start"],
            "end_timestamp": fw["end"],
            "type": "filler",
            "severity": "low",
            "title": f"Filler Word: '{fw['word']}'",
            "description": f"Hesitation at {fw['start']}s.",
            "actionable_fix": "Consider tightening audio cut."
        })

    timeline.sort(key=lambda x: x["timestamp"])

    # 8. Compute Virality Potential & Optimal Posting Windows
    viral_potential = calculate_viral_potential(
        hook_score=hook_res.get("hook_score", 70),
        visual_velocity_score=visual_res.get("visual_velocity_score", 75),
        silence_percentage=silence_pct,
        predicted_completion_rate=retention_curve_res.get("predicted_completion_rate", 75.0),
        safe_zone_score=safe_zone_res.get("safe_zone_score", 85),
        genre_info=genre_info,
        platform_metrics=platform_metrics
    )
    posting_schedule = get_optimal_posting_times(genre_info)

    return {
        "genre": genre_info,
        "hook": hook_res,
        "viral_potential": viral_potential,
        "posting_schedule": posting_schedule,
        "platform_metrics": platform_metrics or {},
        "speech": {
            "transcript_text": transcript,
            "words_per_minute": wpm,
            "word_timestamps": word_timestamps,
            "sentence_segments": sentence_segments,
            "filler_words": filler_words,
            "word_count": speech_res.get("word_count", 0)
        },
        "silence": {
            "intervals": silence_intervals,
            "total_duration": total_silence,
            "percentage": silence_pct
        },
        "visual": visual_res,
        "vocal": vocal_res,
        "safe_zone": safe_zone_res,
        "retention_curve": retention_curve_res,
        "retention_timeline": timeline,
        "duration": duration
    }
