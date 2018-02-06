from helpers import *
from cne import app
import click


@app.cli.command()
@click.option('--gamedir', '-g', help='Game root directory')
def te1_extract_items_data(gamedir):
    """Extract items data from The Escapists 1."""
    from the_escapists.one import ItemsDataParser

    context = click.get_current_context()

    if not gamedir:
        click.echo(te1_extract_items_data.get_help(context))
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
    """Extract items image from The Escapists 1."""
    from the_escapists.one import ItemsImagesExtractor

    click.echo('Extraction started')
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
    """Extract items data from The Escapists 2."""
    from the_escapists.two import ItemsDataExtractor

    context = click.get_current_context()

    if not gamedir or not datadir:
        click.echo(te2_extract_items_data.get_help(context))
        context.exit()

    items_file = app.config['ITEMS_FILE'].format(game_version=2)

    if not click.confirm('This will overwrite the {} file. Are you sure?'.format(items_file)):
        context.exit()

    click.echo('Extraction started')

    extractor = ItemsDataExtractor(gamedir, datadir)
    items = extractor.extract()

    click.echo('Saving {}'.format(items_file))

    save_json(items_file, items)

    click.secho('Done', fg='green')


@app.cli.command()
def generate_sitemap():
    """Generate the sitemap.xml file."""
    from lxml import etree

    click.echo('Generation started')

    sitemap_entries = [
        'https://craft-n-escape.com',
        'https://craft-n-escape.com/2'
    ]

    for game_version in [1, 2]:
        click.echo('Loading items from The Escapists {}'.format(game_version))

        items = load_json(app.config['ITEMS_FILE'].format(game_version=game_version))

        for item_id, item in items.items():
            if game_version == 1:
                url = 'https://craft-n-escape.com/'
            elif game_version == 2:
                url = 'https://craft-n-escape.com/2/'

            url += item_id + '-' + item['name_slug']

            sitemap_entries.append(url)

    click.echo('Generating XML tree')

    urlset_node = etree.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')

    for sitemap_entry_url in sitemap_entries:
        url_node = etree.SubElement(urlset_node, 'url')

        loc_node = etree.SubElement(url_node, 'loc')
        loc_node.text = sitemap_entry_url

    sitemap = etree.ElementTree(urlset_node)

    click.echo('Saving')

    with open('static/sitemap.xml', 'wb') as f:
        sitemap.write(f, encoding='utf-8', xml_declaration=True)

    click.secho('Done', fg='green')
