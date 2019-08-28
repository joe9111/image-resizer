from flask import Flask, make_response, jsonify, request, send_file
from PIL import Image
from io import BytesIO
import requests
import logging
import os
import uuid

logger = logging.getLogger('ftpuploader')
app = Flask(__name__)


@app.route('/images/api/v1/resize', methods=['POST'])
def index():
    urls = request.get_json()['urls']
    logger.warning('URLs are '+str(urls))
    output_urls = []
    for url in urls:
        output_urls.append(handle_image_url(url))
    output_dictionary = {'compressed_images': output_urls}
    return jsonify(output_dictionary)


def handle_image_url(image_url):
    # some code comments
    # what happens if image is less than 100*100
    # if the user is manually looking at the image, he knows it is the same one; if machine is looking at it, ordering is same
        # but still some special case may require mapping of old to new

    # short and friendly output urls
    # cache if same URL is given repeatedly
    # an option: store all output images and give the user URLs to view them
    # for production app as well, it would be better to host all images in S3
    # if they build up, then they need to be cleaned
    # random url generator for output img: could improve security if all are public
    # if output size is variable , like for github, original images need to be stored else the compressed ones will do

    # search thread pool in python and kafka python client
    try:
        response = requests.get(image_url)
    except Exception as e:
        logger.warning('Could not open given url! \nException: \n' + str(e))
        return 'Could not open given url! '
    size = 100, 100
    try:
        img = Image.open(BytesIO(response.content))
    except Exception as e:
        logger.warning(
            'The given url does not point to an image! \nException: \n' + str(e))
        return 'The given url does not point to an image!'
    img.thumbnail(size, Image.ANTIALIAS)
    # succeeds even if directory exists.
    os.makedirs("./tmp", exist_ok=True)
    unique_filename = str(uuid.uuid4())
    img.save('./tmp/{unique_filename}.png'.format(**locals()), format='png')
    return './tmp/{unique_filename}.png'.format(**locals())


def serve_pil_image(pil_img):
    img_io = BytesIO()
    pil_img.save(img_io, 'JPEG', quality=70)
    img_io.seek(0)
    return send_file(img_io, mimetype='image/jpeg', as_attachment=True, attachment_filename='file.png')


if __name__ == '__main__':
    app.run(debug=True)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
