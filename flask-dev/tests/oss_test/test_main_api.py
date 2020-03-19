import pytest
import mock
from flask import current_app, url_for
from tests.func.file_generator import random_file

def test_visit_index(app_content):
    current_app.logger.debug(app_content.app.config['SERVER_NAME'])
    current_app.logger.debug(url_for('main.index'))
    response = app_content.client.get(url_for("main.index"))
    current_app.logger.info(response.data)
    assert response.status_code == 200


@mock.patch("app.wheels.create_unique_name", mock.Mock(return_value="c764d110-69bf-11ea-8cf0-00163e0405b1"))
def test_upload_file(app_content):
    headers = {'content-type': 'multipart/form-data'}
    payload = {'data': 'aaa'}
    fileobj = b'test_file_upload_success'
    payload.update({'file': fileobj})
    response = app_content.client.post(url_for("main.upload_file"), data=payload, headers=headers)
    assert b"upload success, filename is c764d110-69bf-11ea-8cf0-00163e0405b1" == response.data
    assert response.status_code == 200