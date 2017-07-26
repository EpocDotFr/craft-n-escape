from collections import OrderedDict
from configparser import ConfigParser
from mss.windows import MSS as mss
from ctypes.wintypes import RECT, DWORD
from hashlib import md5
from PIL import Image
from time import sleep
import ctypes
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


PUL = ctypes.POINTER(ctypes.c_ulong)


class KeyBdInput(ctypes.Structure):
    _fields_ = [("wVk", ctypes.c_ushort),
                ("wScan", ctypes.c_ushort),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class HardwareInput(ctypes.Structure):
    _fields_ = [("uMsg", ctypes.c_ulong),
                ("wParamL", ctypes.c_short),
                ("wParamH", ctypes.c_ushort)]


class MouseInput(ctypes.Structure):
    _fields_ = [("dx", ctypes.c_long),
                ("dy", ctypes.c_long),
                ("mouseData", ctypes.c_ulong),
                ("dwFlags", ctypes.c_ulong),
                ("time", ctypes.c_ulong),
                ("dwExtraInfo", PUL)]


class Input_I(ctypes.Union):
    _fields_ = [("ki", KeyBdInput),
                ("mi", MouseInput),
                ("hi", HardwareInput)]


class Input(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong),
                ("ii", Input_I)]


def PressKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


def ReleaseKey(hexKeyCode):
    extra = ctypes.c_ulong(0)
    ii_ = Input_I()
    ii_.ki = KeyBdInput(0, hexKeyCode, 0x0008 | 0x0002, 0, ctypes.pointer(extra))
    x = Input(ctypes.c_ulong(1), ii_)
    ctypes.windll.user32.SendInput(1, ctypes.pointer(x), ctypes.sizeof(x))


class ItemsImagesExtractor:
    current_weapon_addr = 0x0E2F4D2C
    weapon_slot_top = 369
    weapon_slot_left = 484
    weapon_slot_width = 106
    weapon_slot_height = 103
    item_background_color = (32, 32, 32, 255)
    item_background_color_replace = (32, 32, 32, 0)

    PROCESS_ALL_ACCESS = 0x1F0FFF

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
        self.game_window = ctypes.windll.user32.FindWindowW(None, 'The Escapists')

        if not self.game_window:
            raise Exception('The game does not seems to be running')

        ctypes.windll.user32.SetForegroundWindow(self.game_window)

    def _set_weapon_slot_pos(self):
        """Set the weapon slot position in the game's window."""
        game_window_rect = RECT()
        ctypes.windll.user32.GetWindowRect(self.game_window, ctypes.byref(game_window_rect))

        self.weapon_slot_pos = {
            'top': game_window_rect.top + self.weapon_slot_top,
            'left': game_window_rect.left + self.weapon_slot_left,
            'width': self.weapon_slot_width,
            'height': self.weapon_slot_height
        }

    def _set_process(self):
        game_window_proc_id = DWORD()
        ctypes.windll.user32.GetWindowThreadProcessId(self.game_window, ctypes.byref(game_window_proc_id))

        if not game_window_proc_id:
            raise Exception('Unable to get the game\'s process ID')

        self.game_process = ctypes.windll.kernel32.OpenProcess(self.PROCESS_ALL_ACCESS, False, game_window_proc_id)

        if not self.game_process:
            raise Exception('Unable open the game\'s process')

    def _set_current_weapon(self, item_id):
        item_id = bytes(item_id, 'utf8')
        buffer_size = len(item_id)
        current_weapon_id = ctypes.create_string_buffer(item_id, size=buffer_size)

        ctypes.windll.kernel32.WriteProcessMemory(self.game_process, self.current_weapon_addr, current_weapon_id, buffer_size)

    def _toggle_profile(self):
        PressKey(0x08)
        sleep(0.2)
        ReleaseKey(0x08)
        sleep(0.2)

    def extract(self):
        scsh = mss()

        # For each available items
        for item_id in self.item_ids:
            # Change the current player's weapon (by writing its ID in the game's memory)
            self._set_current_weapon(item_id)

            sleep(0.2)

            # Show the player's profile by sending key 7 (required in order to be taken into account by the game)
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

            # Hide the player's profile by sending key 7 (required in order to be taken into account by the game)
            self._toggle_profile()
