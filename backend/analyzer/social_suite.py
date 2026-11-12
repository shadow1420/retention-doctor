import re
from typing import Dict, Any, List, Optional
from .virality import calculate_viral_potential, get_optimal_posting_times

def generate_social_suite(
    transcript: str = "",
    hook_recommendations: Optional[List[str]] = None,
    genre_info: Optional[Dict[str, Any]] = None,
    filename: str = "",
    hook_score: int = 75,
    visual_velocity_score: int = 75,
    silence_percentage: float = 0.0,
    predicted_completion_rate: float = 75.0,
    safe_zone_score: int = 85,
    platform_metrics: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Generates high-converting niche-accurate social media metadata:
    - 5 Viral CTR Titles (Shorts / Reels / TikTok)
    - 1 High-Engagement Caption with viral Hook and CTA
    - 15+ Segmented Hashtags (Broad, Niche, Viral Velocity)
    - Viral Reach Potential & Projected Views Tier (calibrated against live YouTube metrics)
    - Optimal Posting Times & Publishing Schedule (by platform & genre)
    """
    if genre_info is None:
        genre_info = {}

    genre = genre_info.get("genre", "talking_head")
    is_music_edit = genre_info.get("is_music_edit", False)

    # Compute Viral Potential & Optimal Posting Windows with live platform calibration
    viral_potential = calculate_viral_potential(
        hook_score=hook_score,
        visual_velocity_score=visual_velocity_score,
        silence_percentage=silence_percentage,
        predicted_completion_rate=predicted_completion_rate,
        safe_zone_score=safe_zone_score,
        genre_info=genre_info,
        platform_metrics=platform_metrics
    )
    posting_schedule = get_optimal_posting_times(genre_info)

    # ========================================================
    # 1. ANIME EDIT / AMV SOCIAL SUITE
    # ========================================================
    if genre == "anime_edit":
        character = genre_info.get("character") or genre_info.get("primary_subject") or "Anime"
        franchise = genre_info.get("franchise") or "Anime"
        move = genre_info.get("move", "")
        styles = genre_info.get("styles", ["Phonk", "60FPS"])
        style_label = " ".join(styles) if styles else "Phonk"

        move_phrase = f" {move}" if move else ""

        viral_titles = [
            f"{character}{move_phrase} at {style_label} Hits Different 🥶⚔️",
            f"The Coldest {character} Edit in {franchise} History 🔥",
            f"When {character} Used{move_phrase}... (Insane {style_label} Edit) 🤯",
            f"{character} Proved Why He's Built Different in {franchise} 👑",
            f"Wait For The {character} Beat Drop (Use Headphones 🎧) ⚡"
        ]

        caption_lines = [
            f"Wait for the beat drop... 🥶⚔️ {character} really proved why he's HIM!",
            "",
            f"Which {franchise} moment should I edit next? Drop your favorite character below! 👇",
            "",
            f"🎬 Anime: {franchise}",
            f"⚔️ Character: {character}"
        ]
        if move:
            caption_lines.append(f"⚡ Move: {move}")
        caption_lines.extend([
            f"🎧 Style: {style_label} Edit",
            "",
            "💬 Rate this edit from 1 to 10 in the comments!",
            f"📌 Save & share with a {franchise} fan who needs to see this!"
        ])
        caption = "\n".join(caption_lines)

        broad_tags = ["#anime", "#animeedit", "#amv", "#animetiktok", "#weeb", "#otaku"]
        niche_tags_raw = genre_info.get("niche_tags", [])
        if not niche_tags_raw:
            niche_tags_raw = [franchise.lower().replace(" ", ""), f"{franchise.lower().replace(' ', '')}edit", character.lower()]
        niche_tags = [f"#{t.lower().replace(' ', '')}" for t in niche_tags_raw[:7]]
        if f"#{character.lower()}" not in niche_tags and character.lower() != "anime":
            niche_tags.insert(0, f"#{character.lower()}")

        velocity_tags = ["#phonk", "#phonkedit", "#60fps", "#alightmotion", "#capcutanime", "#animeedits", "#viral"]

        all_hashtags = broad_tags + [t for t in niche_tags if t not in broad_tags] + velocity_tags
        seen = set()
        unique_hashtags = [x for x in all_hashtags if not (x in seen or seen.add(x))]

        return {
            "genre": "anime_edit",
            "genre_label": "Anime Edit / AMV",
            "primary_subject": character,
            "viral_titles": viral_titles,
            "caption": caption,
            "hashtags": {
                "all": " ".join(unique_hashtags),
                "broad": broad_tags,
                "niche": niche_tags,
                "velocity": velocity_tags
            },
            "viral_potential": viral_potential,
            "posting_schedule": posting_schedule
        }

    # ========================================================
    # 2. PODCAST / INTERVIEW CLIP SOCIAL SUITE
    # ========================================================
    if genre == "podcast_clip":
        primary = genre_info.get("primary_subject") or "Mindset"
        speaker = genre_info.get("character") or ""
        speaker_prefix = f"{speaker} Explains: " if speaker else ""

        viral_titles = [
            f"{speaker_prefix}The Uncomfortable Truth About {primary} Nobody Admits 🎙️",
            f"Why 99% Of People Fail At {primary} (Do This Instead) 🧠",
            f"The Exact Daily Rule That Transforms Your {primary} In 30 Days ⚡",
            f"If You Struggle With {primary}, Stop Scrolling Right Now 🛑",
            f"This One Conversation On {primary} Changed How I Think Forever 💡"
        ]

        caption = f"""The uncomfortable truth about {primary.lower()} that most people avoid talking about... 🎙️🧠

Most people rely on fleeting motivation instead of building friction-free daily systems.

3 Key Takeaways from this clip:
✅ Systems always outperform willpower when motivation runs out
✅ Remove initial friction before attempting deep focus
✅ Small, identity-based shifts compound into radical transformation

What's your single biggest challenge with {primary.lower()} right now? Drop a comment below! 👇

📌 Save this clip for your daily morning focus routine!"""

        broad_tags = ["#podcast", "#podcasts", "#podcastclips", "#mindset", "#motivation"]
        niche_tags = [f"#{primary.lower()}", f"#{primary.lower()}tips", "#discipline", "#selfimprovement", "#wisdom", "#habits", "#psychology"]
        velocity_tags = ["#viralreels", "#explorepage", "#growthmindset", "#successmindset", "#dailymotivation", "#reelsgrowth"]
        unique_hashtags = broad_tags + niche_tags + velocity_tags
        seen = set()
        dedup_hashtags = [x for x in unique_hashtags if not (x in seen or seen.add(x))]

        return {
            "genre": "podcast_clip",
            "genre_label": "Podcast / Interview Clip",
            "primary_subject": primary,
            "viral_titles": viral_titles,
            "caption": caption,
            "hashtags": {
                "all": " ".join(dedup_hashtags),
                "broad": broad_tags,
                "niche": niche_tags,
                "velocity": velocity_tags
            },
            "viral_potential": viral_potential,
            "posting_schedule": posting_schedule
        }

    # ========================================================
    # 3. GAMING MONTAGE & SHOWCASE SOCIAL SUITE
    # ========================================================
    if genre == "gaming_montage":
        game = genre_info.get("primary_subject", "Gaming")
        clean_tag = game.lower().replace(" ", "")
        franchise = genre_info.get("franchise", "Gaming").lower().replace(" ", "")

        viral_titles = [
            f"The Most Broken {game} Showcase You Need To See 💀🔥",
            f"Why Everyone In {genre_info.get('franchise', 'Ranked')} Is Scared Of {game} ⚡",
            f"Wait For The Full Combo... (Clean 60FPS {game}) 🥶",
            f"99% Of Players Don't Know This Secret {game} Tech 📈",
            f"They Thought It Was Over Until This {game} Play 🎯"
        ]
        caption = f"""They really thought they could counter this... 💀🎯
        
Full {game} showcase sequence in 60FPS.
Rate this play from 1 to 10 in the comments below! 👇

💬 What combo or showcase should I do next?
📌 Bookmark & save this before it gets patched!"""

        broad_tags = ["#gaming", "#gamer", "#gameplay", "#gamingclips", "#shorts"]
        niche_tags = [f"#{clean_tag}", f"#{franchise}", f"#{clean_tag}showcase", f"#{clean_tag}clips"]
        if "bloxfruits" in franchise or "roblox" in franchise:
            niche_tags.extend(["#roblox", "#bloxfruits", "#doughfruit", "#robloxfyp"])
        velocity_tags = ["#gamingmontage", "#viralgaming", "#explorepage", "#fyp", "#trending"]
        unique_hashtags = list(dict.fromkeys(broad_tags + niche_tags + velocity_tags))

        return {
            "genre": "gaming_montage",
            "genre_label": genre_info.get("genre_label", "Gaming Showcase"),
            "primary_subject": game,
            "viral_titles": viral_titles,
            "caption": caption,
            "hashtags": {
                "all": " ".join(unique_hashtags),
                "broad": broad_tags,
                "niche": niche_tags,
                "velocity": velocity_tags
            },
            "viral_potential": viral_potential,
            "posting_schedule": posting_schedule
        }

    # ========================================================
    # 4. HIGH-VELOCITY MUSIC / CINEMATIC EDIT SOCIAL SUITE
    # ========================================================
    if genre == "cinematic_edit":
        subject = genre_info.get("primary_subject", "Metamorphosis")
        creator = genre_info.get("character", "")
        styles = genre_info.get("styles", ["Phonk", "4K", "60FPS"])
        style_label = " ".join(styles) if styles else "Phonk"

        track_title = "Metamorphosis x Shadow Lady" if ("metamorphosis" in subject.lower() or "shadow" in filename.lower()) else f"{subject} Phonk"

        viral_titles = [
            f"{track_title} at {style_label} Hits Different 🥶⚡",
            f"The Coldest {subject} Drop on the Timeline 🔥",
            f"When The {subject} Beat Drops... (Use Headphones 🎧) 🤯",
            f"Pure Visual Velocity: {subject} in {style_label} 🏎️💨",
            f"The Pacing On This {subject} Edit Is Unmatched 💀"
        ]

        caption = f"""Wait for the {subject} drop... 🥶⚡ The audio sync on this edit is unmatched!

Which track / aesthetic should I cut next? Drop your favorite phonk below! 👇

🎧 Track: {track_title}
⚡ Quality: {style_label} Edit
🎬 Velocity: Elite Cut Pacing

💬 Rate the visual velocity from 1 to 10 in the comments!
📌 Save & share with someone who loves high-velocity phonk edits!"""

        broad_tags = ["#phonk", "#edit", "#velocity", "#cinematic", "#aesthetic"]
        niche_tags_raw = genre_info.get("niche_tags", ["metamorphosis", "shadowlady", "kagefx", "driftphonk", "alightmotion", "capcut", "aftereffects", "4k", "60fps"])
        niche_tags = [f"#{t.lower().replace(' ', '')}" for t in niche_tags_raw]
        velocity_tags = ["#phonkedit", "#visuals", "#60fps", "#drift", "#fyp", "#viral"]
        all_tags = broad_tags + [t for t in niche_tags if t not in broad_tags] + velocity_tags
        seen = set()
        unique_hashtags = [x for x in all_tags if not (x in seen or seen.add(x))]

        return {
            "genre": "cinematic_edit",
            "genre_label": "Phonk / High-Velocity Edit",
            "primary_subject": subject,
            "viral_titles": viral_titles,
            "caption": caption,
            "hashtags": {
                "all": " ".join(unique_hashtags),
                "broad": broad_tags,
                "niche": niche_tags,
                "velocity": velocity_tags
            },
            "viral_potential": viral_potential,
            "posting_schedule": posting_schedule
        }

    # ========================================================
    # 5. STANDARD TALKING-HEAD CREATOR SOCIAL SUITE
    # ========================================================
    words = [w.lower() for w in re.findall(r"\b[a-zA-Z]{4,}\b", transcript)]
    stop_words = {
        "this", "that", "with", "from", "your", "have", "will", "what", "video", "about",
        "there", "then", "when", "here", "just", "like", "more", "make", "really", "strike",
        "type", "bought", "money", "people", "something", "everything", "nothing", "someone",
        "know", "think", "said", "says", "told", "come", "came", "going", "doing", "look",
        "take", "give", "want", "need", "feel", "thing", "things", "guys", "tell", "much",
        "many", "well", "even", "back", "also", "still", "good", "great"
    }
    topic_keywords = [w for w in words if w not in stop_words]
    
    primary = topic_keywords[0].capitalize() if topic_keywords else "Your Strategy"

    viral_titles = [
        f"Stop Doing {primary} Like This (Watch Till End) 🛑",
        f"The Hidden {primary} Hack 99% Of People Don't Know 🤫",
        f"How I Fixed My {primary} In 60 Seconds ⚡",
        f"The Biggest Mistake With {primary} (Do This Instead) ❌",
        f"Is Your {primary} Costing You Views? Find Out Here 📈"
    ]

    caption = f"""Stop scrolling if you want to master {primary.lower()}! 🛑👇

Here’s the truth most creators never talk about:
If your video pacing drags in the first 3 seconds, viewers will swipe away before getting to your best advice.

3 Key Takeaways to apply right now:
✅ Cut dead-air pauses to keep momentum high
✅ Inflect vocal pitch on emphasis points
✅ Reframe within the 9:16 safe zone

Which of these are you fixing on your next post? Drop a comment below! 💬

Save this post so you don't forget before publishing! 📌"""

    broad_tags = [f"#{primary.lower()}", "#contentcreator", "#videoediting", "#shortformcontent", "#videotips"]
    niche_tags = [f"#{primary.lower()}tips", f"#{primary.lower()}growth", "#reelsgrowth", "#youtubeshorts", "#viralshorts"]
    velocity_tags = ["#creatoreconomy", "#socialmediatips", "#retention", "#tiktokgrowth", "#contentcreation"]

    unique_hashtags = broad_tags + niche_tags + velocity_tags

    return {
        "genre": "talking_head",
        "genre_label": "Talking-Head Creator",
        "primary_subject": primary,
        "viral_titles": viral_titles,
        "caption": caption,
        "hashtags": {
            "all": " ".join(unique_hashtags),
            "broad": broad_tags,
            "niche": niche_tags,
            "velocity": velocity_tags
        },
        "viral_potential": viral_potential,
        "posting_schedule": posting_schedule
    }
