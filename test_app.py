import flask
import os
import tempfile
import app
import pytest
import json
from flask import request


# @pytest.fixture
# def client():
#     yield app


# app = flask.Flask(__name__)


def test_unknown_path():
    with app.app.test_client() as c:
        response = c.get('/bad_uri')
        assert response.status_code == 404
        response = c.get('/images/api/v1/resize')
        # Because GET method is not supported
        assert response.status_code == 405

# test with bad,incomplete json etc
# search: python testing: different function for each test?


def test_2():
    with app.app.test_client() as c:
        with open('test_input.json') as file:
            json_data = json.load(file)
            response = c.post('/images/api/v1/resize', json=json_data)
        assert response.status_code == 200
        assert len(response.get_json()['resized_images']) == len(json_data['urls'])


def test_3():
    with app.app.test_client() as c:
        response = c.post('/images/api/v1/resize', json='{}')
        assert response.status_code == 200
