"""This module listens to and serves all requests from the client.
It also acts as a producer of kafka messages.
"""
from flask import Flask, make_response, jsonify, request, send_file, send_from_directory, abort
from PIL import Image
from kafka import KafkaProducer
from io import BytesIO
import requests
import logging
import os
import uuid
import base64
import concurrent.futures
import json
import psycopg2
import io

logger = logging.getLogger('ftpuploader')

# This basically acts as an in-memory database and stores the contents of
# each request.
# Instead of db, store request ids and responses as a dict for now
# The consumer service will write to this dict after processing
request_map = {}
image_map = {}
app = Flask(__name__)

# connect to Kafka
producer = KafkaProducer(
    bootstrap_servers='kafka:9092', api_version=(0, 10, 0),
    value_serializer=lambda msg: json.dumps(msg).encode('utf-8'),
    key_serializer=lambda msg: json.dumps(msg).encode('utf-8'))

# Assign a topic
topic = 'my-topic'


@app.route('/images/api/v1/send-images', methods=['POST'])
def store_processed_images():
    """Handle post request from the consumer microservice and store the 
    response received after processing
    """
    processed_images = request.get_json()
    logger.warning(processed_images)
    # This can be replaced by an "Insert in DB" step
    logger.warning('Received result for request: ' +
                   processed_images['request_id'])
    request_map[processed_images['request_id']] = processed_images['result']
    image_map.update(processed_images['image_map'])
    return 'Success!'


@app.route('/images/api/v1/send-request', methods=['POST'])
def post_resize_request():
    """Handle post request from the main client API and return the request_id using which the client can access the 
    result later
    """
    try:
        kafka_message = request.get_json()
    except Exception as e:
        return ('The given json input is incorrect!')
    request_id = str(uuid.uuid4())
    kafka_message['url_root'] = request.url_root
    logger.info('Sending to kafka!')
    producer.send(topic, key=request_id, value=kafka_message)
    producer.flush()
    logger.warning('Message sent to kafka!')
    request_map[request_id] = 'Your request is being processed'
    return {'request': request.url_root + 'images/api/v1/get-request/' + request_id}


@app.route('/images/api/v1/get-image/<path:file_name>', methods=['GET'])
def get_image(file_name):
    # return send_from_directory('./static', file_name)
    if file_name in image_map:
        return send_file(
            BytesIO(base64.b64decode(image_map[file_name])),
            mimetype='image/png')
    return 'Image not found, please try again...'


@app.route('/images/api/v1/get-request/<string:request_id>', methods=['GET'])
def get_request(request_id):
    """Handle request to get the result of an image processing request return a json 
    response
    """
    if request_id in request_map:
        return request_map[request_id]
    return 'Request not found, please try again...'
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)


@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)
