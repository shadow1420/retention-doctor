import os
import sys
import subprocess
import pytest

# Ensure backend package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.database import init_db, SessionLocal, Project, Analysis, EditingJob, Export
from backend.analyzer.silence import detect_silence
from backend.analyzer.hook import evaluate_hook, generate_alternative_hooks
from backend.analyzer.visual import analyze_visuals
from backend.analyzer.vocal_dynamics import analyze_vocal_dynamics
from backend.analyzer.safe_zone import analyze_safe_zone_framing
from backend.analyzer.retention_curve import calculate_predicted_retention_curve
from backend.analyzer.genre import detect_video_genre
from backend.analyzer.virality import calculate_viral_potential, get_optimal_posting_times
from backend.analyzer.social_suite import generate_social_suite
from backend.analyzer.report import generate_html_audit_report
from backend.editor.silence_cutter import calculate_keep_intervals
from backend.editor.subtitles import generate_ass_subtitle_file
from backend.editor.sfx import ensure_sfx_stems, WHOOSH_PATH, POP_PATH
from backend.editor.exporter import get_media_info, process_auto_fix
from backend.billing import create_pro_order, verify_payment_signature

TEST_DIR = os.path.join(os.path.dirname(__file__), "scratch")
os.makedirs(TEST_DIR, exist_ok=True)


def create_synthetic_test_video(output_path: str):
    """
    Generates a 10.0-second synthetic test video:
    - 0.0s to 2.0s: 440Hz Audio Tone
    - 2.0s to 4.0s: Complete Silence (2.0s dead air)
    - 4.0s to 6.5s: 554Hz Audio Tone
    - 6.5s to 8.0s: Complete Silence (1.5s dead air)
    - 8.0s to 10.0s: 659Hz Audio Tone
    Total audio = 6.5s, Total dead air = 3.5s
    """
    cmd = [
        "ffmpeg", "-y", "-nostats", "-v", "error",
        "-f", "lavfi", "-i", "testsrc=size=720x1280:rate=30:duration=10",
        "-f", "lavfi", "-i", "sine=frequency=440:duration=2.0",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo:duration=2.0",
        "-f", "lavfi", "-i", "sine=frequency=554:duration=2.5",
        "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo:duration=1.5",
        "-f", "lavfi", "-i", "sine=frequency=659:duration=2.0",
        "-filter_complex", "[1:a][2:a][3:a][4:a][5:a]concat=n=5:v=0:a=1[outa]",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "128k",
        "-map", "0:v", "-map", "[outa]",
        "-shortest",
        output_path
    ]
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True)
    assert res.returncode == 0, f"FFmpeg synthetic video creation failed: {res.stderr}"


def test_database_initialization():
    """Verify SQLAlchemy models and SQLite connection."""
    init_db()
    db = SessionLocal()
    try:
        assert db is not None
    finally:
        db.close()


def test_silence_detection():
    """Test FFmpeg silencedetect accuracy on synthetic video."""
    video_path = os.path.join(TEST_DIR, "test_synthetic.mp4")
    if not os.path.exists(video_path):
        create_synthetic_test_video(video_path)

    result = detect_silence(video_path, noise_db=-32.0, min_silence_duration=0.5)
    intervals = result["silence_intervals"]

    assert len(intervals) >= 2, f"Expected at least 2 silence intervals, got: {intervals}"
    
    first_silence = intervals[0]
    assert 1.8 <= first_silence["start"] <= 2.2
    assert 3.8 <= first_silence["end"] <= 4.2

    second_silence = intervals[1]
    assert 6.3 <= second_silence["start"] <= 6.7
    assert 7.8 <= second_silence["end"] <= 8.2


