# yt-dlp

import json
import subprocess
from pathlib import Path

videos_dir = Path('videos')
dest_dir = Path('pycon-fr-24')
dest_dir.mkdir(exist_ok=True)


def download_video(manifest_path):
    with manifest_path.open() as f:
        doc = json.load(f)

    video_url = next(v['url'] for v in doc['videos'] if v['type'] == 'peertube')
    video_name = manifest_path.with_suffix('.mp4').name
    video_path = dest_dir / video_name
    subprocess.run(['yt-dlp', '-o', str(video_path), video_url])

    url_block = next(v for v in doc['videos'] if v['type'] == 'mp4')
    url_block['url'] = f'https://dl.afpy.org/pycon-fr-24/{video_name}'
    url_block['size'] = video_path.stat().st_size

    with manifest_path.open('w') as f:
        json.dump(doc, f, indent=2)


for path in videos_dir.glob('*.json'):
    download_video(path)
