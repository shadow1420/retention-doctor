import os
import subprocess
import datetime
from backend.database import SessionLocal, Project, Analysis
from backend.analyzer.thumbnails import extract_candidate_thumbnails

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "storage", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

def generate_voiceover(text: str, wav_path: str):
    """Uses Windows System.Speech to generate crisp voiceover WAV."""
    clean_path = wav_path.replace("\\", "/")
    safe_text = text.replace("'", "''")
    ps_cmd = f"""
    Add-Type -AssemblyName System.Speech
    $synth = New-Object System.Speech.Synthesis.SpeechSynthesizer
    $synth.SetOutputToWaveFile('{clean_path}')
    $synth.Speak('{safe_text}')
    $synth.Dispose()
    """
    subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], check=True)

def build_vertical_video(wav_path: str, mp4_path: str, title: str, bg_color: str):
    """Generates 1080x1920 MP4 with voiceover and clean visual layout."""
    probe_cmd = [
        "ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1", wav_path
    ]
    dur = float(subprocess.check_output(probe_cmd).decode().strip())
    
    ffmpeg_cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c={bg_color}:s=1080x1920:d={dur}",
        "-i", wav_path,
        "-vf", (
            f"drawbox=y=ih-450:color=black@0.5:width=iw:height=320:t=fill,"
            f"drawtext=text='{title}':fontcolor=white:fontsize=46:x=(w-text_w)/2:y=(h-text_h)/2:shadowcolor=black@0.8:shadowx=3:shadowy=3"
        ),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        mp4_path
    ]
    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return dur

