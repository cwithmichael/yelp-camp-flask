import pytest
from yelp import create_app
from yelp.db import init_app, seed_db
from yelp.models.campground import Campground
from mongoengine import disconnect


@pytest.fixture
def app():
    app = create_app(
        {
            "TESTING": True,
            "WTF_CSRF_ENABLED": False,
            "MONGODB_SETTINGS": {"host": "mongomock://localhost"},
        }
    )
    with app.app_context():
        init_app(app)
        seed_db()
    yield app
    disconnect()


@pytest.fixture
def client(app):
    return app.test_client()


def login(client, username, password):
    return client.post(
        "/login", data=dict(username=username, password=password), follow_redirects=True
    )


def logout(client):
    return client.get("/logout", follow_redirects=True)


def test_login_logout(client):
    rv = login(client, "fake", "fake")
    assert b"All Campgrounds" in rv.data
    rv = logout(client)
    assert b"Login" in rv.data


def test_show_all_campgrounds(client):
    rv = client.get("/campgrounds/")
    campground = Campground.objects.first()
    assert campground.title.encode("utf-8") in rv.data


def test_show_specific_campground(client):
    campground = Campground.objects.first()
    rv = client.get("/campgrounds/dsafasijfeijfewi/")
    assert rv.status_code == 400
    rv = client.get(f"/campgrounds/{campground.id}")
    assert rv.status_code == 200
    assert campground.title.encode("utf-8") in rv.data
