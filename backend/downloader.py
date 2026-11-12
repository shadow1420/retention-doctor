import os
import uuid
import yt_dlp
from typing import Dict, Any

def download_video_from_url(url: str, output_dir: str) -> Dict[str, Any]:
    project_id = f"proj_{uuid.uuid4().hex[:12]}"
    out_template = os.path.join(output_dir, f"{project_id}_%(title).50s.%(ext)s")

    ydl_opts = {
        'outtmpl': out_template,
        'format': 'bestvideo[height<=1080][ext=mp4]+bestaudio[ext=m4a]/bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',
        'merge_output_format': 'mp4',
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'socket_timeout': 30,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        if not filename.endswith('.mp4'):
            base, _ = os.path.splitext(filename)
            mp4_file = base + '.mp4'
            if os.path.exists(mp4_file):
                filename = mp4_file

        title = info.get('title') or 'Imported Video'
        duration = float(info.get('duration') or 0.0)
        width = int(info.get('width') or 1080)
        height = int(info.get('height') or 1920)

        # Extract live platform statistics from YouTube / TikTok
        view_count = int(info.get('view_count') or 0)
        like_count = int(info.get('like_count') or 0)
        comment_count = int(info.get('comment_count') or 0)
        channel = str(info.get('channel') or info.get('uploader') or '')
        channel_follower_count = int(info.get('channel_follower_count') or 0)
        tags = list(info.get('tags') or [])
        categories = list(info.get('categories') or [])

        platform_metrics = {
            'view_count': view_count,
            'like_count': like_count,
            'comment_count': comment_count,
            'channel': channel,
            'channel_follower_count': channel_follower_count,
            'tags': tags,
            'categories': categories,
            'webpage_url': info.get('webpage_url') or url,
            'is_verified_live': bool(view_count > 0)
        }

        return {
            'project_id': project_id,
            'filepath': filename,
            'filename': os.path.basename(filename),
            'title': title,
            'duration': duration,
            'width': width,
            'height': height,
            'uploader': channel,
            'aspect_ratio': '9:16' if height > width else '16:9',
            'platform_metrics': platform_metrics
        }

if __name__ == "__main__":
    print("Downloader module syntax test passed!")
