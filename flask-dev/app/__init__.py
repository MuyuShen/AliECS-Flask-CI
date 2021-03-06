from flask import Flask
from config import config


def _init_errors(app):
    @app.errorhandler(403)
    def page_permission_deny(e):
        return "403", 403

    @app.errorhandler(404)
    def page_not_found(e):
        return "404", 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return "500", 500
    
    @app.errorhandler(406)
    def http_header_error(e):
        return str(e), 406
    
    @app.errorhandler(413)
    def http_header_error(e):
        return str(e), 413


def _register_blueprints(app):
    from .blueprints.main.views import bp as main_bp

    app.register_blueprint(main_bp, url_prefix="/main")


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config[config_name])
    app.config.from_pyfile("config.py", silent=True)
    app.logger.debug("app_configs: {}".format(app.config))

    _init_errors(app)
    _register_blueprints(app)

    return app


