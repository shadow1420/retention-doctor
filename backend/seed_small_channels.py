import os
import subprocess
import datetime
from backend.database import SessionLocal, Project, Analysis
from backend.analyzer.thumbnails import extract_candidate_thumbnails

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "storage", "uploads")
os.makedirs(UPLOADS_DIR, exist_ok=True)

def generate_voiceover(text: str, wav_path: str):
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
            f"drawtext=text='{title}':fontcolor=white:fontsize=44:x=(w-text_w)/2:y=(h-text_h)/2:shadowcolor=black@0.8:shadowx=3:shadowy=3"
        ),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-preset", "veryfast",
        "-c:a", "aac", "-b:a", "192k",
        "-movflags", "+faststart",
        mp4_path
    ]
    subprocess.run(ffmpeg_cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return dur

def seed_small_channels():
    db = SessionLocal()

    small_channels_spec = [
        {
            "id": "proj_small_001",
            "title": "My Everyday Morning Routine VLOG #3 (Stuck at 214 Views)",
            "filename": "morning_routine_vlog_stuck_214_views.mp4",
            "bg": "#334155",
            "text": "Hey guys welcome back to another video. Um today I wanted to show you my morning routine and what I eat for breakfast.",
            "wpm": 98.0,
            "cuts": [0.0],  # 0 cuts! Complete static camera
            "genre": "talking_head",
            "genre_label": "Vlog / Casual Lifestyle (Small Channel)",
            "subject": "Morning Routine Vlog",
            "score": 38,
            "grade": "F",
            "first_silence": 2.4,
            "silence_pct": 18.5,
            "vocal_energy": 34,
            "visual_velocity": 30,
            "safe_zone": 88,
            "hook_exp": "Severe Opening Latency: 2.4 seconds of dead air followed by generic 'Hey guys' greeting. 54.8% of feed viewers swiped away before hearing any value proposition.",
            "platform_metrics": {
                "view_count": 214,
                "like_count": 8,
                "comment_count": 1,
                "channel": "DailyVlogger_09 (48 Subs)",
                "is_verified": True,
                "vvs_rate": 45.2,
                "apvp_rate": 38.0
            }
        },
        {
            "id": "proj_small_002",
            "title": "Beginner Python Coding Mistakes Nobody Tells You (Stuck at 1.4K Views)",
            "filename": "python_beginner_mistakes_stuck_1400_views.mp4",
            "bg": "#0f172a",
            "text": "The biggest mistake beginners make in Python is mutable default arguments. So let me type this function out here and show you what happens when we append to an empty list.",
            "wpm": 138.0,
            "cuts": [0.0, 4.2],
            "genre": "tech_review",
            "genre_label": "Coding Tutorial (Stuck at Gate 2)",
            "subject": "Python Mistakes",
            "score": 74,
            "grade": "B",
            "first_silence": 0.2,
            "silence_pct": 14.2,
            "vocal_energy": 62,
            "visual_velocity": 48,
            "safe_zone": 55, # Code obscured behind UI buttons!
            "hook_exp": "Good Concept Stalled at Gate 2: Hook cleared the seed test, but a 3.8s silent typing gap and code snippet hidden behind the TikTok right rail caused 53% drop-off at second 5.",
            "platform_metrics": {
                "view_count": 1420,
                "like_count": 64,
                "comment_count": 7,
                "channel": "CodeWithDev (240 Subs)",
                "is_verified": True,
                "vvs_rate": 72.5,
                "apvp_rate": 46.5
            }
        },
        {
            "id": "proj_small_003",
            "title": "How I Scaled Dropshipping to $5K/Mo (Stuck at 850 Views)",
            "filename": "dropshipping_scale_stuck_850_views.mp4",
            "bg": "#1c1917",
            "text": "If you want to scale your dropshipping store to five thousand dollars a month here is the exact dashboard proof. But first let me explain what product research tool I use every single day.",
            "wpm": 142.0,
            "cuts": [0.0, 3.5],
            "genre": "business_advice",
            "genre_label": "Dropshipping Guide (Choked at 850 Views)",
            "subject": "Dropshipping $5K Scale",
            "score": 68,
            "grade": "C",
            "first_silence": 0.5,
            "silence_pct": 8.5,
            "vocal_energy": 55,
            "visual_velocity": 60,
            "safe_zone": 45, # Dashboard proof obscured by bottom audio disc!
            "hook_exp": "Social UI Collision: The revenue proof screenshot is positioned at the bottom right and completely covered by TikTok's caption drawer and audio disc. Viewers could not verify the claim.",
            "platform_metrics": {
                "view_count": 850,
                "like_count": 32,
                "comment_count": 3,
                "channel": "EcomHustle_Jordan (120 Subs)",
                "is_verified": True,
                "vvs_rate": 62.0,
                "apvp_rate": 52.0
            }
        }
    ]

    for spec in small_channels_spec:
        pid = spec["id"]
        wav_path = os.path.join(UPLOADS_DIR, f"{pid}_speech.wav")
        mp4_path = os.path.join(UPLOADS_DIR, f"{pid}_{spec['filename']}")

        if not os.path.exists(mp4_path):
            print(f"Generating video & audio for {pid} ({spec['title'][:35]})...")
            generate_voiceover(spec["text"], wav_path)
            dur = build_vertical_video(wav_path, mp4_path, spec["subject"].upper(), spec["bg"])
        else:
            dur = 12.5

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
        word_ts = [{"word": w, "start": round(i * 0.4, 2), "end": round((i + 1) * 0.4, 2)} for i, w in enumerate(words)]
        
        # Build silence intervals matching the real defects
        sil_intervals = []
        if spec.get("first_silence", 0) > 0.5:
            sil_intervals.append({"start": 0.0, "end": spec["first_silence"], "duration": spec["first_silence"]})
        if pid == "proj_small_002":
            sil_intervals.append({"start": 4.2, "end": 8.0, "duration": 3.8})

        violations = []
        if spec["safe_zone"] < 70:
            violations.append("Critical text/proof placed in bottom-right corner — obscured by TikTok/Shorts action icons.")

        if not ana:
            ana = Analysis(
                id=f"ana_{pid}",
                project_id=pid,
                transcript_text=spec["text"],
                words_per_minute=spec["wpm"],
                word_timestamps=word_ts,
                sentence_segments=[{"start": 0.0, "end": round(dur, 2), "text": spec["text"]}],
                filler_words=["um", "uh"] if pid == "proj_small_001" else [],
                silence_intervals=sil_intervals,
                total_silence_duration=sum(s["duration"] for s in sil_intervals),
                silence_percentage=spec["silence_pct"],
                hook_score=spec["score"],
                hook_grade=spec["grade"],
                hook_explanation=spec["hook_exp"],
                hook_issues=[spec["hook_exp"]],
                hook_recommendations=[
                    "Trim opening silence immediately.",
                    "Reposition text into the central safe zone corridor.",
                    "Inject B-roll insert to break up static talking head."
                ],
                alternative_hooks=[],
                scene_cuts=spec["cuts"],
                static_scenes=[{"start": 0.0, "end": round(dur, 2), "duration": round(dur, 2)}] if len(spec["cuts"]) <= 1 else [],
                visual_dynamics_data={
                    "scene_cuts": spec["cuts"],
                    "static_scenes": [{"start": 0.0, "end": round(dur, 2), "duration": round(dur, 2)}] if len(spec["cuts"]) <= 1 else [],
                    "boredom_windows": [{"start": 0.0, "end": round(dur, 2), "duration": round(dur, 2)}] if len(spec["cuts"]) <= 1 else [],
                    "visual_velocity_score": spec["visual_velocity"],
                    "visual_pace_rating": "Slow Static Visual Pacing",
                    "average_shot_length": round(dur, 1) if len(spec["cuts"]) <= 1 else 3.5,
                    "fps": 30.0,
                    "width": 1080,
                    "height": 1920,
                    "duration": round(dur, 2),
                    "genre_info": {
                        "genre": spec["genre"],
                        "genre_label": spec["genre_label"],
                        "primary_subject": spec["subject"],
                        "is_music_edit": False
                    }
                },
                vocal_data={
                    "pitch_score": spec["vocal_energy"],
                    "vocal_energy_rating": "Monotone Energy Lull" if spec["vocal_energy"] < 50 else "Moderate Delivery",
                    "monotone_segments": [{"start": 2.0, "end": 7.0, "duration": 5.0}] if spec["vocal_energy"] < 50 else [],
                    "emphasis_peaks": [1.5],
                    "waveform": [round(0.1 + 0.2 * (0.5 + 0.5 * __import__("math").sin(i * 0.2)), 3) for i in range(80)]
                },
                safe_zone_data={
                    "safe_zone_score": spec["safe_zone"],
                    "compliance_status": "Failed (UI Collision Risk)" if spec["safe_zone"] < 70 else "Passed",
                    "violations": violations,
                    "face_detected": True,
                    "face_centered": False if spec["safe_zone"] < 70 else True,
                    "top_margin_pct": 10.0,
                    "bottom_margin_pct": 25.0
                },
                retention_curve_data={
                    "predicted_completion_rate": spec["platform_metrics"]["apvp_rate"],
                    "platform_metrics": spec["platform_metrics"]
                },
                retention_timeline=[
                    {"timestamp": 0.0, "type": "hook", "title": f"Weak Hook (Score: {spec['score']}/100)", "description": spec["hook_exp"], "actionable_fix": "Cut opening 2s dead air"},
                    {"timestamp": 3.0, "type": "monotone", "title": "Monotone Voice Drop", "description": "Flat vocal frequency causes 40% scroll-away", "actionable_fix": "Add kinetic subtitle pop + background audio stem"}
                ]
            )
            db.add(ana)
            db.commit()

        # Extract thumbnails
        extract_candidate_thumbnails(mp4_path, pid, dur, spec["cuts"], {"genre": spec["genre"]})
        print(f"Small channel video {pid} generated and analyzed!")

    db.close()
    print("\n--- SMALL CHANNELS SEEDING COMPLETED ---")

if __name__ == "__main__":
    seed_small_channels()
