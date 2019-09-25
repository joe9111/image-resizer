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
import base64
import concurrent.futures
logger = logging.getLogger('ftpuploader')

logger.info("Logger started!")

image_map = {}
INVALID_URL_MESSAGE = 'The given url is invalid! '
# connect to Kafka server and pass the topic we want to consume
consumer = KafkaConsumer(
    'images', bootstrap_servers='kafka:9092',
    api_version=(0, 10, 0),
    value_deserializer=lambda msg: json.loads(msg.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    key_deserializer=lambda msg: json.loads(msg.decode('utf-8')))


def handle_exception_and_get_response(message, exception):
    logger.warning(message + ' \nException: \n' + str(exception))
    return message


def compress_and_get_output_file_name(image_url):
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
    unique_filename = str(uuid.uuid4())
    byte_io = BytesIO()
    img.save(byte_io, 'png')
    img_str = base64.b64encode(byte_io.getvalue()).decode()
    global image_map
    image_map[unique_filename] = img_str
    return unique_filename


def process_urls(urls, url_root):
    output_urls = []
    for url in urls:
        file_name_or_error_string = compress_and_get_output_file_name(url)
        if file_name_or_error_string == INVALID_URL_MESSAGE:
            output_urls.append(file_name_or_error_string)
        else:
            output_urls.append(
                url_root + 'images/api/v1/get-image/' + file_name_or_error_string)
    output_dictionary = {'result': {'resized_images': output_urls}}
    return output_dictionary


def consume_kafka_messages():
    # Continuously listen to the connection and process messages as recieved
    for msg in consumer:
        logger.warning('Processing request ' + str(msg.key))
        processed_images = process_urls(
            msg.value['urls'], msg.value['url_root'])
        processed_images['request_id'] = msg.key
        processed_images['image_map'] = image_map
        logger.warning('Request complete: ' + str(msg.key))
        requests.post('http://host.docker.internal:5000/images/api/v1/send-images',
                      json=processed_images)


logger.info("Consumer starting!")

if __name__ == '__main__':
    consume_kafka_messages()
