from os import environ, urandom
from pymongo import MongoClient
from datetime import timedelta


class Config(object):
    SECRET_KEY = urandom(24)
    SESSION_TYPE = "mongodb"
    ENVIRONMENT = environ.get("FLASK_ENV")
    # PERMANENT_SESSION_LIFETIME=timedelta(hours=1)


class ProductionConfig(Config):
    MONGO_URI = environ.get("DB_URI")
    MONGODB_SETTINGS = {"host": MONGO_URI}


class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    TESTING = True
    WTF_CSRF_ENABLED = False
    MONGODB_SETTINGS = {"host": "mongomock://localhost"}
