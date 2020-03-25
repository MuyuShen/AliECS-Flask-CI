FROM python:3.8.1
COPY ./flask-dev /flask-dev
workdir /flask-dev
ENV FLASK_APP manage.py
ENV FLASK_RUN_HOST 0.0.0.0
ENV FLASK_CONFIG "testing"
RUN pip install -r requirements.txt
CMD ["flask", "run"]