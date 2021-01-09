import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash
import mongoengine
from .models.user import User

bp = Blueprint('auth', __name__, url_prefix='/')

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    error = None
    username = request.form['username']
    password = request.form['password']
    email = request.form['email']
    user = User(
        username=username, password=generate_password_hash(password),email=email)
    try:
        user.save()
    except mongoengine.errors.NotUniqueError as e:
        if 'username' in str(e):
            error = f'Username {username} already taken'
        elif 'email' in str(e):
            error = f'Email {email} already in use'

        flash(error, "error")
        return redirect(url_for("auth.register"))
    session['prev_view'] = "register"
    return redirect(url_for("auth.login", _method='POST'), code=307)

@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == "GET":
        return render_template("auth/login.html")
    error = None
    user = None
    username = request.form['username']
    password = request.form['password']
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
        session['user_id'] = str(user.id)
        
        if prev_view == "register":
            flash("Registered Successfully - Welcome to Yelp Camp", "success")
        else:
            flash("Successfully logged in", "success")

        from urllib.parse import urlparse
        parsed = urlparse(prev_view)
        return redirect(parsed.path)

    flash(error, "error")
    return redirect(url_for("auth.login"))

@bp.route('/logout')
def logout():
    session.clear()
    flash("Successfully logged out", "success")
    return redirect(url_for('auth.login'))

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = User.objects.get(id=user_id)


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            flash("You must be signed in to view this page.", "error")
            session["prev_view"] = request.referrer
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view
