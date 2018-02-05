from collections import OrderedDict
from flask import request, url_for
from urllib.parse import urlparse
from cne import app, cache
from glob import glob
import json
import os


__all__ = [
    'is_local',
    'get_images',
    'load_json',
    'save_json',
    'get_items_with_recipe',
    'get_items_for_recipes_editor',
    'merge_recipe_items_in_items',
    'merge_images_in_items',
    'get_item_by_id',
    'set_items_permalink'
]


def is_local():
    url = urlparse(request.url_root)

    if url.hostname != 'localhost':
        return False

    return True


@cache.cached(timeout=60 * 60 * 6, key_prefix='te1_items_images')
def get_images(game_version=1):
    items_images = {}

    detected_images = glob(os.path.join(app.config['ITEMS_IMAGES_DIR'].format(game_version=game_version), '*.*'))

    for detected_image in detected_images:
        detected_image = os.path.splitext(os.path.basename(detected_image))

        items_images[detected_image[0]] = detected_image[1]

    return items_images


def load_json(file):
    if not os.path.isfile(file):
        raise FileNotFoundError('The {} file does not exists'.format(file))

    with open(file, 'r', encoding='utf-8') as f:
        return json.load(f, object_pairs_hook=OrderedDict)


def save_json(file, data):
    with open(file, 'w', encoding='utf-8') as f:
        json.dump(data, f)

    return data


def get_items_with_recipe(items):
    items_with_recipe = OrderedDict()

    for item_id, item in items.items():
        if 'craft' in item:
            items_with_recipe[item_id] = item

    return items_with_recipe


def get_items_for_recipes_editor(items, recipes):
    for item_id, item in items.items():
        item['recipe_do_not_exists'] = True
        item['recipe_out_of_date'] = False

        if item_id not in recipes:
            continue

        item['recipe_do_not_exists'] = False

        if item['craft']['_recipe_hash'] != recipes[item_id]['_recipe_hash']:
            item['recipe_out_of_date'] = True

    return items


def merge_recipe_items_in_items(items, recipes):
    for item_id, item in items.items():
        if 'craft' not in item:
            continue

        if item_id in recipes:
            item['craft']['recipe_items'] = recipes[item_id]['items']

    return items


def merge_images_in_items(items, images):
    for item_id, item in items.items():
        if item_id in images:
            item['_img_ext'] = images[item_id]

    return items


def get_item_by_id(items, id):
    id = str(id)

    for item_id, item in items.items():
        if id == item_id:
            item['id'] = item_id

            return item

    return None


def set_items_permalink(items, game_version):
    for item_id, item in items.items():
        item['permalink'] = url_for('home', game_version=None if game_version == 1 else game_version, item_id=item_id, item_slug=item['name_slug'])

    return items
