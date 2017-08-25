import os


def parse_items_localization(file, lang='en'):
    locales = {
        'en': 1,
        'de': 2,
        'fr': 3,
        'es': 4,
        'ru': 5,
        'it': 6,
        'zh': 7
    }

    if lang not in locales:
        raise ValueError(lang + ' is not supported')

    if not os.path.isfile(file):
        raise FileNotFoundError(file + ' does not exists')

    with open(file, 'r') as f:
        file_content = f.read().strip()

    localization = {}

    for line in file_content.splitlines()[1:]:
        line = line.strip()

        if not line: # Empty line
            continue

        cols = [c.strip() for c in line.split('\t')]

        if len(cols) <= 1:
            continue

        text_id = cols[0]

        if not text_id.startswith('Text.Item'):
            continue

        localization[text_id] = cols[locales[lang]]

    return localization
