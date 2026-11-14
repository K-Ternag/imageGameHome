"""Check generated HTML, links, locale assets, and the deployable file boundary."""
import argparse
import hashlib
import json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

PROJECT = Path(__file__).resolve().parents[1]


class Document(HTMLParser):
    def __init__(self, path):
        super().__init__(convert_charrefs=True)
        self.path, self.ids, self.links, self.images = path, set(), [], []
        self.h1, self.lang, self.main = 0, None, 0
        self.errors = []
        self.feed(path.read_text(encoding='utf-8'))

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == 'html': self.lang = values.get('lang')
        if tag == 'h1': self.h1 += 1
        if tag == 'main': self.main += 1
        if 'id' in values:
            if values['id'] in self.ids: self.errors.append('Duplicate id: '+values['id'])
            self.ids.add(values['id'])
        for key in ('href', 'src', 'data-preview'):
            if values.get(key): self.links.append(values[key])
        if values.get('srcset'):
            self.links.extend(item.strip().split()[0] for item in values['srcset'].split(','))
        if tag == 'img':
            self.images.append(values)
            if 'alt' not in values: self.errors.append('Image missing alt')
        if tag == 'script' and values.get('src','').startswith('http'):
            self.errors.append('Unexpected third-party script')


def check(root):
    errors = []
    paths = sorted(root.glob('*.html'))
    docs = {path.resolve(): Document(path) for path in paths}
    if len(docs) != 13: errors.append(f'Expected 13 HTML files, found {len(docs)}')
    references = 0
    for path, doc in docs.items():
        errors.extend(f'{path.name}: {e}' for e in doc.errors)
        if doc.h1 != 1 or doc.main != 1: errors.append(f'{path.name}: expected one h1 and main')
        lang = 'en' if '.en.' in path.name else 'ko'
        if doc.lang != lang: errors.append(f'{path.name}: incorrect language')
        for img in doc.images:
            if img.get('src','').startswith('assets/') and f'assets/{lang}/' not in img['src']:
                errors.append(f'{path.name}: wrong locale image {img["src"]}')
        for link in doc.links:
            references += 1
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc: continue
            if parsed.path.startswith('/'):
                errors.append(f'{path.name}: root-relative URL breaks project Pages: {link}')
                continue
            target = (path.parent/unquote(parsed.path)).resolve() if parsed.path else path
            if not target.is_relative_to(root.resolve()):
                errors.append(f'{path.name}: path outside publication: {link}')
            elif not target.is_file():
                errors.append(f'{path.name}: missing target {link}')
            elif parsed.fragment and target.suffix=='.html':
                if unquote(parsed.fragment) not in docs[target].ids:
                    errors.append(f'{path.name}: missing anchor {link}')
    for lang in ['ko','en']:
        entries=json.loads((root/'assets'/lang/'manifest.json').read_text(encoding='utf-8'))
        if len(entries)!=8: errors.append(f'{lang}: expected eight original assets')
        for entry in entries:
            original=root/'assets'/lang/'originals'/entry['file']
            if hashlib.sha256(original.read_bytes()).hexdigest()!=entry['sha256']:
                errors.append(f'Original was changed: {original}')
    if root!=PROJECT:
        unwanted=[item.name for item in root.iterdir() if item.name not in {'assets','styles.css','app.js','.nojekyll','robots.txt','sitemap.xml'} and item.suffix!='.html']
        if unwanted: errors.append('Development files in deployment: '+', '.join(unwanted))
    return {'pages':len(docs),'local_and_external_references_checked':references,'original_images_verified':16,'errors':errors}


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('directory',type=Path,nargs='?',default=PROJECT)
    args=parser.parse_args()
    result=check(args.directory.resolve())
    print(json.dumps(result,ensure_ascii=False,indent=2))
    raise SystemExit(bool(result['errors']))
