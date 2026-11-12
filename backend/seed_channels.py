import os
import subprocess
import datetime
from backend.database import SessionLocal, Project, Analysis

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "storage", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

def generate_voiceover(text: str, wav_path: str):
    """Uses Windows System.Speech to generate crisp voiceover WAV."""
    clean_path = wav_path.replace("\\", "/")
    ps_cmd = f"""
    Add-Type -AssemblyName System.Speech
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.SetOutputToWaveFile('{clean_path}')
    $synth.Speak('{text}')
    $synth.Dispose()
    """
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True)

def build_vertical_video(wav_path: str, mp4_path: str, title: str, bg_color: str):
    """Generates 1080x1920 MP4 with voiceover and clean visual layout."""
    # Probe audio duration
    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", wav_path
    ]
    dur = float(subprocess.check_output(probe_cmd).decode().strip())
    
    # FFmpeg generate 1080x1920 video with gradient/color background and audio
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c={bg_color}:s=1080x1920:d={dur}",
        "-i", wav_path,
        "-vf", (
            f"drawbox=y=ih-400:color=black@0.4:width=iw:height=300:t=fill,"
            f"drawtext=text='{title}':fontcolor=white:fontsize=48:x=(w-text_w)/2:y=(h-text_h)/2:shadowcolor=black@0.8:shadowx=3:shadowy=3"
        ),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        mp4_path
    ]
    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return dur

