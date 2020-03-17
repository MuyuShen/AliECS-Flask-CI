import pytest
from flask import current_app
from tasks import Bucket


def test_get_bucket_lists(app_content):
    bucket = Bucket('lxq-photo')