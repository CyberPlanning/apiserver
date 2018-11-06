from flask import current_app, g
from pymongo import MongoClient


def initMongo():
    url = current_app.config.get("MONGO_URI", "localhost")
    client = MongoClient(url, 27017)
    return client

def getClient():
    client = g.get('mongo', None)
    if not client:
        client = initMongo()
        g.mongo = client
    return client