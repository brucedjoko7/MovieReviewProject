from ast import Pass
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, FileAllowed
from werkzeug.utils import secure_filename
from wtforms import StringField, SubmitField, TextAreaField, PasswordField, FileField
from wtforms.validators import (
    InputRequired,
    Length,
    Email,
    EqualTo,
    ValidationError
)


from .models import User


class SearchForm(FlaskForm):
    search_query = StringField(
        "Query", validators=[InputRequired(), Length(min=1, max=100)]
    )
    submit = SubmitField("Search")


class MovieReviewForm(FlaskForm):
    text = TextAreaField(
        "Comment", validators=[InputRequired(), Length(min=5, max=500)]
    )
    submit = SubmitField("Enter Comment")


class RegistrationForm(FlaskForm):
    username = StringField(
        "Username", validators=[InputRequired(), Length(min=1, max=40)]
    )
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired()])
    confirm_password = PasswordField(
        "Confirm Password", validators=[InputRequired(), EqualTo("password")]
    )
    submit = SubmitField("Sign Up")

    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken")

    def validate_email(self, email):
        user = User.objects(email=email.data).first()
        if user is not None:
            raise ValidationError("Email is taken")


# TODO: implement fields
# Should be all
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])
    submit = SubmitField('Login')


# TODO: implement
# Think I am done
class UpdateUsernameForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(min=1, max=40)])
    submit_username = SubmitField('Update')

    # TODO: implement
    # Might need to modify this
    def validate_username(self, username):
        user = User.objects(username=username.data).first()
        if user is not None:
            raise ValidationError("Username is taken")

# TODO: implement
# Think I am done
class UpdateProfilePicForm(FlaskForm):
    picture = FileField('Profile Picture', validators=[FileRequired(), FileAllowed(['png', 'jpg'])])
    # picture = ImageField
    submit_picture = SubmitField('Update')

# Modified for final project
class ReplyForm(FlaskForm):
    text = TextAreaField(
        "Reply", validators=[InputRequired(), Length(min=5, max=500)]
    )
    submit = SubmitField("Enter Reply")

class FavoriteMovieForm(FlaskForm):
    movie_title = StringField("Movie Title", validators=[InputRequired(), Length(min=1, max=100)])
    submit = SubmitField("Add to Favorites")

class SnackForm(FlaskForm):
    snack = StringField("Snack/Drink", validators=[InputRequired(), Length(min=1, max=100)])
    submit = SubmitField("Check Calories")

class FollowForm(FlaskForm):
    submit = SubmitField('Follow')

class UnfollowForm(FlaskForm):
    submit = SubmitField("Unfollow")