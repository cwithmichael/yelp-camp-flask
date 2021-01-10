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
from cloudinary.uploader import upload
from cloudinary.api import delete_resources
from cloudinary.utils import cloudinary_url
from yelp.auth import login_required, campground_ownership_required
from yelp.models.campground import Campground, Image
from yelp.models.review import Review
from yelp.forms.camp import NewCampForm, ReviewForm
import wtforms

bp = Blueprint("campgrounds", __name__, url_prefix="/campgrounds")


@bp.route("/", methods=["GET"])
def campgrounds():
    campgrounds = Campground.objects
    return render_template("campgrounds/index.html", campgrounds=campgrounds)


@bp.route("", methods=["POST"])
@login_required
def add_campground():
    upload_result = None
    image_results = upload_images_to_cloudinary(request.files)
    camp = Campground(
        title=request.form.get("title", None),
        location=request.form.get("location", None),
        images=image_results,
        description=request.form.get("description", None),
        price=request.form.get("price", None),
        author=session.get("user_id", None),
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
@campground_ownership_required
def modify_campground(camp_id):
    camp = Campground.objects.get(id=camp_id)
    image_results = upload_images_to_cloudinary(request.files)
    if request.form["method"] == "put":
        camp.title = request.form.get("title", None)
        camp.location = request.form.get("location", None)
        camp.images = [*camp.images, *image_results]
        camp.description = request.form.get("description", None)
        camp.price = request.form.get("price", None)
        camp.save()
        deleted_images = request.form.items(multi=True)
        for key, value in deleted_images:
            if key == "images_to_delete":
                camp.update(pull__images__filename=value)
                delete_resources(value)
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
@campground_ownership_required
def edit_campground(camp_id):
    camp = Campground.objects.get(id=camp_id)
    form = NewCampForm(request.form, title=camp.title, location=camp.location)
    return render_template("campgrounds/edit.html", camp=camp, form=form)


@bp.route("/new")
@login_required
def new_campground():
    form = NewCampForm(request.form)
    return render_template("campgrounds/new.html", form=form)


def upload_images_to_cloudinary(request_files):
    image_results = []
    for name, file in request_files.items(multi=True):
        file_to_upload = file
        if file_to_upload:
            upload_result = upload(file_to_upload, folder="yelp_camp")
            thumbnail_url, options = cloudinary_url(
                upload_result["public_id"],
                format="jpg",
                crop="fill",
                width=200,
                height=200,
            )
            image_results.append(
                Image(
                    url=upload_result["url"],
                    filename=upload_result["public_id"],
                    thumbnail_url=thumbnail_url,
                )
            )
    return image_results