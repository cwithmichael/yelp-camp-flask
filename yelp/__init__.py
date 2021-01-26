import os
from pathlib import Path
from flask import Flask
from flask import request, url_for, redirect, render_template
import mongoengine
from dotenv import load_dotenv


def create_app(testing=False):
    app = Flask(__name__, instance_relative_config=True)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    load_dotenv(dotenv_path=Path(app.instance_path) / ".env")
    from config import Config

    if not testing:
        if "development" == Config.ENVIRONMENT:
            app.config.from_object("config.DevelopmentConfig")
        elif "production" == Config.ENVIRONMENT:
            app.config.from_object("config.ProductionConfig")
    else:
        app.config.from_object("config.TestingConfig")

    from . import db

    db.init_app(app)

    from . import campgrounds

    app.register_blueprint(campgrounds.bp)

    from . import reviews

    app.register_blueprint(reviews.bp)

    from . import auth

    app.register_blueprint(auth.bp)

    @app.route("/")
    def index():
        return render_template("home.html")

    @app.errorhandler(mongoengine.errors.ValidationError)
    def handle_bad_mongo_validation(e):
        app.logger.exception(e)
        return (
            render_template(
                "error.html", error_message="Something went wrong with your request"
            ),
            400,
        )

    @app.errorhandler(ValueError)
    def bad_request(e):
        app.logger.exception(e)
        return render_template("error.html", error_message="Bad Request"), 400

    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.exception(e)
        return render_template("error.html", error_message="Page Not Found"), 400

    return app
