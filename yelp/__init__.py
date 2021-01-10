import os
from flask import Flask
from flask import request, url_for, redirect, render_template
import mongoengine
from dotenv import load_dotenv


def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)

    app.config.from_mapping(SECRET_KEY=os.getenv("SECRET_KEY", b"_5#secret"))

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    # load the environment vars
    from pathlib import Path

    load_dotenv(dotenv_path=Path(app.instance_path) / ".env")

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
        return redirect("/campgrounds")

    @app.errorhandler(mongoengine.errors.ValidationError)
    def handle_bad_mongo_validation(e):
        return (
            render_template(
                "error.html", error_message="Something went wrong with your request"
            ),
            400,
        )

    @app.errorhandler(ValueError)
    def bad_request(e):
        return render_template("error.html", error_message="Bad Request"), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template("error.html", error_message="Page Not Found"), 400

    return app
