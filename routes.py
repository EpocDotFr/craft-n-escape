from flask import render_template, abort, request, flash
from helpers import *
from cne import app


@app.route('/')
@app.route('/<int:item_id>-<item_slug>')
@app.route('/<int:game_version>')
@app.route('/<int:game_version>/<int:item_id>-<item_slug>')
def home(game_version=1, item_id=None, item_slug=None):
    items = load_json(app.config['ITEMS_FILE'].format(game_version=game_version))
    recipes = load_json(app.config['RECIPES_FILE'].format(game_version=game_version))

    items = merge_recipe_items_in_items(items, recipes)
    items = set_items_permalink(items, game_version=game_version)

    if game_version == 1:
        images = get_images(game_version=game_version)
        items = merge_images_in_items(items, images)

    permalink_item = get_item_by_id(items, item_id) if item_id else None

    return render_template(
        'home.html',
        items=items,
        game_version=game_version,
        permalink_item=permalink_item
    )


@app.route('/recipes-editor')
def recipes_editor():
    if not is_local(): # Can only edit crafting recipes locally
        abort(404)

    game_version = 1 # TODO

    items = load_json(app.config['ITEMS_FILE'].format(game_version=game_version))
    recipes = load_json(app.config['RECIPES_FILE'].format(game_version=game_version))

    items = get_items_with_recipe(items) # Only get items with a crafting recipe

    # Highlight items with crafting recipe but not in the Craft N' Escape recipes file
    # Also highlight items with no up-to-date crafting recipe in comparison of the game's one
    items = get_items_for_recipes_editor(items, recipes)

    if game_version == 1:
        images = get_images(game_version=game_version)
        items = merge_images_in_items(items, images)

    return render_template(
        'recipes_editor/home.html',
        items=items
    )


@app.route('/recipes-editor/<item_id>', methods=['GET', 'POST'])
def recipes_editor_item(item_id):
    if not is_local(): # Can only edit crafting recipes locally
        abort(404)

    game_version = 1 # TODO

    items = load_json(app.config['ITEMS_FILE'].format(game_version=game_version))
    recipes = load_json(app.config['RECIPES_FILE'].format(game_version=game_version))

    # Highlight items with crafting recipe but not in the Craft N' Escape recipes file
    # Also highlight items with no up-to-date crafting recipe in comparison of the game's one
    items = get_items_for_recipes_editor(items, recipes)

    if game_version == 1:
        images = get_images(game_version=game_version)
        items = merge_images_in_items(items, images)

    if item_id not in items:
        abort(404)

    if request.method == 'POST':
        recipe_hash = request.form.get('_recipe_hash')
        recipe_items = json.loads(request.form.get('recipe_items'))

        try:
            if item_id not in recipes:
                recipes[item_id] = {}

            recipes[item_id]['_recipe_hash'] = recipe_hash
            recipes[item_id]['items'] = recipe_items

            save_json(app.config['RECIPES_FILE'].format(game_version=game_version), recipes)

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
