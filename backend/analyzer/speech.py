import os
import re
import subprocess
import random
from typing import Dict, Any, List
from faster_whisper import WhisperModel

# Common filler words to detect
FILLER_PATTERNS = {
    "um", "uh", "er", "ah", "like", "you know", "actually", 
    "basically", "literally", "sort of", "kind of", "i mean", "so yeah"
}

_model_cache = None

def get_whisper_model():
    global _model_cache
    if _model_cache is None:
        # Load 'base' model with int8 CPU compute type for fast, reliable local processing
        # Base model is superior to 'tiny' for avoiding repetition loops and higher accuracy
        _model_cache = WhisperModel("base", device="cpu", compute_type="int8")
    return _model_cache


def analyze_speech(audio_or_video_path: str) -> Dict[str, Any]:
    """
    Transcribes video/audio using faster-whisper with word-level timestamps,
    calculates WPM, identifies filler words and sentence pacing.
    """
    model = get_whisper_model()

    # Pre-extract 16kHz mono audio via FFmpeg to avoid PyAV demuxing heavy 4K video streams
    temp_wav = None
    input_path = audio_or_video_path
    if audio_or_video_path.lower().endswith(('.mp4', '.mov', '.avi', '.mkv', '.webm')):
        temp_wav = os.path.join(os.path.dirname(audio_or_video_path), f"temp_whisper_{os.getpid()}_{random.randint(1000, 9999)}.wav")
        cmd = ["ffmpeg", "-y", "-nostats", "-v", "error", "-vn", "-i", audio_or_video_path, "-ac", "1", "-ar", "16000", temp_wav]
        try:
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            if os.path.exists(temp_wav) and os.path.getsize(temp_wav) > 0:
                input_path = temp_wav
        except Exception:
            input_path = audio_or_video_path

    try:
        segments_generator, info = model.transcribe(
            input_path,
            beam_size=1,
            word_timestamps=True,
            condition_on_previous_text=False,
            repetition_penalty=1.2,
            no_repeat_ngram_size=3,
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
    finally:
        pass

    full_transcript_parts = []
    word_timestamps = []
    sentence_segments = []
    detected_fillers = []

    total_words = 0
    spoken_duration = 0.0

    for segment in segments_generator:
        seg_text = segment.text.strip()
        if not seg_text:
            continue

        full_transcript_parts.append(seg_text)
        
        sentence_segments.append({
            "text": seg_text,
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "duration": round(segment.end - segment.start, 2)
        })

        if segment.words:
            for w in segment.words:
                clean_w = re.sub(r"[^\w\s']", "", w.word).strip().lower()
                if not clean_w:
                    continue

                total_words += 1
                word_info = {
                    "word": w.word.strip(),
                    "clean": clean_w,
                    "start": round(w.start, 2),
                    "end": round(w.end, 2),
                    "probability": round(w.probability, 2)
                }
                word_timestamps.append(word_info)

                # Check filler words
                if clean_w in FILLER_PATTERNS:
                    detected_fillers.append({
                        "word": w.word.strip(),
                        "start": round(w.start, 2),
                        "end": round(w.end, 2),
                        "severity": "medium"
                    })

    # Calculate overall Words Per Minute (WPM)
    total_audio_duration = info.duration if hasattr(info, "duration") and info.duration else 0.0
    if total_audio_duration <= 0 and word_timestamps:
        total_audio_duration = word_timestamps[-1]["end"]

    wpm = 0.0
    if total_audio_duration > 0 and total_words > 0:
        wpm = round((total_words / (total_audio_duration / 60.0)), 1)

    full_transcript = " ".join(full_transcript_parts)

    if temp_wav and os.path.exists(temp_wav):
        try:
            os.remove(temp_wav)
        except Exception:
            pass

    return {
        "transcript_text": full_transcript,
        "word_timestamps": word_timestamps,
        "sentence_segments": sentence_segments,
        "filler_words": detected_fillers,
        "word_count": total_words,
        "words_per_minute": wpm,
        "audio_duration": round(total_audio_duration, 2),
        "language": getattr(info, "language", "en"),
        "language_probability": round(getattr(info, "language_probability", 1.0), 2)
    }
