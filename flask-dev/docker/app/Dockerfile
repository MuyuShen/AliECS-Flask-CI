FROM aliecs-flask-ci_app
COPY ./flask-dev /flask-dev
workdir /flask-dev
ENV FLASK_APP manage.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_CONFIG "develop"
ENV FLASK_ENV "develop"
ENV FLASK_DEBUG "True"
CMD ["flask", "run"]