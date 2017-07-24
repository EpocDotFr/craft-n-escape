# Craft N' Escape

Items and crafting recipes for [The Escapists](http://escapistgame.com/), on one searchable page. Available at [craft-n-escape.epoc.fr](https://craft-n-escape.epoc.fr/).

_Because everyone loves it when a plan comes together_

## Features

  - Web-based
  - List of all available items with all their attributes (attack power, illegal, price, etc)
    - Can be filtered by item name
    - Crafting recipes
    - Links to [The Escapists wiki](http://theescapists.gamepedia.com/)
    - (WIP) Items image
  - Given a list of items you own, you can get the list of items you can craft
  - (Internal) Crafting recipes editor (used to convert The Escapists crafting recipes format to the Craft N' Escape one)
  - (WIP) (Internal) Items image editor (used to assign items image from The Escapists wiki)

## Prerequisites

  - Should work on any Python 3.x version. Feel free to test with another Python version and give me feedback
  - A [uWSGI](https://uwsgi-docs.readthedocs.io/en/latest/)-capable web server (optional, but recommended)
  - (Optional) The Escapists game, if you need to extract the items data

## Installation

  1. Clone this repo somewhere
  2. `pip install -r requirements.txt`
  3. (Optional) `export FLASK_APP=cnc.py` (Windows users: `set FLASK_APP=cnc.py`)
  4. (Optional) `flask itemsdata --gamedir="path to the game root directory"`

## Configuration

Copy the `config.example.py` file to `config.py` and fill in the configuration parameters.

Available configuration parameters are:

  - `SECRET_KEY` Set this to a complex random value
  - `DEBUG` Enable/disable debug mode
  - `LOGGER_HANDLER_POLICY` Policy of the default logging handler

More informations on the three above can be found [here](http://flask.pocoo.org/docs/0.12/config/#builtin-configuration-values).

  - `ESCAPISTS_WIKI_USERNAME` and `ESCAPISTS_WIKI_PASSWORD` Bot credentials to use The Escapists Wiki API
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

A Flask command (`flask itemsdata`) can be used to regenerate the items listing file, i.e when the game has been
updated. Run `flask itemsdata --help` for more information.

## How it works

This project is mainly powered by [Flask](http://flask.pocoo.org/) (Python) for the backend and
[Vue.js](http://vuejs.org/) 2 for the frontend.

Data is stored in [JSON](https://en.wikipedia.org/wiki/JSON) files:

  - `storage/data/items.json` is built by the `flask itemsdata` command by parsing the game's files (the `Data/items_*.dat` ones). It contains all items information.
  - `storage/data/recipes.json` contains all crafting recipes of the items contained in the file above.
  - `storage/data/images.json` stores the relation between an item in Craft N' Escape and an item image on The Escapists wiki. Items image are stored locally in `static/images/items`.

A recipes editor (only available locally at `http://localhost:8080/recipes-editor`) is used to convert
The Escapists crafting recipes format to the Craft N' Escape one.

An items image editor (only available locally at `http://localhost:8080/items-image-editor`) is used to
assign The Escapists wiki items image to items in Craft N' Escape.

For more information, I suggest you do dive into the code starting with the `cnc.py` file.

## Credits

  - Logo, items image, The Escapists © 2015 - 2017 Mouldy Toof Studios / Team17 Digital (items image are pulled from The Escapists wiki)
  - This project isn't supported nor endorsed by Mouldy Toof Studios / Team17 Digital
