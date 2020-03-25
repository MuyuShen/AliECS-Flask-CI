from flask import Blueprint
from flask import current_app, request, abort

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return "welcome to CI/CD world 🌏"


@bp.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file'].read()
        from app.wheel import put_photo
        try:
            name = put_photo(f)
        except:
            abort(413, 'Save File Failed')
        from flask import make_response
        resp = make_response({"filename": name})
        resp.headers['Content-Type'] = 'application/json'
        return resp


@bp.route("/download", methods=['GET'])
def download_file():
    filename = request.args.get('filename')
    from app.wheel import get_photo
    photo = get_photo(filename).resp.read()
    return photo
