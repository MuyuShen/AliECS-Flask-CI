import pytest
from flask import current_app, url_for
from tests.func.file_generator import random_file

def test_visit_index(app_content):
    current_app.logger.debug(app_content.app.config['SERVER_NAME'])
    current_app.logger.debug(url_for('main.index'))
    response = app_content.client.get(url_for("main.index"))
    current_app.logger.info(response.data)
    assert response.status_code == 200


def test_upload_file(app_content):
    headers = {'content-type': 'multipart/form-data'}
    payload = {'data': 'aaa'}
    fileobj = b'test_file_upload_success'
    payload.update({'file': fileobj})
    response = app_content.client.post(url_for("main.upload_file"), data=payload, headers=headers)
    assert response.data == b"upload success"
    assert response.status_code == 200