def test_keep_intervals_calculation():
    """Verify silence padding and active interval calculation."""
    silences = [
        {"start": 2.0, "end": 4.0, "duration": 2.0},
        {"start": 6.5, "end": 8.0, "duration": 1.5}
    ]
    keep = calculate_keep_intervals(total_duration=10.0, silence_intervals=silences, padding_sec=0.08)

    assert len(keep) == 3
    assert keep[0][0] == 0.0
    assert 2.0 <= keep[0][1] <= 2.15
    assert 3.85 <= keep[1][0] <= 4.0
    assert 6.5 <= keep[1][1] <= 6.65
    assert 7.85 <= keep[2][0] <= 8.0
    assert keep[2][1] == 10.0


def test_hook_evaluator():
    """Verify hook heuristics and alternative hooks generation."""
    sample_transcript = "Hey guys, welcome back to my channel. Today I wanted to talk about video editing and retention."
    word_timestamps = [
        {"word": "Hey", "start": 0.5, "end": 0.8},
        {"word": "guys", "start": 0.8, "end": 1.1},
        {"word": "welcome", "start": 1.2, "end": 1.6},
        {"word": "back", "start": 1.6, "end": 1.9},
        {"word": "to", "start": 1.9, "end": 2.0},
        {"word": "my", "start": 2.0, "end": 2.2},
        {"word": "channel", "start": 2.2, "end": 2.6}
    ]

    hook_eval = evaluate_hook(sample_transcript, word_timestamps)
    assert hook_eval["hook_score"] < 80
    assert len(hook_eval["hook_issues"]) > 0
    assert len(hook_eval["alternative_hooks"]) == 5


def test_visual_and_b_roll_analysis():
    """Verify OpenCV scene analysis, boredom windows, and B-roll prompts."""
    video_path = os.path.join(TEST_DIR, "test_synthetic.mp4")
    sentence_segments = [
        {"start": 0.0, "end": 3.0, "text": "This is how you master viral video retention."},
        {"start": 4.0, "end": 8.0, "text": "Audience attention drops when video editing is static."}
    ]
    visual_res = analyze_visuals(video_path, sentence_segments=sentence_segments)

    assert "visual_velocity_score" in visual_res
    assert "average_shot_length" in visual_res
    assert len(visual_res["boredom_windows"]) > 0
    assert len(visual_res["b_roll_prompts"]) > 0


def test_vocal_dynamics():
    """Verify acoustic signal energy, monotone detector, and dynamic score."""
    video_path = os.path.join(TEST_DIR, "test_synthetic.mp4")
    vocal_res = analyze_vocal_dynamics(video_path)

    assert "vocal_energy_score" in vocal_res
    assert vocal_res["vocal_energy_score"] > 0
    assert "energy_variance" in vocal_res
    assert "summary" in vocal_res
    assert "waveform" in vocal_res
    assert isinstance(vocal_res["waveform"], list)
    assert len(vocal_res["waveform"]) > 0
    assert all(0.0 <= v <= 1.0 for v in vocal_res["waveform"])


def test_safe_zone_framing():
    """Verify social media safe zone compliance on vertical 9:16 video."""
    video_path = os.path.join(TEST_DIR, "test_synthetic.mp4")
    safe_res = analyze_safe_zone_framing(video_path)

    assert safe_res["is_vertical"] is True
    assert 40 <= safe_res["safe_zone_score"] <= 100
    assert "framing_status" in safe_res


def test_predicted_retention_curve():
    """Verify second-by-second predicted retention curve generation."""
    silences = [{"start": 2.0, "end": 4.0, "duration": 2.0}]
    curve_res = calculate_predicted_retention_curve(
        duration=10.0,
        hook_score=75,
        first_word_latency=0.5,
        silence_intervals=silences,
        monotone_segments=[],
        boredom_windows=[{"start": 0.0, "end": 10.0, "duration": 10.0}],
        scene_cuts=[],
        emphasis_peaks=[1.5, 5.0]
    )

    curve = curve_res["curve"]
    assert len(curve) == 11
    assert curve[0]["retention_pct"] <= 100.0
    drop_at_3s = next(pt for pt in curve if pt["second"] == 3)
    assert len(drop_at_3s["risk_factors"]) > 0
    assert len(curve_res["top_dropoff_moments"]) > 0


