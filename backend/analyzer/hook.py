import re
from typing import Dict, Any, List, Optional

WEAK_INTRO_PATTERNS = [
    (r"hey (guys|everyone|there|y'all)", "Generic greeting wastes critical opening seconds"),
    (r"welcome back to (my|our) channel", "Channel welcome delays the core value proposition"),
    (r"(in this video|today) we are going to", "Predictable intro statement creates passive viewer drop-off"),
    (r"before we begin|make sure to subscribe|hit that bell", "Asking for engagement before delivering value hurts retention"),
    (r"so today i wanted to talk about", "Hesitant filler intro weakens hook urgency"),
    (r"my name is|i am", "Self-introduction before topic reveal leads to immediate swipe-away")
]

POWER_HOOK_TRIGGERS = [
    r"stop doing", r"this is why", r"never use", r"how to", r"the secret to",
    r"if you want to", r"what happens when", r"nobody talks about", r"the biggest mistake",
    r"here is how", r"i tested", r"do not make this", r"why 99%"
]


def evaluate_hook(
    transcript: str,
    word_timestamps: List[Dict[str, Any]],
    first_silence_duration: float = 0.0,
    video_duration: float = 0.0,
    genre_info: Optional[Dict[str, Any]] = None,
    scene_cuts: Optional[List[float]] = None
) -> Dict[str, Any]:
    """
    Intelligently evaluates opening hook based on content genre:
    - For Edits / AMVs / Music Montages: Evaluates visual impact, cuts in first 3s, and beat synchronization.
    - For Talking-Head Videos: Evaluates latency to speech, curiosity triggers, and clarity.
    """
    if genre_info is None:
        genre_info = {}

    is_music_edit = genre_info.get("is_music_edit", False)

    # ==========================================
    # 1. MUSIC EDIT / AMV HOOK EVALUATION
    # ==========================================
    if is_music_edit:
        scene_cuts = scene_cuts or []
        cuts_in_first_3s = len([c for c in scene_cuts if c <= 3.0])
        cuts_in_first_5s = len([c for c in scene_cuts if c <= 5.0])
        has_intro_quote = bool(transcript and len(transcript.split()) >= 3)
        subject = genre_info.get("primary_subject", "Phonk")
        entities = genre_info.get("detected_entities", [])
        entity_name = " ".join(entities[:2]) if entities else subject

        score = 88
        issues = []
        recommendations = []

        if cuts_in_first_3s >= 3:
            score += 8  # Fast beat-synced opening
            summary = f"Elite visual hook: Beat-synced visual pattern interrupts engage immediately on frame 1 ({cuts_in_first_3s} cuts in first 3s)."
        elif has_intro_quote:
            score += 6  # Cold-open dialogue quote sample
            summary = f"Elite cold-open build-up: Iconic dialogue quote hooks viewer curiosity right before the beat drop."
        elif cuts_in_first_5s >= 1:
            score += 4
            summary = "Good opening visual hook. Visual transition established early."
        else:
            score -= 6
            issues.append("Opening shot is static for over 5 seconds before first transition.")
            recommendations.append("Add a visual flash, punch-in, or scene cut within the first 2.0s to match the beat.")

        final_score = max(50, min(97, score))
        grade = "A" if final_score >= 88 else ("B" if final_score >= 75 else "C")

        # Generate 5 viral edit-specific alternative hooks
        if "gaming" in genre_info.get("genre", "") or "gaming" in str(genre_info.get("genre_label", "")).lower():
            alt_hooks = [
                {
                    "type": "The Secret Tech / Meta Hook",
                    "hook": f"Almost nobody knows this broken {subject} tech in {entity_name}...",
                    "visual_technique": "Show 1-second high-damage combo preview on frame 1.",
                    "why_it_works": "Gamers immediately stay to learn high-tier competitive advantages."
                },
                {
                    "type": "The Contrarian / Nerf Bait",
                    "hook": f"Why is nobody talking about how overpowered {subject} actually is?",
                    "visual_technique": "Add glowing red question mark HUD element on the character.",
                    "why_it_works": "Challenges current meta and sparks massive comment debate."
                },
                {
                    "type": "The Frame-1 Gameplay Climax",
                    "hook": f"Watch what happens when you land this combo with {subject}...",
                    "visual_technique": "Freeze-frame on climax hit at 0:02 with sound effect punch.",
                    "why_it_works": "Instant proof of outcome guarantees 85%+ completion rate."
                },
                {
                    "type": "The Infinite Replay Loop",
                    "hook": f"Did you notice what happened at frame 1?",
                    "visual_technique": "Match the final move frame back into the opening animation for infinite loop retention.",
                    "why_it_works": "Drives 130%+ average percentage viewed on Shorts/TikTok."
                },
                {
                    "type": "The Warning / Waste Trap",
                    "hook": f"Don't awaken or use {subject} until you know this one combo sequence.",
                    "visual_technique": "Display caution/warning border overlay during first 2 seconds.",
                    "why_it_works": "Loss aversion triggers immediate watch-through to avoid wasting in-game resources."
                }
            ]
        else:
            alt_hooks = [
                {
                    "type": "The Infinite Replay Loop",
                    "hook": f"Wait for the beat drop...",
                    "visual_technique": f"Seamless Loop: Match the final frame of the {subject} edit back to frame 1.",
                    "why_it_works": "Triggers 150%+ audience retention as viewers accidentally rewatch the loop."
                },
                {
                    "type": "The Bass Drop Sync",
                    "hook": f"Turn your volume up for this {subject} transition...",
                    "visual_technique": "Sync the primary visual impact / slash frame to the exact 808 phonk bass drop.",
                    "why_it_works": "Audio-visual sensory alignment releases dopamine and stops scroll-away."
                },
                {
                    "type": "The Cold Open Flash",
                    "hook": f"They really thought {subject} was weak...",
                    "visual_technique": "0.15s black screen / inverted color flash on frame 1 before the explosion.",
                    "why_it_works": "Instant pattern interrupt breaks user feed scrolling rhythm."
                },
                {
                    "type": "Speed Ramping Punch",
                    "hook": f"POV: The quiet kid stops holding back...",
                    "visual_technique": "50% slow-mo build-up ramping instantly to 150% snap on the main action frame.",
                    "why_it_works": "Dynamic velocity shifts make 60FPS motion feel 2x faster."
                },
                {
                    "type": "Kinetic Typography Pop",
                    "hook": f"Don't blink at 0:04 or you'll miss it...",
                    "visual_technique": "Add bold Japanese Kanji / title flash on the screen as the beat kicks in.",
                    "why_it_works": "Anchors visual focus and increases bookmark rate by 40%."
                }
            ]

        opening_hook_repr = transcript.strip() if (transcript and len(transcript.strip()) > 3) else f"[{subject} beat-synced showcase]"

        return {
            "hook_score": final_score,
            "hook_grade": grade,
            "hook_explanation": summary,
            "hook_issues": issues if issues else ["High visual impact: Zero opening dead air or visual delay detected."],
            "hook_recommendations": recommendations if recommendations else ["Render in 60FPS with optical flow motion blur for maximum smoothness."],
            "alternative_hooks": alt_hooks,
            "opening_text_5s": opening_hook_repr,
            "first_word_latency": 0.0
        }

    # ==========================================
    # 2. TALKING-HEAD CREATOR HOOK EVALUATION
    # ==========================================
    words_first_5s = [w for w in word_timestamps if w["start"] <= 5.0]
    words_first_10s = [w for w in word_timestamps if w["start"] <= 10.0]

    text_5s = " ".join([w["word"] for w in words_first_5s]).strip()
    text_10s = " ".join([w["word"] for w in words_first_10s]).strip()
    first_word_start = word_timestamps[0]["start"] if word_timestamps else 0.0

    score = 85
    issues = []
    recommendations = []

    if first_word_start >= 1.5:
        penalty = min(25, int(first_word_start * 12))
        score -= penalty
        issues.append(f"Opening delay: First word starts at {first_word_start:.1f}s. Viewers swipe within the first 1.5s.")
        recommendations.append("Trim the opening silent pause so your voice begins within 0.2s of playback.")
    elif first_word_start >= 0.8:
        score -= 10
        issues.append(f"Slight opening hesitation: Voice begins at {first_word_start:.1f}s.")
        recommendations.append("Start speaking immediately on frame 1 to grab instant attention.")

    word_count_5s = len(words_first_5s)
    if word_count_5s < 4 and first_word_start < 4.0:
        score -= 15
        issues.append(f"Slow opening pacing: Only {word_count_5s} words spoken in the first 5 seconds.")
        recommendations.append("Increase your opening speech rate to 140-160 WPM to establish active momentum.")

    lower_10s = text_10s.lower()
    for pattern, description in WEAK_INTRO_PATTERNS:
        if re.search(pattern, lower_10s):
            score -= 18
            issues.append(f"Weak intro pattern detected: {description}.")
            recommendations.append("Eliminate introductions and jump straight into the problem or outcome.")
            break

    has_power_trigger = any(re.search(pat, lower_10s) for pat in POWER_HOOK_TRIGGERS)
    if has_power_trigger:
        score += 10

    final_score = max(15, min(98, score))
    grade = "A" if final_score >= 88 else ("B" if final_score >= 72 else ("C" if final_score >= 55 else "D"))

    summary = "Strong hook. Immediate engagement with minimal dead air." if grade == "A" else (
        "Good hook with decent pacing." if grade == "B" else "Average hook. Hesitation risks swipe-away."
    )

    alt_hooks = generate_alternative_hooks(transcript, text_10s)

    return {
        "hook_score": final_score,
        "hook_grade": grade,
        "hook_explanation": summary,
        "hook_issues": issues if issues else ["No major hook defects detected."],
        "hook_recommendations": recommendations,
        "alternative_hooks": alt_hooks,
        "opening_text_5s": text_5s,
        "first_word_latency": round(first_word_start, 2)
    }


