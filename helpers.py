import json
import os


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


def get_items_without_recipe(items):
    return [item for item in items if 'craft' in item]


def get_items_for_editor(items, recipes):
    for item in items:
        item['do_not_exists'] = True
        item['out_of_date'] = False

        for recipe in recipes:
            if item['id'] == recipe['id']:
                item['do_not_exists'] = False

                if item['craft']['_recipe_hash'] != recipe['_recipe_hash']:
                    item['out_of_date'] = True

                break

    return items


def get_item(items, item_id):
    for item in items:
        if item['id'] == item_id:
            return item

    return None


def merge_recipe_items_in_items(items, recipes):
    for item in items:
        if 'craft' not in item:
            continue

        recipe = get_recipe(recipes, item['id'])

        if recipe:
            item['craft']['recipe_items'] = recipe['items']

    return items


def get_recipe(recipes, item_id):
    for recipe in recipes:
        if recipe['id'] == item_id:
            return recipe

    return None


def create_or_update_recipe(recipes, item_id, recipe_hash, recipe_items):
    found = False

    # Update the existing recipe if it exists
    for recipe in recipes:
        if recipe['id'] == item_id:
            recipe['_recipe_hash'] = recipe_hash
            recipe['items'] = recipe_items

            found = True

            break

    # Create a new recipe if it doesn't exists
    if not found:
        recipes.append({
            'id': item_id,
            '_recipe_hash': recipe_hash,
            'items': recipe_items
        })
