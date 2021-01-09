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
from yelp.auth import login_required
from yelp.models.campground import Campground
from yelp.models.review import Review
from yelp.forms.camp import NewCampForm, ReviewForm
import wtforms

bp = Blueprint("campgrounds", __name__, url_prefix="/campgrounds")


@bp.route("/", methods=["GET"])
def campgrounds():
    campgrounds = Campground.objects
    return render_template("campgrounds/index.html", campgrounds=campgrounds)

@bp.route("/", methods=["POST"])
@login_required
def add_campground():
    camp = Campground(
        title=request.form.get("title", None),
        location=request.form.get("location", None),
        image=request.form.get("image", None),
        description=request.form.get("description", None),
        price=request.form.get("price", None),
    )
    camp.save()
    flash("The campground was added successfully", "success")
    return redirect(url_for("campgrounds.show_campground", camp_id=str(camp.id)))

@bp.route("/<camp_id>", methods=["GET"])
def show_campground(camp_id):
    camp = None
    try:
        camp = Campground.objects.get(id=camp_id)
    except:
        flash("Cannot find that campground", "error")
        return redirect(url_for("campgrounds.campgrounds"))
    form = ReviewForm(request.form)
    return render_template("campgrounds/show.html", camp=camp, form=form)


@bp.route("/<camp_id>", methods=["POST", "PUT", "DELETE"])
@login_required
def modify_campground(camp_id):
    camp = Campground.objects.get(id=camp_id)
    if request.form["method"] == "put":
        camp.title = request.form.get("title", None)
        camp.location = request.form.get("location", None)
        camp.image = request.form.get("image", None)
        camp.description = request.form.get("description", None)
        camp.price = request.form.get("price", None)
        camp.save()
        flash("Campground updated!", "success")
        return redirect(
            url_for("campgrounds.show_campground", camp_id=camp_id), code=303
        )
    elif request.form["method"] == "delete":
        for review in camp.reviews:
            review.delete()
            camp.delete()
        flash("Campground deleted", "success")
        return redirect(url_for("campgrounds.campgrounds"))
    return "bad request!", 400


@bp.route("/<camp_id>/edit")
@login_required
def edit_campground(camp_id):
    camp = Campground.objects.get(id=camp_id)
    form = NewCampForm(request.form, title=camp.title, location=camp.location)
    return render_template("campgrounds/edit.html", camp=camp, form=form)


@bp.route("/new")
@login_required
def new_campground():
    form = NewCampForm(request.form)
    return render_template("campgrounds/new.html", form=form)