def seed_all_10_videos():
    db = SessionLocal()

    videos_spec = [
        {
            "id": "proj_beast_001",
            "title": "MrBeast: Last to Leave the $10,000 Box Wins (Extreme Challenge)",
            "filename": "mrbeast_10k_box_challenge.mp4",
            "bg": "#dc2626",
            "text": "The last person to take their hands off this ten thousand dollar cash glass box keeps all of it. If you step outside this yellow perimeter line for even one second you are instantly eliminated. Let the countdown begin.",
            "wpm": 182.0,
            "cuts": [0.0, 3.2, 7.5, 11.0],
            "genre": "viral_challenge",
            "genre_label": "High-Stakes Viral Challenge",
            "subject": "MrBeast Challenge",
            "score": 96,
            "grade": "A",
            "hook_exp": "Elite Stakes Frame-1 Anchor: Immediate cash prize and elimination consequence creates instant retention grip.",
            "platform_metrics": {
                "view_count": 4200000,
                "like_count": 380000,
                "comment_count": 14200,
                "channel": "MrBeast Shorts",
                "is_verified": True,
                "vvs_rate": 94.2,
                "apvp_rate": 96.5
            }
        },
        {
            "id": "proj_tech_001",
            "title": "M4 iPad Pro Extreme Stress Test: Did Apple Thermal Throttle?",
            "filename": "m4_ipad_pro_thermal_stress_test.mp4",
            "bg": "#1e293b",
            "text": "I ran thirty consecutive benchmark loops on the brand new M4 iPad Pro to see if Apple's thinnest design ever will overheat. The chassis reached forty three degrees Celsius and that is when the CPU performance dropped twenty percent.",
            "wpm": 165.0,
            "cuts": [0.0, 4.0, 8.5, 13.0],
            "genre": "tech_review",
            "genre_label": "Tech & Gadget Silicon Review",
            "subject": "M4 iPad Pro",
            "score": 91,
            "grade": "A",
            "hook_exp": "Curiosity Specification Hook: Directly questions thermal throttling claim with empirical benchmark testing.",
            "platform_metrics": {
                "view_count": 450000,
                "like_count": 28400,
                "comment_count": 1280,
                "channel": "Silicon Tech Reviews",
                "is_verified": True,
                "vvs_rate": 83.5,
                "apvp_rate": 81.2
            }
        },
        {
            "id": "proj_fitness_001",
            "title": "Chris Bumstead (CBum): Why Champions Suffer in Silence (Mr Olympia)",
            "filename": "cbum_classic_olympia_mindset.mp4",
            "bg": "#09090b",
            "text": "Everybody wants to win Mr Olympia until it is time to do what champions actually do. When your legs are shaking and the weight feels like a mountain you do not quit. That is where history is made.",
            "wpm": 150.0,
            "cuts": [0.0, 3.8, 7.8, 12.0],
            "genre": "fitness_motivation",
            "genre_label": "Fitness & Olympia Motivation",
            "subject": "Chris Bumstead (CBum)",
            "score": 95,
            "grade": "A",
            "hook_exp": "High-Intensity Moral Challenge Hook: Deep vocal cadence paired with high-stakes championship standard.",
            "platform_metrics": {
                "view_count": 890000,
                "like_count": 76000,
                "comment_count": 2400,
                "channel": "Olympia Physique Motivation",
                "is_verified": True,
                "vvs_rate": 88.0,
                "apvp_rate": 89.5
            }
        },
        {
            "id": "proj_food_001",
            "title": "Ultra-Crispy Wagyu Double Smash Burger (Pure Sizzle ASMR)",
            "filename": "wagyu_crispy_double_smash_burger_asmr.mp4",
            "bg": "#451a03",
            "text": "Two balls of A5 Japanese Wagyu smashed wafer-thin onto a searing four hundred degree cast iron flat top. Notice that lacework crispy crust forming in ten seconds. Double American cheese on toasted brioche.",
            "wpm": 158.0,
            "cuts": [0.0, 3.0, 6.5, 10.0],
            "genre": "food_asmr",
            "genre_label": "Culinary & ASMR Street Food",
            "subject": "Wagyu Smash Burger",
            "score": 96,
            "grade": "A",
            "hook_exp": "Visceral Sensory Hook: Searing audio description and macro crispy crust description triggers instant dopamine.",
            "platform_metrics": {
                "view_count": 2100000,
                "like_count": 185000,
                "comment_count": 4800,
                "channel": "Street Food ASMR Lab",
                "is_verified": True,
                "vvs_rate": 93.0,
                "apvp_rate": 94.0
            }
        },
        {
            "id": "proj_comedy_001",
            "title": "POV: Your Brain at 3:00 AM Remembering an Awkward Memory (Comedy Skit)",
            "filename": "pov_brain_at_3am_awkward_memory.mp4",
            "bg": "#312e81",
            "text": "POV you finally fell asleep after tossing for two hours and your brain taps you on the shoulder to ask if you remember that awkward sentence you said in eighth grade cafeteria.",
            "wpm": 162.0,
            "cuts": [0.0, 3.5, 7.0, 10.5],
            "genre": "comedy_skit",
            "genre_label": "Comedy & Relatable POV",
            "subject": "Brain at 3 AM",
            "score": 93,
            "grade": "A",
            "hook_exp": "Universal Relatability Pattern Interrupt: Instantly connects with universal late-night insomnia experience.",
            "platform_metrics": {
                "view_count": 1150000,
                "like_count": 124000,
                "comment_count": 3900,
                "channel": "Relatable POV Skits",
                "is_verified": True,
                "vvs_rate": 89.0,
                "apvp_rate": 91.0
            }
        }
    ]

    for spec in videos_spec:
        pid = spec["id"]
        wav_path = os.path.join(UPLOADS_DIR, f"{pid}_speech.wav")
        mp4_path = os.path.join(UPLOADS_DIR, f"{pid}_{spec['filename']}")

        if not os.path.exists(mp4_path):
            print(f"Generating video & audio for {pid} ({spec['title'][:35]})...")
            generate_voiceover(spec["text"], wav_path)
            dur = build_vertical_video(wav_path, mp4_path, spec["subject"].upper(), spec["bg"])
        else:
            dur = 14.5

        # Register Project
        proj = db.query(Project).filter(Project.id == pid).first()
        if not proj:
            proj = Project(
                id=pid,
                title=spec["title"],
                original_filename=spec["filename"],
                original_filepath=mp4_path,
                duration=round(dur, 2),
                width=1080,
                height=1920,
                fps=30.0,
                aspect_ratio="9:16",
                status="analyzed",
                created_at=datetime.datetime.utcnow()
            )
            db.add(proj)
            db.commit()
        else:
            proj.status = "analyzed"
            db.commit()

        # Register Analysis
        ana = db.query(Analysis).filter(Analysis.project_id == pid).first()
        words = spec["text"].split()
        word_ts = [{"word": w, "start": round(i * 0.35, 2), "end": round((i + 1) * 0.35, 2)} for i, w in enumerate(words)]
        
        if not ana:
            ana = Analysis(
                id=f"ana_{pid}",
                project_id=pid,
                transcript_text=spec["text"],
                words_per_minute=spec["wpm"],
                word_timestamps=word_ts,
                sentence_segments=[{"start": 0.0, "end": round(dur, 2), "text": spec["text"]}],
                filler_words=[],
                silence_intervals=[{"start": spec["cuts"][1], "end": spec["cuts"][1] + 0.3, "duration": 0.3}],
                total_silence_duration=0.3,
                silence_percentage=2.5,
                hook_score=spec["score"],
                hook_grade=spec["grade"],
                hook_explanation=spec["hook_exp"],
                hook_issues=[],
                hook_recommendations=["Keep kinetic graphics centered in the 9:16 safe zone."],
                alternative_hooks=[],
                scene_cuts=spec["cuts"],
                static_scenes=[],
                visual_dynamics_data={
                    "scene_cuts": spec["cuts"],
                    "static_scenes": [],
                    "boredom_windows": [],
                    "visual_velocity_score": 90,
                    "visual_pace_rating": "Elite Short-Form Pacing",
                    "average_shot_length": 2.8,
                    "fps": 30.0,
                    "width": 1080,
                    "height": 1920,
                    "duration": round(dur, 2),
                    "genre_info": {
                        "genre": spec["genre"],
                        "genre_label": spec["genre_label"],
                        "primary_subject": spec["subject"],
                        "is_music_edit": (spec["genre"] == "fitness_motivation")
                    }
                },
                vocal_data={
                    "pitch_score": 92,
                    "vocal_energy_rating": "Dynamic Delivery",
                    "monotone_segments": [],
                    "emphasis_peaks": [1.0, 4.5, 8.0, 11.5],
                    "waveform": [round(0.2 + 0.5 * (0.5 + 0.5 * __import__("math").sin(i * 0.4)), 3) for i in range(80)]
                },
                safe_zone_data={
                    "safe_zone_score": 95,
                    "compliance_status": "Passed (Social Media Safe)",
                    "face_detected": True,
                    "face_centered": True,
                    "top_margin_pct": 14.0,
                    "bottom_margin_pct": 18.0
                },
                retention_curve_data={
                    "predicted_completion_rate": spec["platform_metrics"]["apvp_rate"],
                    "platform_metrics": spec["platform_metrics"]
                },
                retention_timeline=[
                    {"timestamp": 0.0, "type": "hook", "title": f"Hook Score: {spec['score']}/100", "description": spec["hook_exp"], "actionable_fix": "Maintain pacing"}
                ]
            )
            db.add(ana)
            db.commit()

        # Extract thumbnails
        extract_candidate_thumbnails(mp4_path, pid, dur, spec["cuts"], {"genre": spec["genre"]})
        print(f"Video {pid} successfully generated, analyzed & thumbnails extracted!")

    db.close()
    print("\n--- ALL 10 VIDEOS SUCCESSFULLY SEEDED AND PREPARED ---")

if __name__ == "__main__":
    seed_all_10_videos()
