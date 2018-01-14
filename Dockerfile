FROM python:3

ENV PYTHONUNBUFFERED 1

ARG PORT=3001
ENV DJANGO_PORT $PORT

EXPOSE $PORT

RUN mkdir /code

WORKDIR /code

ADD requirements.txt /code/
RUN pip install -r requirements.txt

ADD . /code/

CMD python3 manage.py runserver 0.0.0.0:${DJANGO_PORT}