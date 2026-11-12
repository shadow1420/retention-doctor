from typing import List, Dict, Any

def calculate_predicted_retention_curve(
    duration: float,
    hook_score: int,
    first_word_latency: float,
    silence_intervals: List[Dict[str, Any]],
    monotone_segments: List[Dict[str, Any]],
    boredom_windows: List[Dict[str, Any]],
    scene_cuts: List[float],
    emphasis_peaks: List[float]
) -> Dict[str, Any]:
    """
    Computes a realistic second-by-second estimated retention curve (0.0 to 100.0%)
    based on combined acoustic, linguistic, and visual friction heuristics.
    Pinpoints the Top 3 Critical Drop-off moments for actionable creator fixes.
    """
    if duration <= 0:
        return {
            "curve": [],
            "predicted_completion_rate": 65.0,
            "top_dropoff_moments": []
        }

    total_seconds = int(duration) + 1
    curve = []
    current_retention = 100.0

    # Critical drop-off tracker
    drop_candidates = []

    # Calculate initial hook decay baseline (swipe-away rate in first 2 seconds)
    # Elite hooks (score >= 90) lose only ~4% per second initially; weaker hooks lose up to 12%
    hook_decay_rate = max(3.5, 12.0 - (hook_score / 12.0))

    for t in range(total_seconds):
        sec_float = float(t)
        risk_factors = []
        delta = 0.0

        if t == 0:
            # Frame 0 is always 100% initial reach
            delta = 0.0
        elif t <= 2:
            # 1. Opening Hook Swipe-Away Friction
            delta -= hook_decay_rate
            if first_word_latency >= 1.2:
                delta -= 4.0
                risk_factors.append(f"Opening silence: Speech starts late at {first_word_latency}s")
            elif first_word_latency >= 0.7:
                delta -= 2.0
                risk_factors.append("Hesitant opening: Delayed speech delivery")

            if hook_score < 70:
                delta -= 3.0
                risk_factors.append("Low hook urgency: Opening lacks high-curiosity thumb stop")
            else:
                risk_factors.append("Initial feed scroll-away test (First 2s)")
        else:
            # 2. Natural short-form attention decay baseline (1.2% - 1.6% per second)
            delta -= 1.35

            # 3. Dead-Air & Silence Penalties (Sharpest drop in short-form)
            in_silence = False
            for s in silence_intervals:
                if s["start"] <= sec_float <= s["end"]:
                    delta -= 4.5
                    risk_factors.append(f"Dead-air silence ({s.get('duration', 0.6)}s pause)")
                    in_silence = True
                    break

            # 4. Monotone Vocal Delivery Penalty
            for m in monotone_segments:
                if m["start"] <= sec_float <= m["end"]:
                    delta -= 2.0
                    risk_factors.append("Monotone vocal delivery: Energy lacks pitch variation")
                    break

            # 5. Visual Boredom / Stagnation Penalty (Compounds the longer a shot remains static)
            for b in boredom_windows:
                if b["start"] <= sec_float <= b["end"]:
                    elapsed = max(0.5, sec_float - b["start"])
                    stagnation_penalty = 1.8 + min(3.2, elapsed * 0.35)
                    delta -= stagnation_penalty
                    risk_factors.append(f"Visual stagnation: Static shot for {elapsed:.1f}s")
                    break

            # 6. Retention Stabilizers (Pattern interrupts, cuts, beat drops)
            # In short-form analytics, a cut maintains visual momentum and mitigates decay
            if any(abs(sec_float - c) <= 0.55 for c in scene_cuts):
                delta = min(-0.45, delta + 1.2)  # Refreshes visual engagement, reducing loss

            if any(abs(sec_float - ep) <= 0.55 for ep in emphasis_peaks):
                delta = min(-0.35, delta + 1.0)

        # Update retention value
        prev_retention = current_retention
        current_retention = max(15.0, min(100.0, current_retention + delta))
        loss = round(prev_retention - current_retention, 1)

        primary_factor = risk_factors[0] if risk_factors else "Pacing deceleration / viewer attention fatigue"

        actionable_remedy = "Insert quick B-Roll cutaway or 1.15x zoom punch-in"
        if "Dead-air" in primary_factor or "pause" in primary_factor:
            actionable_remedy = "Cut dead-air silence gap using 1-Click Auto-Fixer"
        elif "Hesitant" in primary_factor or "Opening" in primary_factor:
            actionable_remedy = "Start speaking within 0.2s of frame 1 to halt immediate swipe"
        elif "Monotone" in primary_factor:
            actionable_remedy = "Add pitch inflection or sound effect riser to revitalize vocal energy"
        elif "Visual stagnation" in primary_factor or "Static" in primary_factor:
            actionable_remedy = "Punch in 1.2x scale or transition to dynamic b-roll clip"
        elif "scroll-away" in primary_factor.lower():
            actionable_remedy = "Strengthen visual hook with inverted flash or bold kinetic caption"
        else:
            actionable_remedy = "Add audio riser or graphic pop to sustain audience curiosity"

        if t > 0:
            drop_candidates.append({
                "second": t,
                "loss_pct": max(0.5, loss),
                "remaining_retention": round(current_retention, 1),
                "primary_cause": primary_factor,
                "actionable_remedy": actionable_remedy,
                "all_factors": list(risk_factors)
            })

        curve.append({
            "second": t,
            "retention_pct": round(current_retention, 1),
            "severity": "high" if loss >= 4.0 else ("med" if loss >= 2.0 else "low"),
            "risk_factors": risk_factors
        })

    # Sort drop candidates to find Top 3 distinct critical moments (spaced by at least 2 seconds)
    drop_candidates.sort(key=lambda x: x["loss_pct"], reverse=True)
    top_dropoffs = []
    selected_seconds = set()

    for cand in drop_candidates:
        sec = cand["second"]
        if not any(abs(sec - s) < 2 for s in selected_seconds):
            selected_seconds.add(sec)
            top_dropoffs.append(cand)
            if len(top_dropoffs) == 3:
                break

    # Sort the Top 3 chronologically for easy timeline comprehension
    top_dropoffs.sort(key=lambda x: x["second"])

    predicted_completion = round(curve[-1]["retention_pct"], 1) if curve else 60.0

    return {
        "curve": curve,
        "predicted_completion_rate": predicted_completion,
        "top_dropoff_moments": top_dropoffs
    }
