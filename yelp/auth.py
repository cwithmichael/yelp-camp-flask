import functools

from flask import (
    Blueprint,
    flash,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash
import mongoengine
from yelp.models.user import User
from yelp.models.campground import Campground
from yelp.models.review import Review
from yelp.forms.auth import LoginForm, RegisterForm

bp = Blueprint("auth", __name__, url_prefix="/")


@bp.route("/register", methods=("GET", "POST"))
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        error = None
        username = request.form["username"]
        password = request.form["password"]
        email = request.form["email"]
        user = User(
            username=username, password=generate_password_hash(password), email=email
        )
        try:
            user.save()
        except mongoengine.errors.NotUniqueError as e:
            if "username" in str(e):
                error = f"Username {username} already taken"
            elif "email" in str(e):
                error = f"Email {email} already in use"

            flash(error, "error")
            return redirect(url_for("auth.register"))
        session["prev_view"] = "register"
        return redirect(url_for("auth.login", _method="POST"), code=307)
    return render_template("auth/register.html", form=form)


@bp.route("/login", methods=("GET", "POST"))
def login():
    form = LoginForm()
    if form.validate_on_submit():
        error = None
        user = None
        username = form.username.data
        password = form.password.data
        bad_creds = "Incorrect username or password"
        try:
            user = User.objects.get(username=username)
        except:
            error = bad_creds

        if user and not check_password_hash(user.password, password):
            error = bad_creds

        if not error:
            prev_view = session.get("prev_view", None)
            session.clear()
            session["user_id"] = str(user.id)

            if prev_view == "register":
                flash("Registered Successfully - Welcome to Yelp Camp", "success")
            else:
                flash("Successfully logged in", "success")
                if prev_view != "register":
                    from urllib.parse import urlparse

                    parsed = urlparse(prev_view)
                    if parsed.path:
                        return redirect(url_for(f"campgrounds.{parsed.path}"))
            return redirect(url_for("campgrounds.campgrounds"))
        flash(error, "error")
        return redirect(url_for("auth.login"))
    return render_template("auth/login.html", form=form)


@bp.route("/logout")
def logout():
    session.clear()
    flash("Successfully logged out", "success")
    return redirect(url_for("auth.login"))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    if user_id is None:
        g.user = None
    else:
        try:
            g.user = User.objects.get(id=user_id)
        except:
            g.user = None


def login_required(view):
    @functools.wraps(view)
    def authentication_wrapped_view(**kwargs):
        if g.user is None:
            flash("You must be signed in to view this page.", "error")
            session["prev_view"] = view.__name__
            return redirect(url_for("auth.login"))
        return view(**kwargs)

    return authentication_wrapped_view


def campground_ownership_required(view):
    @functools.wraps(view)
    def authorization_wrapped_view(**kwargs):
        camp_id = kwargs.get("camp_id", None)
        camp = Campground.objects.get(id=camp_id)
        if g.user and g.user.id != camp.author.id:
            flash("You do not have permission to do that", "error")
            return redirect(url_for("campgrounds.modify_campground", camp_id=camp_id))
        return view(**kwargs)

    return authorization_wrapped_view


def review_ownership_required(view):
    @functools.wraps(view)
    def authorization_wrapped_view(**kwargs):
        camp_id = kwargs.get("camp_id", None)
        review_id = kwargs.get("review_id", None)
        review = Review.objects.get(id=review_id)
        if g.user and g.user.id != review.author.id:
            flash("You do not have permission to do that", "error")
            return redirect(url_for("campgrounds.modify_campground", camp_id=camp_id))
        return view(**kwargs)

    return authorization_wrapped_view