def seed_channels():
    db = SessionLocal()

    # =========================================================================
    # Channel 4: Alex Hormozi - Business & Wealth Advice (proj_hormozi_001)
    # =========================================================================
    hormozi_text = (
        "If you want to make your first million dollars stop selling your time for hourly wages. "
        "When you trade hours for dollars your income is mathematically capped at twenty four hours in a day. "
        "Instead productize your skill or build an offer so good people feel stupid saying no. "
        "Here is the exact pricing framework you need to scale."
    )
    hormozi_wav = os.path.join(UPLOADS_DIR, "proj_hormozi_speech.wav")
    hormozi_mp4 = os.path.join(UPLOADS_DIR, "proj_hormozi_001_alex_hormozi_pricing_rule.mp4")
    
    if not os.path.exists(hormozi_mp4):
        print("Generating Alex Hormozi voiceover and video...")
        generate_voiceover(hormozi_text, hormozi_wav)
        h_dur = build_vertical_video(hormozi_wav, hormozi_mp4, "ALEX HORMOZI // PRICING RULE", "#111827")
    else:
        h_dur = 16.5

    # Register Project 4
    p4 = db.query(Project).filter(Project.id == "proj_hormozi_001").first()
    if not p4:
        p4 = Project(
            id="proj_hormozi_001",
            title="Alex Hormozi: How to Price Your Product ($100M Offer Rule)",
            original_filename="alex_hormozi_pricing_rule.mp4",
            original_filepath=hormozi_mp4,
            duration=round(h_dur, 2),
            width=1080,
            height=1920,
            fps=30.0,
            aspect_ratio="9:16",
            status="analyzed",
            created_at=datetime.datetime.utcnow()
        )
        db.add(p4)
        db.commit()

    # Analysis 4
    a4 = db.query(Analysis).filter(Analysis.project_id == "proj_hormozi_001").first()
    if not a4:
        a4 = Analysis(
            id="an_hormozi_001",
            project_id="proj_hormozi_001",
            transcript_text=hormozi_text,
            words_per_minute=178.0,
            word_timestamps=[
                {"word": w, "start": round(i * 0.34, 2), "end": round((i + 1) * 0.34, 2)}
                for i, w in enumerate(hormozi_text.split())
            ],
            sentence_segments=[
                {"start": 0.0, "end": 4.5, "text": "If you want to make your first million dollars stop selling your time for hourly wages."},
                {"start": 4.5, "end": 9.5, "text": "When you trade hours for dollars your income is mathematically capped at twenty four hours in a day."},
                {"start": 9.5, "end": 13.5, "text": "Instead productize your skill or build an offer so good people feel stupid saying no."},
                {"start": 13.5, "end": 16.5, "text": "Here is the exact pricing framework you need to scale."}
            ],
            filler_words=[],
            silence_intervals=[
                {"start": 4.5, "end": 4.85, "duration": 0.35},
                {"start": 9.5, "end": 9.85, "duration": 0.35}
            ],
            total_silence_duration=0.70,
            silence_percentage=4.2,
            hook_score=92,
            hook_grade="A",
            hook_explanation="Elite Contrarian Pattern Interrupt: Directly attacks conventional hourly wage mindset in frame 1 with bold financial stakes.",
            hook_issues=[],
            hook_recommendations=["Keep kinetic subtitle captions centered in the 9:16 safe zone."],
            alternative_hooks=[
                {
                    "type": "The Bold Contrarian",
                    "hook": "Stop trading your hours for dollars if you ever want to get wealthy.",
                    "visual_technique": "Display bold red ✖ over clock icon in first 1.5s.",
                    "why_it_works": "Directly confronts comfortable beliefs and triggers psychological pattern interrupt."
                },
                {
                    "type": "The Curiosity Gap",
                    "hook": "The mathematically impossible trap ninety percent of workers fall into...",
                    "visual_technique": "Flash mathematical equation graphic: 24 hrs x Wage = Capped.",
                    "why_it_works": "Creates an open loop requiring explanation of the mathematical trap."
                },
                {
                    "type": "The High-Stakes Framework",
                    "hook": "Here is how I price products so clients feel stupid saying no.",
                    "visual_technique": "Fast 1-second preview of the 3-step offer matrix.",
                    "why_it_works": "Offers instant proprietary insight from a verified high-net-worth operator."
                }
            ],
            scene_cuts=[0.0, 4.5, 9.5, 13.5],
            static_scenes=[],
            visual_dynamics_data={
                "scene_cuts": [0.0, 4.5, 9.5, 13.5],
                "static_scenes": [],
                "boredom_windows": [],
                "visual_velocity_score": 88,
                "visual_pace_rating": "Good Visual Pacing",
                "average_shot_length": 3.8,
                "fps": 30.0,
                "width": 1080,
                "height": 1920,
                "duration": round(h_dur, 2),
                "genre_info": {
                    "genre": "business_advice",
                    "genre_label": "Business & Wealth Direct Advice",
                    "primary_subject": "Alex Hormozi",
                    "is_music_edit": False
                }
            },
            vocal_data={
                "pitch_score": 90,
                "vocal_energy_rating": "High Dynamic Energy",
                "monotone_segments": [],
                "emphasis_peaks": [1.2, 5.8, 11.2, 14.8],
                "waveform": [round(0.25 + 0.5 * (0.5 + 0.5 * __import__("math").sin(i * 0.38)), 3) for i in range(80)]
            },
            safe_zone_data={
                "safe_zone_score": 94,
                "compliance_status": "Passed (Social Media Safe)",
                "face_detected": True,
                "face_centered": True,
                "top_margin_pct": 14.0,
                "bottom_margin_pct": 18.0
            },
            retention_curve_data={
                "predicted_completion_rate": 86.8,
                "platform_metrics": {
                    "is_verified": True,
                    "view_count": 680000,
                    "like_count": 34200,
                    "comment_count": 1150,
                    "channel": "Acquisition Media / Alex Hormozi",
                    "vvs_rate": 84.2,
                    "apvp_rate": 86.8
                }
            },
            retention_timeline=[
                {"timestamp": 0.0, "type": "hook", "title": "Hook Score: 92/100 (Grade A)", "description": "Contrarian pattern interrupt hooks audience immediately.", "actionable_fix": "Highlight key power words in yellow kinetic subtitle style."},
                {"timestamp": 4.5, "type": "cut", "title": "Cut / Transition (4.5s)", "description": "Transition to mathematical breakdown of time vs money.", "actionable_fix": "Keep rapid verbal velocity steady."}
            ]
        )
        db.add(a4)
        db.commit()
    print("Channel 4 (Alex Hormozi) seeded successfully!")

    # =========================================================================
    # Channel 5: MrBallen - Suspense & Mystery Storytelling (proj_story_001)
    # =========================================================================
    story_text = (
        "Three teenagers hiked into this abandoned iron mine in upstate New York despite seven different warning signs. "
        "As they stepped past the rusted steel doors the temperature dropped twenty degrees. "
        "And that is when they noticed fresh footprints leading deeper into the dark."
    )
    story_wav = os.path.join(UPLOADS_DIR, "proj_story_speech.wav")
    story_mp4 = os.path.join(UPLOADS_DIR, "proj_story_001_mrballen_abandoned_mine.mp4")

    if not os.path.exists(story_mp4):
        print("Generating MrBallen Storytelling voiceover and video...")
        generate_voiceover(story_text, story_wav)
        s_dur = build_vertical_video(story_wav, story_mp4, "MRBALLEN // THE ABANDONED MINE", "#0f172a")
    else:
        s_dur = 17.2

    # Register Project 5
    p5 = db.query(Project).filter(Project.id == "proj_story_001").first()
    if not p5:
        p5 = Project(
            id="proj_story_001",
            title="MrBallen: The Abandoned Mine Warning (Dark Mystery)",
            original_filename="mrballen_abandoned_mine.mp4",
            original_filepath=story_mp4,
            duration=round(s_dur, 2),
            width=1080,
            height=1920,
            fps=30.0,
            aspect_ratio="9:16",
            status="analyzed",
            created_at=datetime.datetime.utcnow()
        )
        db.add(p5)
        db.commit()

    # Analysis 5
    a5 = db.query(Analysis).filter(Analysis.project_id == "proj_story_001").first()
    if not a5:
        a5 = Analysis(
            id="an_story_001",
            project_id="proj_story_001",
            transcript_text=story_text,
            words_per_minute=154.0,
            word_timestamps=[
                {"word": w, "start": round(i * 0.38, 2), "end": round((i + 1) * 0.38, 2)}
                for i, w in enumerate(story_text.split())
            ],
            sentence_segments=[
                {"start": 0.0, "end": 6.8, "text": "Three teenagers hiked into this abandoned iron mine in upstate New York despite seven different warning signs."},
                {"start": 6.8, "end": 12.0, "text": "As they stepped past the rusted steel doors the temperature dropped twenty degrees."},
                {"start": 12.0, "end": 17.2, "text": "And that is when they noticed fresh footprints leading deeper into the dark."}
            ],
            filler_words=[],
            silence_intervals=[
                {"start": 6.8, "end": 7.3, "duration": 0.50},
                {"start": 12.0, "end": 12.45, "duration": 0.45}
            ],
            total_silence_duration=0.95,
            silence_percentage=5.5,
            hook_score=95,
            hook_grade="A",
            hook_explanation="Elite Curiosity Open Loop: Frame 1 immediately establishes severe danger and human vulnerability, locking psychological curiosity.",
            hook_issues=[],
            hook_recommendations=["Add subtle dark ambient drone beneath voiceover to intensify tension."],
            alternative_hooks=[
                {
                    "type": "The Unresolved Mystery",
                    "hook": "They ignored seven warning signs before stepping into this abandoned mine...",
                    "visual_technique": "Flash rusted 'DO NOT ENTER' sign at 0.1s with bass rumble.",
                    "why_it_works": "The brain cannot scroll past an unresolved catastrophe in progress."
                },
                {
                    "type": "The Physical Climax",
                    "hook": "The moment they stepped past the doors the temperature dropped twenty degrees...",
                    "visual_technique": "Rapid zoom-in to pitch black tunnel opening.",
                    "why_it_works": "Sensory description triggers visceral viewer immersion."
                },
                {
                    "type": "The Chilling Discovery",
                    "hook": "Nobody had entered this mine in fifty years until they found fresh footprints...",
                    "visual_technique": "Macro flashlight beam discovering muddy boot print.",
                    "why_it_works": "Immediate threat presence compels 90%+ completion rate."
                }
            ],
            scene_cuts=[0.0, 6.8, 12.0],
            static_scenes=[],
            visual_dynamics_data={
                "scene_cuts": [0.0, 6.8, 12.0],
                "static_scenes": [],
                "boredom_windows": [],
                "visual_velocity_score": 85,
                "visual_pace_rating": "Good Visual Pacing",
                "average_shot_length": 5.4,
                "fps": 30.0,
                "width": 1080,
                "height": 1920,
                "duration": round(s_dur, 2),
                "genre_info": {
                    "genre": "storytelling",
                    "genre_label": "Suspense & Mystery Storytelling",
                    "primary_subject": "MrBallen Mystery",
                    "is_music_edit": False
                }
            },
            vocal_data={
                "pitch_score": 93,
                "vocal_energy_rating": "Dynamic Narrative Delivery",
                "monotone_segments": [],
                "emphasis_peaks": [0.8, 6.2, 11.5, 15.2],
                "waveform": [round(0.20 + 0.55 * (0.5 + 0.5 * __import__("math").sin(i * 0.45)), 3) for i in range(80)]
            },
            safe_zone_data={
                "safe_zone_score": 92,
                "compliance_status": "Passed (Social Media Safe)",
                "face_detected": True,
                "face_centered": True,
                "top_margin_pct": 15.0,
                "bottom_margin_pct": 20.0
            },
            retention_curve_data={
                "predicted_completion_rate": 92.4,
                "platform_metrics": {
                    "is_verified": True,
                    "view_count": 1820000,
                    "like_count": 142000,
                    "comment_count": 5600,
                    "channel": "MrBallen / Dark Mystery Tales",
                    "vvs_rate": 91.5,
                    "apvp_rate": 92.4
                }
            },
            retention_timeline=[
                {"timestamp": 0.0, "type": "hook", "title": "Hook Score: 95/100 (Grade A)", "description": "High-urgency curiosity opening locks viewer focus.", "actionable_fix": "Maintain background audio tension throughout."},
                {"timestamp": 6.8, "type": "cut", "title": "Cut / Transition (6.8s)", "description": "Atmospheric shift to temperature drop.", "actionable_fix": "Add low-frequency rumble stem."}
            ]
        )
        db.add(a5)
        db.commit()
    print("Channel 5 (MrBallen Storytelling) seeded successfully!")

if __name__ == "__main__":
    seed_channels()
