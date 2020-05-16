FROM python:3.7

# ENV PYTHONUNBUFFERED 1

ENV FLASK_APP /usr/src/app/cyberapi/app.py
ENV CYBERPLANNING_SETTINGS /usr/src/app/config/prod.cfg

EXPOSE 3001

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD flask run --host=0.0.0.0 --port=3001
