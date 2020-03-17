import pytest
from flask import current_app
from app.oss import Bucket


def test_get_bucket_lists():
    bucket = Bucket('lxq-photo')