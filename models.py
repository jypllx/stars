from app import db

class Channel(db.Model):
    __tablename__ = 'channels'

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String())
    description     = db.Column(db.String())
    genre           = db.Column(db.String())
    language        = db.Column(db.String())
    url             = db.Column(db.String())
    link            = db.Column(db.String())

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return '<id {}>'.format(self.id)

class User(db.Model):
    __tablename__ = 'users'

    id              = db.Column(db.Integer, primary_key=True)
    email           = db.Column(db.String())
    password        = db.Column(db.String())
    authenticated   = db.Column(db.Boolean, default=False)

    def is_active(self):
        """True, as all users are active."""
        return True

    def get_id(self):
        """Return the email address to satisfy Flask-Login's requirements."""
        return self.email

    def is_authenticated(self):
        """Return True if the user is authenticated."""
        return self.authenticated

    def is_anonymous(self):
        """False, as anonymous users aren't supported."""
        return False