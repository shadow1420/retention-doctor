import requests
import json
import sys

sys.stdout.reconfigure(encoding='utf-8')

res = requests.get('http://127.0.0.1:8000/api/analysis/proj_122f8cb19f66').json()
seo = res.get('seo', {})
thumbs = res.get('thumbnails', [])

print("=== SEO AUDIT ===")
for t in seo.get('titles', []):
    print(f"[{t['type']}] ({t['ctr_boost']}): {t['title']}")
print("Hashtags:", seo.get('hashtag_matrix', {}).get('all_formatted'))

print("\n=== THUMBNAILS EXTRACTED ===")
print(f"Count: {len(thumbs)}")
for t in thumbs:
    print(f"Frame {t['index']} @ {t['timestamp_formatted']}: {t['label']} - Score: {t['thumb_stop_score']}/100 ({t['thumb_grade']}) -> URL: {t['url']}")
