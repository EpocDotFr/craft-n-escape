from collections import OrderedDict
from configparser import ConfigParser
from mss.windows import MSS as mss
from ctypes import windll, byref, create_string_buffer
from ctypes.wintypes import RECT, DWORD
from hashlib import md5
from PIL import Image
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
            items_file_content = f.readlines()[1:] # Removes the first line, because it makes the parser to crash
            items_file_content = '\n'.join(items_file_content) # Reconstruct the whole file

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
    current_weapon_addr = 0x0D4C422C
    weapon_slot_top = 369
    weapon_slot_left = 484
    weapon_slot_width = 106
    weapon_slot_height = 103
    item_background_color = (32, 32, 32, 255)
    item_background_color_replace = (32, 32, 32, 0)

    PROCESS_ALL_ACCESS = 0x1F0FFF
    WM_CHAR = 0x0102
    SEVEN_KEY = 0x37

    def __init__(self, item_ids, output_dir):
        self.item_ids = item_ids
        self.output_dir = output_dir

        if not os.path.isdir(self.output_dir):
            raise FileNotFoundError(self.output_dir + ' does not exists')

        self._set_window()
        self._set_weapon_slot_pos()
        self._set_process()

    def _set_window(self):
        """Set the game's window."""
        self.game_window = windll.user32.FindWindowW(None, 'The Escapists')

        if not self.game_window:
            raise Exception('The game does not seems to be running')

    def _set_weapon_slot_pos(self):
        """Set the weapon slot position in the game's window."""
        game_window_rect = RECT()
        windll.user32.GetWindowRect(self.game_window, byref(game_window_rect))

        self.weapon_slot_pos = {
            'top': game_window_rect.top + self.weapon_slot_top,
            'left': game_window_rect.left + self.weapon_slot_left,
            'width': self.weapon_slot_width,
            'height': self.weapon_slot_height
        }

    def _set_process(self):
        game_window_proc_id = DWORD()
        windll.user32.GetWindowThreadProcessId(self.game_window, byref(game_window_proc_id))

        if not game_window_proc_id:
            raise Exception('Unable to get the game\'s process ID')

        self.game_process = windll.kernel32.OpenProcess(self.PROCESS_ALL_ACCESS, False, game_window_proc_id)

        if not self.game_process:
            raise Exception('Unable open the game\'s process')

    def _set_current_weapon(self, item_id):
        buffer_size = len(item_id)
        current_weapon_id = create_string_buffer(bytes(item_id, 'utf8'), size=buffer_size)

        windll.kernel32.WriteProcessMemory(self.game_process, self.current_weapon_addr, current_weapon_id, buffer_size)

    def _toggle_profile(self):
        windll.user32.SendMessage(self.game_window, self.WM_CHAR, self.SEVEN_KEY, 0)

    def extract(self):
        scsh = mss()

        # For each available items
        for item_id in self.item_ids:
            # Change the current player's weapon (by writing its ID in the game's memory)
            self._set_current_weapon(item_id)

            # Show the player's profile by sending keystrokes (required in order to be taken into account by the game)
            self._toggle_profile()

            # Take screenshot of the weapon slot
            weapon_slot = scsh.grab(self.weapon_slot_pos)

            weapon_slot_img = Image.frombytes('RGBA', weapon_slot.size, bytes(weapon_slot.raw), 'raw', 'RGBA')

            pixdata = weapon_slot_img.load()
            width, height = weapon_slot_img.size

            # Make the grey background transparent
            for y in range(height):
                for x in range(width):
                    if pixdata[x, y] == self.item_background_color:
                        pixdata[x, y] = self.item_background_color_replace

            # Save the image with the item ID as its name
            weapon_slot_img.save(os.path.join(self.output_dir, item_id + '.png'))

            # Hide the player's profile by sending keystrokes (required in order to be taken into account by the game)
            self._toggle_profile()
