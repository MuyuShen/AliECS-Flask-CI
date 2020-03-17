.PHONY: app test

FLASK_APP_NAME='flask-dev/manage.py'

all: app

app:
	FLASK_APP=$(FLASK_APP_NAME) FLASK_ENV='default' flask run --host=0.0.0.0

test:
	FLASK_APP=$(FLASK_APP_NAME) FLASK_ENV='testing' pytest
