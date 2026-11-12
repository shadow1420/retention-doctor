# RetentionDoctor 🎬🩺
> **Stop Losing Viewers. Fix Your Videos Before You Publish.**

RetentionDoctor is an AI-powered Video Retention Analysis and Editing SaaS built specifically for YouTube Shorts, Instagram Reels, TikTok creators, podcasters, and video editors.

Unlike generic video editors, RetentionDoctor identifies **why viewers swipe away** (weak opening hooks, dead-air pauses, slow speech pacing, and visual monotony) and provides a **One-Click Auto-Fixer** that transforms your raw footage into high-retention video.

---

## ⚡ Key Features

### 1. Maximum AI Video Retention Audit
- **Second-by-Second Predicted Retention Curve:** Acoustic, linguistic, and visual friction model charting audience retention decay from 100% to completion, pinpointing the **Top 3 Critical Drop-off Moments** with click-to-seek playback.
- **0–5s & 10s Hook Score (0–100, Grade A–D):** Uses explainable retention heuristics (first word latency, curiosity gaps, pattern interrupts, and weak intro phrase detection).
- **Vocal Dynamics & Monotone Detector:** Acoustic signal RMS energy variance and pitch dynamics monitoring to flag flat monotone delivery and sudden energy crashes.
- **Visual Velocity & Pattern Interrupts:** Computes Average Shot Length (ASL) and Visual Velocity Score (0–100), flagging every boredom window $> 3.0\text{s}$ with zero visual transition.
- **Social Media UI Safe Zone Framing:** OpenCV face and composition analyzer checking vertical 9:16 video against Instagram Reels and TikTok overlay danger zones (captions, username, like/share buttons).
- **AI B-Roll & Visual Insert Prompt Generator:** Contextual Midjourney/DALL-E image prompts and stock video search terms generated for every visual boredom window based on spoken transcript context.
- **5 Viral Alternative Hooks:** Automatically generates 5 high-converting hook angles (Contrarian, Curiosity Gap, Immediate Outcome, The Warning, and The Bold Question) tailored to your video's topic.
- **Dead-Air & Silence Detection:** Millisecond-precision audio signal analysis via FFmpeg `silencedetect` mapping every pause > 0.55s.
- **Speech & Transcript Engine:** Powered by `faster-whisper` (`base` model on CPU `int8`) with word-level timestamps, Words Per Minute (WPM) pacing meter, and filler word detection (`um`, `uh`, `like`, `you know`).
- **Interactive Retention-Risk Timeline:** Color-coded markers for weak hooks (red), dead-air pauses (yellow), static shots (blue), monotone voice (purple), and UI safe-zone collisions (rose). Click any marker to immediately seek video playback.

### 2. Feature Two: One-Click Auto-Fixer ("Fix My Video")
- **Smart Silence Removal:** Losslessly cuts dead-air pauses with configurable vocal padding (default 80ms) to avoid clipping vocal tails or breaths, with zero audio/video desync.
- **Dynamic Punch-in Zoom:** Subtle 1.12x–1.15x emphasis zooms to eliminate visual monotony on long static camera angles.
- **Audio Loudness Normalization:** Automatically balances vocal loudness to the industry standard **-16 LUFS (EBU R128)** for punchy mobile audio.
- **Kinetic Subtitles:** Optional Alex Hormozi-style kinetic word-highlighted subtitles burned directly into the output.
- **Lossless 1080p Export:** Browser-compatible H.264/AAC MP4 with `+faststart` progressive streaming.
- **Before-and-After Comparison:** Shows exact seconds of dead-air eliminated and total cuts applied.

---

## 🛠️ Technology Stack

- **Frontend:** HTML5, Tailwind CSS, Lucide Icons, Vanilla Reactive Controller (zero bundle lag, instant responsive dark UI inspired by Linear, Stripe, and Vercel).
- **Backend:** Python 3.11, FastAPI, Pydantic, Uvicorn.
- **Speech Processing:** `faster-whisper` (OpenAI Whisper base model running locally on CPU in `int8` with hallucination repetition penalty).
- **Signal & Video Processing:** FFmpeg 8.1 with `libx264`, `libass`, `loudnorm`, and OpenCV (`cv2`).
- **Database:** SQLAlchemy ORM with SQLite for zero-config local development, fully compatible with PostgreSQL / Supabase in production.
- **Hosting / Cost:** **₹0 API Cost**. Runs 100% locally with zero paid third-party API dependencies.

---

## 🚀 Quickstart Guide

### 1. Prerequisites
Ensure you have Python 3.11+ and FFmpeg installed and in your system PATH:
```bash
ffmpeg -version
python --version
```

### 2. Install Dependencies
```bash
pip install fastapi uvicorn pydantic sqlalchemy faster-whisper opencv-python soundfile torch razorpay pytest
```

### 3. Run the Application
Start the FastAPI server:
```bash
uvicorn backend.app:app --host 127.0.0.1 --port 8000 --reload
```

Open your browser and navigate to:
```
http://127.0.0.1:8000
```

---

## 🧪 Running Automated Tests
Run the comprehensive end-to-end pipeline verification test suite:
```bash
python tests/test_pipeline.py
```
This tests:
1. SQLite database and table persistence
2. Synthetic video generation with known silence intervals
3. FFmpeg silence detection accuracy
4. Active speech interval calculation with padding
5. Hook score heuristics and 5 alternative hook generators
6. OpenCV visual and static scene detection
7. One-Click Auto-Fixer rendering, audio normalization, and 1080p MP4 validation

---

## 📁 Repository Structure
```
ip/
├── backend/
│   ├── app.py                 # FastAPI endpoints, background tasks, and streaming
│   ├── database.py            # SQLAlchemy models (User, Project, Analysis, Job, Export)
│   ├── auth.py                # Local dev token + Supabase Auth verification
│   ├── analyzer/              # AI Retention Audit Engines
│   │   ├── speech.py          # Faster-Whisper transcription & word timestamps
│   │   ├── silence.py         # FFmpeg dead-air signal analyzer
│   │   ├── hook.py            # Heuristic 5s/10s hook score & 5 viral hook generator
│   │   └── visual.py          # OpenCV scene cuts & static shot detection
│   ├── editor/                # One-Click Auto-Fixer Engine
│   │   ├── silence_cutter.py  # Synchronized pause trimming with speech padding
│   │   ├── zoom.py            # Dynamic punch-in zoom filter generator
│   │   ├── subtitles.py       # Kinetic ASS subtitle generator
│   │   └── exporter.py        # FFmpeg 1080p MP4 render & loudnorm normalization
│   └── storage/               # Isolated uploads, exports, and temp scratch files
├── frontend/
│   └── index.html             # High-polish Linear/Stripe dark charcoal studio SPA
├── tests/
│   └── test_pipeline.py       # Full end-to-end verification test suite
├── ARCHITECTURE.md            # Technical system architecture and data flows
├── TESTING.md                 # Testing protocols and validation results
├── ROADMAP.md                 # Product vision, Phase 2 features, and monetization
├── .env.example               # Environment variables configuration template
└── README.md                  # This file
```

---

## 🔒 Privacy & Safety Guarantee
All video analysis and rendering occurs locally inside your workspace. Video frames and audio streams are never transmitted to external servers or third-party cloud APIs.