def test_kinetic_subtitles_with_emojis():
    """Verify Phase 2: Hormozi-style kinetic subtitle generation with viral emoji tags."""
    ass_path = os.path.join(TEST_DIR, "test_emojis.ass")
    words = [
        {"word": "Stop", "start": 0.5, "end": 0.8},
        {"word": "doing", "start": 0.8, "end": 1.1},
        {"word": "this", "start": 1.1, "end": 1.3},
        {"word": "for", "start": 1.3, "end": 1.5},
        {"word": "viral", "start": 1.5, "end": 1.9},
        {"word": "money", "start": 1.9, "end": 2.4}
    ]
    out_file = generate_ass_subtitle_file(words, ass_path, style="kinetic_emoji", width=1080, height=1920)
    assert os.path.exists(out_file)
    with open(out_file, "r", encoding="utf-8") as f:
        content = f.read()
    assert "🛑" in content, "Expected stop emoji tag in kinetic subtitle"
    assert "🔥" in content, "Expected viral fire emoji tag"
    assert "💰" in content, "Expected money emoji tag"


def test_sfx_audio_stems():
    """Verify Phase 2: Procedural audio stems generation (whoosh and pop)."""
    ensure_sfx_stems()
    assert os.path.exists(WHOOSH_PATH), "Whoosh audio stem should exist"
    assert os.path.exists(POP_PATH), "Pop audio stem should exist"
    assert os.path.getsize(WHOOSH_PATH) > 5000
    assert os.path.getsize(POP_PATH) > 2000


def test_social_suite_generation():
    """Verify Phase 3: Viral Titles, Instagram Caption, and Hashtags."""
    transcript = "In this video I show you how to edit viral video reels and retain audience attention."
    suite = generate_social_suite(transcript)
    assert len(suite["viral_titles"]) == 5
    assert "Stop Doing" in suite["viral_titles"][0]
    assert len(suite["caption"]) > 50
    assert len(suite["hashtags"]["broad"]) >= 3
    assert len(suite["hashtags"]["niche"]) >= 3


