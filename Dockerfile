FROM python:3

ENV PYTHONUNBUFFERED 1

ENV FLASK_APP /usr/src/app/app.py
ENV FLASK_DEBUG 1

EXPOSE 3001

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD flask run --host=0.0.0.0 --port=3001