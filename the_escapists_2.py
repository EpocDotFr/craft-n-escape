from collections import OrderedDict
import unitypack
import os


class ItemsDataExtractor:
    available_locales = {
        'eng': 1,
        'ger': 2,
        'fre': 3,
        'spa': 4,
        'rus': 5,
        'ita': 6,
        'chi': 7
    }

    def __init__(self, game_dir):
        self.game_dir = game_dir
        self.data_dir = os.path.join(self.game_dir, 'TheEscapists2_Data')

    def extract(self, lang='eng'):
        """Actually run the extraction process."""

        resources_file = os.path.join(self.data_dir, 'resources.assets')

        if not os.path.isfile(resources_file):
            raise FileNotFoundError(resources_file + ' does not exists')

        items = OrderedDict()

        with open(resources_file, 'rb') as f:
            assets = unitypack.Asset.from_file(f)

            # self._parse_localization(stream, lang=lang)

        return items

    def _parse_localization(self, stream, lang='eng'):
        if lang not in self.available_locales:
            raise ValueError(lang + ' is not supported')

        # with open(stream, 'r', encoding='utf-8') as f:
        #     file_content = f.read().strip()
        file_content = stream.read().strip()

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

            text_id = text_id.replace('Text.Item.', '', 1)

            localization[text_id] = cols[self.available_locales[lang]]

        return localization
