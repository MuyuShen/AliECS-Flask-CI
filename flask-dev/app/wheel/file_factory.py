import uuid
import oss2
from flask import current_app


def _init_bucket():
    access_key_id = current_app.config['OSS_AK_ID']
    access_key_secret = current_app.config['OSS_AK_SECRET']
    endpoint = current_app.config['OSS_ENDPOINT']

    bucket_name = current_app.config['OSS_SERVER_BUCKET'][current_app.config['ENV']]
    bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
    return bucket


def create_unique_name():
    return str(uuid.uuid1())


def put_photo(f, name=None):
    name = "{}.jpg".format(name or create_unique_name())
    bucket = _init_bucket()
    bucket.put_object(name, f)
    return name


def get_photo(name):
    bucket = _init_bucket()
    photo = bucket.get_object(name)
    return photo


def file_url(filename):
    endpoint = current_app.config['OSS_PUBPOINT']
    bucket_name = current_app.config['OSS_SERVER_BUCKET'][current_app.config['ENV']]
    return "https://{0}.{1}/{2}".format(bucket_name, endpoint, filename)


def img_preview_url(filename):
    return "{0}/{1}".format(current_app.config['IMG_DOMAIN'], filename)