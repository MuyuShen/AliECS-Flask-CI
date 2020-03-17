import os
from web import create_app

app = create_app(os.getenv("FLASK_CONFIG", "default"))


@app.shell_context_processor
def make_shell_context():
    context = dict(app=app)
    return context
