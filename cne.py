from logging.handlers import RotatingFileHandler
from flask_caching import Cache
from flask import Flask
import logging


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

handler = RotatingFileHandler('storage/logs/errors.log', maxBytes=10000000, backupCount=2)
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
import hooks
