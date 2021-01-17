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
from yelp.auth import login_required, review_ownership_required
from yelp.models.campground import Campground
from yelp.models.review import Review
from yelp.forms.camp import ReviewForm
import wtforms

bp = Blueprint("reviews", __name__, url_prefix="/campgrounds/<camp_id>/reviews")


@bp.route("", methods=["POST"])
@login_required
def add_review(camp_id):
    form = ReviewForm()
    if form.validate_on_submit():
        camp = Campground.objects.get(id=camp_id)
        review = Review(body=form.body.data, rating=form.rating.data)
        if g.user:
            review.author = g.user.id
        camp.reviews.append(review)
        review.save()
        camp.save()
        flash("Review saved successfully", "success")
        return redirect(url_for("campgrounds.show_campground", camp_id=camp_id))
    flash("Your review needs a star rating and text", "error")
    session["review_body"] = form.body.data
    return redirect(url_for("campgrounds.show_campground", camp_id=camp_id))


@bp.route("/<review_id>", methods=["POST", "DELETE"])
@login_required
@review_ownership_required
def modify_review(camp_id, review_id):
    camp = Campground.objects.get(id=camp_id)
    review = Review.objects.get(id=review_id)
    review_form = ReviewForm()
    if review_form.method.data == "DELETE":
        camp.update(pull__reviews=review)
        review.delete()
    flash("Review deleted", "success")
    return redirect(url_for("campgrounds.show_campground", camp_id=camp_id))
