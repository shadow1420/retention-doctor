import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

channels = [
    ("Gaming / Blox Fruits", "proj_122f8cb19f66"),
    ("Anime Phonk Edit (4K)", "proj_0f73fc2025c0"),
    ("Podcast / Science (Huberman)", "proj_podcast_001"),
    ("Finance & Wealth (Hormozi)", "proj_hormozi_001"),
    ("Storytelling / Mystery (MrBallen)", "proj_story_001")
]

print("=================================================================")
print("     5-CHANNEL REAL-WORLD BENCHMARK AUDIT & ACCURACY CHECK       ")
print("=================================================================")

for name, pid in channels:
    res = requests.get(f"http://127.0.0.1:8000/api/analysis/{pid}")
    if res.status_code != 200:
        print(f"FAILED to fetch {name} ({pid}): {res.status_code}")
        continue
    d = res.json()
    post = d.get("posting_schedule", {})
    vir = d.get("viral_potential", {})
    hook = d.get("hook", {})
    visual = d.get("visual", {})
    vocal = d.get("vocal", {})
    gates = vir.get("cohort_gates", [])
    perf = vir.get("platform_performance", {})
    views_range = vir.get("views_range", {})
    
    # Fetch title
    proj_res = requests.get(f"http://127.0.0.1:8000/api/projects/{pid}").json()
    title = proj_res.get("title", "")
    
    print(f"\n>>> [{name}] (Project ID: {pid})")
    print(f"  Title: {title[:65]}")
    genre_data = d.get('genre') or {}
    print(f"  Genre Label: {genre_data.get('genre_label', genre_data.get('genre'))} | Duration: {d.get('duration')}s")
    print(f"  Hook Score: {hook.get('score')}/100 (Grade {hook.get('grade')}) | Pacing Score: {visual.get('pacing_score', 'N/A')}/100")
    print(f"  Virality Readiness: {vir.get('virality_score')}/100 | Tier: {vir.get('reach_tier')}")
    print(f"  Expected Views Range: {views_range.get('formatted')}")
    print(f"  Verified Live Actual Views: {perf.get('actual_views_formatted')} ({perf.get('actual_views'):,} views)" if perf.get('actual_views') else "  Verified Views: None (Predictive Sandbox)")
    passed_gates = [g.get('gate') for g in gates if g.get('passed')]
    print(f"  Cohort Gates Cleared: {len(passed_gates)}/4 -> Gates {passed_gates}")
    sched = post.get("schedule", {})
    print(f"  Upload Window: {post.get('upload_window')}")
    print(f"  Audience Peak Slots: Weekday {sched.get('peak_weekday')} | Weekend {sched.get('weekend')}")
    print(f"  Algorithm Mechanical Hack: {post.get('algorithm_hack')}")
