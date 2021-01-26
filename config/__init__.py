from os import environ, urandom
from pymongo import MongoClient
from datetime import timedelta


class Config(object):
    SECRET_KEY = urandom(24)
    SESSION_TYPE = "mongodb"
    # PERMANENT_SESSION_LIFETIME=timedelta(hours=1)


class ProductionConfig(Config):
    MONGO_URI = environ.get("DB_URI")
    MONGODB_SETTINGS = {"host": MONGO_URI}
    SESSION_MONGODB = MongoClient(host=MONGO_URI)


class DevelopmentConfig(Config):
    DEBUG = True
    SESSION_MONGODB = MongoClient(host="localhost", port=27017)


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    MONGODB_SETTINGS = {"host": "mongomock://localhost"}
