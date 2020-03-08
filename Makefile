.PHONY: app shell

FLASK_APP_NAME='flask-dev/app.py'

all: app

app:
	FLASK_APP=$(FLASK_APP_NAME) FLASK_ENV='default' flask run --host=0.0.0.0

shell:
	FLASK_APP=$(FLASK_APP_NAME) FLASK_ENV='development' flask shell