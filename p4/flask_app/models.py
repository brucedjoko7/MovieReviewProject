from flask_login import UserMixin
from datetime import datetime
from . import db, login_manager


# TODO: implement
# Think I am done
@login_manager.user_loader
def load_user(user_id):
    return User.objects(username=user_id).first()

# TODO: implement fields
class User(db.Document, UserMixin):
    username = db.StringField(unique=True, required=True, min_length=1, max_length=40) # length should be 1 to 40
    email = db.EmailField(unique=True, required=True)
    password = db.StringField(required=True) # Only store slow hashed
    profile_pic = db.ImageField()
    # Modified for final project
    followers = db.ListField(db.ReferenceField('User'))
    following = db.ListField(db.ReferenceField('User'))
    favorite_movies = db.ListField(db.StringField())

    # Returns unique string identifying our object
    def get_id(self):
        # TODO: implement
        # Think that is enough
        return self.username


# TODO: implement fields
class Review(db.Document):
    commenter = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=5, max_length=500) # Length should be between 5 to 500
    date = db.StringField(required=True) # Might change to string field
    imdb_id = db.StringField(required=True, min_length=9, max_length=9) # Length should be 9
    movie_title = db.StringField(required=True, min_length=1, max_length=100) # Length shoudl be between 1 and 100
    # image = db.StringField()
    #Uncomment when other fields are ready for review pictures
    # Modified for final project
    likes = db.ListField(db.ReferenceField("User"))

# Comment class to mimic threaded comments like in social media
class Comment(db.Document):
    commenter = db.ReferenceField(User, required=True)
    content = db.StringField(required=True, min_length=5, max_length=500)
    date = db.StringField(required=True)
    parent = db.ReferenceField('Comment', required=False) # For nested comments
    review = db.ReferenceField(Review, required=True)
    likes = db.ListField(db.ReferenceField('User'))