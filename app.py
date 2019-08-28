from flask import Flask, make_response, jsonify, request, send_file
from PIL import Image
import requests
from io import BytesIO
import logging
logger = logging.getLogger('ftpuploader')
app = Flask(__name__)


@app.route('/images/api/v1/resize', methods=['GET'])
def index():
    image_url = request.args.get('image_url')
    return handle_image_url(image_url)
    # return 'hi'


def handle_image_url(image_url):
    # what happens if image is less than 100*100
    # handle exception if url does not point to an image
    # change to json and take many images as input in a single request
    # cache if same URL is given repeatedly
    # an option: store all output images and give the user URLs to view them
    # for production app as well, it would be better to host all images in S3
    # if they build up, then they need to be cleaned
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
        logger.warning('The given url does not point to an image! \nException: \n' + str(e))
    img.thumbnail(size, Image.ANTIALIAS)
    return serve_pil_image(img)


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
