FROM python:3.8.3

ENV PYTHONUNBUFFERED 1

RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
ADD ./gatgu /code/
RUN pip install -r requirements.txt
RUN python3 manage.py migrate
