from flask_assets import Environment, Bundle
from flask_caching import Cache
from environs import Env
from flask import Flask

# -----------------------------------------------------------
# App bootstrap

env = Env()
env.read_env()

app = Flask(__name__, static_url_path='')

app.config.update(
    # Default config values that may be overwritten by environment values
    SECRET_KEY=env.str('SECRET_KEY'),

    CACHE_TYPE=env.str('CACHE_TYPE', default='FileSystemCache'),
    CACHE_DIR=env.str('CACHE_DIR', default='instance/cache'),

    ASSETS_CACHE=env.str('ASSETS_CACHE', default='instance/webassets-cache'),

    COMPRESS_REGISTER=env.bool('COMPRESS_REGISTER', default=False),
    MINIFY_HTML=env.bool('MINIFY_HTML', default=False),

    # Config values that cannot be overwritten
    ITEMS_IMAGES_DIR='static/images/items/{game_version}',
    ITEMS_FILE='data/{game_version}/items.json',
    RECIPES_FILE='data/{game_version}/recipes.json',
    ESCAPISTS_WIKI_DOMAIN='theescapists.gamepedia.com',
)

# -----------------------------------------------------------
# Debugging-related behaviours

if app.config['DEBUG']:
    import logging

    logging.basicConfig(level=logging.DEBUG)

# -----------------------------------------------------------
# Flask extensions initialization and configuration

# Flask-DebugToolbar
if app.config['DEBUG']:
    try:
        from flask_debugtoolbar import DebugToolbarExtension

        debug_toolbar = DebugToolbarExtension(app)

        app.config.update(
            DEBUG_TB_INTERCEPT_REDIRECTS=env.bool('DEBUG_TB_INTERCEPT_REDIRECTS', False)
        )
    except ImportError:
        pass

# Flask-Compress
try:
    from flask_compress import Compress

    compress = Compress(app)

    app.config.update(
        COMPRESS_MIN_SIZE=env.int('COMPRESS_MIN_SIZE', 512)
    )
except ImportError:
    pass

# Flask-HTMLmin
try:
    from flask_htmlmin import HTMLMIN

    htmlmin = HTMLMIN(app)
except ImportError:
    pass

# Flask-Assets
assets = Environment(app)

assets.register('js_home', Bundle('js/common.js', 'js/home.js', filters='jsmin', output='js/home.min.js'))
assets.register('js_recipes_editor', Bundle('js/common.js', 'js/recipes_editor.js', filters='jsmin', output='js/recipes_editor.min.js'))
assets.register('css_app', Bundle('css/app.css', filters='cssutils', output='css/app.min.css'))

# Flask-Caching
cache = Cache(app)

from helpers import *

# -----------------------------------------------------------
# After-bootstrap imports

import routes
import commands
import hooks
