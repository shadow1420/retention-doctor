import os
import re
from typing import List, Dict, Any

EMOJI_KEYWORDS = {
    "money": "💰", "cash": "💰", "rich": "💰", "dollar": "💵", "profit": "📈",
    "fire": "🔥", "viral": "🔥", "views": "🔥", "hot": "🔥",
    "stop": "🛑", "never": "🛑", "dont": "🛑", "warning": "⚠️", "danger": "⚠️",
    "secret": "🔑", "key": "🔑", "trick": "🔑", "hack": "🔑",
    "mind": "🤯", "crazy": "🤯", "blown": "🤯", "insane": "🤯",
    "time": "⏳", "fast": "⚡", "quick": "⚡", "seconds": "⏱️",
    "grow": "🚀", "boost": "🚀", "rocket": "🚀", "scale": "🚀",
    "idea": "💡", "think": "💡", "smart": "🧠", "brain": "🧠",
    "look": "👀", "watch": "👀", "see": "👀",
    "goal": "🎯", "target": "🎯", "perfect": "💯", "100": "💯",
    "love": "❤️", "video": "🎬", "edit": "✂️", "audio": "🎙️"
}

def format_ass_time(seconds: float) -> str:
    """Converts seconds into ASS timestamp format: H:MM:SS.cc"""
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = seconds % 60
    return f"{hrs:d}:{mins:02d}:{secs:05.2f}"


def get_emoji_for_word(word: str) -> str:
    """Returns matching viral emoji tag if keyword is detected."""
    clean = re.sub(r"[^\w]", "", word.lower())
    return EMOJI_KEYWORDS.get(clean, "")


def generate_ass_subtitle_file(
    word_timestamps: List[Dict[str, Any]],
    output_path: str,
    style: str = "kinetic_emoji",
    width: int = 1080,
    height: int = 1920
) -> str:
    """
    Generates an .ass file with dynamic word-level kinetic styling
    and automatic viral emoji tags inspired by Alex Hormozi short-form editing.
    """
    is_vertical = height > width
    font_size = 62 if is_vertical else 46
    margin_v = 230 if is_vertical else 90

    # Primary: White (&H00FFFFFF), Highlight: Electric Yellow (&H0000FFFF)
    ass_header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {width}
PlayResY: {height}
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Kinetic,Arial Black,{font_size},&H00FFFFFF,&H0000FFFF,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,3,2,40,40,{margin_v},1
Style: Clean,Arial,{int(font_size * 0.85)},&H00FFFFFF,&H00E0E0E0,&H00000000,&H60000000,1,0,0,0,100,100,0,0,1,2,1,2,30,30,{margin_v},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    if not word_timestamps:
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(ass_header)
        return output_path

    events = []
    chunk_size = 4
    for i in range(0, len(word_timestamps), chunk_size):
        chunk = word_timestamps[i : i + chunk_size]
        if not chunk:
            continue

        start_time = chunk[0]["start"]
        end_time = chunk[-1]["end"] + 0.1
        words_text = " ".join([w["word"].upper() for w in chunk])

        if style in ["kinetic", "kinetic_emoji"]:
            for curr_w in chunk:
                w_start = curr_w["start"]
                w_end = curr_w["end"]
                
                # Check for viral emoji match
                emoji_tag = get_emoji_for_word(curr_w["word"]) if style == "kinetic_emoji" else ""

                highlighted_parts = []
                for w in chunk:
                    clean_w = w["word"].upper()
                    if w is curr_w:
                        # Highlight active word in Electric Yellow with glowing black outline
                        tag_prefix = f"{emoji_tag} " if emoji_tag else ""
                        highlighted_parts.append(f"{{\\c&H0022FFFF&\\b1}}{tag_prefix}{clean_w}{{\\c&H00FFFFFF&}}")
                    else:
                        highlighted_parts.append(clean_w)

                dialogue_line = f"Dialogue: 0,{format_ass_time(w_start)},{format_ass_time(w_end)},Kinetic,,0,0,0,,{' '.join(highlighted_parts)}\n"
                events.append(dialogue_line)
        else:
            dialogue_line = f"Dialogue: 0,{format_ass_time(start_time)},{format_ass_time(end_time)},Clean,,0,0,0,,{words_text}\n"
            events.append(dialogue_line)

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(ass_header + "".join(events))

    return output_path
