from flask import current_app
from pymongo import MongoClient


def getClient():
    url = current_app.config.get("MONGO_URI", "localhost")
    client = MongoClient(url, 27017)
    return client
