from collections import OrderedDict
import json
import os


__all__ = [
    'load_json',
    'save_json',
    'get_items_with_recipe',
    'get_items_for_recipes_editor',
    'merge_recipe_items_in_items',
    'merge_images_in_items'
]


def load_json(file):
    data = None

    if not os.path.isfile(file):
        raise FileNotFoundError('The {} file does not exists'.format(file))

    with open(file, 'r') as f:
        data = f.read()

    return json.loads(data) if data else data


def save_json(file, data):
    with open(file, 'w') as f:
        f.write(json.dumps(data))

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
