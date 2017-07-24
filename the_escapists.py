from collections import OrderedDict
from configparser import ConfigParser
from hashlib import md5
from mss.windows import MSS as mss
from PIL import Image
import win32gui
import os


class ItemsDataParser:
    """
    ['name', 'illegal', 'gift', 'decay', 'info', 'desk', 'npc_carry', 'fat',
    'outfit', 'buy', 'craft', 'digging', 'chipping', 'hp', 'camdis', 'weapon',
    'unscrewing', 'cutting', 'found', 'carry']
    """
    def __init__(self, game_dir):
        self.game_dir = game_dir
        self.data_dir = os.path.join(self.game_dir, 'Data')

    def parse(self, lang='eng'):
        items_file = os.path.join(self.data_dir, 'items_' + lang + '.dat')

        if not os.path.isfile(items_file):
            raise FileNotFoundError(items_file + ' does not exists')

        items = OrderedDict()

        with open(items_file, 'r') as f:
            items_file_content = f.readlines()[1:] # Removes the first line
            items_file_content = '\n'.join(items_file_content)

        items_parser = ConfigParser(interpolation=None)
        items_parser.read_string(items_file_content)

        for item_id in items_parser.sections():
            items[item_id] = {}

            for name, value in items_parser.items(item_id):
                value = self._get_item_attribute_value(name, value)

                items[item_id][name] = value

        return items

    def _get_item_attribute_value(self, name, value):
        if name in ['gift', 'decay', 'desk', 'fat', 'outfit', 'buy', 'digging', 'chipping', 'hp', 'camdis', 'weapon', 'unscrewing', 'cutting']:
            value = int(value)
        elif name in ['illegal', 'npc_carry', 'carry']:
            value = bool(value)
        elif name == 'craft':
            value = self._parse_craft_attribute_value(value)

        return value

    def _parse_craft_attribute_value(self, value):
        craft = {}

        intelligence, recipe = value.split('_', maxsplit=1)

        craft['intelligence'] = int(intelligence)

        craft['_recipe'] = recipe
        craft['_recipe_hash'] = md5(recipe.encode('utf-8')).hexdigest()

        return craft


class ItemsImagesExtractor:
    def __init__(self):
        pass

    def extract(self):
        current_weapon_addr = 0x0D7C5E5C # String[3]

        game_handle = win32gui.FindWindow(None, 'The Escapists')

        if not game_handle:
            raise Exception('The game does not seems to be running')

        game_window = win32gui.GetWindowRect(game_handle)

        game_window_x = game_window[0]
        game_window_y = game_window[1]

        sct = mss()

        sct_img = sct.grab({ # Screenshot the weapon part of the inventory
            'top': game_window_y + 369,
            'left': game_window_x + 484,
            'width': 106,
            'height': 103
        })

        img = Image.frombytes('RGBA', sct_img.size, bytes(sct_img.raw), 'raw', 'RGBA')

        pixdata = img.load()
        width, height = img.size

        # Make the grey background transparent
        for y in range(height):
            for x in range(width):
                if pixdata[x, y] == (32, 32, 32, 255):
                    pixdata[x, y] = (32, 32, 32, 0)

        img.save('t.png')
