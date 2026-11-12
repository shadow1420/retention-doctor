import re
from typing import Dict, Any, List, Optional


POWER_WORDS = [
    "stop", "never", "mistake", "warning", "ruining", "banned", "illegal", "danger",
    "destroy", "insane", "waste", "trap", "worst", "fatal", "protect", "urgent",
    "secret", "hack", "algorithm", "millionaire", "fool", "lie", "cheat", "truth",
    "exposed", "hidden", "deadly", "guarantee", "formula", "crazy", "shocking",
    "broken", "nerfed", "overpowered", "clutch", "glitch", "combo", "blink", "drop",
    "transition", "power", "weak", "quiet"
]

CURIOSITY_TRIGGERS = [
    r"\bwhy\b", r"\bhow\b", r"this is why", r"the reason", r"what happens",
    r"nobody (talks about|knows|tells you)", r"almost nobody", r"hidden trick",
    r"the truth about", r"what if", r"this one trick", r"don't do this until",
    r"if you are still", r"i tested", r"i spent", r"watch this before",
    r"\bwait (for|until|till)\b", r"\bpov\b", r"\bdon't blink\b",
    r"\bturn (your )?volume up\b", r"\bthey really thought\b", r"\bwatch what happens\b"
]

WEAK_OPENERS = [
    (r"^hey (guys|everyone|there|y'all)", "Generic greeting wastes critical 0-1s swipe window"),
    (r"^welcome back", "Channel welcome delays value delivery"),
    (r"^(in this video|today we are going to)", "Predictable passive intro triggers instant drop-off"),
    (r"^so today i wanted to", "Hesitant filler intro weakens hook urgency"),
    (r"^my name is|^i am", "Self-introduction before topic reveal leads to swipe-away"),
    (r"^(subscribe|hit the bell|like this)", "Premature call to action hurts viewer trust")
]

IMPERATIVE_VERBS = [
    "stop", "never", "don't", "avoid", "watch", "look", "check", "delete",
    "quit", "drop", "steal", "use", "try", "fix", "remember", "beware",
    "wait", "turn", "blink", "listen", "notice"
]


