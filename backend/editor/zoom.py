from typing import List, Dict, Any

ZOOM_FACTORS = {
    "none": 1.0,
    "low": 1.08,
    "medium": 1.15,
    "high": 1.25
}

def generate_dynamic_zoom_filter(
    zoom_level: str,
    zoom_intervals: List[Dict[str, Any]],
    width: int = 1920,
    height: int = 1080
) -> str:
    """
    Builds a centered crop+scale filter string that applies punch-in zoom
    during specified intervals to add visual energy without camera jitter.
    """
    scale_factor = ZOOM_FACTORS.get(zoom_level.lower(), 1.0)
    if scale_factor <= 1.0 or not zoom_intervals:
        return ""

    # Build condition: (between(t, s1, e1)+between(t, s2, e2)...) > 0
    conditions = []
    for z in zoom_intervals:
        s = z.get("timestamp", z.get("start", 0.0))
        d = z.get("duration", 2.5)
        e = z.get("end", s + d)
        conditions.append(f"between(t,{s:.2f},{e:.2f})")

    if not conditions:
        return ""

    cond_expr = "+".join(conditions)
    
    # Target crop dimensions when zoomed: in_w / scale_factor, in_h / scale_factor
    # When not zoomed: in_w, in_h
    crop_w_expr = f"if(gt({cond_expr},0),in_w/{scale_factor:.2f},in_w)"
    crop_h_expr = f"if(gt({cond_expr},0),in_h/{scale_factor:.2f},in_h)"

    filter_str = f"crop=w='{crop_w_expr}':h='{crop_h_expr}':x='(in_w-out_w)/2':y='(in_h-out_h)/2',scale={width}:{height}:flags=lanczos"
    return filter_str
