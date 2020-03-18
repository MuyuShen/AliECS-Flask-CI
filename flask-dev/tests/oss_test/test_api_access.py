import pytest
from flask import current_app
from tests.func.file_generator import random_file, random_string


@pytest.fixture(scope='module')
def test_bucket_access(app_content):
    import oss2
    access_key_id = current_app.config['OSS_AK_ID']
    access_key_secret = current_app.config['OSS_AK_SECRET']
    endpoint = current_app.config['OSS_ENDPOINT']
    bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, 'lxq-photo')
    bucketinfo = bucket.get_bucket_info()
    assert bucketinfo.name == 'lxq-photo'
    return bucket


@pytest.fixture()
def test_create_file():
    filename = random_file("test_only")
    yield filename
    import os
    assert filename in os.listdir()
    os.remove(filename)


def test_upload_success(test_bucket_access, test_create_file):
    bucket = test_bucket_access
    bucket_stat = bucket.get_bucket_stat()
    count_before_upload = bucket_stat.object_count
    current_app.logger.info('storage: ' + str(bucket_stat.storage_size_in_bytes))
    current_app.logger.info('object count: ' + str(bucket_stat.object_count))
    current_app.logger.info('multi part upload count: ' + str(bucket_stat.multi_part_upload_count))
    filename = test_create_file
    # 也可以直接调用分片上传接口。
    # 首先可以用帮助函数设定分片大小，设我们期望的分片大小为128KB
    import os
    import oss2
    total_size = os.path.getsize(filename)
    current_app.logger.info('filesize: ' + str(total_size))
    part_size = oss2.determine_part_size(total_size, preferred_size=128 * 1024)
    # 初始化分片上传，得到Upload ID。接下来的接口都要用到这个Upload ID。
    key = '{0}.txt'.format(random_string(10))
    upload_id = bucket.init_multipart_upload(key).upload_id

    # 逐个上传分片
    # 其中oss2.SizedFileAdapter()把fileobj转换为一个新的文件对象，新的文件对象可读的长度等于size_to_upload
    with open(filename, 'rb') as fileobj:
        parts = []
        part_number = 1
        offset = 0
        while offset < total_size:
            size_to_upload = min(part_size, total_size - offset)
            result = bucket.upload_part(key, upload_id, part_number,
                                        oss2.SizedFileAdapter(fileobj, size_to_upload))
            parts.append(oss2.models.PartInfo(part_number, result.etag, size = size_to_upload, part_crc = result.crc))

            offset += size_to_upload
            part_number += 1

        # 完成分片上传
        bucket.complete_multipart_upload(key, upload_id, parts)
    count_after_upload = bucket.get_bucket_stat().object_count
    assert count_before_upload < count_after_upload
    

def test_download_success(test_bucket_access):
    import os
    import oss2
    bucket = test_bucket_access
    key = 'remote-multipart2.txt'
    filename = 'test_download_success.txt'
    oss2.resumable_download(bucket, key, filename,
                        multiget_threshold=200*1024,
                        part_size=100*1024,
                        num_threads=3)
    assert filename in os.listdir()
    os.remove(filename)