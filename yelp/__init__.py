import os
from flask import Flask
from flask import request, url_for, redirect, render_template
from flask_mongoengine import MongoEngine
import mongoengine
from .models.campground import Campground
from .models.review import Review
from .forms.camp import NewCampForm, ReviewForm
import wtforms
from dotenv import load_dotenv

app = Flask(__name__)
load_dotenv()
app.config.update({
    "SECRET_KEY":os.getenv("SECRET_KEY", None)
})
db = MongoEngine(app)

@app.route('/')
def index():
    return redirect(url_for('campgrounds'))

@app.route('/campgrounds', methods=['GET', 'POST'])
def campgrounds():
    if request.method == 'GET':
        campgrounds = Campground.objects
        return render_template('campgrounds/index.html', campgrounds=campgrounds)
    camp = Campground(
        title=request.form.get("title", None),
        location=request.form.get("location", None),
        image=request.form.get("image", None),
        description=request.form.get("description", None),
        price=request.form.get("price", None),
    )
    camp.save()
    return redirect(url_for('show_campground', camp_id=str(camp.id)))

@app.route('/campgrounds/<camp_id>', methods=['GET'])
def show_campground(camp_id):
    camp = Campground.objects.get(id=camp_id)
    form = ReviewForm(request.form)
    return render_template('campgrounds/show.html', camp=camp, form=form)

@app.route('/campgrounds/<camp_id>', methods=['POST', 'PUT', 'DELETE'])
def modify_campground(camp_id):
    camp = Campground.objects.get(id=camp_id)
    if request.form["method"] == "put":
        camp.title = request.form.get("title", None)
        camp.location = request.form.get("location", None)
        camp.image = request.form.get("image", None)
        camp.description = request.form.get("description", None)
        camp.price = request.form.get("price", None)
        camp.save()
        return redirect(url_for('show_campground', camp_id=camp_id), code=303)
    elif request.form["method"] == "delete":
        for review in camp.reviews:
            review.delete()
        camp.delete()
        return redirect(url_for('campgrounds'))
    return 'bad request!', 400

@app.route('/campgrounds/<camp_id>/edit')
def edit_campground(camp_id):
    camp = Campground.objects.get(id=camp_id)
    form = NewCampForm(request.form, title=camp.title, location=camp.location)
    return render_template('campgrounds/edit.html', camp=camp, form=form)

@app.route('/campgrounds/new')
def new_campground():
    form = NewCampForm(request.form)
    return render_template('campgrounds/new.html', form=form)

@app.route('/campgrounds/<camp_id>/reviews', methods=['POST'])
def show_reviews(camp_id):
    camp = Campground.objects.get(id=camp_id)
    review = Review(body=request.form["body"], rating=request.form["rating"])
    camp.reviews.append(review)
    review.save()
    camp.save()
    return redirect(url_for('show_campground', camp_id=camp_id))

@app.route('/campgrounds/<camp_id>/reviews/<review_id>', methods=['POST', 'DELETE'])
def modify_review(camp_id, review_id):
    camp = Campground.objects.get(id=camp_id)
    review = Review.objects.get(id=review_id)
    if request.form["method"] == "delete":
        camp.update(pull__reviews=review)
        review.delete()
    return redirect(url_for('show_campground', camp_id=camp_id))

@app.errorhandler(mongoengine.errors.ValidationError)
def handle_bad_mongo_validation(e):
    print(e)
    return render_template('error.html', error_message="Invalid Campground Data"), 400

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error_message="Page Not Found"), 400
