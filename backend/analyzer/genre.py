import os
import re
from typing import Dict, Any, List, Optional

FRANCHISES = {
    "one_piece": {
        "name": "One Piece",
        "keywords": ["one_piece", "onepiece", "strawhat", "luffy", "zoro", "shanks", "kamusari", "kaido", "sanji", "wano", "egghead"],
        "tags": ["onepiece", "onepieceedit", "luffy", "zoro", "shanks", "kamusari", "strawhats", "oda"]
    },
    "naruto": {
        "name": "Naruto",
        "keywords": ["naruto", "shippuden", "sasuke", "itachi", "madara", "kakashi", "obito", "pain", "boruto"],
        "tags": ["naruto", "narutoedit", "shippuden", "itachi", "sasuke", "madara", "uchiha", "konoha"]
    },
    "jujutsu_kaisen": {
        "name": "Jujutsu Kaisen",
        "keywords": ["jujutsu", "jjk", "gojo", "sukuna", "toji", "megumi", "yuji", "geto", "kashimo"],
        "tags": ["jjk", "jjkedit", "jujutsukaisen", "gojo", "sukuna", "toji", "domainexpansion", "anime"]
    },
    "bleach": {
        "name": "Bleach",
        "keywords": ["bleach", "ichigo", "aizen", "bankai", "kenpachi", "byakuya", "ulquiorra", "tybw"],
        "tags": ["bleach", "bleachedit", "ichigo", "aizen", "bankai", "tybw", "soulreaper", "animeamv"]
    },
    "demon_slayer": {
        "name": "Demon Slayer",
        "keywords": ["demon_slayer", "demonslayer", "kimetsu", "tanjiro", "zenitsu", "rengoku", "muzan", "giyu", "inosuke"],
        "tags": ["demonslayer", "demonslayeredit", "kimetsunoyaiba", "tanjiro", "rengoku", "hashira", "kny"]
    },
    "dragon_ball": {
        "name": "Dragon Ball",
        "keywords": ["dragonball", "dbz", "dbs", "goku", "vegeta", "gohan", "broly", "saiyan"],
        "tags": ["dbz", "dbzedit", "dragonball", "dragonballsuper", "goku", "vegeta", "ultraego", "ultrainstinct"]
    },
    "attack_on_titan": {
        "name": "Attack on Titan",
        "keywords": ["attack_on_titan", "attackontitan", "aot", "shingeki", "eren", "levi", "mikasa"],
        "tags": ["aot", "aotedit", "attackontitan", "erenyeager", "leviackerman", "shingeki", "rumbling"]
    }
}

CHARACTERS = {
    "shanks": {"name": "Shanks", "franchise": "One Piece", "epithet": "Red-Haired Shanks", "move": "Kamusari (Divine Departure)"},
    "kamusari": {"name": "Kamusari", "franchise": "One Piece", "character": "Shanks", "move": "Divine Departure"},
    "luffy": {"name": "Luffy", "franchise": "One Piece", "epithet": "Gear 5 Monkey D. Luffy"},
    "zoro": {"name": "Zoro", "franchise": "One Piece", "epithet": "Roronoa Zoro King of Hell"},
    "gojo": {"name": "Gojo Satoru", "franchise": "Jujutsu Kaisen", "move": "Hollow Purple"},
    "sukuna": {"name": "Ryomen Sukuna", "franchise": "Jujutsu Kaisen", "move": "Malevolent Shrine"},
    "toji": {"name": "Toji Fushiguro", "franchise": "Jujutsu Kaisen", "epithet": "The Sorcerer Killer"},
    "itachi": {"name": "Itachi Uchiha", "franchise": "Naruto", "move": "Tsukuyomi"},
    "madara": {"name": "Madara Uchiha", "franchise": "Naruto", "epithet": "Ghost of the Uchiha"},
    "sasuke": {"name": "Sasuke Uchiha", "franchise": "Naruto", "move": "Indra's Arrow"},
    "aizen": {"name": "Sosuke Aizen", "franchise": "Bleach", "move": "Kyoka Suigetsu"},
    "ichigo": {"name": "Ichigo Kurosaki", "franchise": "Bleach", "move": "Getsuga Tensho"},
    "goku": {"name": "Goku", "franchise": "Dragon Ball", "move": "Kamehameha"},
    "vegeta": {"name": "Vegeta", "franchise": "Dragon Ball", "move": "Final Flash"},
    "tanjiro": {"name": "Tanjiro", "franchise": "Demon Slayer", "move": "Hinokami Kagura"},
    "eren": {"name": "Eren Yeager", "franchise": "Attack on Titan", "epithet": "Founding Titan"}
}

