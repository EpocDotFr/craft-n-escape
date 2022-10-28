try:
    from flask_debugtoolbar import DebugToolbarExtension

    has_debug_toolbar_ext = True
except ImportError:
    has_debug_toolbar_ext = False

from logging.handlers import RotatingFileHandler
from flask_assets import Environment, Bundle
from flask_caching import Cache
from environs import Env
from flask import Flask
import logging


# -----------------------------------------------------------
# Boot


env = Env()
env.read_env()


app = Flask(__name__, static_url_path='')

app.config.update(
    SECRET_KEY=env.str('SECRET_KEY'),
    CACHE_TYPE='FileSystemCache',
    CACHE_DIR='instance/cache',
    ITEMS_IMAGES_DIR='static/images/items/{game_version}',
    ITEMS_FILE='data/{game_version}/items.json',
    RECIPES_FILE='data/{game_version}/recipes.json',
    ESCAPISTS_WIKI_DOMAIN='theescapists.gamepedia.com',
    COMPRESS_MIN_SIZE=1024,
)

cache = Cache(app)
assets = Environment(app)

if not app.config['DEBUG']:
    from flask_compress import Compress

    Compress(app)

if has_debug_toolbar_ext:
    toolbar = DebugToolbarExtension(app)

assets.cache = 'instance/webassets-cache/'

assets.register('js_home', Bundle('js/common.js', 'js/home.js', filters='jsmin', output='js/home.min.js'))
assets.register('js_recipes_editor', Bundle('js/common.js', 'js/recipes_editor.js', filters='jsmin', output='js/recipes_editor.min.js'))
assets.register('css_app', Bundle('css/app.css', filters='cssutils', output='css/app.min.css'))

handler = RotatingFileHandler('instance/logs/errors.log', maxBytes=10000000, backupCount=2)
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
