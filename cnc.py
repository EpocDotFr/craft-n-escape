from flask import Flask, render_template, make_response, request, abort, flash
from werkzeug.exceptions import HTTPException
from configparser import ConfigParser
from hashlib import md5
from flask_cache import Cache
from urllib.parse import urlparse
from collections import OrderedDict
from helpers import *
import logging
import click
import sys
import os


# -----------------------------------------------------------
# Local helpers


def is_local():
    url = urlparse(request.url_root)

    if url.hostname != 'localhost':
        return False

    return True


# -----------------------------------------------------------
# Boot


app = Flask(__name__, static_url_path='')
app.config.from_pyfile('config.py')

app.config['CACHE_TYPE'] = 'filesystem'
app.config['CACHE_DIR'] = 'storage/cache'

app.jinja_env.globals.update(is_local=is_local)

cache = Cache(app)

# Default Python logger
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%d/%m/%Y %H:%M:%S',
    stream=sys.stdout
)

logging.getLogger().setLevel(logging.INFO)

# Default Flask loggers
for handler in app.logger.handlers:
    handler.setFormatter(logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S'))


# -----------------------------------------------------------
# Routes


@app.route('/')
def home():
    items = load_json(app.config['ITEMS_FILE'])
    recipes = load_json(app.config['RECIPES_FILE'])

    items = merge_recipe_items_in_items(items, recipes)

    return render_template('home.html', items=items, recipes=recipes)


@app.route('/recipes-editor')
def recipes_editor():
    if not is_local(): # Can only edit crafting recipes locally
        abort(404)

    items = load_json(app.config['ITEMS_FILE'])
    recipes = load_json(app.config['RECIPES_FILE'])

    items = get_items_without_recipe(items) # Remove items without crafting recipe

    # Highlight items with crafting recipe but not in the Craft N' Escape recipes file
    # Also highlight items with no up-to-date crafting recipe in comparison of the game's one
    items = get_items_for_editor(items, recipes)

    return render_template('recipes_editor/home.html', items=items)


@app.route('/recipes-editor/<item_id>', methods=['GET', 'POST'])
def recipes_editor_item(item_id):
    if not is_local(): # Can only edit crafting recipes locally
        abort(404)

    items = load_json(app.config['ITEMS_FILE'])
    recipes = load_json(app.config['RECIPES_FILE'])

    # Highlight items with crafting recipe but not in the Craft N' Escape recipes file
    # Also highlight items with no up-to-date crafting recipe in comparison of the game's one
    items = get_items_for_editor(items, recipes)

    if item_id not in items:
        abort(404)

    if request.method == 'POST':
        recipe_items = get_form_values([
            ('id', int),
            ('amount', int)
        ])

        recipe_hash = request.form.get('_recipe_hash')

        try:
            recipes[item_id]['_recipe_hash'] = recipe_hash
            recipes[item_id]['items'] = recipe_items

            save_json(app.config['RECIPES_FILE'], recipes)

            flash('Recipe saved successfully.', 'success')
        except Exception as e:
            flash('Error saving this recipe: {}'.format(e), 'error')

    current_item = items[item_id]

    if item_id in recipes:
        current_recipe = recipes[item_id]
    else:
        current_recipe = {'items': []}

    return render_template(
        'recipes_editor/item.html',
        current_item=current_item,
        current_item_id=item_id,
        current_recipe=current_recipe,
        items=items
    )


@app.route('/items-image-editor')
def items_image_editor():
    if not is_local(): # Can only edit items image locally
        abort(404)

    items = load_json(app.config['ITEMS_FILE'])

    return render_template('items_image_editor/home.html', items=items)


@app.route('/items-image-editor/<item_id>', methods=['GET', 'POST'])
def items_image_editor_item(item_id):
    if not is_local(): # Can only edit items image locally
        abort(404)

    return render_template(
        'items_image_editor/item.html'
    )


# -----------------------------------------------------------
# Classes


class ItemsParser:
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


# -----------------------------------------------------------
# CLI commands


@app.cli.command()
@click.option('--gamedir', '-g', help='Game root directory')
def build(gamedir):
    """Extract data from items_eng.dat """
    context = click.get_current_context()

    if not gamedir:
        click.echo(build.get_help(context))
        context.exit()

    if not click.confirm('This will overwrite the {} file. Are you sure?'.format(app.config['ITEMS_FILE'])):
        context.exit()

    app.logger.info('Build started')

    items_parser = ItemsParser(gamedir)
    items = items_parser.parse()

    app.logger.info('Saving {}'.format(app.config['ITEMS_FILE']))

    save_json(app.config['ITEMS_FILE'], items)

    # Initialize the recipes file as it doesn't exists
    if not os.path.isfile(app.config['RECIPES_FILE']):
        app.logger.info('Saving {}'.format(app.config['RECIPES_FILE']))

        save_json(app.config['RECIPES_FILE'], {})

    # Initialize the images file as it doesn't exists
    if not os.path.isfile(app.config['IMAGES_FILE']):
        app.logger.info('Saving {}'.format(app.config['IMAGES_FILE']))

        save_json(app.config['IMAGES_FILE'], {})

    app.logger.info('Done')


# -----------------------------------------------------------
# HTTP errors handler


@app.errorhandler(401)
@app.errorhandler(403)
@app.errorhandler(404)
@app.errorhandler(500)
@app.errorhandler(503)
def http_error_handler(error, without_code=False):
    if isinstance(error, HTTPException):
        error = error.code
    elif not isinstance(error, int):
        error = 500

    body = render_template('errors/{}.html'.format(error))

    if not without_code:
        return make_response(body, error)
    else:
        return make_response(body)


# -----------------------------------------------------------
# Local helpers


def get_form_values(names):
    values = [request.form.getlist(h[0], type=h[1]) for h in names]
    items = [{} for i in range(len(values[0]))]

    for x, i in enumerate(values):
        for _x, _i in enumerate(i):
            items[_x][names[x][0]] = _i

    return items


@cache.cached(timeout=60 * 6)
def get_wiki_images():
    pass
