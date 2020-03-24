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


@pytest.fixture()
def test_upload_file(app_content):
    headers = {'content-type': 'multipart/form-data'}
    filename = random_file('uploadtest.test.pytest')
    files = {'file': (filename, 'multipart/form-data')}
    response = app_content.client.post(url_for("main.upload_file"), data=files, headers=headers)
    import json
    filename = json.loads(response.data)['filename']
    yield filename
    import uuid
    try:
        current_app.logger.info(uuid.UUID(filename))
    except:
        raise "not an uuid name"
    assert response.status_code == 200


def test_download_file(app_content, test_upload_file):
    filename = test_upload_file
    headers = {'content-type': 'multipart/form-data'}
    payload = {'data': 'aaa'}
    payload.update({'filename': filename})
    response = app_content.client.get(url_for("main.download_file"), data=payload, headers=headers)
    assert response.status_code == 200