def score_single_hook(hook_text: str, genre: str = "general") -> Dict[str, Any]:
    text = (hook_text or "").strip()
    if not text:
        return {
            "hook_text": "",
            "score": 0,
            "word_count": 0,
            "estimated_speak_time": 0.0,
            "dimensions": {
                "curiosity_gap": 0,
                "urgency_power": 0,
                "brevity_cadence": 0,
                "pattern_interrupt": 0
            },
            "strengths": [],
            "weaknesses": ["Hook text is empty."],
            "recommendations": ["Enter a hook phrase to analyze."]
        }

    words = re.findall(r"\b[\w'-]+\b", text)
    word_count = len(words)
    lower = text.lower()
    first_word = words[0].lower() if words else ""

    # Estimated speaking time (average 2.8 words/sec in short-form videos)
    speak_time = round(word_count / 2.8, 1)

    strengths: List[str] = []
    weaknesses: List[str] = []
    recommendations: List[str] = []

    # 1. Brevity & Cadence (Optimal short-form hook: 6 - 11 words)
    if 6 <= word_count <= 11:
        brevity_score = 98
        strengths.append(f"Ideal short-form cadence ({word_count} words / ~{speak_time}s delivery)")
    elif 4 <= word_count <= 5:
        brevity_score = 86
        strengths.append(f"Ultra-punchy ({word_count} words)")
    elif 12 <= word_count <= 14:
        brevity_score = 80
        weaknesses.append("Slightly wordy for a short-form intro")
        recommendations.append("Trim 2-3 words to increase verbal velocity")
    elif word_count > 14:
        over = word_count - 14
        brevity_score = max(35, 75 - (over * 5))
        weaknesses.append(f"Too long ({word_count} words / ~{speak_time}s). Viewers may swipe before payoff")
        recommendations.append("Condense the core idea into 8-10 words maximum")
    else:  # < 4 words
        brevity_score = 55
        weaknesses.append("Too brief to establish clear context or stakes")
        recommendations.append("Add the specific consequence or problem being solved")

    # 2. Curiosity Gap (Creating open loop / psychological deficit)
    curiosity_score = 50
    matched_curiosity = [pat for pat in CURIOSITY_TRIGGERS if re.search(pat, lower)]
    if matched_curiosity:
        curiosity_score += min(35, len(matched_curiosity) * 20)
        strengths.append("High curiosity gap creates an irresistible open loop")
    if "?" in text:
        curiosity_score += 12
        strengths.append("Direct question activates viewer internal monologue")

    if curiosity_score < 65:
        recommendations.append("Introduce a knowledge gap (e.g. 'The real reason...', 'Almost nobody knows...')")
    curiosity_score = min(100, curiosity_score)

    # 3. Urgency & Power Words
    found_power = [w for w in POWER_WORDS if re.search(rf"\b{re.escape(w)}\b", lower)]
    urgency_score = 45
    if found_power:
        urgency_score += min(45, len(found_power) * 18)
        strengths.append(f"Strong emotional power words: {', '.join(found_power[:3])}")
    else:
        weaknesses.append("Lacks visceral power words or urgency")
        recommendations.append("Include high-retention trigger words like 'stop', 'mistake', 'secret', or 'truth'")

    has_urgency_token = bool(re.search(r"\b(before|immediately|now|today|in \d+|in under \d+)\b", lower))
    if has_urgency_token:
        urgency_score += 10
        strengths.append("Time-bound urgency prompts immediate attention")
    urgency_score = min(100, urgency_score)

    # 4. Pattern Interrupt & Opening Command
    pattern_score = 55
    # Weak opener check (huge penalty)
    has_weak_opener = False
    for pat, desc in WEAK_OPENERS:
        if re.search(pat, lower):
            pattern_score -= 35
            weaknesses.append(f"Weak intro detected: {desc}")
            recommendations.append("Cut greetings completely and start directly with the hook verb or question")
            has_weak_opener = True
            break

    if not has_weak_opener:
        if first_word in IMPERATIVE_VERBS:
            pattern_score += 25
            strengths.append(f"Commands attention with active imperative verb ('{first_word.capitalize()}')")
        if re.search(r"\b(\d+%?|\$\d+)\b", text):
            pattern_score += 15
            strengths.append("Specific numerical data grounds credibility")

    pattern_score = max(10, min(100, pattern_score))

    # Genre weight adjustments
    g = (genre or "general").lower()
    if "tech" in g or "edu" in g:
        composite = (0.30 * curiosity_score) + (0.20 * urgency_score) + (0.25 * brevity_score) + (0.25 * pattern_score)
    elif "story" in g:
        composite = (0.45 * curiosity_score) + (0.20 * urgency_score) + (0.15 * brevity_score) + (0.20 * pattern_score)
    elif "finance" in g or "business" in g:
        composite = (0.25 * curiosity_score) + (0.35 * urgency_score) + (0.20 * brevity_score) + (0.20 * pattern_score)
    elif "comedy" in g or "entertainment" in g:
        composite = (0.25 * curiosity_score) + (0.20 * urgency_score) + (0.25 * brevity_score) + (0.30 * pattern_score)
    elif "gaming" in g or "roblox" in g or "bloxfruits" in g:
        composite = (0.35 * curiosity_score) + (0.20 * urgency_score) + (0.20 * brevity_score) + (0.25 * pattern_score)
    else:
        composite = (0.35 * curiosity_score) + (0.25 * urgency_score) + (0.20 * brevity_score) + (0.20 * pattern_score)

    final_score = int(round(max(15, min(99, composite))))

    return {
        "hook_text": text,
        "score": final_score,
        "word_count": word_count,
        "estimated_speak_time": speak_time,
        "dimensions": {
            "curiosity_gap": int(curiosity_score),
            "urgency_power": int(urgency_score),
            "brevity_cadence": int(brevity_score),
            "pattern_interrupt": int(pattern_score)
        },
        "strengths": strengths[:3],
        "weaknesses": weaknesses[:3],
        "recommendations": recommendations[:2]
    }


