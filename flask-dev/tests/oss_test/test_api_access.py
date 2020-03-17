import pytest
from flask import current_app


def test_access_bucket_success(app_content):
    import oss2
    access_key_id = current_app.config['OSS_AK_ID']
    access_key_secret = current_app.config['OSS_AK_SECRET']
    endpoint = current_app.config['OSS_ENDPOINT']
    bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, 'lxq-photo')
    bucketinfo = bucket.get_bucket_info()
    assert bucketinfo.name == 'lxq-photo'