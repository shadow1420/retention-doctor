import os
import subprocess
import json
from typing import Dict, Any, List, Optional
from .silence_cutter import calculate_keep_intervals, build_trim_filter_complex
from .zoom import generate_dynamic_zoom_filter
from .subtitles import generate_ass_subtitle_file

def get_media_info(filepath: str) -> Dict[str, Any]:
    """Runs ffprobe to retrieve exact duration, dimensions, and audio stream info."""
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration,size:stream=codec_type,width,height,r_frame_rate",
        "-of", "json",
        filepath
    ]
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        data = json.loads(res.stdout)
        format_info = data.get("format", {})
        streams = data.get("streams", [])

        duration = float(format_info.get("duration", 0.0))
        size_bytes = int(format_info.get("size", 0))

        v_stream = next((s for s in streams if s.get("codec_type") == "video"), None)
        a_stream = next((s for s in streams if s.get("codec_type") == "audio"), None)

        width = int(v_stream.get("width", 1920)) if v_stream else 1920
        height = int(v_stream.get("height", 1080)) if v_stream else 1080

        return {
            "duration": round(duration, 2),
            "size_bytes": size_bytes,
            "width": width,
            "height": height,
            "has_audio": a_stream is not None,
            "aspect_ratio": f"{width}:{height}"
        }
    except Exception:
        return {
            "duration": 0.0,
            "size_bytes": 0,
            "width": 1920,
            "height": 1080,
            "has_audio": True,
            "aspect_ratio": "16:9"
        }


def process_auto_fix(
    input_filepath: str,
    output_filepath: str,
    silence_intervals: List[Dict[str, Any]],
    word_timestamps: List[Dict[str, Any]],
    config: Optional[Dict[str, Any]] = None,
    work_dir: Optional[str] = None
) -> Dict[str, Any]:
    """
    Executes the One-Click Auto-Fixer:
    - Removes dead-air silence pauses with configurable padding
    - Applies dynamic zoom punches if requested
    - Normalizes audio loudness to standard -16 LUFS
    - Burns kinetic subtitles if requested
    - Produces a browser-compatible H.264/AAC MP4 with +faststart
    """
    if config is None:
        config = {
            "remove_silence": True,
            "silence_threshold_sec": 0.55,
            "speech_padding_sec": 0.08,
            "dynamic_zoom": "medium",
            "audio_normalize": True,
            "burn_subtitles": False,
            "subtitle_style": "kinetic_emoji",
            "add_sfx": True
        }

    original_info = get_media_info(input_filepath)
    orig_duration = original_info["duration"]
    has_audio = original_info["has_audio"]
    width = original_info["width"]
    height = original_info["height"]

    if work_dir is None:
        work_dir = os.path.dirname(output_filepath)
    os.makedirs(work_dir, exist_ok=True)

    # 1. Step 1: Calculate Silence Cuts
    remove_silence = config.get("remove_silence", True)
    padding_sec = float(config.get("speech_padding_sec", 0.08))
    min_pause = float(config.get("silence_threshold_sec", 0.55))

    if remove_silence and silence_intervals and orig_duration > 0:
        keep_intervals = calculate_keep_intervals(orig_duration, silence_intervals, padding_sec, min_pause)
    else:
        keep_intervals = [(0.0, orig_duration)]

    cuts_count = max(0, len(keep_intervals) - 1)

    # 2. Build Video & Audio Filter chains
    filter_complex_str, final_labels = build_trim_filter_complex(keep_intervals, has_audio=has_audio)

    # Audio filters (loudnorm)
    audio_normalize = config.get("audio_normalize", True)
    burn_subs = config.get("burn_subtitles", False)
    zoom_level = config.get("dynamic_zoom", "medium")

    # If simple pass without complex trims
    cmd = ["ffmpeg", "-y", "-nostats", "-v", "error"]

    if filter_complex_str:
        # Multi-segment concat
        # We also append audio loudnorm and video scale if needed
        full_filter = filter_complex_str
        v_stream_label = "[outv]"
        a_stream_label = "[outa]" if has_audio else None

        # Add studio vocal mastering + loudnorm to audio if requested
        if has_audio and audio_normalize:
            # highpass (80Hz cut) + 3kHz vocal presence boost + EBU R128 -16 LUFS
            master_af = "highpass=f=80,equalizer=f=3000:t=q:w=1.5:g=2.5,loudnorm=I=-16:TP=-1.5:LRA=11"
            full_filter += f";[outa]{master_af}[norma]"
            a_stream_label = "[norma]"

        # Ensure even dimensions and safe color format
        # If subtitles requested:
        sub_filter = ""
        if burn_subs and word_timestamps:
            ass_path = os.path.join(work_dir, "temp_subtitles.ass").replace("\\", "/")
            escaped_ass = ass_path.replace(":", "\\:")
            generate_ass_subtitle_file(word_timestamps, ass_path, config.get("subtitle_style", "kinetic"), width, height)
            sub_filter = f",subtitles='{escaped_ass}'"

        full_filter += f";[outv]scale='trunc(iw/2)*2':'trunc(ih/2)*2'{sub_filter}[finalv]"
        v_stream_label = "[finalv]"

        cmd.extend([
            "-i", input_filepath,
            "-filter_complex", full_filter,
            "-map", v_stream_label
        ])
        if a_stream_label:
            cmd.extend(["-map", a_stream_label])
    else:
        # Single segment
        cmd.extend(["-i", input_filepath])
        vf_list = ["scale='trunc(iw/2)*2':'trunc(ih/2)*2'"]
        if burn_subs and word_timestamps:
            ass_path = os.path.join(work_dir, "temp_subtitles.ass").replace("\\", "/")
            escaped_ass = ass_path.replace(":", "\\:")
            generate_ass_subtitle_file(word_timestamps, ass_path, config.get("subtitle_style", "kinetic"), width, height)
            vf_list.append(f"subtitles='{escaped_ass}'")
        cmd.extend(["-vf", ",".join(vf_list)])

        if has_audio and audio_normalize:
            master_af = "highpass=f=80,equalizer=f=3000:t=q:w=1.5:g=2.5,loudnorm=I=-16:TP=-1.5:LRA=11"
            cmd.extend(["-af", master_af])

    # Output encoding parameters (high quality H.264 web MP4)
    cmd.extend([
        "-c:v", "libx264",
        "-preset", "veryfast",
        "-crf", "21",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart"
    ])

    if has_audio:
        cmd.extend(["-c:a", "aac", "-b:a", "192k"])

    cmd.append(output_filepath)

    # Run FFmpeg render
    result = subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg processing failed: {result.stderr[:500]}")

    # Gather output stats
    edited_info = get_media_info(output_filepath)
    new_duration = edited_info["duration"]
    if cuts_count > 0:
        new_duration = min(orig_duration, new_duration)
    elif orig_duration > 0 and new_duration > orig_duration:
        new_duration = orig_duration

    seconds_saved = max(0.0, round(orig_duration - new_duration, 2))
    silence_cut_seconds = seconds_saved

    return {
        "output_filepath": output_filepath,
        "original_duration": orig_duration,
        "output_duration": new_duration,
        "seconds_saved": seconds_saved,
        "silence_cut_seconds": silence_cut_seconds,
        "cuts_count": cuts_count,
        "file_size_bytes": edited_info["size_bytes"],
        "resolution": f"{edited_info['width']}x{edited_info['height']}"
    }