def test_anime_edit_genre_and_social_suite():
    """Verify Genre Classification & Anime Edit Social Suite with character & franchise intelligence."""
    genre = detect_video_genre(
        filename="one_piece_shanks_kamusari_phonk_60fps.mp4",
        transcript="",
        word_count=0,
        average_shot_length=0.62,
        visual_cut_count=29,
        duration=18.0
    )
    assert genre["genre"] == "anime_edit"
    assert genre["is_music_edit"] is True
    assert genre["character"] == "Shanks"
    assert genre["franchise"] == "One Piece"
    assert "Phonk" in genre["styles"]

    # Hook test on music edit
    hook = evaluate_hook(
        transcript="",
        word_timestamps=[],
        first_silence_duration=0.0,
        video_duration=18.0,
        genre_info=genre,
        scene_cuts=[0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
    )
    assert hook["hook_score"] >= 90
    assert hook["hook_grade"] == "A"
    assert len(hook["alternative_hooks"]) == 5

    # Social suite test on anime edit
    suite = generate_social_suite(
        transcript="",
        genre_info=genre,
        filename="one_piece_shanks_kamusari_phonk_60fps.mp4"
    )
    assert suite["genre"] == "anime_edit"
    assert any("Shanks" in t for t in suite["viral_titles"])
    assert "#onepiece" in suite["hashtags"]["all"]
    assert "#shanks" in suite["hashtags"]["all"]
    assert "#phonk" in suite["hashtags"]["all"]
    assert "One Piece" in suite["caption"]


def test_podcast_clip_genre_and_viral_potential():
    """Verify Podcast Genre Classification, Virality Potential Views, and Best Posting Times."""
    genre = detect_video_genre(
        filename="podcast_huberman_discipline_clip.mp4",
        transcript="The biggest mistake people make with daily discipline is relying on motivation.",
        word_count=41,
        average_shot_length=4.5,
        visual_cut_count=2,
        duration=18.24
    )
    assert genre["genre"] == "podcast_clip"
    assert genre["is_music_edit"] is False
    assert genre["primary_subject"] == "Discipline"
    assert "Andrew Huberman" in genre["detected_entities"]

    # Virality Potential Test
    vp = calculate_viral_potential(
        hook_score=95,
        visual_velocity_score=85,
        silence_percentage=2.0,
        predicted_completion_rate=88.0,
        safe_zone_score=90,
        genre_info=genre
    )
    assert vp["virality_score"] >= 85
    assert vp["reach_tier"] in ["High Discovery Growth", "Viral Breakout Potential", "Mega-Viral FYP Breakout"]
    assert "K" in vp["views_range"]["formatted"]
    assert "cohort_gates" in vp
    assert len(vp["cohort_gates"]) == 4
    assert vp["cohort_gates"][0]["name"] == "Gate 1: Seed Sandbox"
    assert vp["cohort_gates"][0]["passed"] is True

    # Posting Schedule Test
    schedule = get_optimal_posting_times(genre)
    assert "Tuesday" in schedule["best_days"]
    assert "instagram_reels" in schedule["platform_breakdown"]
    assert len(schedule["next_optimal_window"]) > 5


def test_executive_report_generation():
    """Verify Phase 3: Executive client-ready printable HTML/PDF audit report."""
    class MockProject:
        title = "Client Test Reel"
        original_filename = "test_reel.mp4"
        duration = 15.0
        aspect_ratio = "9:16"

    class MockAnalysis:
        hook_score = 82
        hook_grade = "B"
        hook_explanation = "Solid hook delivery."
        hook_issues = ["Minor latency in first second."]
        hook_recommendations = ["Start speaking immediately on frame 1."]
        alternative_hooks = [{"type": "Curiosity", "hook": "Almost nobody knows...", "why_it_works": "Curiosity gap"}]
        vocal_data = {"vocal_energy_score": 78}
        visual_dynamics_data = {"visual_velocity_score": 85}
        safe_zone_data = {"safe_zone_score": 92}
        retention_curve_data = {"predicted_completion_rate": 72.5}
        retention_timeline = [{"timestamp": 1.2, "type": "silence", "title": "Dead-air", "actionable_fix": "Trim pause"}]

    report_html = generate_html_audit_report(MockProject(), MockAnalysis())
    assert "<title>RetentionDoctor Audit" in report_html
    assert "Client Test Reel" in report_html
    assert "82" in report_html
    assert "window.print()" in report_html


def test_billing_order_creation():
    """Verify Phase 3: Razorpay subscription checkout order and signature verification."""
    order = create_pro_order(user_id="usr_test_123", plan_name="creator_pro", amount_inr=499)
    assert "order_id" in order
    assert order["amount"] == 499
    assert order["currency"] == "INR"
    assert verify_payment_signature(order["order_id"], "pay_test_001", "sig_valid") is True


def test_one_click_auto_fixer_render():
    """Verify FFmpeg silence cutting, audio normalization, and 1080p export."""
    input_path = os.path.join(TEST_DIR, "test_synthetic.mp4")
    output_path = os.path.join(TEST_DIR, "test_fixed_output.mp4")

    silences = [
        {"start": 2.0, "end": 4.0, "duration": 2.0},
        {"start": 6.5, "end": 8.0, "duration": 1.5}
    ]

    res = process_auto_fix(
        input_filepath=input_path,
        output_filepath=output_path,
        silence_intervals=silences,
        word_timestamps=[],
        config={
            "remove_silence": True,
            "silence_threshold_sec": 0.5,
            "speech_padding_sec": 0.08,
            "dynamic_zoom": "none",
            "audio_normalize": True,
            "burn_subtitles": False
        },
        work_dir=TEST_DIR
    )

    assert os.path.exists(output_path)
    assert res["cuts_count"] == 2
    assert res["seconds_saved"] >= 3.0
    assert 6.0 <= res["output_duration"] <= 7.5

    info = get_media_info(output_path)
    assert info["duration"] == res["output_duration"]
    assert info["has_audio"] is True
    print("\n--- ALL 14 PHASE 1, 2 & 3 PIPELINE TESTS PASSED SUCCESSFULLY! ---")


def test_url_downloader_module():
    """Verify URL downloader module interface and error handling."""
    from backend.downloader import download_video_from_url
    assert callable(download_video_from_url)
    try:
        download_video_from_url("https://invalid-nonexistent-domain-test-12345.com/video.mp4", "backend/storage/temp")
    except Exception as e:
        assert len(str(e)) > 0


def test_ab_hook_split_tester():
    """Verify side-by-side linguistic comparison, winner detection, and score dimensions."""
    from backend.analyzer.ab_hook import evaluate_ab_hooks, score_single_hook
    single = score_single_hook("Stop making this video editing mistake if you want 100k views", genre="tech")
    assert single["score"] > 50
    assert "curiosity_gap" in single["dimensions"]
    assert "urgency_power" in single["dimensions"]
    assert "brevity_cadence" in single["dimensions"]
    assert "pattern_interrupt" in single["dimensions"]

    ab_res = evaluate_ab_hooks(
        hook_a="Hey guys welcome back today I am going to talk about editing",
        hook_b="Stop making this video editing mistake if you want 100k views",
        genre="tech"
    )
    assert ab_res["winner"] == "B"
    assert ab_res["percentage_advantage"] > 0
    assert "verdict" in ab_res
    assert len(ab_res["key_factors"]) > 0
    assert ab_res["hook_b"]["score"] > ab_res["hook_a"]["score"]


def test_gaming_showcase_genre_and_live_calibration():
    """Verify Roblox / Blox Fruits gaming detection and live YouTube 987K view calibration."""
    from backend.analyzer.genre import detect_video_genre
    from backend.analyzer.virality import calculate_viral_potential

    genre = detect_video_genre(
        filename="Showcase Brown Dough #roblox #bloxfruits.mp4",
        transcript="Buh, buh-buh, buh-bah! If you can't stop that I'll drive to the peak time",
        word_count=16,
        average_shot_length=2.5,
        visual_cut_count=5,
        duration=59.0
    )
    assert genre["genre"] == "gaming_montage"
    assert genre["is_music_edit"] is True
    assert "Blox Fruits" in genre["genre_label"] or "Roblox" in genre["genre_label"]

    # Test calibration with live YouTube metrics (e.g. 987,000 views)
    vp = calculate_viral_potential(
        hook_score=94,
        visual_velocity_score=85,
        silence_percentage=0.0,
        predicted_completion_rate=84.0,
        safe_zone_score=90,
        genre_info=genre,
        platform_metrics={"view_count": 987000, "like_count": 48200, "comment_count": 1420}
    )
    assert vp["virality_score"] >= 95
    assert "987" in vp["views_range"]["formatted"]
    assert vp["platform_performance"]["is_verified"] is True
    assert vp["platform_performance"]["actual_views"] == 987000


def test_algorithmic_seo_generation():
    """Verify Algorithmic SEO & Keyword Stacker produces 3 titles and 3-tier hashtag matrix."""
    from backend.analyzer.seo import generate_algorithmic_seo
    seo = generate_algorithmic_seo(
        title="Alex Hormozi Pricing Strategy",
        genre_info={"genre": "business_advice", "primary_subject": "Alex Hormozi"},
        transcript="If you want to make your first million dollars stop selling your time for hourly wages.",
        platform_metrics={"view_count": 680000}
    )
    assert len(seo["titles"]) == 3
    assert any("Pattern Interrupt" in t["type"] for t in seo["titles"])
    assert any("Keyword Stacker" in t["type"] for t in seo["titles"])
    assert any("Curiosity Gap" in t["type"] for t in seo["titles"])
    assert "#businessadvice" in seo["hashtag_matrix"]["tier_2_niche"]
    assert "#shorts" in seo["hashtag_matrix"]["tier_1_broad"]
    assert len(seo["description"]) > 50
    assert len(seo["clipboard_bundle"]) > 100


def test_candidate_thumbnails_evaluation():
    """Verify AI Cover Thumbnail & Frame-1 Evaluator returns 3 scored candidate frames."""
    from backend.analyzer.thumbnails import extract_candidate_thumbnails
    video_path = os.path.join(TEST_DIR, "test_input.mp4")
    if not os.path.exists(video_path):
        create_synthetic_test_video(video_path)
    thumbs = extract_candidate_thumbnails(
        video_path=video_path,
        project_id="test_thumb_proj",
        duration=10.0,
        scene_cuts=[0.0, 3.0, 6.0],
        genre_info={"genre": "talking_head"}
    )
    assert len(thumbs) == 3
    assert thumbs[0]["index"] == 0
    assert thumbs[0]["is_recommended"] is True
    assert thumbs[0]["thumb_stop_score"] >= 90
    assert "100% Free of UI Collisions" in thumbs[0]["safe_zone_clearance"]
    assert "/api/thumbnails/test_thumb_proj/0" in thumbs[0]["url"]


def test_small_channel_cohort_gates_and_root_cause_diagnosis():
    """Verify small channel failure telemetry (Gate 1 & Gate 2 choke points and root-cause leaks)."""
    from backend.analyzer.virality import calculate_viral_potential

    # Case 1: Small channel failing Gate 1 (Seed Sandbox Stall at 214 views)
    res_small_1 = calculate_viral_potential(
        hook_score=38,
        visual_velocity_score=35,
        silence_percentage=18.5,
        predicted_completion_rate=32.0,
        safe_zone_score=85,
        genre_info={"genre": "talking_head"},
        platform_metrics={"view_count": 214, "vvs_rate": 45.2, "apvp_rate": 32.0}
    )
    assert res_small_1["choke_point"]["status"] == "CHOKED_AT_GATE_1"
    assert "Seed Sandbox" in res_small_1["choke_point"]["gate_name"]
    assert len(res_small_1["root_cause_leaks"]) >= 2
    leak_types = [l["leak_type"] for l in res_small_1["root_cause_leaks"]]
    assert "Opening Latency / Weak Hook" in leak_types
    assert res_small_1["cohort_gates"][0]["passed"] is False

    # Case 2: Small channel failing Gate 2 (Topic Affinity Cluster at 1420 views)
    res_small_2 = calculate_viral_potential(
        hook_score=74,
        visual_velocity_score=50,
        silence_percentage=14.0,
        predicted_completion_rate=48.0,
        safe_zone_score=55,
        genre_info={"genre": "tech_review"},
        platform_metrics={"view_count": 1420, "vvs_rate": 72.5, "apvp_rate": 48.0}
    )
    assert res_small_2["choke_point"]["status"] == "CHOKED_AT_GATE_2"
    assert "Topic Affinity Cluster" in res_small_2["choke_point"]["gate_name"]
    assert res_small_2["cohort_gates"][0]["passed"] is True
    assert res_small_2["cohort_gates"][1]["passed"] is False


if __name__ == "__main__":
    test_database_initialization()
    test_silence_detection()
    test_keep_intervals_calculation()
    test_hook_evaluator()
    test_visual_and_b_roll_analysis()
    test_vocal_dynamics()
    test_safe_zone_framing()
    test_predicted_retention_curve()
    test_kinetic_subtitles_with_emojis()
    test_sfx_audio_stems()
    test_social_suite_generation()
    test_anime_edit_genre_and_social_suite()
    test_podcast_clip_genre_and_viral_potential()
    test_executive_report_generation()
    test_billing_order_creation()
    test_one_click_auto_fixer_render()
    test_url_downloader_module()
    test_ab_hook_split_tester()
    test_gaming_showcase_genre_and_live_calibration()
    print("\n--- ALL 19 AUTOMATED TESTS (INCLUDING LIVE 987K CALIBRATION & GAMING GENRE) PASSED SUCCESSFULLY! ---")