def evaluate_ab_hooks(hook_a: str, hook_b: str, genre: str = "general") -> Dict[str, Any]:
    """
    Compares two short-form video hooks side-by-side using linguistic thumb-stop metrics,
    predicting retention outcome, winner probability delta, and actionable tuning.
    """
    res_a = score_single_hook(hook_a, genre)
    res_b = score_single_hook(hook_b, genre)

    score_a = res_a["score"]
    score_b = res_b["score"]

    if score_a > score_b:
        winner = "A"
        delta = score_a - score_b
        pct_advantage = round((delta / max(score_b, 1)) * 100, 1)
        reason = ""
        if res_a["dimensions"]["pattern_interrupt"] >= res_b["dimensions"]["pattern_interrupt"] + 15:
            reason = "stronger pattern interrupt that breaks scrolling inertia"
        elif res_a["dimensions"]["brevity_cadence"] >= res_b["dimensions"]["brevity_cadence"] + 15:
            reason = "tighter verbal velocity and quicker value delivery"
        elif res_a["dimensions"]["curiosity_gap"] >= res_b["dimensions"]["curiosity_gap"] + 15:
            reason = "an unresolved curiosity loop that compels watch-through"
        elif res_a["dimensions"]["urgency_power"] >= res_b["dimensions"]["urgency_power"] + 15:
            reason = "higher-stakes power words and urgency cues"
        else:
            reason = "superior linguistic pacing and audience thumb-stop power"
        verdict = f"Hook A wins with {reason}, predicting +{pct_advantage}% higher retention through the critical first 3 seconds."
    elif score_b > score_a:
        winner = "B"
        delta = score_b - score_a
        pct_advantage = round((delta / max(score_a, 1)) * 100, 1)
        reason = ""
        if res_b["dimensions"]["pattern_interrupt"] >= res_a["dimensions"]["pattern_interrupt"] + 15:
            reason = "stronger pattern interrupt that breaks scrolling inertia"
        elif res_b["dimensions"]["brevity_cadence"] >= res_a["dimensions"]["brevity_cadence"] + 15:
            reason = "tighter verbal velocity and quicker value delivery"
        elif res_b["dimensions"]["curiosity_gap"] >= res_a["dimensions"]["curiosity_gap"] + 15:
            reason = "an unresolved curiosity loop that compels watch-through"
        elif res_b["dimensions"]["urgency_power"] >= res_a["dimensions"]["urgency_power"] + 15:
            reason = "higher-stakes power words and urgency cues"
        else:
            reason = "superior linguistic pacing and audience thumb-stop power"
        verdict = f"Hook B wins with {reason}, predicting +{pct_advantage}% higher retention through the critical first 3 seconds."
    else:
        winner = "TIE"
        delta = 0
        pct_advantage = 0.0
        verdict = "Both hook variants deliver balanced psychological retention momentum. Combine Hook A's opener with Hook B's stakes for maximum punch."

    # Dimension winners
    dim_comparison = {}
    for dim in ["curiosity_gap", "urgency_power", "brevity_cadence", "pattern_interrupt"]:
        val_a = res_a["dimensions"][dim]
        val_b = res_b["dimensions"][dim]
        dim_comparison[dim] = {
            "score_a": val_a,
            "score_b": val_b,
            "winner": "A" if val_a > val_b else ("B" if val_b > val_a else "TIE")
        }

    # High-level strategic commentary
    key_factors = []
    winning_res = res_a if winner == "A" else (res_b if winner == "B" else None)
    losing_res = res_b if winner == "A" else (res_a if winner == "B" else None)

    if winning_res and losing_res:
        if winning_res["dimensions"]["pattern_interrupt"] > losing_res["dimensions"]["pattern_interrupt"]:
            key_factors.append("Stronger initial pattern interrupt breaks feed scrolling inertia")
        if winning_res["dimensions"]["curiosity_gap"] > losing_res["dimensions"]["curiosity_gap"]:
            key_factors.append("Superior curiosity gap keeps viewers curious for the punchline")
        if winning_res["dimensions"]["brevity_cadence"] > losing_res["dimensions"]["brevity_cadence"]:
            key_factors.append("Tighter cadence delivers value faster before swipe threshold")
        if winning_res["dimensions"]["urgency_power"] > losing_res["dimensions"]["urgency_power"]:
            key_factors.append("Visceral power trigger words compel immediate psychological focus")

    if not key_factors:
        key_factors = ["Balanced pacing and engaging delivery across both variants"]

    return {
        "winner": winner,
        "delta": delta,
        "percentage_advantage": pct_advantage,
        "verdict": verdict,
        "key_factors": key_factors,
        "hook_a": res_a,
        "hook_b": res_b,
        "dimension_comparison": dim_comparison,
        "genre": genre
    }
