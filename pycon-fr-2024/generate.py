import json
import re
import unicodedata
from pathlib import Path


def read_json(path):
    if not isinstance(path, Path):
        path = Path(path)
    with path.open() as f:
        return json.load(f)


def write_json(path, doc):
    if not isinstance(path, Path):
        path = Path(path)
    with path.open('w') as f:
        json.dump(doc, f, indent=2)
    print('Wrote', path)


def slugify(text, sep='_'):
    text = unicodedata.normalize('NFKD', text.lower())
    text = ''.join(c for c in text if c.isascii())
    words = re.split(r'[^a-z0-9]+', text)
    words = [w for w in words if w]
    return sep.join(words)


talks = read_json('talks.json')
videos = read_json('videos.json')
write_json('category.json', {'title': 'PyCon FR 2024'})

videos_dir = Path('videos')
videos_dir.mkdir(exist_ok=True)


def find_talk(name):
    def simple_find():
        if ' - ' in name:
            _, title = name.split(' - ', 1)
        else:
            title = name

        for talk in talks:
            if talk['Titre de la proposition'] == title:
                return talk

    def word_find():
        found = None
        max_score = 0
        words = {slugify(w) for w in re.findall(r'\w+', name)}

        for talk in talks:
            talk_words = {
                slugify(w) for w in (
                    *(
                        w
                        for s in (talk['Titre de la proposition'], *talk['Noms des intervenants'])
                        for w in re.findall(r'\w+', s)
                    ),
                )
            }
            score = len(words & talk_words)
            if score > max_score:
                max_score = score
                found = talk

        return found

    talk = simple_find() or word_find()
    if talk:
        talks.remove(talk)
        return talk

    raise ValueError(f"Cannot find talk for {name!r}")


for video in videos['data']:
    talk = find_talk(video['name'])
    print('---')
    print(video['name'])
    print(talk['Titre de la proposition'], talk['Noms des intervenants'])
    write_json(
        f'videos/{slugify(talk["Titre de la proposition"])}.json',
        {
            'title': talk['Titre de la proposition'],
            'description': talk['Description'],
            'duration': video['duration'],
            'language': {'fr': 'fra', 'en': 'eng'}[talk['Langue']],
            'recorded': talk['Début'].split('T')[0],
            'speakers': talk['Noms des intervenants'],
            'videos': [
                {
                    'type': 'mp4',
                    'url': '',
                    'size': 0,
                },
                {
                    'type': 'peertube',
                    'url': video['url'],
                },
            ],
            'related_urls': [
                {
                    'label': 'Conference schedule',
                    'url': 'https://www.pycon.fr/2024/fr/schedule.html',
                },
            ],
            'thumbnail_url': f'https://indymotion.fr{video["thumbnailPath"]}',
        },
    )
