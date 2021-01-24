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
    jsonify,
    current_app,
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
    page = None
    try:
        page = int(request.args.get("page", 1))
    except:
        current_app.logger.exception("Something other than an int used for page number")
        return render_template("error.html", error_message="Invalid Page Number")
    paginated_campgrounds = Campground.objects.paginate(page=page, per_page=10)
    campgrounds_json = None

    # The code below is needed for cluster map popups
    campgrounds = Campground.objects
    campground_locs_with_props = []
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
        campgrounds_json = json.htmlsafe_dumps({"features": campground_locs_with_props})
    return render_template(
        "campgrounds/index.html",
        campgrounds=campgrounds,
        paginated_campgrounds=paginated_campgrounds,
        campgrounds_json=campgrounds_json,
    )


@bp.route("/<camp_id>", methods=["GET"])
def show_campground(camp_id):
    camp = None
    prev_body = session.get("review_body", None)
    if prev_body:
        session.pop("review_body")
    try:
        camp = Campground.objects.get(id=camp_id)
    except:
        flash("Cannot find that campground", "error")
        return redirect(url_for("campgrounds.campgrounds"))
    review_form = ReviewForm(body=prev_body)
    show_form = ShowForm()
    return render_template(
        "campgrounds/show.html", camp=camp, form=review_form, show_form=show_form
    )


@bp.route("/<camp_id>/edit", methods=["GET", "POST", "PUT", "DELETE"])
@login_required
@campground_ownership_required
def modify_campground(camp_id):
    camp = Campground.objects.get(id=camp_id)
    form = CampForm(description=camp.description)
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
    if show_form.method.data == "DELETE":
        for review in camp.reviews:
            review.delete()
        camp.delete()
        flash("Campground deleted", "success")
        return redirect(url_for("campgrounds.campgrounds"))

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
