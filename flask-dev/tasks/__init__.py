import time
import os

import oss2
from config import OSS_AK_ID as access_key_id
from config import OSS_AK_SECRET as access_key_secret
from config import OSS_ENDPOINT as endpoint


class Bucket:
    def __init__(self, bucket_name):
        self = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, bucket_name)
