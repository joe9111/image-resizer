"""This module consumes and processes kafka messages and then updates the status and content of each request in 
the main app
"""
from flask import Flask, make_response, jsonify, request, send_file, send_from_directory, abort
from kafka import KafkaConsumer
import logging
from PIL import Image
import json
import requests
import logging
import os
import uuid
from io import BytesIO
import concurrent.futures
logger = logging.getLogger('ftpuploader')


app = Flask(__name__)
INVALID_URL_MESSAGE = 'The given url is invalid! '
# connect to Kafka server and pass the topic we want to consume
consumer = KafkaConsumer(
    'my-topic', group_id='view', bootstrap_servers='kafka:9092',
    api_version=(0, 10, 0),
    value_deserializer=lambda msg: json.loads(msg.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    key_deserializer=lambda msg: json.loads(msg.decode('utf-8')))


def handle_exception_and_get_response(message, exception):
    logger.warning(message + ' \nException: \n' + str(exception))
    return message


def compress_and_get_output_file(image_url):
    try:
        response = requests.get(image_url)
    except Exception as e:
        return handle_exception_and_get_response(INVALID_URL_MESSAGE, e)

    size = 100, 100
    try:
        img = Image.open(BytesIO(response.content))
    except Exception as e:
        return handle_exception_and_get_response(INVALID_URL_MESSAGE, e)
    img.thumbnail(size, Image.ANTIALIAS)
    image_directory_name = 'static'
    # succeeds even if directory exists.
    os.makedirs(image_directory_name, exist_ok=True)
    unique_filename = str(uuid.uuid4())
    byte_io = BytesIO()
    img.save(byte_io, 'png')
    byte_io.seek(0)
    global image_map
    image_map[unique_filename] = byte_io
    # return img
    # save and send blobs
    # create image map id:img_object
    # create request to images map: 1 to many
    # img.save(
    #     './{image_directory_name}/{unique_filename}.png'.format(**locals()), format='png')
    return '{unique_filename}.png'.format(**locals())


def process_urls(urls, url_root):
    output_urls = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for file_or_error_string in executor.map(compress_and_get_output_file, urls):
            if ".png" in file_or_error_string:
                output_urls.append(
                    url_root + 'images/api/v1/get-image/' + file_or_error_string)
            else:
                output_urls.append(file_or_error_string)
    output_dictionary = {'result': {'resized_images': output_urls}}
    return output_dictionary


# image_map = {}

# Continuously listen to the connection and process messages as recieved
for msg in consumer:
    global image_map
    image_map = {}
    logger.warning('Msg is ' + str(msg))
    processed_images = process_urls(msg.value['urls'], msg.value['url_root'])
    processed_images['request_id'] = msg.key
    processed_images['image_map']=image_map
    requests.post('http://host.docker.internal:5000/images/api/v1/send-images',
                  processed_images)
    # requests.post('http://host.docker.internal:5000/images/api/v1/send-images',
    #               json=processed_images)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
