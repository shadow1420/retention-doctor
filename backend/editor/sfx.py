import os
import subprocess
from typing import List, Dict, Any, Optional

SFX_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "storage", "sfx")
os.makedirs(SFX_DIR, exist_ok=True)

WHOOSH_PATH = os.path.join(SFX_DIR, "whoosh.wav")
POP_PATH = os.path.join(SFX_DIR, "pop.wav")


def ensure_sfx_stems():
    """
    Synthesizes crisp, procedural audio stems for video transitions
    using FFmpeg audio filters (zero external audio file dependencies).
    - Whoosh: Swept filtered noise burst (0.28s) for punch-in cuts
    - Pop: Fast frequency envelope click (0.12s) for kinetic word accents
    """
    if not os.path.exists(WHOOSH_PATH):
        # Generate whoosh: bandpass-filtered noise with volume envelope
        cmd_whoosh = [
            "ffmpeg", "-y", "-nostats", "-v", "error",
            "-f", "lavfi",
            "-i", "anoisesrc=d=0.28:c=white:r=48000:a=0.5",
            "-af", "bandpass=f=1200:w=800,afade=t=in:ss=0:d=0.08,afade=t=out:st=0.15:d=0.13,volume=1.2",
            WHOOSH_PATH
        ]
        subprocess.run(cmd_whoosh, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    if not os.path.exists(POP_PATH):
        # Generate pop: sine blip with quick decay
        cmd_pop = [
            "ffmpeg", "-y", "-nostats", "-v", "error",
            "-f", "lavfi",
            "-i", "sine=f=880:d=0.10:r=48000",
            "-af", "afade=t=out:st=0.02:d=0.08,volume=1.4",
            POP_PATH
        ]
        subprocess.run(cmd_pop, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def build_sfx_overlay_filter(
    sfx_timestamps: List[float],
    total_duration: float,
    sfx_type: str = "whoosh"
) -> Optional[str]:
    """
    Constructs an FFmpeg audio filter that delays and mixes the SFX stem
    at specified transition timestamps.
    """
    ensure_sfx_stems()
    sfx_file = WHOOSH_PATH if sfx_type == "whoosh" else POP_PATH
    if not os.path.exists(sfx_file) or not sfx_timestamps:
        return None

    # Filter out timestamps beyond total duration
    valid_times = [round(t, 2) for t in sfx_timestamps if 0.1 <= t <= total_duration - 0.2]
    if not valid_times:
        return None

    return sfx_file, valid_times
