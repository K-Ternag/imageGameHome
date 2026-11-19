"""Import the verified marketing deliverable; keep PNG originals byte-for-byte."""
import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from content import SCREENS


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--source', type=Path, default=Path(r'D:\Projects\familyGame\artifacts\marketing-current\deliverables\website'))
    source = parser.parse_args().source.resolve()
    manifest = json.loads((source / 'manifest.json').read_text(encoding='utf-8'))
    # Validate the whole supplied package before replacing website files.
    for entry in manifest['files']:
        path = (source / entry['file']).resolve()
        if not path.is_relative_to(source) or not path.is_file():
            raise ValueError('Invalid package file: ' + entry['file'])
        if hashlib.sha256(path.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError('Package hash mismatch: ' + entry['file'])
    for stem, *_ in SCREENS:
        if not (source / 'source-screens' / (stem + '.png')).is_file():
            raise ValueError('Missing source screenshot: ' + stem)
    shutil.copytree(source / 'assets', ROOT / 'assets', dirs_exist_ok=True)
    for lang in ['ko', 'en']:
        destination = ROOT / 'assets' / lang
        entries = []
        for stem, *_ in SCREENS:
            original = source / 'source-screens' / (stem + '.png')
            shutil.copy2(original, destination / 'originals' / original.name)
            with Image.open(original) as img:
                for width in (480, 800):
                    target = destination / 'screens' / f'{stem}-{width}.webp'
                    if not (source / 'assets' / lang / 'screens' / target.name).exists():
                        preview = img.convert('RGB')
                        preview.thumbnail((width, 2400), Image.Resampling.LANCZOS)
                        preview.save(target, 'WEBP', quality=88, method=6)
                entries.append(dict(file=original.name, width=img.width, height=img.height,
                                    sha256=hashlib.sha256(original.read_bytes()).hexdigest(),
                                    app_ui_language='ko-KR', source='current actual app capture'))
        (destination / 'manifest.json').write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f'Verified package; imported {len(SCREENS)} actual Korean captures for each website language.')


if __name__ == '__main__':
    main()
