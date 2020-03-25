FROM python:3.8.1
COPY ./flask-dev /flask-dev
workdir /flask-dev
ENV FLASK_APP manage.py
ENV FLASK_RUN_HOST 0.0.0.0
<<<<<<< HEAD
ENV FLASK_CONFIG "develop"
=======
ENV OSS_AK_ID '<你的access_key_id>'
ENV OSS_AK_SECRET '<你的access_key_secret>'
ENV OSS_ENDPOINT '<你的服务器访问域名>'
>>>>>>> 6dc70565149d310250ef20b6b877c2faf7a0873c
RUN pip install -r requirements.txt
CMD ["flask", "run"]