PHONK_TRACKS = {
    "metamorphosis": {"title": "Metamorphosis", "artist": "Interworld"},
    "shadow_lady": {"title": "Shadow Lady", "artist": "Portwave"},
    "shadow": {"title": "Shadow Lady", "artist": "Portwave"},
    "lady": {"title": "Shadow Lady", "artist": "Portwave"},
    "kagefx": {"title": "Metamorphosis Edit", "artist": "KageFX"},
    "kage": {"title": "Metamorphosis Edit", "artist": "Kage"},
    "murder_in_my_mind": {"title": "Murder In My Mind", "artist": "Kordhell"},
    "kordhell": {"title": "Murder In My Mind", "artist": "Kordhell"},
    "rave": {"title": "Rave", "artist": "Dxrk"},
    "dxrk": {"title": "Rave", "artist": "Dxrk"},
    "drift": {"title": "Tokyo Drift", "artist": "Drift Phonk"},
    "montagem": {"title": "Montagem", "artist": "Brazilian Phonk"}
}

PHONK_KEYWORDS = {
    "phonk", "metamorphosis", "shadow", "lady", "kage", "kagefx",
    "portwave", "interworld", "drift", "cowbell", "brazilian", "funk",
    "bateman", "sigma", "montage", "amv", "edit", "edits", "slowed", "reverb",
    "aftereffects", "alightmotion", "velocity"
}

GAMING_KEYWORDS = {
    "gaming", "gameplay", "roblox", "bloxfruits", "blox", "fruit", "fruits", "dough",
    "valorant", "cod", "warzone", "fortnite", "minecraft", "apex", "csgo", "cs2",
    "clutch", "ace", "montage", "kills", "streamer", "ranked", "showcase", "combo",
    "pvp", "brawlstars", "genshin", "gta", "fifa", "pubg", "freefire", "clashroyale",
    "eldenring", "pokemon", "speedrun", "awakened", "bossfight", "v4", "leopard", "kitsune"
}

PODCAST_KEYWORDS = {
    "podcast", "podcasts", "interview", "episode", "guest", "host",
    "dialogue", "rogan", "huberman", "conversational", "diary_of_a_ceo",
    "lex", "talkshow", "discipline", "mindset", "habits", "psychology", "business", "dopamine"
}

STYLE_KEYWORDS = {
    "phonk": "Phonk",
    "amv": "AMV",
    "60fps": "60FPS",
    "4k": "4K",
    "edit": "Edit",
    "alight": "Alight Motion",
    "capcut": "CapCut",
    "slowed": "Slowed & Reverb",
    "reverb": "Reverb",
    "velocity": "Velocity"
}