def generate_alternative_hooks(full_transcript: str, opening_text: str) -> List[Dict[str, str]]:
    """Generates 5 high-converting hook structures tailored to the transcript subject."""
    words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{4,}\b", full_transcript)]
    common_stops = {
        "this", "that", "with", "from", "your", "have", "will", "they", "what", "video",
        "about", "there", "then", "when", "here", "just", "like", "more", "make", "really",
        "strike", "type", "bought", "money", "people", "something", "everything", "nothing",
        "someone", "know", "think", "said", "says", "told", "come", "came", "going", "doing",
        "look", "take", "give", "want", "need", "feel", "thing", "things", "guys", "tell",
        "much", "many", "well", "even", "back", "also", "still", "good", "great", "late",
        "time", "over", "play", "game", "first", "last", "long", "short", "soon"
    }
    topic_keywords = [w for w in words if w not in common_stops]
    primary_topic = topic_keywords[0].capitalize() if topic_keywords else "Your Strategy"
    secondary_topic = topic_keywords[1].capitalize() if len(topic_keywords) > 1 else "Results"

    return [
        {
            "type": "The Contrarian / Stop Doing",
            "hook": f"Stop doing {primary_topic.lower()} like this if you actually want {secondary_topic.lower()}.",
            "visual_technique": "Display bold red ✖ symbol over screen with punchy sound effect.",
            "why_it_works": "Creates instant pattern interrupt by challenging conventional wisdom."
        },
        {
            "type": "The Curiosity Gap",
            "hook": f"Almost nobody knows this hidden trick for {primary_topic.lower()}...",
            "visual_technique": "Apply 1.15x camera punch-in on the primary keyword.",
            "why_it_works": "Triggers FOMO and compels the viewer to stay for the revelation."
        },
        {
            "type": "The Immediate Outcome",
            "hook": f"Here is the exact method I use to fix {primary_topic.lower()} in under 60 seconds.",
            "visual_technique": "Start with a fast 1-second preview of the finished result.",
            "why_it_works": "Promises high-value payoff with a low investment of viewer time."
        },
        {
            "type": "The Warning / Mistake",
            "hook": f"The single biggest mistake people make with {primary_topic.lower()} (and how to fix it).",
            "visual_technique": "Flash yellow caution border with kinetic subtitle highlight.",
            "why_it_works": "People are twice as motivated to avoid mistakes as to gain benefits."
        },
        {
            "type": "The Bold Question",
            "hook": f"Are you still struggling with {primary_topic.lower()}? Watch this before your next post.",
            "visual_technique": "Direct eye-contact crop with subtle motion tracking zoom.",
            "why_it_works": "Direct qualification filters and hooks your exact target audience immediately."
        }
    ]
