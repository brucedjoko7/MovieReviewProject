import base64,io
from io import BytesIO
from flask import Blueprint, render_template, url_for, redirect, request, flash
from flask_login import current_user, login_user, login_required

from .. import movie_client
from ..forms import MovieReviewForm, SearchForm, LoginForm, UpdateUsernameForm, RegistrationForm, UpdateProfilePicForm, FollowForm, UnfollowForm, ReplyForm
from ..models import User, Review, Comment
from ..utils import current_time


movies = Blueprint("movies", __name__)
""" ************ Helper for pictures uses username to get their profile picture************ """
def get_b64_img(username):
    user = User.objects(username=username).first()
    bytes_im = io.BytesIO(user.profile_pic.read())
    image = base64.b64encode(bytes_im.getvalue()).decode()
    return image

""" ************ View functions ************ """
# Modified for the final project
# Building threaded comments with replies
def building_comment(comments):
    comment_map = {}
    for comm in comments:
        parent_id = str(comm.parent.id) if comm.parent else None
        comment_map.setdefault(parent_id, []).append(comm)

    def building_tree(parent_id=None):
        nodes = []
        for comm in comment_map.get(parent_id, []):
            replies = building_tree(str(comm.id))
            nodes.append({'comment': comm, 'replies': replies})
        return nodes
    
    return building_tree(None)

@movies.route("/", methods=["GET", "POST"])
def index():
    form = SearchForm()

    if form.validate_on_submit():
        return redirect(url_for("movies.query_results", query=form.search_query.data))

    return render_template("index.html", form=form)


@movies.route("/search-results/<query>", methods=["GET"])
def query_results(query):
    try:
        results = movie_client.search(query)
    except ValueError as e:
        return render_template("query.html", error_msg=str(e))

    return render_template("query.html", results=results)

# Modified for final project
@movies.route("/movies/<movie_id>", methods=["GET", "POST"])
def movie_detail(movie_id):
    try:
        result = movie_client.retrieve_movie_by_id(movie_id)
    except ValueError as e:
        return render_template("movie_detail.html", error_msg=str(e))

    form = MovieReviewForm()
    form_reply = ReplyForm()

    if form.validate_on_submit():
        review = Review(
            commenter=current_user._get_current_object(),
            content=form.text.data,
            date=current_time(),
            imdb_id=movie_id,
            movie_title=result.title,
        )
        review.save()
        return redirect(request.path)

    reviews = Review.objects(imdb_id=movie_id)

    # For each review, we build a comment tree
    review_data = []
    for rev in reviews:
        comments = Comment.objects(review=rev)
        comment_tree = building_comment(comments)
        review_data.append({'review': rev, 'comment_tree': comment_tree})

    return render_template(
        "movie_detail.html",
        form= form,
        form_reply=form_reply,
        movie=result,
        review_data=review_data
    )

    

@movies.route("/add_comment/<review_id>", methods=["POST"])
@login_required
def add_comment(review_id):
    parent_id = request.args.get('parent_id', None)
    review = Review.objects(id=review_id).first()
    if not review:
        flash("Review not found.")
        return redirect(url_for('movies.index'))

    content = request.form.get('content')
    # parent_id = request.args.get('parent_id') # Optional

    form_reply = ReplyForm()
    if form_reply.validate_on_submit():
        new_comment = Comment(
            commenter=current_user._get_current_object(),
            content=form_reply.text.data,
            date=current_time(),
            review=review
        )

        if parent_id:
            parent_comment = Comment.objects(id=parent_id).first()
            if parent_comment:
                new_comment.parent = parent_comment

        new_comment.save()
        return redirect(url_for('movies.movie_detail', movie_id=review.imdb_id))
    else:
        flash("Failed to submit reply")
        return redirect(url_for('movies.movie_detail', movie_id=review.imdb_id))
    
@movies.route("/toggle_like/<comment_id>", methods=["POST"])
@login_required
def toggle_like(comment_id):
    comment = Comment.objects(id=comment_id).first()
    if not comment:
        flash("Comment not found.")
        return redirect(url_for('movies.index'))

    user = current_user._get_current_object()

    # If the user already liked the comment, unlike it; otherwise, like it.
    if user in comment.likes:
        comment.update(pull__likes=user)
    else:
        comment.update(push__likes=user)

    # Redirect back to the movie detail page
    return redirect(url_for('movies.movie_detail', movie_id=comment.review.imdb_id))


# Think I am done
@movies.route("/user/<username>")
def user_detail(username):
    # uncomment to get review image
    # user = find first match in db
    user = User.objects(username=username).first()

    # Checking if the user exists
    if user:   
        user_reviews = list(Review.objects(commenter=user))
        img = get_b64_img(username) # use their username for helper function

        form = FollowForm()
        already_following = False
        if current_user.is_authenticated and user in current_user.following:
            already_following = True
            form = UnfollowForm()

        return render_template(
            'user_detail.html', 
            username=username, 
            user_reviews=user_reviews, 
            image=img,
            user=user,
            already_following=already_following,
            form=form
            )
    
    # User does not exists so we render an error message
    return render_template('user_detail.html', error='User does not exists')
