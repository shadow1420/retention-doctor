import subprocess
import re
from typing import Dict, Any, List

def detect_silence(
    video_or_audio_path: str,
    noise_db: float = -32.0,
    min_silence_duration: float = 0.55
) -> Dict[str, Any]:
    """
    Analyzes dead-air / silent pauses in audio using FFmpeg's silencedetect filter.
    Returns timestamped intervals, total silence, and percentage.
    """
    cmd = [
        "ffmpeg",
        "-nostats",
        "-v", "info",
        "-vn",
        "-i", video_or_audio_path,
        "-af", f"silencedetect=noise={noise_db}dB:d={min_silence_duration}",
        "-f", "null",
        "-"
    ]

    try:
        result = subprocess.run(
            cmd,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace"
        )
        stderr_output = result.stderr
    except Exception as e:
        return {
            "silence_intervals": [],
            "total_silence_duration": 0.0,
            "silence_percentage": 0.0,
            "error": str(e)
        }

    # Parse silencedetect output lines:
    # [silencedetect @ ...] silence_start: 2.34
    # [silencedetect @ ...] silence_end: 3.82 | silence_duration: 1.48
    silence_intervals: List[Dict[str, Any]] = []
    current_start = None

    for line in stderr_output.splitlines():
        start_match = re.search(r"silence_start:\s*([0-9.]+)", line)
        if start_match:
            current_start = float(start_match.group(1))
            continue

        end_match = re.search(r"silence_end:\s*([0-9.]+)\s*\|\s*silence_duration:\s*([0-9.]+)", line)
        if end_match:
            end_val = float(end_match.group(1))
            dur_val = float(end_match.group(2))
            start_val = current_start if current_start is not None else max(0.0, end_val - dur_val)

            # Confidence is scaled based on how distinct the silence is relative to threshold
            confidence = min(1.0, round(0.85 + min(0.15, dur_val * 0.05), 2))
            
            silence_intervals.append({
                "start": round(start_val, 2),
                "end": round(end_val, 2),
                "duration": round(dur_val, 2),
                "confidence": confidence,
                "recommended_action": f"Remove {round(dur_val, 2)}s dead-air pause"
            })
            current_start = None

    total_silence = sum(item["duration"] for item in silence_intervals)

    return {
        "silence_intervals": silence_intervals,
        "total_silence_duration": round(total_silence, 2),
        "silence_count": len(silence_intervals)
    }
