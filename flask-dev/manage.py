import os
from app import create_app

app = create_app(os.getenv("FLASK_ENV", "production"))


@app.shell_context_processor
def make_shell_context():
    context = dict(app=app)
    return context


if __name__ == "__main__":
    app.run(debug=True)