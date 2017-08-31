from unitypack.utils import BinaryReader
from collections import OrderedDict
from unitypack.asset import Asset
from glob import glob
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

    def __init__(self, game_dir, items_data_dir):
        self.game_dir = game_dir
        self.data_dir = os.path.join(self.game_dir, 'TheEscapists2_Data')
        self.items_data_dir = items_data_dir

        if not os.path.isdir(self.data_dir):
            raise FileNotFoundError(self.data_dir + ' does not exists')

        if not os.path.isdir(self.items_data_dir):
            raise FileNotFoundError(self.items_data_dir + ' does not exists')

    def extract(self, lang='eng'):
        """Actually run the extraction process."""

        resources_file = os.path.join(self.data_dir, 'resources.assets')

        if not os.path.isfile(resources_file):
            raise FileNotFoundError(resources_file + ' does not exists')

        # --------------------------------------------------------
        # STEP 1 - Parse and load the item names localization file

        with open(resources_file, 'rb') as f:
            asset = Asset.from_file(f)

            for id, obj in asset.objects.items():
                if obj.type != 'TextAsset': # We only want text objects
                    continue

                d = obj.read()

                if d.name == 'LocalizationItems':
                    self._parse_localization(d.script, lang=lang)

                    break

            # Loop through each objects in the resources file to find the items
            # data config files. If found, parse them.
            # for id, obj in asset.objects.items():
            #     if obj.type_id > 0: # Ignore known object types
            #         continue

            #     d = obj.read()

            #     if isinstance(d, dict) and 'm_Name' in d and d['m_Name'].endswith('_ItemData'):
            #         print(d) # TODO
            #         break

            #     if not d.name.startswith('ITM_') and obj.type != 'Texture2D':
            #         continue

            #     image = ImageOps.flip(d.image)
            #     image.save(d.name + '.png')

        # --------------------------------------------------------
        # STEP 2 - Parse the items data files (they must be extracted manually from the resources.assets file)

        items = OrderedDict()

        for file in glob(os.path.join(self.items_data_dir, '*.dat')):
            with open(file, 'rb') as file:
                item_id, item = self._parse_item_data_file(BinaryReader(file))

                if not item['name']:
                    continue

                items[item_id] = item

        return items

    def _pad_bytes(self, buf):
        c = b''

        while True:
            pos = buf.tell()

            c = buf.read(1)

            if c != b"\0":
                buf.seek(pos)

                break

    def _parse_item_data_file(self, buf):
        """Parse a raw item data file coming form the game resources.assets file."""
        item = {}

        buf.read_int()
        buf.read_int()
        buf.read_int()
        buf.read_int()
        buf.read_int()
        buf.read_int()
        buf.read_int()

        buf.read_string(buf.read_int()) # Unity object name
        self._pad_bytes(buf)

        item_id = buf.read_int()

        locale_id = buf.read_string(buf.read_int())

        item['name'] = self._get_localization(locale_id)
        self._pad_bytes(buf)

        buf.read_int() # Health

        item['buy'] = buf.read_int()

        gift_inmate = buf.read_int()
        gift_guard = buf.read_int()

        if gift_inmate != 0 or gift_guard != 0:
            item['gift'] = [gift_inmate, gift_guard]

        item['illegal'] = buf.read_boolean()

        self._pad_bytes(buf)

        buf.read_boolean() # Can be equiped?

        self._pad_bytes(buf)

        buf.read_boolean()

        self._pad_bytes(buf)

        buf.read_int()

        return item_id, item

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

    def _get_localization(self, key):
        """Get a localized string identified by its ID."""
        if key in self.localization:
            return self.localization[key]

        return None
