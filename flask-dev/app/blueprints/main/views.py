from flask import Blueprint
from flask import current_app, request, abort
from app.wheel import put_photo, get_photo, file_url, img_preview_url


bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return "welcome to CI/CD world 🌏"


@bp.route("/upload/jpg", methods=['GET', 'POST'])
def upload_jpg():
    if request.method == 'POST':
        try:
            f = request.files['file'].read()
        except Exception as e:
            current_app.logger.debug(e)
            current_app.logger.debug("file_data: {}".format(request.files))
            abort(406, '上传文件格式错误')
        try:
            name = put_photo(f)
        except Exception as e:
            current_app.logger.debug(e)
            abort(413, 'Save File Failed')
        from flask import make_response
        url = file_url(name)
        preview = img_preview_url(name)
        resp = make_response({"filename": name, "url": url, "preview": preview})
        resp.headers['Content-Type'] = 'application/json'
        return resp


@bp.route("/download", methods=['GET'])
def download_file():
    filename = request.args.get('filename')
    photo = get_photo(filename).resp.read()
    return photo
