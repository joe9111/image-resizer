from flask import Flask, make_response, jsonify, request, send_file, send_from_directory, abort
from PIL import Image
from kafka import KafkaProducer
from io import BytesIO
import requests
import logging
import os
import uuid
import concurrent.futures

logger = logging.getLogger('ftpuploader')
app = Flask(__name__)
# connect to Kafka
producer = KafkaProducer(
    bootstrap_servers='localhost:9092', api_version=(0, 10, 0))
# Assign a topic
topic = 'my-topic'


def handle_exception_and_get_response(message, exception):
    logger.warning(message + ' \nException: \n' + str(exception))
    return message


@app.route('/images/api/v1/resize', methods=['POST'])
def post_resize_request():
    """Handle post request from the API and return a json response
    """
    try:
        urls = request.get_json()['urls']
    except Exception as e:
        return handle_exception_and_get_response('The given json input is incorrect!', e)
    logger.warning('Sending to kafka!')
    producer.send(topic, urls.tobytes())
    logger.warning('Message sent to kafka!')
    return process_urls(urls)


def process_urls(urls):
    output_urls = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for file_name_or_error_string in executor.map(compress_and_get_output_filename, urls):
            if ".png" in file_name_or_error_string:
                output_urls.append(
                    request.url_root + 'images/api/v1/get/' + file_name_or_error_string)
            else:
                output_urls.append(file_name_or_error_string)
    output_dictionary = {'resized_images': output_urls}
    return jsonify(output_dictionary)


@app.route('/images/api/v1/get/<path:file_name>', methods=['GET'])
def get_image(file_name):
    return send_from_directory('./static', file_name)

# why is this not covered while testing


def compress_and_get_output_filename(image_url):
    # what if only 1 url is wrong: give proper
    # test with multiple clients
    # load testing
    # https://stackoverflow.com/questions/41454049/finding-the-cause-of-a-brokenprocesspool-in-pythons-concurrent-futures
    # move to mvc architecture:separate controller and service
    # some code comments
    # benchmark performance of kafka vs multithreading etc
    # what happens if image is less than 100*100: orginal is returned
    # if the user is manually looking at the image, he knows it is the same one; if machine is looking at it, ordering is same
        # but still some special case may require mapping of old to new

    # short and friendly output urls
    # cache if same URL is given repeatedly
    # an option: store all output images and give the user URLs to view them
    # for production app as well, it would be better to host all images in S3
    # if they build up, then they need to be cleaned(reason in terms of image size)
    # random url generator for output img: could improve security if all are public
    # if output size is variable , like for github, original images need to be stored else the compressed ones will do
    # auth so one user cannot see another
    # maybe login service
    # an option for user/client to abort request
    # understand docker compose
    try:
        response = requests.get(image_url)
    except Exception as e:
        return handle_exception_and_get_response('Could not open given url! ', e)

    size = 100, 100
    try:
        img = Image.open(BytesIO(response.content))
    except Exception as e:
        return handle_exception_and_get_response('The given url does not point to an image!', e)
    img.thumbnail(size, Image.ANTIALIAS)
    image_directory_name = 'static'
    # succeeds even if directory exists.
    os.makedirs(image_directory_name, exist_ok=True)
    unique_filename = str(uuid.uuid4())
    img.save(
        './{image_directory_name}/{unique_filename}.png'.format(**locals()), format='png')
    return '{unique_filename}.png'.format(**locals())


if __name__ == '__main__':
    app.run(debug=True, threaded=True)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
