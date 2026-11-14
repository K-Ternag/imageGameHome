"""Import the provided screenshots without changing originals; generate web previews."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--source', type=Path, default=Path(r'D:\Projects\familyGame\artifacts\marketing-v2\website'))
parser.add_argument('--locale', choices=['ko', 'en'], default='ko')
args = parser.parse_args()
destination = ROOT / 'assets' / args.locale
(destination / 'originals').mkdir(parents=True, exist_ok=True)
(destination / 'screens').mkdir(exist_ok=True)
manifest = []
for source in sorted(args.source.glob('*.png')):
    shutil.copy2(source, destination / 'originals' / source.name)
    with Image.open(source) as original:
        for width in (480, 800):
            preview = original.convert('RGB')
            preview.thumbnail((width, 2400), Image.Resampling.LANCZOS)
            preview.save(destination / 'screens' / f'{source.stem}-{width}.webp', 'WEBP', quality=88, method=6)
        manifest.append({'file': source.name, 'width': original.width, 'height': original.height,
                         'sha256': hashlib.sha256(source.read_bytes()).hexdigest()})
(destination / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
print(f'Prepared {len(manifest)} original screenshots and 16 WebP previews.')
