import flask
import os
import tempfile
import app
# import pytest
import json
from flask import request


def test_unknown_path():
    with app.app.test_client() as c:
        response = c.get('/bad_uri')
        assert response.status_code == 404


def test_get_method():
    with app.app.test_client() as c:
        response = c.get('/images/api/v1/resize')
        # Because GET method is not supported
        assert response.status_code == 405


def test_post_method():
    with app.app.test_client() as c:
        with open('test_input.json') as file:
            json_data = json.load(file)
            response = c.post('/images/api/v1/resize', json=json_data)
        assert response.status_code == 200
        assert len(response.get_json()['resized_images']) == len(
            json_data['urls'])
        get_image_response = c.get(response.get_json()['resized_images'][0])
        assert get_image_response.status_code == 200


def test_post_method_with_empty_json():
    with app.app.test_client() as c:
        response = c.post('/images/api/v1/resize', json='{}')
        assert response.status_code == 200
