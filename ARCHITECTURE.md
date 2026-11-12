# RetentionDoctor Architecture & Technical Design

## 1. System Overview

RetentionDoctor is structured into three decoupled layers:
1. **Frontend Presentation Layer:** High-performance responsive web dashboard styled with deep charcoal tones (`#07090E`), electric purple (`#8B5CF6`), and blue accents, providing a fluid dual-player studio with an interactive retention-risk timeline.
2. **FastAPI Application & Task Orchestrator:** Asynchronous REST API managing file uploads, SQLite/PostgreSQL persistence, and non-blocking background analysis and rendering pipelines.
3. **Core Video Processing Engines:**
   - **Retention Audit Subsystem:** Combines `faster-whisper` (speech-to-text with millisecond timestamps), FFmpeg `silencedetect` (audio dead-air analysis), OpenCV (scene cut and static shot detection), and an explainable heuristic hook evaluator.
   - **One-Click Auto-Fixer Subsystem:** Builds complex FFmpeg filter graphs to losslessly trim dead-air pauses, inject subtle punch-in zooms, normalize audio loudness to -16 LUFS (EBU R128), and burn kinetic subtitles into an H.264 MP4 container.

---

## 2. Retention Audit Data Flow

```
+------------------------------------------------------------------------+
| 1. Creator uploads MP4/MOV/WebM video via Drag-and-Drop               |
+------------------------------------+-----------------------------------+
                                     |
                                     v
+------------------------------------+-----------------------------------+
| 2. FastAPI stores video & enqueues Background Audit Task               |
+------------------------------------+-----------------------------------+
                                     |
         +---------------------------+---------------------------+---------------------------+
         |                           |                           |                           |
         v                           v                           v                           v
+------------------+       +-------------------+       +-----------------+       +-------------------+
| faster-whisper   |       | FFmpeg            |       | OpenCV (cv2)    |       | Audio RMS & Pitch |
| - Base model     |       | silencedetect     |       | - Color Hist/Diff|       | - Vocal dynamics  |
| - Word timestamps|       | - Threshold: -32dB|       | - Pattern cuts  |       | - Monotone alert  |
| - WPM pacing     |       | - Min pause: 0.55s|       | - 9:16 Safe Zone|       | - Emphasis peaks  |
| - Filler words   |       |                   |       | - AI B-roll     |       |                   |
+--------+---------+       +---------+---------+       +--------+--------+       +---------+---------+
         |                           |                          |                          |
         +---------------------------+--------------------------+--------------------------+
                                     |
                                     v
+------------------------------------+-----------------------------------+
| 3. Multi-Dimensional Retention Engines                                 |
|    - 0-5s / 10s Hook Evaluator & 5 Viral Hooks Generator               |
|    - Second-by-Second Predicted Retention Risk Curve                   |
|    - Top 3 Critical Drop-Off Moments (Acoustic + Visual Friction)      |
+------------------------------------+-----------------------------------+
                                     |
                                     v
+------------------------------------+-----------------------------------+
| 4. Consolidated Retention-Risk Timeline & Interactive Studio           |
|    - Chronological list of events with exact video timestamps          |
|    - Interactive seeking in frontend video player                      |
+------------------------------------------------------------------------+
```

---

## 3. One-Click Auto-Fixer Data Flow

```
+------------------------------------------------------------------------+
| 1. User configures Auto-Fixer (Silence Removal, Zoom, Normalization)  |
+------------------------------------+-----------------------------------+
                                     |
                                     v
+------------------------------------+-----------------------------------+
| 2. Silence Cutter: Calculate Keep Intervals                            |
|    - Subtract silence pauses (>0.55s)                                  |
|    - Add +80ms vocal padding around speech boundaries                  |
|    - Prevent AV desync via trim + concat filter graph                  |
+------------------------------------+-----------------------------------+
                                     |
                                     v
+------------------------------------+-----------------------------------+
| 3. Dynamic Zoom & Punch-in Generation                                  |
|    - Crop-scale expressions on emphasis or prolonged static moments    |
+------------------------------------+-----------------------------------+
                                     |
                                     v
+------------------------------------+-----------------------------------+
| 4. Audio Loudness Normalization (EBU R128)                             |
|    - Integrated loudness target: -16 LUFS                              |
|    - True peak ceiling: -1.5 dBFS                                      |
+------------------------------------+-----------------------------------+
                                     |
                                     v
+------------------------------------+-----------------------------------+
| 5. FFmpeg High-Performance Render                                      |
|    - Codec: libx264 (crf 21, preset veryfast)                          |
|    - Audio: aac (192kbps)                                              |
|    - Flags: -pix_fmt yuv420p, -movflags +faststart                     |
+------------------------------------+-----------------------------------+
                                     |
                                     v
+------------------------------------+-----------------------------------+
| 6. Comparison & Instant Progressive Streaming                          |
|    - Before/After duration saved metrics                               |
|    - HTTP Range Request streaming support                              |
+------------------------------------------------------------------------+
```

---

## 4. Key Architectural Safeguards & Lessons Learned

1. **Deadlock Prevention on FFmpeg Subprocesses:** Always pipe stderr with `-nostats -v error` and use `stdout=subprocess.DEVNULL` to avoid Windows pipe buffer deadlocks.
2. **Even Pixel Dimensions for H.264:** Libx264 rejects odd width or height dimensions. All video filters enforce `trunc(iw/2)*2` and `trunc(ih/2)*2` to ensure universal web player compatibility.
3. **No Double-Seek Black Screens:** Avoid pairing `-ss` fast seek with identical filter `trim=start=X`. Use clean filter-complex trims with `setpts=PTS-STARTPTS`.
4. **HTML5 Video HEAD Request Support:** Chrome, Safari, and Edge send `HEAD` requests to inspect `Accept-Ranges` and `Content-Length`. API streaming routes explicitly support both `GET` and `HEAD` methods to prevent `405 Method Not Allowed` black screens.
5. **Whisper Phonk/Beat Repetition Suppression:** Transcribing speech over loud music can cause repetition loops. We set `condition_on_previous_text=False`, `repetition_penalty=1.2`, and `no_repeat_ngram_size=3` with `faster-whisper` base model on CPU `int8`.
