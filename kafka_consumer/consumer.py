from flask import Flask, make_response, jsonify, request, send_file, send_from_directory, abort
from kafka import KafkaConsumer
# from kafka_producer import app
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

"""This module consumes and processes kafka messages and then updates the status and content of each request in 
the main app
"""
app = Flask(__name__)

# connect to Kafka server and pass the topic we want to consume
consumer = KafkaConsumer(
    'my-topic', group_id='view', bootstrap_servers='kafka:9092',
    api_version=(0, 10, 0),
    value_deserializer=lambda msg: json.loads(msg.value.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    key_deserializer=lambda msg: json.loads(msg.decode('utf-8')))


for msg in consumer:
    logger.warning('Msg is ' + str(msg))
    process_urls(msg.value['urls'])
# Continuously listen to the connection and process messages as recieved


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
    img.save(
        './{image_directory_name}/{unique_filename}.png'.format(**locals()), format='png')
    return '{unique_filename}.png'.format(**locals())


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


# @app.route('/')
# def index():
#     # return a multipart response
#     # logger.warning('Sending to kafka!')
#     return Response(kafkastream())


def kafkastream():
    logger.warning('Sending msg!')
    for msg in consumer:
        logger.warning('Msg is !' + str(msg))
        yield msg


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
