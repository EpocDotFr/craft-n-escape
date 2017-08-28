from collections import OrderedDict
from unitypack.asset import Asset
from PIL import ImageOps
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
            asset = Asset.from_file(f)

            # Loop through each objects in the resources file to find the items
            # localization file. If found, parse and load it.
            for id, obj in asset.objects.items():
                d = obj.read()

                if d.name == 'LocalizationItems':
                    self._parse_localization(d.script, lang=lang)

                    break

            # Loop through each objects in the resources file to find the items
            # image file. If found, extract them.
            # for id, obj in asset.objects.items():
            #     d = obj.read()

            #     if not d.name.startswith('ITM_') and obj.type != 'Texture2D':
            #         continue

            #     image = ImageOps.flip(d.image)
            #     image.save(d.name + '.png')

        return items

    def _parse_localization(self, content, lang='eng'):
        """Parse the items localization file."""
        if lang not in self.available_locales:
            raise ValueError(lang + ' is not supported')

        self.localization = {}

        for line in content.strip().splitlines()[1:]:
            line = line.strip()

            if not line: # Empty line
                continue

            cols = [c.strip() for c in line.split('\t')]

            if len(cols) <= 1:
                continue

            text_id = cols[0]

            if not text_id.startswith('Text.Item'):
                continue

            self.localization[text_id] = cols[self.available_locales[lang]]