def detect_video_genre(
    filename: str,
    transcript: str,
    word_count: int,
    average_shot_length: float,
    visual_cut_count: int,
    duration: float
) -> Dict[str, Any]:
    """
    Intelligently classifies video into creator genre:
    - 'anime_edit': Anime Music Videos / Manga / Phonk Edits
    - 'cinematic_edit': Fast-cut aesthetic / gym / phonk montages
    - 'gaming_montage': Gaming highlights and motion clips
    - 'podcast_clip': Podcast and conversational interview clips
    - 'talking_head': Standard talking creator / podcast / tutorial
    """
    clean_filename = re.sub(r"[^a-zA-Z0-9]", "_", filename.lower())
    fn_tokens = set([t for t in clean_filename.split("_") if t])
    transcript_tokens = set([t.lower() for t in re.findall(r"\b[a-zA-Z0-9]+\b", transcript)])
    combined_tokens = fn_tokens.union(transcript_tokens)

    # Check for style attributes (Phonk, 60FPS, 4K, etc.)
    detected_styles = []
    for s_key, s_label in STYLE_KEYWORDS.items():
        if s_key in clean_filename or s_key in combined_tokens:
            if s_label not in detected_styles:
                detected_styles.append(s_label)

    # Calculate speech velocity across the total video duration
    duration_min = max(0.1, duration / 60.0)
    wpm_overall = word_count / duration_min

    # ========================================================
    # 1. ANIME FRANCHISE & CHARACTER MATCHES
    # ========================================================
    detected_franchise = None
    matched_tags = []
    for f_key, f_data in FRANCHISES.items():
        if any(kw in clean_filename or kw in combined_tokens for kw in f_data["keywords"]):
            detected_franchise = f_data["name"]
            matched_tags.extend(f_data["tags"])
            break

    detected_char = None
    detected_char_data = None
    for c_key, c_data in CHARACTERS.items():
        if c_key in clean_filename or c_key in combined_tokens:
            detected_char = c_data["name"]
            detected_char_data = c_data
            if not detected_franchise:
                detected_franchise = c_data.get("franchise")
            break

    is_anime = bool(
        detected_franchise or 
        detected_char or 
        "anime" in clean_filename or 
        "amv" in clean_filename or 
        "manga" in clean_filename or
        any(k in combined_tokens for k in ["anime", "amv", "manga", "weeb", "otaku"])
    )

    if is_anime:
        subject = detected_char or detected_franchise or "Anime"
        entities = []
        if detected_franchise:
            entities.append(detected_franchise)
        if detected_char and detected_char != detected_franchise:
            entities.append(detected_char)
        if detected_char_data and "move" in detected_char_data:
            entities.append(detected_char_data["move"])
        entities.extend(detected_styles)

        return {
            "genre": "anime_edit",
            "genre_label": "Anime Edit / AMV",
            "is_music_edit": True,
            "detected_entities": entities or ["Anime", "Phonk"],
            "primary_subject": subject,
            "franchise": detected_franchise or "Anime",
            "character": detected_char or "",
            "move": detected_char_data.get("move", "") if detected_char_data else "",
            "styles": detected_styles,
            "niche_tags": matched_tags
        }

    # ========================================================
    # 2. PHONK & HIGH-VELOCITY MUSIC EDIT DETECTION
    # ========================================================
    phonk_matches = combined_tokens.intersection(PHONK_KEYWORDS)
    is_phonk_named = bool(phonk_matches or any(k in clean_filename for k in ["phonk", "metamorphosis", "shadow_lady", "kage", "drift"]))
    # Edit detection: fast cuts (ASL <= 2.2s or visual cuts >= 8) and low continuous speech (WPM <= 50)
    is_visual_music_edit = (average_shot_length <= 2.2 or visual_cut_count >= 8) and (word_count <= 25 and wpm_overall <= 55.0)

    if is_phonk_named or is_visual_music_edit:
        # Detect track or artist
        detected_track = "Metamorphosis" if "metamorphosis" in clean_filename else (
            "Shadow Lady" if "shadow" in clean_filename or "lady" in clean_filename else "Phonk"
        )
        detected_creator = "KageFX" if "kage" in clean_filename else ("Interworld / Portwave" if "metamorphosis" in clean_filename else "Velocity Edit")

        entities = [detected_track, detected_creator] + [s for s in detected_styles if s not in [detected_track, detected_creator]]

        tags = [
            "phonk", "metamorphosis", "shadowlady", "phonkedit", "amv",
            "driftphonk", "velocity", "aftereffects", "alightmotion", "4k", "60fps", "fyp"
        ]
        if "kagefx" in clean_filename or "kage" in clean_filename:
            tags.insert(0, "kagefx")

        return {
            "genre": "cinematic_edit",
            "genre_label": "Phonk / High-Velocity Edit",
            "is_music_edit": True,
            "detected_entities": entities,
            "primary_subject": detected_track,
            "franchise": "Phonk",
            "character": detected_creator,
            "move": "",
            "styles": detected_styles or ["Phonk", "4K", "60FPS"],
            "niche_tags": tags
        }

    # ========================================================
    # 3. GAMING & SHOWCASE MONTAGE DETECTION
    # ========================================================
    gaming_matches = combined_tokens.intersection(GAMING_KEYWORDS)
    is_gaming_named = bool(
        gaming_matches or
        "montage" in clean_filename or
        "showcase" in clean_filename or
        any(k in clean_filename for k in ["roblox", "bloxfruits", "blox", "dough", "minecraft", "fortnite", "valorant"])
    )

    if is_gaming_named:
        game_title = "Gaming"
        if "bloxfruits" in clean_filename or "bloxfruits" in combined_tokens:
            game_title = "Blox Fruits"
        elif "roblox" in clean_filename or "roblox" in combined_tokens:
            game_title = "Roblox"
        elif "valorant" in clean_filename or "valorant" in combined_tokens:
            game_title = "Valorant"
        elif "fortnite" in clean_filename or "fortnite" in combined_tokens:
            game_title = "Fortnite"
        elif "cod" in clean_filename or "warzone" in clean_filename:
            game_title = "Call of Duty"
        elif "csgo" in clean_filename or "cs2" in clean_filename:
            game_title = "CS2"
        elif "minecraft" in clean_filename:
            game_title = "Minecraft"

        # Detect specific feature or item (e.g. Dough, Brown Dough, Leopard, V4)
        item_title = ""
        for item in ["dough", "leopard", "kitsune", "dragon", "portal", "buddha", "v4", "combo", "showcase"]:
            if item in clean_filename or item in combined_tokens:
                item_title = item.capitalize()
                break

        subject = f"{game_title} {item_title}".strip() if item_title else game_title

        entities = [game_title]
        if item_title and item_title != game_title:
            entities.append(item_title)
        entities.extend([t.capitalize() for t in gaming_matches if len(t) > 2 and t not in [game_title.lower(), item_title.lower()]][:3])
        entities.extend(detected_styles)

        niche_tags = [
            game_title.lower().replace(" ", ""),
            f"{game_title.lower().replace(' ', '')}clips",
            "gaming", "gamer", "shorts", "fyp"
        ]
        if item_title:
            niche_tags.insert(1, f"{item_title.lower()}")
            niche_tags.insert(2, f"{game_title.lower().replace(' ', '')}{item_title.lower()}")

        return {
            "genre": "gaming_montage",
            "genre_label": f"{game_title} Showcase / Edit" if item_title or "showcase" in clean_filename else f"{game_title} Gaming",
            "is_music_edit": True,
            "detected_entities": entities,
            "primary_subject": subject,
            "franchise": game_title,
            "character": item_title or game_title,
            "move": "Gameplay Showcase",
            "styles": detected_styles or ["Gaming Showcase", "60FPS"],
            "niche_tags": niche_tags
        }

    # ========================================================
    # 4. PODCAST / INTERVIEW CLIP DETECTION
    # ========================================================
    podcast_matches = combined_tokens.intersection(PODCAST_KEYWORDS)
    if "podcast" in clean_filename or "interview" in clean_filename or len(podcast_matches) >= 1:
        core_themes = ["discipline", "motivation", "dopamine", "habits", "focus", "mindset", "business", "psychology", "money", "health", "sleep", "workout"]
        primary_topic = None
        for theme in core_themes:
            if theme in clean_filename or theme in combined_tokens:
                primary_topic = theme.capitalize()
                break
        
        if not primary_topic:
            stop_words = {"this", "that", "with", "from", "your", "have", "will", "what", "video", "about", "there", "then", "when", "here", "podcast", "episode", "clip", "mp4", "biggest", "exact", "daily", "people", "clients", "make"}
            meaningful_words = [t.capitalize() for t in combined_tokens if len(t) >= 4 and t.lower() not in stop_words]
            primary_topic = meaningful_words[0] if meaningful_words else "Mindset"
        
        entities = ["Podcast", primary_topic]
        if "huberman" in combined_tokens or "huberman" in clean_filename:
            entities.insert(0, "Andrew Huberman")
        elif "rogan" in combined_tokens or "rogan" in clean_filename:
            entities.insert(0, "Joe Rogan")

        return {
            "genre": "podcast_clip",
            "genre_label": "Podcast / Interview Clip",
            "is_music_edit": False,
            "detected_entities": entities,
            "primary_subject": primary_topic,
            "franchise": "Podcast",
            "character": entities[0] if len(entities) > 1 and ("Huberman" in entities[0] or "Rogan" in entities[0]) else "",
            "move": "",
            "styles": ["Conversation", "Thought Leadership"],
            "niche_tags": ["podcast", "podcastclips", "mindset", "motivation", "interview", primary_topic.lower(), "discipline", "selfimprovement"]
        }

    # ========================================================
    # 4b. BUSINESS, WEALTH & HORMOZI DIRECT-ADVICE CREATOR
    # ========================================================
    business_keywords = {"hormozi", "business", "money", "offer", "sales", "revenue", "millionaire", "marketing", "pricing", "wealth", "founder", "startup", "ecommerce", "agency"}
    if any(k in clean_filename or k in combined_tokens for k in business_keywords):
        subject = "Alex Hormozi" if "hormozi" in clean_filename or "hormozi" in combined_tokens else "Business Strategy"
        return {
            "genre": "business_advice",
            "genre_label": "Business & Wealth Direct Advice",
            "is_music_edit": False,
            "detected_entities": [subject, "Pricing & Offers", "Entrepreneurship"],
            "primary_subject": subject,
            "franchise": "Business",
            "character": subject,
            "move": "Value Delivery",
            "styles": ["Direct Advice", "Kinetic Captions", "High Verbal Velocity"],
            "niche_tags": ["business", "money", "entrepreneur", "wealth", "sales", "hormozi", "success", "mindset"]
        }

    # ========================================================
    # 4c. SUSPENSE, MYSTERY & TRUE CRIME STORYTELLING
    # ========================================================
    story_keywords = {"mrballen", "mystery", "story", "stories", "unsolved", "crime", "dark", "creepy", "cave", "tunnel", "horror", "bizarre", "incident"}
    if any(k in clean_filename or k in combined_tokens for k in story_keywords):
        subject = "MrBallen Mystery" if "mrballen" in clean_filename or "mrballen" in combined_tokens else "Dark Mystery Story"
        return {
            "genre": "storytelling",
            "genre_label": "Suspense & Mystery Storytelling",
            "is_music_edit": False,
            "detected_entities": [subject, "Curiosity Open Loop", "Narrative Hook"],
            "primary_subject": subject,
            "franchise": "Storytelling",
            "character": "Narrator",
            "move": "Suspense Reveal",
            "styles": ["Narrative Arc", "Curiosity Loop", "Dramatic Tone"],
            "niche_tags": ["storytime", "mystery", "truecrime", "scarystories", "darkmystery", "mrballen", "unsolved"]
        }

    # ========================================================
    # 4d. VIRAL HIGH-STAKES CHALLENGE (MRBEAST STYLE)
    # ========================================================
    challenge_keywords = {"beast", "challenge", "survive", "box", "10000", "hours", "prize", "win", "trapped", "escape", "bounty"}
    if any(k in clean_filename or k in combined_tokens for k in challenge_keywords):
        subject = "MrBeast Challenge" if "beast" in clean_filename or "beast" in combined_tokens else "High-Stakes Challenge"
        return {
            "genre": "viral_challenge",
            "genre_label": "High-Stakes Viral Challenge",
            "is_music_edit": False,
            "detected_entities": [subject, "Cash Prize", "Countdown Timer"],
            "primary_subject": subject,
            "franchise": "Entertainment",
            "character": "MrBeast Challenger",
            "move": "Instant Climax",
            "styles": ["Rapid Cuts", "High Energy", "Stakes Countdown"],
            "niche_tags": ["mrbeast", "challenge", "viral", "survive", "competition", "insane", "shorts"]
        }

    # ========================================================
    # 4e. TECH REVIEW & SILICON STRESS TEST
    # ========================================================
    tech_keywords = {"tech", "ipad", "iphone", "apple", "m4", "review", "unboxing", "gadget", "silicon", "camera", "pro", "benchmark"}
    if any(k in clean_filename or k in combined_tokens for k in tech_keywords):
        subject = "M4 iPad Pro" if "ipad" in clean_filename or "ipad" in combined_tokens else "Tech Hardware"
        return {
            "genre": "tech_review",
            "genre_label": "Tech & Gadget Silicon Review",
            "is_music_edit": False,
            "detected_entities": [subject, "Stress Test", "Benchmark"],
            "primary_subject": subject,
            "franchise": "Technology",
            "character": "Tech Reviewer",
            "move": "Macro Detail",
            "styles": ["Crisp Audio", "Macro B-Roll", "Clean Lighting"],
            "niche_tags": ["tech", "apple", "ipadpro", "gadgets", "review", "unboxing", "m4", "technology"]
        }

    # ========================================================
    # 4f. FITNESS & BODYBUILDING MOTIVATION
    # ========================================================
    fitness_keywords = {"fitness", "workout", "gym", "cbum", "bumstead", "olympia", "physique", "muscle", "lifting", "bodybuilding", "chest", "motivation"}
    if any(k in clean_filename or k in combined_tokens for k in fitness_keywords):
        subject = "Chris Bumstead (CBum)" if "cbum" in clean_filename or "bumstead" in clean_filename or "cbum" in combined_tokens else "Bodybuilding Motivation"
        return {
            "genre": "fitness_motivation",
            "genre_label": "Fitness & Olympia Motivation",
            "is_music_edit": True,
            "detected_entities": [subject, "Classic Physique", "Gym Mindset"],
            "primary_subject": subject,
            "franchise": "Fitness",
            "character": subject,
            "move": "Heavy Set PR",
            "styles": ["Hardstyle / Phonk", "Slow Motion Lift", "Vocal Grit"],
            "niche_tags": ["gym", "fitness", "bodybuilding", "cbum", "workout", "motivation", "gymtok", "discipline"]
        }

    # ========================================================
    # 4g. FOOD & ASMR STREET COOKING
    # ========================================================
    food_keywords = {"food", "burger", "cooking", "asmr", "recipe", "wagyu", "smash", "crispy", "delicious", "steak", "streetfood", "cheese"}
    if any(k in clean_filename or k in combined_tokens for k in food_keywords):
        subject = "Wagyu Smash Burger" if "burger" in clean_filename or "wagyu" in clean_filename or "burger" in combined_tokens else "Street Food ASMR"
        return {
            "genre": "food_asmr",
            "genre_label": "Culinary & ASMR Street Food",
            "is_music_edit": False,
            "detected_entities": [subject, "Sizzle Audio", "Sauce Drip"],
            "primary_subject": subject,
            "franchise": "Food",
            "character": "Chef ASMR",
            "move": "Macro Sizzle",
            "styles": ["Crisp Foley Audio", "Macro Food Shot", "Zero Talking"],
            "niche_tags": ["food", "foodie", "asmr", "burger", "cooking", "streetfood", "delicious", "wagyu"]
        }

    # ========================================================
    # 4h. COMEDY & RELATABLE POV SKIT
    # ========================================================
    comedy_keywords = {"comedy", "skit", "pov", "relatable", "funny", "3am", "brain", "humor", "joke", "roommate", "student"}
    if any(k in clean_filename or k in combined_tokens for k in comedy_keywords):
        subject = "Brain at 3 AM" if "3am" in clean_filename or "brain" in clean_filename or "3am" in combined_tokens else "Relatable POV Skit"
        return {
            "genre": "comedy_skit",
            "genre_label": "Comedy & Relatable POV",
            "is_music_edit": False,
            "detected_entities": [subject, "Relatable Humor", "POV Text Banner"],
            "primary_subject": subject,
            "franchise": "Comedy",
            "character": "POV Character",
            "move": "Punchline Delivery",
            "styles": ["Facial Comedy", "Awkward Silence Cut", "Punchy Timing"],
            "niche_tags": ["comedy", "pov", "relatable", "funny", "skit", "humor", "memes", "viralcomedy"]
        }

    # ========================================================
    # 4i. SHORT-FORM SOUNDBITE / REEL / VIRAL MONTAGE
    # Only if the video exhibits fast cut pacing or beat synchronization
    # ========================================================
    if word_count <= 25 and duration >= 15.0 and wpm_overall <= 45.0 and average_shot_length <= 2.5 and visual_cut_count >= 5:
        return {
            "genre": "cinematic_edit",
            "genre_label": "Short-Form Soundbite / Reel",
            "is_music_edit": True,
            "detected_entities": ["Viral Soundbite", "Short"],
            "primary_subject": "Soundbite Short",
            "franchise": "Shorts",
            "character": "",
            "move": "",
            "styles": detected_styles or ["Short-Form"],
            "niche_tags": ["shorts", "reels", "viral", "fyp", "trending"]
        }

    # ========================================================
    # 5. STANDARD TALKING-HEAD CREATOR
    # ========================================================
    return {
        "genre": "talking_head",
        "genre_label": "Talking-Head Creator",
        "is_music_edit": False,
        "detected_entities": [],
        "primary_subject": "Content",
        "franchise": "",
        "character": "",
        "move": "",
        "styles": [],
        "niche_tags": []
    }
