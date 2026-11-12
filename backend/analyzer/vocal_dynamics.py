import os
import subprocess
import numpy as np
import soundfile as sf
from typing import Dict, Any, List

def analyze_vocal_dynamics(video_or_audio_path: str, temp_dir: str = None) -> Dict[str, Any]:
    """
    Extracts audio and analyzes:
    - RMS Energy variance (enthusiasm and vocal dynamics)
    - Monotone delivery intervals (flat pitch/energy with low variance)
    - Energy crash segments (sharp drop in volume)
    - Emphasis peaks (words spoken with high vocal punch)
    - Overall Vocal Energy Score (0-100)
    """
    if temp_dir is None:
        temp_dir = os.path.dirname(video_or_audio_path)

    temp_wav = os.path.join(temp_dir, f"temp_vocal_{os.getpid()}_{np.random.randint(1000, 9999)}.wav")

    # Extract 16kHz mono audio via FFmpeg for clean signal analysis
    cmd = [
        "ffmpeg", "-y", "-nostats", "-v", "error",
        "-i", video_or_audio_path,
        "-vn", "-ac", "1", "-ar", "16000",
        temp_wav
    ]
    try:
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        data, sample_rate = sf.read(temp_wav)
    except Exception as e:
        return {
            "vocal_energy_score": 75,
            "monotone_segments": [],
            "energy_crashes": [],
            "emphasis_peaks": [],
            "summary": "Standard vocal profile.",
            "error": str(e)
        }
    finally:
        if os.path.exists(temp_wav):
            try:
                os.remove(temp_wav)
            except Exception:
                pass

    if len(data) == 0:
        return {
            "vocal_energy_score": 50,
            "monotone_segments": [],
            "energy_crashes": [],
            "emphasis_peaks": [],
            "summary": "No audio signal detected."
        }

    total_duration = len(data) / sample_rate

    # Calculate RMS energy in 0.5s windows with 0.25s step
    window_samples = int(sample_rate * 0.5)
    step_samples = int(sample_rate * 0.25)
    
    rms_values = []
    timestamps = []

    for i in range(0, len(data) - window_samples, step_samples):
        chunk = data[i : i + window_samples]
        rms = np.sqrt(np.mean(chunk**2))
        rms_values.append(float(rms))
        timestamps.append(round(i / sample_rate, 2))

    if not rms_values:
        return {
            "vocal_energy_score": 70,
            "monotone_segments": [],
            "energy_crashes": [],
            "emphasis_peaks": [],
            "summary": "Audio too short for vocal dynamics.",
            "waveform": []
        }

    rms_arr = np.array(rms_values)
    mean_rms = float(np.mean(rms_arr))
    std_rms = float(np.std(rms_arr))

    # Detect Monotone Windows (3.0s window where standard deviation of energy is very low)
    # A flat delivery lacks inflection and causes listener fatigue
    monotone_segments: List[Dict[str, Any]] = []
    window_len = 12  # approx 3.0 seconds (12 * 0.25s)

    for i in range(0, len(rms_values) - window_len, 4):
        sub_window = rms_arr[i : i + window_len]
        sub_mean = np.mean(sub_window)
        sub_std = np.std(sub_window)

        # If active speech (not dead silence) but energy variance is minimal
        if sub_mean > mean_rms * 0.35 and sub_std < mean_rms * 0.15:
            start_t = timestamps[i]
            end_t = timestamps[min(i + window_len, len(timestamps) - 1)]
            duration = round(end_t - start_t, 2)
            
            # Avoid overlapping duplicate alerts
            if not monotone_segments or start_t > monotone_segments[-1]["end"] + 1.0:
                monotone_segments.append({
                    "start": start_t,
                    "end": end_t,
                    "duration": duration,
                    "severity": "high" if duration >= 5.0 else "med",
                    "description": f"Monotone vocal delivery for {duration}s. Lacks vocal inflection and tonal contrast.",
                    "recommendation": "Inflect pitch up on key words or insert punch-in zoom."
                })

    # Detect Energy Crashes (sudden drop of >50% energy compared to preceding speech)
    energy_crashes: List[Dict[str, Any]] = []
    for i in range(4, len(rms_values) - 2):
        prev_mean = np.mean(rms_arr[i-4 : i])
        curr_val = rms_arr[i]
        if prev_mean > mean_rms * 0.5 and curr_val < prev_mean * 0.3:
            t = timestamps[i]
            if not energy_crashes or t > energy_crashes[-1]["timestamp"] + 3.0:
                energy_crashes.append({
                    "timestamp": t,
                    "severity": "med",
                    "description": f"Vocal energy dropped sharply at {t}s.",
                    "recommendation": "Maintain vocal projection and diaphragm support."
                })

    # Detect Emphasis Peaks (top 5% energy moments for automated punch-in zooms)
    emphasis_threshold = mean_rms + (1.35 * std_rms)
    emphasis_peaks: List[float] = []
    for i, val in enumerate(rms_values):
        if val > emphasis_threshold:
            t = timestamps[i]
            if not emphasis_peaks or t > emphasis_peaks[-1] + 2.0:
                emphasis_peaks.append(t)

    # Compute Vocal Energy Score (0-100)
    # Balanced dynamic range = higher score; monotone flatline = lower score
    dynamic_ratio = std_rms / (mean_rms + 1e-6)
    base_score = int(np.clip(dynamic_ratio * 120, 45, 96))
    
    # Penalize prolonged monotone sections
    if monotone_segments:
        base_score = max(35, base_score - (len(monotone_segments) * 8))

    if base_score >= 85:
        summary = "Dynamic and engaging vocal delivery with expressive inflection."
    elif base_score >= 70:
        summary = "Solid vocal pacing with occasional flat moments."
    elif base_score >= 55:
        summary = "Slightly monotone delivery. More pitch variation is recommended."
    else:
        summary = "High retention risk: Monotone speech causes viewer scroll-away."

    # Generate normalized waveform peaks (downsampled to 80 points for studio timeline track)
    max_val = float(np.max(rms_arr)) if len(rms_arr) > 0 and np.max(rms_arr) > 0 else 1.0
    norm_peaks = [round(float(max(0.08, min(1.0, val / max_val))), 3) for val in rms_values]
    target_bars = 80
    if len(norm_peaks) > target_bars:
        step = len(norm_peaks) / target_bars
        waveform = [norm_peaks[int(i * step)] for i in range(target_bars)]
    else:
        waveform = norm_peaks

    return {
        "vocal_energy_score": base_score,
        "mean_energy": round(mean_rms, 4),
        "energy_variance": round(std_rms, 4),
        "monotone_segments": monotone_segments,
        "energy_crashes": energy_crashes[:5],
        "emphasis_peaks": emphasis_peaks[:8],
        "waveform": waveform,
        "summary": summary
    }
