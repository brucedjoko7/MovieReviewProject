from flask import Blueprint, redirect, url_for, render_template, flash, request, current_app
from flask_login import current_user, login_required, login_user, logout_user
import base64
from io import BytesIO
from .. import bcrypt
from werkzeug.utils import secure_filename
from ..forms import RegistrationForm, LoginForm, UpdateUsernameForm, UpdateProfilePicForm, FavoriteMovieForm, SnackForm
from ..models import User
import requests

users = Blueprint("users", __name__)

""" ************ User Management views ************ """


# TODO: implement
# Think I am done
@users.route("/register", methods=["GET", "POST"])
def register():

    # Checking if the current user is authenticated
    if current_user.is_authenticated:
        # Redirecting to the '/' route if so
        return redirect(url_for('movies.index'))
    
    # If not authenticated, we load a RegistrationForm
    form = RegistrationForm()

    if request.method == 'POST':
        # Checking that the form is valid
        if form.validate_on_submit():
            # Hashing the password
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

            # Creating a new user object
            user = User(username=form.username.data, email=form.email.data, password=hashed_password)

            # Saving the new user object
            user.save()

            # Redirecting to the '/login' route after a successful registration
            # flash("Registration successful! Please log in.")

            return redirect(url_for('users.login'))
        else:
            flash("Failed to register")
    
    # Handling GET request by rendering the registration form
    return render_template('register.html', form=form)


# TODO: implement
# Think I am done
@users.route("/login", methods=["GET", "POST"])
def login():
    
    # Checking if the current user is authenticated
    if current_user.is_authenticated:
        # If already authenticated, we redirect to the '/' route
        return redirect(url_for('movies.index'))
    
    # Loading the LoginFOrm
    form = LoginForm()

    if request.method == 'POST':
        # Checking if the form is valid
        if form.validate_on_submit():

            # Getting the first user object that matches the username
            user = User.objects(username=form.username.data).first()

            # Checking if the user exists and that the password matches
            if user is not None and bcrypt.check_password_hash(user.password, form.password.data):

                # Loging the user
                login_user(user)

                # Redirecting to '/account' route
                return redirect(url_for('users.account'))
            else:
                # If the user does not exists or if the password was not correct, we flash a message
                flash("Failed to login! Check your username and/or password!")

    # Redirecting to the login page again so that the user can successfully login
    return render_template("login.html", form=form)


# TODO: implement
# Think I am done
@users.route("/logout")
@login_required
def logout():
    # Login out the current user
    logout_user()

    # Redirecting to the '/' route
    return redirect(url_for('movies.index'))

# Think I am done
@users.route("/account", methods=["GET", "POST"])
@login_required
def account():
    update_username_form = UpdateUsernameForm()
    update_profile_pic_form = UpdateProfilePicForm()
    form = FavoriteMovieForm()
    
    if request.method == "POST":
        if update_username_form.validate_on_submit():
            # TODO: handle update username form submit
            # Updating the username
            current_user.modify(username=update_username_form.username.data)
            
            # Committing the change to the database
            current_user.save()
            
            # Logout and login again with updated username
            logout_user
            return redirect(url_for('users.login'))

        if update_profile_pic_form.validate_on_submit():
            # TODO: handle update profile pic form submit
            picture_file = update_profile_pic_form.picture.data
            filename = secure_filename(picture_file.filename)
            content_type = f'images/{filename[-3:]}'

            if current_user.profile_pic.get() is None:
                # User does not have a profile picture
                current_user.profile_pic.put(picture_file.stream, content_type=content_type)
            else:
                # User has a profile picture
                current_user.profile_pic.replace(picture_file.stream, content_type=content_type)
            
            # Saving the new profile picture
            current_user.save()
            
            # Refreshing the page
            return redirect(url_for('users.account'))

    # TODO: handle get requests
    # Initializing the image as None
    image = None

    # Checking if there was already a profile picture
    if current_user.profile_pic:
        # image = current_user.profile_pic
        bytes_im = BytesIO(current_user.profile_pic.read())
        image = base64.b64encode(bytes_im.getvalue()).decode()

    # Rendering the account page template with the forms
    return render_template(
        "account.html", 
        update_username_form=update_username_form, 
        update_profile_pic_form=update_profile_pic_form, 
        form=form,
        user=current_user._get_current_object(), 
        image=image
    )

# Modified for final project
@users.route("/follow/<username>", methods=["POST"])
@login_required
def follow(username):
    # Getting the user object to follow
    user_to_follow = User.objects(username=username).first()

    # Checking that the user exist and is not the current user loged in
    if user_to_follow and user_to_follow != current_user._get_current_object():
        # Adding user_to_follow in the current_user's following list if not already there
        if user_to_follow not in current_user._get_current_object().following:
            current_user._get_current_object().update(push__following=user_to_follow)

        # Adding the current_user in the user_to_follow's followers list if not already there
        if current_user._get_current_object() not in user_to_follow.followers:
            user_to_follow.update(push__followers=current_user._get_current_object())

    # return redirect(url_for('users.account'))
    return redirect(url_for('movies.user_detail', username=username))

@users.route("/unfollow/<username>", methods=["POST"])
@login_required
def unfollow(username):
    user_to_unfollow = User.objects(username=username).first()
    
    # Check that the user_to_unfollow exists and is not the current user
    if user_to_unfollow and user_to_unfollow != current_user._get_current_object():
        # If current_user is following this user, remove them from following
        if user_to_unfollow in current_user._get_current_object().following:
            current_user._get_current_object().update(pull__following=user_to_unfollow)
        
        # Remove current_user from user_to_unfollow's followers
        if current_user._get_current_object() in user_to_unfollow.followers:
            user_to_unfollow.update(pull__followers=current_user._get_current_object())
    
    # Redirect back to the user's profile page that was just unfollowed
    return redirect(url_for('movies.user_detail', username=username))

@users.route("/add_favorite", methods=["POST"])
@login_required
def add_favorite():
    form = FavoriteMovieForm()
    if form.validate_on_submit():
        movie_title = form.movie_title.data.strip()
        user = current_user._get_current_object()
        # Check if the movie is already in the list of favorites
        if movie_title not in user.favorite_movies:
            user.update(push__favorite_movies=movie_title)
            user.reload()
            flash(f"'{movie_title}' added to favorites!")
        else:
            flash("This movie is already in your favorites.")
    else:
        flash("Failed to add movie. Check the title and try again.")
    return redirect(url_for('users.account'))

@users.route("/snack_info", methods=["GET", "POST"])
@login_required
def snack_info():
    form = SnackForm()
    snack_data = None

    if form.validate_on_submit():
        snack_name = form.snack.data.strip()
        # Call the CalorieNinjas API
        headers = {'X-Api-Key': current_app.config['CALORIENINJAS_API_KEY']}
        response = requests.get(
            f"https://api.calorieninjas.com/v1/nutrition?query={snack_name}",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            # data['items'] should be a list of nutritional info
            # We'll just take the first item if it exists
            if data.get("items"):
                snack_data = data["items"][0]  # The most relevant result
            else:
                flash("No nutrition info found for that snack.")
        else:
            flash("Failed to fetch data. Please try again later.")

    return render_template("snack_info.html", form=form, snack_data=snack_data)