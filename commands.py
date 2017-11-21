from helpers import *
from cne import app
import click


@app.cli.command()
@click.option('--gamedir', '-g', help='Game root directory')
def te1_extract_items_data(gamedir):
    """Extract items data from The Escapists 1"""
    from the_escapists import ItemsDataParser

    context = click.get_current_context()

    if not gamedir:
        click.echo(the_escapists.get_help(context))
        context.exit()

    items_file = app.config['ITEMS_FILE'].format(game_version=1)

    if not click.confirm('This will overwrite the {} file. Are you sure?'.format(items_file)):
        context.exit()

    click.echo('Parsing started')

    parser = ItemsDataParser(gamedir)
    items = parser.parse()

    click.echo('Saving {}'.format(items_file))

    save_json(items_file, items)

    click.secho('Done', fg='green')


@app.cli.command()
def te1_extract_items_image():
    """Extract items image from The Escapists 1"""
    from the_escapists import ItemsImagesExtractor

    click.echo('Extracting started')
    click.echo('Do not do anything else until it is finished (you will be noticed)')

    click.echo('Loading items')

    items = load_json(app.config['ITEMS_FILE'].format(game_version=1))

    click.echo('Extracting images')

    extractor = ItemsImagesExtractor(item_ids=items.keys(), output_dir=app.config['ITEMS_IMAGES_DIR'].format(game_version=1))
    extractor.extract()

    click.secho('Done', fg='green')


@app.cli.command()
@click.option('--gamedir', '-g', help='Game root directory')
@click.option('--datadir', '-d', help='Items data files location')
def te2_extract_items_data(gamedir, datadir):
    """Extract items data from The Escapists 2"""
    from the_escapists_2 import ItemsDataExtractor

    context = click.get_current_context()

    if not gamedir or not datadir:
        click.echo(te2_extract_items_data.get_help(context))
        context.exit()

    items_file = app.config['ITEMS_FILE'].format(game_version=2)

    if not click.confirm('This will overwrite the {} file. Are you sure?'.format(items_file)):
        context.exit()

    click.echo('Extracting started')

    extractor = ItemsDataExtractor(gamedir, datadir)
    items = extractor.extract()

    click.echo('Saving {}'.format(items_file))

    save_json(items_file, items)

    click.secho('Done', fg='green')
