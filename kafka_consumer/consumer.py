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


def compress_and_get_output_filename(image_url):
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
    # save and send blobs
    # img.save(
    #     './{image_directory_name}/{unique_filename}.png'.format(**locals()), format='png')
    # return '{unique_filename}.png'.format(**locals())


def process_urls(urls, url_root):
    output_urls = []
    with concurrent.futures.ProcessPoolExecutor() as executor:
        for file_name_or_error_string in executor.map(compress_and_get_output_filename, urls):
            if ".png" in file_name_or_error_string:
                output_urls.append(
                    url_root + 'images/api/v1/get-image/' + file_name_or_error_string)
            else:
                output_urls.append(file_name_or_error_string)
    output_dictionary = {'result': {'resized_images': output_urls}}
    return output_dictionary


# Continuously listen to the connection and process messages as recieved
for msg in consumer:
    logger.warning('Msg is ' + str(msg))
    processed_images = process_urls(msg.value['urls'], msg.value['url_root'])
    processed_images['request_id'] = msg.key
    # requests.post(msg.value['url_root']+'images/api/v1/send-images',
    #               json=processed_images)
    requests.post('http://host.docker.internal:5000/images/api/v1/send-images',
                  json=processed_images)

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
