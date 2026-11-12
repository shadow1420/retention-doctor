# RetentionDoctor Product Roadmap

## Phase 1: MVP Core (Completed ✅)
- [x] Local AI speech transcription using `faster-whisper` (`base` model CPU `int8`).
- [x] Millisecond-precision dead-air pause detector with FFmpeg `silencedetect`.
- [x] Explainable heuristic 5s & 10s Hook Scorer with grade and specific recommendations.
- [x] 5 Viral Alternative Hook scripts generator.
- [x] OpenCV visual dynamics and prolonged static frame analyzer.
- [x] Interactive Retention-Risk Timeline with clickable video seeking.
- [x] One-Click Auto-Fixer:
  - Lossless silence removal with vocal padding (+80ms).
  - Dynamic punch-in zoom filters (Low / Medium / High).
  - Audio loudness normalization (EBU R128 -16 LUFS).
  - Browser-compatible 1080p MP4 rendering with `+faststart`.
- [x] Before-and-After analytics card (seconds saved, cuts applied).
- [x] Linear / Stripe dark charcoal UI (`#07090E`) with electric purple highlights.
- [x] End-to-end automated test suite (`tests/test_pipeline.py`).

---

## Phase 2: Creative & Auto-Fixer Upgrades (Completed ✅)
- [x] **Hormozi-Style Kinetic Subtitles with Viral Emojis:** Automatic keyword detection mapping spoken words to viral emojis (`money` -> 💰, `fire` -> 🔥, `stop` -> 🛑, `rocket` -> 🚀) burned in ASS subtitles.
- [x] **SFX Audio Stems Auto-Injector:** Procedural synthesis and mixing of whoosh transitions on punch-in cuts and pop blips on kinetic word accents.
- [x] **Vocal Dynamics & Monotone Pitch Detector:** RMS energy variance and pitch dynamics monitoring to flag flat monotone delivery.
- [x] **Visual Velocity & Pattern Interrupt Tracker:** Average Shot Length (ASL) and Visual Velocity Score (0–100), flagging every boredom window $> 3.0\text{s}$.
- [x] **AI B-Roll & Visual Insert Prompt Generator:** Contextual Midjourney/DALL-E image prompts and stock video search terms generated for every visual boredom window.
- [x] **Social Media UI Safe Zone Framing Inspector:** OpenCV face and composition analyzer checking vertical 9:16 video against Instagram Reels and TikTok overlay danger zones.

---

## Phase 3: Agency & Monetization Suite (Completed ✅)
- [x] **Executive Client-Ready Retention Audit Report:** Branded, high-contrast HTML audit report optimized for viewing in-browser and 1-click vector printing/exporting to PDF for agencies selling audits for $50–$150.
- [x] **Viral Social Publishing Suite:**
  - 5 High-CTR YouTube Shorts / Reels titles
  - 1 High-converting Instagram Reel caption with engagement hooks & question CTA
  - 15 Segmented viral hashtags (Broad, Niche, Velocity)
- [x] **Razorpay Monetization & Subscription API:**
  - Integration with Razorpay checkout (`/api/billing/create-order` and `/api/billing/verify`).
  - Creator Pro tier upgrade mechanism (₹499/mo).
  - Local sandbox simulation for instant testing.
- [x] **14/14 End-to-End Automated Pipeline Test Suite:** Deterministic verification of database, acoustic analysis, OpenCV tracking, kinetic subtitle emojis, SFX stems, social suite, PDF report, and 1080p rendering.
