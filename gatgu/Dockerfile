FROM python:3.8.3

ENV PYTHONUNBUFFERED 1

RUN mkdir /docker-server
ADD . /docker-server
WORKDIR /docker-server
RUN /usr/local/bin/python -m pip install --upgrade pip
RUN pip install -r requirements.txt
RUN python3 manage.py migrate
EXPOSE 8000
# ENTRYPOINT ["gunicorn","gatgu.wsgi:application","--bind","0.0.0.0:8000", "--access-logfile","/var/log/gunicorn.access.log","--error-logfile","/var/log/gunicorn.error.log"]
