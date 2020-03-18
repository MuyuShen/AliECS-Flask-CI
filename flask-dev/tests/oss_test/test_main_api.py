import pytest
from flask import current_app, url_for

def test_visit_index(app_content):
    current_app.logger.debug(app_content.app.config['SERVER_NAME'])
    current_app.logger.debug(url_for('main.index'))
    response = app_content.client.get(url_for("main.index"))
    current_app.logger.info(response.data)
    assert response.status_code == 200