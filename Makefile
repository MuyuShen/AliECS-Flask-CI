.PHONY: app test test-one

FLASK_APP_NAME='flask-dev/manage.py'

all: app

app:
	FLASK_APP=$(FLASK_APP_NAME) FLASK_ENV='default' flask run --host=0.0.0.0

test:
	FLASK_APP=$(FLASK_APP_NAME) FLASK_ENV='testing' pytest -o log_cli=true -o log_cli_level=INFO

test-one:
	FLASK_APP=$(FLASK_APP_NAME) FLASK_ENV='testing' pytest flask-dev/tests/oss_test/test_main_api.py -o log_cli=true -o log_cli_level=INFO
