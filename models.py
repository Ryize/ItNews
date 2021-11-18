from __init__ import *

class Usering(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique = True)
    login = db.Column(db.String(100), nullable=False, unique = True)
    password = db.Column(db.String(100), nullable=False)
    
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(64), unique = True)
    login = db.Column(db.String(100), nullable=False, unique = True)
    password = db.Column(db.String(100), nullable=False)
    avatar = db.Column(db.Text)
    aboutme = db.Column(db.String(257), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    work_status = db.Column(db.String(27), nullable=False)
    admin_status = db.Column(db.Integer, nullable=False)
    banned = db.Column(db.Integer, nullable=False)
    muted = db.Column(db.Integer, nullable=False)
    
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    about = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=False)
    data = db.Column(db.Text, nullable=False)
    
    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        
    def __repr__(self):
        return '<Post id: {}, login: {}, title: {}, text: {}>'.format(self.id, self.login, self.title, self.text)
        
class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=False)
    data = db.Column(db.Text, nullable=False)
    post_id = db.Column(db.Integer, nullable=False)
    
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    title = db.Column(db.Text, nullable=False)
    text = db.Column(db.Text, nullable=False)
    data = db.Column(db.Text, nullable=False)
    
class Rating(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Text, nullable=False)
    voted = db.Column(db.Float, nullable=False)
    
    def __init__(self, *args, **kwargs):
        super(Rating, self).__init__(*args, **kwargs)
        
    def __repr__(self):
        return '<Post id: {}, name: {}, voted: {}, position: {}>'.format(self.id, self.name, self.voted, self.position)
    
class CookieUser(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    unique_key = db.Column(db.String(33), unique = True)
    login = db.Column(db.String(64), unique = True)
    
class EmailConfirm(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique = True)
    code = db.Column(db.String(11))
    
class ResetPassword(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    email = db.Column(db.String(64), unique = True)
    code = db.Column(db.String(11))
    
db.create_all()
    
@manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
