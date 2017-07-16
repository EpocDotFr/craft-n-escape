from flask import Flask, render_template, make_response, request, abort
from werkzeug.exceptions import HTTPException
from configparser import ConfigParser
from urllib.parse import urlparse
from hashlib import md5
import logging
import click
import json
import sys
import os


# -----------------------------------------------------------
# Boot


app = Flask(__name__, static_url_path='')
app.config.from_pyfile('config.py')

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
    items = load_data(app.config['ITEMS_FILE'])

    return render_template('home.html', items=items)


@app.route('/recipes-editor')
def recipes_editor():
    url = urlparse(request.url_root)

    if url.hostname != 'localhost': # Can only edit crafting recipes locally
        abort(403)

    items = load_data(app.config['ITEMS_FILE'], toJson=True)

    return render_template('recipes_editor/home.html', items=items)


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

        items = []

        with open(items_file, 'r') as f:
            items_file_content = f.readlines()[1:] # Removes the first line
            items_file_content = '\n'.join(items_file_content)

        items_parser = ConfigParser(interpolation=None)
        items_parser.read_string(items_file_content)

        for item_id in items_parser.sections():
            item = {}
            item['id'] = int(item_id)

            for name, value in items_parser.items(item_id):
                value = self._get_item_attribute_value(name, value)

                item[name] = value

            items.append(item)

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

        # for item in value.split(','):
        #     item = item.strip().rsplit(' x', maxsplit=1)

        #     if len(item) == 1:
        #         item_name = item[0].strip()
        #         amount = 1
        #     else:
        #         item_name = item[0].strip()
        #         amount = int(item[1].strip())

        #     craft['items'].append({
        #         'name': item_name,
        #         'amount': amount
        #     })

        return craft


# -----------------------------------------------------------
# CLI commands


@app.cli.command()
@click.option('--gamedir', '-g', help='Game root directory')
def build(gamedir):
    """Extract data from items_eng.dat """

    if not gamedir:
        context = click.get_current_context()

        click.echo(build.get_help(context))
        context.exit()

    app.logger.info('Build started')

    items_parser = ItemsParser(gamedir)
    items = items_parser.parse()

    save_data(app.config['ITEMS_FILE'], items, toJson=True)

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
# Helpers


def load_data(file, toJson=False):
    data = None

    if not os.path.isfile(file):
        raise FileNotFoundError('The {} file does not exists'.format(file))

    with open(file, 'r') as f:
        data = f.read()

    return json.loads(data) if toJson and data else data


def save_data(file, data, toJson=False):
    data = json.dumps(data) if toJson else data

    with open(file, 'w') as f:
        f.write(data)
