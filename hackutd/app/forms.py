from wsgiref.validate import validator
from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    FileField,
    TextAreaField,
    FloatField,
)
from wtforms.validators import (
    ValidationError,
    DataRequired,
    EqualTo,
    NumberRange,
    Regexp,
)
from app.models import User


class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    remember_me = BooleanField("Remember Me")
    submit = SubmitField("Sign In")


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    name = StringField("Display Name", validators=[DataRequired()])
    is_artist = BooleanField("I'm an artist")
    password = PasswordField("Password", validators=[DataRequired()])
    password2 = PasswordField(
        "Repeat Password", validators=[DataRequired(), EqualTo("password")]
    )
    submit = SubmitField("Register")
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username')


class PostForm(FlaskForm):
    image = FileField("Upload Image", validators=[DataRequired()])

    def validate_image(self, image):
        if image.data.filename.endswith(".jpg") or image.data.filename.endswith(".png"):
            return
        else:
            raise ValidationError("Expected image file in jpg or png format")

    caption = TextAreaField("A Descriptive Caption", validators=[DataRequired()])
    tags = StringField("A comma separated list of tags describing your work")
    price = FloatField("Price", validators=[NumberRange(min=0)])
    submit = SubmitField("Create")
class SearchForm(FlaskForm):
   search_tag = StringField("Search Tag")
   search_artist = StringField("Search Artist")
   search_price = FloatField("Price Range",validators=[NumberRange(min=0)])
   submit = SubmitField('Search')
