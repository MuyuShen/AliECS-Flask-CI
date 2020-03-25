from flask import Blueprint
from flask import current_app, request, abort
<<<<<<< HEAD
<<<<<<< HEAD
from app.wheel import put_photo, get_photo

=======
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
=======
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    return "welcome to CI/CD world 🌏"


@bp.route("/upload", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        f = request.files['file'].read()
<<<<<<< HEAD
<<<<<<< HEAD
=======
        from app.wheel import put_photo
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
=======
        from app.wheel import put_photo
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
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
<<<<<<< HEAD
<<<<<<< HEAD
=======
    from app.wheel import get_photo
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
=======
    from app.wheel import get_photo
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
    photo = get_photo(filename).resp.read()
    return photo
