import uuid
import oss2
from flask import current_app


def _init_bucket():
    access_key_id = current_app.config['OSS_AK_ID']
    access_key_secret = current_app.config['OSS_AK_SECRET']
    endpoint = current_app.config['OSS_ENDPOINT']
<<<<<<< HEAD
<<<<<<< HEAD

    bucket_name = current_app.config['OSS_SERVER_BUCKET'][current_app.config['ENV']]
    bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
    return bucket


=======
=======
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
    bucket_name = current_app.config['GRAPH_SERVER_BUCKET']
    bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
    return bucket

<<<<<<< HEAD
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
=======
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
def create_unique_name():
    return str(uuid.uuid1())


def put_photo(f, name=None):
    name = name or create_unique_name()
    bucket = _init_bucket()
    bucket.put_object(name, f)
    return name


def get_photo(name):
    bucket = _init_bucket()
    photo = bucket.get_object(name)
    return photo
