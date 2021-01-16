from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed, FileStorage
from wtforms import (
    StringField,
    DecimalField,
    TextAreaField,
    MultipleFileField,
    HiddenField,
    RadioField,
)
from wtforms.validators import DataRequired, NumberRange, Regexp, StopValidation
from wtforms.fields.html5 import IntegerRangeField
from collections.abc import Iterable


class MultiFileAllowed(object):
    def __init__(self, upload_set, message=None):
        self.upload_set = upload_set
        self.message = message

    def __call__(self, form, field):

        # FileAllowed only expects a single instance of FileStorage
        # if not (isinstance(field.data, FileStorage) and field.data):
        #     return

        # Check that all the items in field.data are FileStorage items
        if not (
            all(isinstance(item, FileStorage) for item in field.data) and field.data
        ):
            return

        for data in field.data:

            filename = data.filename.lower()
            if not filename:
                # The user probably didn't upload an image and that's okay
                return
            if isinstance(self.upload_set, Iterable):
                if any(filename.endswith("." + x) for x in self.upload_set):
                    return

                raise StopValidation(
                    self.message
                    or field.gettext(
                        "File does not have an approved extension: {extensions}"
                    ).format(extensions=", ".join(self.upload_set))
                )

            if not self.upload_set.file_allowed(field.data, filename):
                raise StopValidation(
                    self.message
                    or field.gettext("File does not have an approved extension.")
                )


class CampForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()], id="title")
    location = StringField("Location", validators=[DataRequired()], id="location")
    description = TextAreaField(
        "Description", validators=[DataRequired()], id="description", default=""
    )
    price = DecimalField("Price", validators=[DataRequired()], id="price")
    image = MultipleFileField(
        "Add Image(s)",
        validators=[MultiFileAllowed(["jpg", "png", "bmp", ""])],
        id="image",
    )
    method = HiddenField()


class ReviewForm(FlaskForm):
    rating = RadioField(
        "Rating",
        choices=[
            ("", "0 stars"),
            ("1", "1 star"),
            ("2", "2 stars"),
            ("3", "3 stars"),
            ("4", "4 stars"),
            ("5", "5 stars"),
        ],
        validators=[DataRequired()],
    )
    body = TextAreaField("Body", validators=[DataRequired()])
    method = HiddenField()


class ShowForm(FlaskForm):
    method = HiddenField()
