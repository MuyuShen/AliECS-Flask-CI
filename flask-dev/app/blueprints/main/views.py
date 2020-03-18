from flask import Blueprint
from flask import current_app

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return "welcome to CI/CD world 🌏"


@bp.route("/upload")
def upload_file():
    if request.method == 'POST':
        f = request.files['file']
        import oss2
        access_key_id = current_app.config['OSS_AK_ID']
        access_key_secret = current_app.config['OSS_AK_SECRET']
        endpoint = current_app.config['OSS_ENDPOINT']
        bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, 'lxq-photo')
        oss2.resumable_upload(bucket, 'test_public_upload.txt', f)
        return "upload success"