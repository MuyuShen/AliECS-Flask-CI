.PHONY: app test

FLASK_APP_NAME='flask-dev/manage.py'
Ali_OSS_AK_ID='<你的access_key_id>'
Ali_OSS_AK_SECRET='<你的access_key_secret>'
Ali_OSS_ENDPOINT='<你的服务器访问域名>'

all: app

app:
	FLASK_APP=$(FLASK_APP_NAME) FLASK_ENV='default' flask run --host=0.0.0.0

test:
	FLASK_APP=$(FLASK_APP_NAME) FLASK_ENV='testing' OSS_AK_ID=$(Ali_OSS_AK_ID) \
	OSS_AK_SECRET=$(Ali_OSS_AK_SECRET) OSS_ENDPOINT=$(Ali_OSS_ENDPOINT) pytest