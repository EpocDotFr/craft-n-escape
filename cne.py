try:
    from flask_debugtoolbar import DebugToolbarExtension

    has_debug_toolbar_ext = True
except ImportError:
    has_debug_toolbar_ext = False

from logging.handlers import RotatingFileHandler
from flask_assets import Environment, Bundle
from flask_caching import Cache
from flask import Flask
import logging


# -----------------------------------------------------------
# Boot


app = Flask(__name__, static_url_path='')
app.config.from_pyfile('config.py')

app.config['CACHE_TYPE'] = 'filesystem'
app.config['CACHE_DIR'] = 'storage/cache'
app.config['ITEMS_IMAGES_DIR'] = 'static/images/items/{game_version}'
app.config['ITEMS_FILE'] = 'storage/data/{game_version}/items.json'
app.config['RECIPES_FILE'] = 'storage/data/{game_version}/recipes.json'
app.config['ESCAPISTS_WIKI_DOMAIN'] = 'theescapists.gamepedia.com'
app.config['COMPRESS_MIN_SIZE'] = 1024

cache = Cache(app)
assets = Environment(app)

if app.config['ENV'] == 'production':
    from flask_compress import Compress

    Compress(app)

if has_debug_toolbar_ext:
    toolbar = DebugToolbarExtension(app)

assets.cache = 'storage/webassets-cache/'

assets.register('js_home', Bundle('js/common.js', 'js/home.js', filters='jsmin', output='js/home.min.js'))
assets.register('js_recipes_editor', Bundle('js/common.js', 'js/recipes_editor.js', filters='jsmin', output='js/recipes_editor.min.js'))
assets.register('css_app', Bundle('css/app.css', filters='cssutils', output='css/app.min.css'))

handler = RotatingFileHandler('storage/logs/errors.log', maxBytes=10000000, backupCount=2)
handler.setLevel(logging.WARNING)
formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d/%m/%Y %H:%M:%S')
handler.setFormatter(formatter)
app.logger.addHandler(handler)

from helpers import *


# -----------------------------------------------------------
# After-init imports


import routes
import commands
import hooks
