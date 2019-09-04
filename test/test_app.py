import flask
import os
import tempfile
import json
from flask import request
from unittest.mock import patch
import importlib.util
import sys
from kafka_producer import app

SEND_RESIZING_REQUEST_API_URI = '/images/api/v1/send-resizing-request'
SEND_IMAGES_API = '/images/api/v1/send-images'

TEST_FILE_WITH_IMAGE_LINKS = './test/test_input_with_image_links.json'
TEST_PAYLOAD_TO_STORE_IMAGES = './test/test_payload_to_store_images.json'


def test_unknown_path():
    with app.app.test_client() as c:
        response = c.get('/bad_uri')
        assert response.status_code == 404


def test_post_resize_request_with_get_method():
    with app.app.test_client() as c:
        response = c.get(SEND_RESIZING_REQUEST_API_URI)
        # Because GET method is not supported
        assert response.status_code == 405


def test_post_resize_request_with_empty_json():
    with app.app.test_client() as c:
        response = c.post(SEND_RESIZING_REQUEST_API_URI, json='{}')
        assert response.status_code == 200


@patch('kafka_producer.app.producer.send')
def test_post_resize_request(send_mock):
    with app.app.test_client() as c:
        with open(TEST_FILE_WITH_IMAGE_LINKS) as file:
            json_data = json.load(file)
        response = c.post(SEND_RESIZING_REQUEST_API_URI, json=json_data)
        assert response.status_code == 200


def test_store_processed_images():
    with app.app.test_client() as c:
        with open(TEST_PAYLOAD_TO_STORE_IMAGES) as file:
            json_data = json.load(file)
        response = c.post(SEND_IMAGES_API, json=json_data)
        assert response.status_code == 200


# def test_get_image(image_id):
#     with app.app.test_client() as c:
#         response = c.get(GET_IMAGE_API)
#         assert response.status_code == 200
