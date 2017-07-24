from flask import Flask, render_template, make_response, request, abort, flash
from werkzeug.exceptions import HTTPException
from flask_cache import Cache
from urllib.parse import urlparse
from glob import glob
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
app.config['ITEMS_IMAGES_DIR'] = 'static/images/items'
app.config['ITEMS_FILE'] = 'storage/data/items.json'
app.config['RECIPES_FILE'] = 'storage/data/recipes.json'
app.config['ESCAPISTS_WIKI_DOMAIN'] = 'theescapists.gamepedia.com'

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
    images = get_images()

    items = merge_recipe_items_in_items(items, recipes)
    items = merge_images_in_items(items, images)

    return render_template('home.html', items=items, recipes=recipes)


@app.route('/recipes-editor')
def recipes_editor():
    if not is_local(): # Can only edit crafting recipes locally
        abort(404)

    items = load_json(app.config['ITEMS_FILE'])
    recipes = load_json(app.config['RECIPES_FILE'])

    items = get_items_with_recipe(items) # Only get items with a crafting recipe

    # Highlight items with crafting recipe but not in the Craft N' Escape recipes file
    # Also highlight items with no up-to-date crafting recipe in comparison of the game's one
    items = get_items_for_recipes_editor(items, recipes)

    return render_template('recipes_editor/home.html', items=items)


@app.route('/recipes-editor/<item_id>', methods=['GET', 'POST'])
def recipes_editor_item(item_id):
    if not is_local(): # Can only edit crafting recipes locally
        abort(404)

    items = load_json(app.config['ITEMS_FILE'])
    recipes = load_json(app.config['RECIPES_FILE'])

    # Highlight items with crafting recipe but not in the Craft N' Escape recipes file
    # Also highlight items with no up-to-date crafting recipe in comparison of the game's one
    items = get_items_for_recipes_editor(items, recipes)

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


# -----------------------------------------------------------
# CLI commands


@app.cli.command()
@click.option('--gamedir', '-g', help='Game root directory')
def itemsdata(gamedir):
    """Extract data from items_eng.dat"""
    from the_escapists import ItemsDataParser

    context = click.get_current_context()

    if not gamedir:
        click.echo(itemsdata.get_help(context))
        context.exit()

    if not click.confirm('This will overwrite the {} file. Are you sure?'.format(app.config['ITEMS_FILE'])):
        context.exit()

    app.logger.info('Extracting started')

    parser = ItemsDataParser(gamedir)
    items = parser.parse()

    app.logger.info('Saving {}'.format(app.config['ITEMS_FILE']))

    save_json(app.config['ITEMS_FILE'], items)

    # Initialize the recipes file as it doesn't exists
    if not os.path.isfile(app.config['RECIPES_FILE']):
        app.logger.info('Saving {}'.format(app.config['RECIPES_FILE']))

        save_json(app.config['RECIPES_FILE'], {})

    app.logger.info('Done')


@app.cli.command()
def itemsimages():
    """Extract items images"""
    from the_escapists import ItemsImagesExtractor

    app.logger.info('Extracting started')

    app.logger.info('Loading items')

    items = load_json(app.config['ITEMS_FILE'])

    item_ids = [item_id for item_id, item in items.items()]

    app.logger.info('Extracting')

    extractor = ItemsImagesExtractor(item_ids=item_ids, output_dir=app.config['ITEMS_IMAGES_DIR'])
    extractor.extract()

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


@cache.cached(timeout=60 * 60 * 6)
def get_images():
    items_images = {}

    detected_images = glob(os.path.join(app.config['ITEMS_IMAGES_DIR'], '*.*'))

    for detected_image in detected_images:
        detected_image = os.path.splitext(os.path.basename(detected_image))

        items_images[detected_image[0]] = detected_image[1]

    return items_images
