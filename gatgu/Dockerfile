FROM python:3.8.3

ENV PYTHONUNBUFFERED 1

RUN mkdir /docker-server
ADD . /docker-server
WORKDIR /docker-server
RUN pip install -r requirements.txt
RUN python3 manage.py migrate
EXPOSE 8000
#CMD ["python","manage.py","runserver"]
CMD ["uwsgi","--ini","gatgu_uwsgi.ini"]
