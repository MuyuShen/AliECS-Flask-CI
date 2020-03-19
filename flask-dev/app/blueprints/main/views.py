from flask import Blueprint
from flask import current_app, request, jsonify

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return "welcome to CI/CD world 🌏"


@bp.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.form['file']
        current_app.logger.info(f)
        from app.wheels import put_photo
        name = put_photo(f)
        return {"filename": name}


@bp.route("/download", methods=['GET'])
def download_file():
    filename = request.form['filename']
    from app.wheels import get_photo
    photo = get_photo(filename).resp.read()
    return photo
