
# Danish String Quartet

import os
import mimetypes

from flask import Flask
from flask import jsonify
from flask import render_template

from google.cloud import storage
from google.oauth2 import service_account

from PIL import Image, ImageDraw

GOOGLE_STORAGE_PROJECT = "StrainChain"
GOOGLE_STORAGE_BUCKET = "strainchain_tokens"

COIN = 'images/coin/pot_token.png'
COIN_PADDING = 3
COIN_SIZE = 400 - COIN_PADDING


app = Flask(__name__)


STRAINS = ['Sour Diesel', 'Alaskan Thunderfuck', 'OG', 'Trainwreck', 'Girlscout Cookies']
@app.route('/api/<name>')
@app.route('/api/<int:token_id>')
@app.route('/api/')
def home_route(name=None, token_id=None):
    if token_id is not None:
        token_id = int(token_id)
        # image_url = _compose_image(token_id)

        # num_first_names = len(FIRST_NAMES)
        # num_last_names = len(LAST_NAMES)
        num_strains = len(STRAINS)
        strain_name = "%s" % (STRAINS[token_id % num_strains])
        strain_name = "%s" % (STRAINS[token_id % num_strains])
        
        return render_template('index.html', name=strain_name)
    else:
        return render_template('index.html', name=name)

@app.route('/api/token/<token_id>')
def token(token_id):
    token_id = int(token_id)
    image_url = _compose_image(token_id)

    # num_first_names = len(FIRST_NAMES)
    # num_last_names = len(LAST_NAMES)
    num_strains = len(STRAINS)
    # strain_name = "%s %s" % (FIRST_NAMES[token_id % num_first_names], LAST_NAMES[token_id % num_last_names])
    strain_name = "%s" % (STRAINS[token_id % num_strains])

    image_url = _compose_image(token_id)

    return jsonify({
        'name': strain_name,
        'description': "A TokinToken to represent your ownership of your strain on the StrainChain.",
        'image': image_url,
        'external_url': 'https://openseacreatures.io/%s' % token_id,
        # 'attributes': attributes
        'attributes': []
    })


@app.route('/api/factory/<token_id>')
def factory(token_id):
    token_id = int(token_id)
    name = "One Strain TokinToken"
    description = "When you purchase this option, you will receive a single OpenSea creature of a random variety. " \
                  "Enjoy and take good care of your aquatic being!"
    image_url = _compose_image(token_id)
    num_inside = 1
    attributes = []
    _add_attribute(attributes, 'number_inside', [num_inside], token_id)

    return jsonify({
        'name': name,
        'description': description,
        'image': image_url,
        'external_url': 'https://openseacreatures.io/%s' % token_id,
        'attributes': attributes
    })


def _add_attribute(existing, attribute_name, options, token_id, display_type=None):
    trait = {
        'trait_type': attribute_name,
        'value': options[token_id % len(options)]
    }
    if display_type:
        trait['display_type'] = display_type
    existing.append(trait)


def _compose_image(token_id, path="token"):

    bkg = Image.new('RGBA', (COIN_SIZE + COIN_PADDING, COIN_SIZE + COIN_PADDING), (0, 0, 0, 0))
    draw = ImageDraw.Draw(bkg)
    draw.ellipse((COIN_PADDING, COIN_PADDING, COIN_SIZE, COIN_SIZE))
    base_img = COIN
    base = Image.open(base_img).convert("RGBA")
    output_path = "images/output/%s.png" % token_id
    composite = Image.alpha_composite(bkg, base)
    composite.save(output_path)

    blob = _get_bucket().blob(f"{path}/{token_id}.png")
    blob.upload_from_filename(filename=output_path)
    return blob.public_url


def _get_bucket():
    credentials = service_account.Credentials.from_service_account_file(
        'credentials.json')
    if credentials.requires_scopes:
        credentials = credentials.with_scopes(
            ['https://www.googleapis.com/auth/devstorage.read_write'])
    client = storage.Client(
        project=GOOGLE_STORAGE_PROJECT, credentials=credentials)
    return client.get_bucket(GOOGLE_STORAGE_BUCKET)


if __name__ == '__main__':
    app.run(debug=True, use_reloader=True)