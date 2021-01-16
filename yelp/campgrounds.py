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
    json,
)
import os
import wtforms
import requests
from cloudinary.uploader import upload
from cloudinary.api import delete_resources
from cloudinary.utils import cloudinary_url
from yelp.auth import login_required, campground_ownership_required
from yelp.models.campground import Campground, Image
from yelp.models.review import Review
from yelp.forms.camp import CampForm, ReviewForm, ShowForm


bp = Blueprint("campgrounds", __name__, url_prefix="/campgrounds")


@bp.route("/", methods=["GET"])
def campgrounds():
    campgrounds = Campground.objects
    campground_locs_with_props = []
    # The code below is needed for cluster map popups
    for campground in campgrounds:
        campy = {
            "geometry": campground.geometry,
            "properties": {
                "title": campground.title,
                "id": str(campground.id),
                "location": campground.location,
            },
        }
        campground_locs_with_props.append(campy)
        campgrounds_json = json.dumps({"features": campground_locs_with_props})
    return render_template(
        "campgrounds/index.html",
        campgrounds=campgrounds,
        campgrounds_json=campgrounds_json,
    )


@bp.route("/<camp_id>", methods=["GET"])
def show_campground(camp_id):
    camp = None
    try:
        camp = Campground.objects.get(id=camp_id)
    except:
        flash("Cannot find that campground", "error")
        return redirect(url_for("campgrounds.campgrounds"))
    form = ReviewForm()
    show_form = ShowForm()
    return render_template(
        "campgrounds/show.html", camp=camp, form=form, show_form=show_form
    )


@bp.route("/<camp_id>", methods=["POST", "PUT", "DELETE"])
@login_required
@campground_ownership_required
def modify_campground(camp_id):
    camp = Campground.objects.get(id=camp_id)
    form = CampForm()
    show_form = ShowForm()
    if form.method.data == "PUT" and form.validate_on_submit():
        try:
            image_results = upload_images_to_cloudinary(form.image.data)
        except:
            flash("Something went wrong while uploading image", "error")
            return redirect(url_for("campgrounds.edit_campground", camp_id=camp_id))
        camp.title = form.title.data
        camp.location = form.location.data
        camp.images = [*camp.images, *image_results]
        camp.description = form.description.data
        camp.price = form.price.data
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
    elif show_form.method.data == "DELETE":
        for review in camp.reviews:
            review.delete()
        camp.delete()
        flash("Campground deleted", "success")
        return redirect(url_for("campgrounds.campgrounds"))
    return render_template("error.html", error_message="Bad Request"), 400


@bp.route("/<camp_id>/edit")
@login_required
@campground_ownership_required
def edit_campground(camp_id):
    camp = Campground.objects.get(id=camp_id)
    form = CampForm(description=camp.description)
    return render_template("campgrounds/edit.html", camp=camp, form=form)


@bp.route("/new", methods=["GET", "POST"])
@login_required
def new_campground():
    upload_result = None
    form = CampForm()
    if form.validate_on_submit():
        geocoded = forward_geocode(form.location.data)
        image_results = upload_images_to_cloudinary(form.image.data)
        camp = Campground(
            title=form.title.data,
            location=form.location.data,
            images=image_results,
            description=form.description.data,
            price=form.price.data,
            author=session.get("user_id", None),
            geometry=geocoded,
        )
        camp.save()
        flash("The campground was added successfully", "success")
        return redirect(url_for("campgrounds.show_campground", camp_id=str(camp.id)))
    for field, errors in form.errors.items():
        if "image" in field.lower():
            flash(f"Something went wrong uploading your image(s): {errors[0]}", "error")
    return render_template("campgrounds/new.html", form=form)


def forward_geocode(location):
    token = os.environ.get("MAPBOX_TOKEN", None)
    mapbox_url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/{location}.json?access_token={token}"
    # TODO: Add error handling :)
    r = requests.get(mapbox_url)
    return r.json().get("features")[0].get("geometry")


def upload_images_to_cloudinary(request_files):
    image_results = []
    for file in request_files:
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
