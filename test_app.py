import flask
import os
import tempfile
from kafka_producer import app
import json
from flask import request
from unittest.mock import patch

SEND_RESIZING_REQUEST_API_URI = '/images/api/v1/send-resizing-request'


def test_unknown_path():
    with app.app.test_client() as c:
        response = c.get('/bad_uri')
        assert response.status_code == 404


def test_get_method():
    with app.app.test_client() as c:
        response = c.get(SEND_RESIZING_REQUEST_API_URI)
        # Because GET method is not supported
        assert response.status_code == 405


@patch('kafka_producer.app.producer.send')
def test_post_method(send_mock):
    with app.app.test_client() as c:
        with open('test_input.json') as file:
            json_data = json.load(file)
        response = c.post(SEND_RESIZING_REQUEST_API_URI, json=json_data)
        assert response.status_code == 200


def test_post_method_with_empty_json():
    with app.app.test_client() as c:
        response = c.post(SEND_RESIZING_REQUEST_API_URI, json='{}')
        assert response.status_code == 200
