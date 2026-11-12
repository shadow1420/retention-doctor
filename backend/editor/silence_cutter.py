from typing import List, Dict, Any, Tuple

def calculate_keep_intervals(
    total_duration: float,
    silence_intervals: List[Dict[str, Any]],
    padding_sec: float = 0.08,
    min_pause_to_cut: float = 0.55
) -> List[Tuple[float, float]]:
    """
    Computes active speech intervals to keep by subtracting silence intervals.
    Adds padding around speech boundaries to preserve natural vocal tails and breaths.
    """
    # Filter out silences shorter than min_pause_to_cut
    filtered_silences = [
        s for s in silence_intervals
        if s.get("duration", (s.get("end", 0) - s.get("start", 0))) >= min_pause_to_cut
    ]

    if not filtered_silences:
        return [(0.0, total_duration)]

    # Sort silences by start
    filtered_silences.sort(key=lambda s: s["start"])

    keep_intervals: List[Tuple[float, float]] = []
    last_end = 0.0

    for s in filtered_silences:
        # Proposed end of speech block with padding
        cut_start = max(last_end, s["start"] + padding_sec)
        # Proposed resume of speech block with padding
        cut_end = max(cut_start, s["end"] - padding_sec)

        if cut_start > last_end + 0.1:
            keep_intervals.append((round(last_end, 3), round(cut_start, 3)))
        last_end = cut_end

    if last_end < total_duration - 0.1:
        keep_intervals.append((round(last_end, 3), round(total_duration, 3)))

    # Merge any overlapping or micro intervals
    merged: List[Tuple[float, float]] = []
    for start, end in keep_intervals:
        if end <= start:
            continue
        if not merged:
            merged.append((start, end))
        else:
            prev_s, prev_e = merged[-1]
            if start <= prev_e + 0.05:
                # Merge
                merged[-1] = (prev_s, max(prev_e, end))
            else:
                merged.append((start, end))

    return merged if merged else [(0.0, total_duration)]


def build_trim_filter_complex(
    keep_intervals: List[Tuple[float, float]],
    has_audio: bool = True
) -> Tuple[str, str]:
    """
    Constructs an FFmpeg filter_complex that trims and concatenates
    the active intervals without losing audio/video sync.
    """
    if len(keep_intervals) <= 1:
        return "", "[0:v][0:a]"

    filter_parts = []
    v_labels = []
    a_labels = []

    for i, (start, end) in enumerate(keep_intervals):
        v_out = f"v{i}"
        a_out = f"a{i}"
        # Video trim with reset PTS
        filter_parts.append(
            f"[0:v]trim=start={start}:end={end},setpts=PTS-STARTPTS[{v_out}]"
        )
        if has_audio:
            # Audio trim with reset PTS
            filter_parts.append(
                f"[0:a]atrim=start={start}:end={end},asetpts=PTS-STARTPTS[{a_out}]"
            )
            v_labels.append(f"[{v_out}]")
            a_labels.append(f"[{a_out}]")

    num_segments = len(keep_intervals)
    if has_audio:
        concat_inputs = "".join(f"[{'v'+str(i)}][{'a'+str(i)}]" for i in range(num_segments))
        concat_part = f"{concat_inputs}concat=n={num_segments}:v=1:a=1[outv][outa]"
        filter_parts.append(concat_part)
        return ";".join(filter_parts), "[outv][outa]"
    else:
        concat_inputs = "".join(f"[{'v'+str(i)}]" for i in range(num_segments))
        concat_part = f"{concat_inputs}concat=n={num_segments}:v=1:a=0[outv]"
        filter_parts.append(concat_part)
        return ";".join(filter_parts), "[outv]"
