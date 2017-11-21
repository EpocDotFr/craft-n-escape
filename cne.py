from flask import Flask, render_template, make_response, request
from logging.handlers import RotatingFileHandler
from werkzeug.exceptions import HTTPException
from flask_caching import Cache
import logging
import os


# -----------------------------------------------------------
# Boot


app = Flask(__name__, static_url_path='')
app.config.from_pyfile('config.py')

app.config['LOGGER_HANDLER_POLICY'] = 'production'
app.config['CACHE_TYPE'] = 'filesystem'
app.config['CACHE_DIR'] = 'storage/cache'
app.config['ITEMS_IMAGES_DIR'] = 'static/images/items/{game_version}'
app.config['ITEMS_FILE'] = 'storage/data/{game_version}/items.json'
app.config['RECIPES_FILE'] = 'storage/data/{game_version}/recipes.json'
app.config['ESCAPISTS_WIKI_DOMAIN'] = 'theescapists.gamepedia.com'

cache = Cache(app)

handler = RotatingFileHandler('storage/logs/errors.log', maxBytes=25000, backupCount=2)
handler.setLevel(logging.WARNING)
formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

from helpers import *

app.jinja_env.globals.update(is_local=is_local)


# -----------------------------------------------------------
# After-init imports


import routes
import commands


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
# Hooks


@app.url_defaults
def hashed_static_file(endpoint, values):
    """Add a cache-buster value in the URL of each static assets."""
    if endpoint == 'static':
        filename = values.get('filename')

        if filename:
            blueprint = request.blueprint

            if '.' in endpoint:
                blueprint = endpoint.rsplit('.', 1)[0]

            static_folder = app.static_folder

            if blueprint and app.blueprints[blueprint].static_folder:
                static_folder = app.blueprints[blueprint].static_folder

            fp = os.path.join(static_folder, filename)

            if os.path.exists(fp):
                values[int(os.stat(fp).st_mtime)] = ''
