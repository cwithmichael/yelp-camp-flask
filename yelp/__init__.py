import os
from flask import Flask
from flask import request, url_for, redirect, render_template
import mongoengine
from dotenv import load_dotenv

def create_app(test_config=None):
    app = Flask(__name__, instance_relative_config=True)
    load_dotenv()
    app.config.from_mapping(
        SECRET_KEY = os.getenv("SECRET_KEY", b'_5#secret')
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    from . import db
    db.init_app(app)

    from . import campgrounds
    app.register_blueprint(campgrounds.bp)

    from . import reviews
    app.register_blueprint(reviews.bp)
    
    @app.route('/')
    def index():
        return redirect('/campgrounds')

    @app.errorhandler(mongoengine.errors.ValidationError)
    def handle_bad_mongo_validation(e):
        print(e)
        return render_template('error.html', error_message="Invalid Campground Data"), 400

    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error.html', error_message="Page Not Found"), 400
    return app
