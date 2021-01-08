import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from .models.campground import Campground
from .models.review import Review
from .forms.camp import NewCampForm, ReviewForm
import wtforms

bp = Blueprint('campgrounds', __name__, url_prefix='/campgrounds')

@bp.route('/', methods=['GET', 'POST'])
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

@bp.route('/<camp_id>', methods=['GET'])
def show_campground(camp_id):
    camp = Campground.objects.get(id=camp_id)
    form = ReviewForm(request.form)
    return render_template('campgrounds/show.html', camp=camp, form=form)

@bp.route('/<camp_id>', methods=['POST', 'PUT', 'DELETE'])
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

@bp.route('/<camp_id>/edit')
def edit_campground(camp_id):
    camp = Campground.objects.get(id=camp_id)
    form = NewCampForm(request.form, title=camp.title, location=camp.location)
    return render_template('campgrounds/edit.html', camp=camp, form=form)

@bp.route('/new')
def new_campground():
    form = NewCampForm(request.form)
    return render_template('campgrounds/new.html', form=form)

@bp.route('/<camp_id>/reviews', methods=['POST'])
def show_reviews(camp_id):
    camp = Campground.objects.get(id=camp_id)
    review = Review(body=request.form["body"], rating=request.form["rating"])
    camp.reviews.append(review)
    review.save()
    camp.save()
    return redirect(url_for('show_campground', camp_id=camp_id))

@bp.route('/<camp_id>/reviews/<review_id>', methods=['POST', 'DELETE'])
def modify_review(camp_id, review_id):
    camp = Campground.objects.get(id=camp_id)
    review = Review.objects.get(id=review_id)
    if request.form["method"] == "delete":
        camp.update(pull__reviews=review)
        review.delete()
    return redirect(url_for('show_campground', camp_id=camp_id))
