# Craft N' Escape

Items and crafting recipes for [The Escapists](http://escapistgame.com/), on one filterable page. Available at [craft-n-escape.epoc.fr](https://craft-n-escape.epoc.fr/).

_Because everyone loves it when a plan comes together_

## Features

  - Web-based
  - List of all available items with all their attributes
    - Can be filtered in many ways (is craftable, is buyable, is illegal, etc)
    - Crafting recipes
    - Links to [The Escapists wiki](http://theescapists.gamepedia.com/)
    - Items image
  - Given a list of items you own, you can get the list of items you can craft
  - (Internal) Crafting recipes editor (used to convert The Escapists crafting recipes format to the Craft N' Escape one)
  - (Internal) Items images extractor
  - Only The Escapists is supported. The Escapists 2 support is - hopefuly - ongoing

## Prerequisites

  - Should work on any Python 3.x version. Feel free to test with another Python version and give me feedback
  - A [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/)-capable web server (optional, but recommended)
  - (Optional) The Escapists game, if you need to extract the items data or images

## Installation

  1. Clone this repo somewhere
  2. `pip install -r requirements.txt`

## Configuration

Copy the `config.example.py` file to `config.py` and fill in the configuration parameters.

Available configuration parameters are:

  - `SECRET_KEY` Set this to a complex random value
  - `DEBUG` Enable/disable debug mode
  - `LOGGER_HANDLER_POLICY` Policy of the default logging handler

More informations on the three above can be found [here](http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values).

  - `GAUGES_SITE_ID` A [Gauges](https://gaug.es/) site ID used to track visits on Craft N' Escape (optional)

I'll let you search yourself about how to configure a web server along uWSGI.

## Usage

  - Standalone

Run the internal web server, which will be accessible at `http://localhost:8080`:

```
python local.py
```

Edit this file and change the interface/port as needed.

  - uWSGI

The uWSGI file you'll have to set in your uWSGI configuration is `uwsgi.py`. The callable is `app`.

  - Others

You'll probably have to hack with this application to make it work with one of the solutions described
[here](http://flask.pocoo.org/docs/0.12/deploying/). Send me a pull request if you make it work.

### Extracting items data

The Flask command `flask te1_extract_items_data` is used to regenerate the items listing file, i.e when the game has been updated.

**This command only works on Windows**, and requires the game to be installed.

  1. `set FLASK_APP=cnc.py`
  2. `flask te1_extract_items_data --gamedir="{path to the game root directory}"`

### Extracting items images

The Flask command `flask te1_extract_items_image` is used to extract items images from the game itself.

**This command only works on Windows**, and requires the game to be already running in any map without any internal game
window opened. The game's window must be visible at all times, and must not be moved or resized.

  1. `pip install -r requirements-dev.txt`
  2. `set FLASK_APP=cnc.py`
  3. `flask te1_extract_items_image`

## How it works

This project is mainly powered by [Flask](http://flask.pocoo.org/) (Python) for the backend and
[Vue.js](http://vuejs.org/) 2 for the frontend.

Data is stored in [JSON](https://en.wikipedia.org/wiki/JSON) files. Why? And why not an [SQLite](https://en.wikipedia.org/wiki/SQLite)
database or some kind of embedded relational database? Because JSON files are easy to read using every programming languages,
even Javascript on the client-side. In addition I didn't want to mess with the SQLite => JSON processing, so instead
we directly use JSON as the data storage format.

  - `storage/data/1/items.json` is built by the `flask te1_extract_items_data` command by parsing the game's files (the `Data/items_*.dat` ones). It contains all items information.
  - `storage/data/1/recipes.json` contains all crafting recipes of the items contained in the file above. A recipes editor (only available locally at `http://localhost:8080/recipes-editor`) is used to convert The Escapists crafting recipes format (simple, unformatted, non-machine friendly text) to the Craft N' Escape one (relation to items IDs).

Items images are extracted using, huh, a brutal solution. Basically, the `flask te1_extract_items_image` command edit the game's
process memory for each existing items by assigning them in your weapon slot. A screenshot of the current weapon is then
taken, the background is converted to a transparent one and the final image saved at `static/images/items/1/{item ID}.png`.

For more information, I suggest you do dive into the code starting with the `cnc.py` file.

## Credits

  - Logos, items image, The Escapists, The Escapists © 2015 - 2017 Mouldy Toof Studios / Team17 Digital
  - This project isn't supported nor endorsed by Mouldy Toof Studios / Team17 Digital

## End words

If you have questions or problems, you can either submit an issue [here on GitHub](https://github.com/EpocDotFr/craft-n-escape/issues)
or in [this Reddit thread](https://www.reddit.com/r/theescapists/comments/6s8ip5/craft_n_escape_all_items_and_crafting_recipes_on/).