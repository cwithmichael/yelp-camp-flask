from flask import current_app, g
from flask.cli import with_appcontext
from flask_mongoengine import MongoEngine
import click
import random
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash
from seed.seedhelpers import descriptors, places
from seed.cities import cities
from yelp.models import campground, user, review


def seed_db():
    user.User.drop_collection()
    review.Review.drop_collection()
    campground.Campground.drop_collection()
    hashed_pw = generate_password_hash("fake")
    user.User(email="fake@fake.com", username="fake", password=hashed_pw).save()
    author = user.User.objects.first()
    for i in range(300):
        random_loc = random.choice(cities)
        city = random_loc["city"]
        state = random_loc["state"]
        descriptor = random.choice(descriptors)
        place = random.choice(places)
        camp = campground.Campground(
            location=f"{city}, {state}",
            title=f"{descriptor} {place}",
            images=[
                campground.Image(
                    url="https://source.unsplash.com/collection/483251",
                    filename="camp.jpg",
                    thumbnail_url="https://source.unsplash.com/collection/483251",
                )
            ],
            description="This is a description.",
            price=(random.random() * 20) + 10,
            author=author.id,
            geometry={
                "type": "Point",
                "coordinates": [random_loc["longitude"], random_loc["latitude"]],
            },
        )
        camp.save()


@click.command("seed-db")
@with_appcontext
def seed_db_command():
    """Clear the existing date and create new collection"""
    seed_db()
    click.echo("Seeded the database.")


def init_app(app):
    db = MongoEngine(app)
    app.cli.add_command(seed_db_command)
