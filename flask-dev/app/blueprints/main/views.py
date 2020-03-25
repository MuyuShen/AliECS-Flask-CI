from flask import Blueprint
from flask import current_app, request

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return "welcome to CI/CD world 🌏"


@bp.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.form['file']
        current_app.logger.info(f)
        import oss2
        access_key_id = current_app.config['OSS_AK_ID']
        access_key_secret = current_app.config['OSS_AK_SECRET']
        endpoint = current_app.config['OSS_ENDPOINT']
        bucket = oss2.Bucket(oss2.Auth(access_key_id, access_key_secret), endpoint, 'lxq-photo')
        bucket.put_object('upload_file_test.txt', f)
        return "upload success"