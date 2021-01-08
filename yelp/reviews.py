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
from .models.campground import Campground
from .models.review import Review
from .forms.camp import ReviewForm
import wtforms

bp = Blueprint("reviews", __name__, url_prefix="/campgrounds/<camp_id>/reviews")


@bp.route("", methods=["POST"])
def add_review(camp_id):
    camp = Campground.objects.get(id=camp_id)
    review = Review(body=request.form["body"], rating=request.form["rating"])
    camp.reviews.append(review)
    review.save()
    camp.save()
    flash("Review saved successfully", "success")
    return redirect(url_for("campgrounds.show_campground", camp_id=camp_id))


@bp.route("/<review_id>", methods=["POST", "DELETE"])
def modify_review(camp_id, review_id):
    camp = Campground.objects.get(id=camp_id)
    review = Review.objects.get(id=review_id)
    if request.form["method"] == "delete":
        camp.update(pull__reviews=review)
        review.delete()
    flash("Review deleted", "success")
    return redirect(url_for("campgrounds.show_campground", camp_id=camp_id))
