from app import db
from podtime import PodTime
from flask.ext.security import UserMixin, RoleMixin

class Channel(db.Model):
    __tablename__ = 'channels'

    id              = db.Column(db.Integer, primary_key=True)
    created         = db.Column(db.DateTime)
    name            = db.Column(db.String())
    description     = db.Column(db.String())
    genre           = db.Column(db.String())
    language        = db.Column(db.String())
    url             = db.Column(db.String())
    link            = db.Column(db.String())
    img_url         = db.Column(db.String())

    def __init__(self, name, description, genre, language, url, link, img_url):
        self.name = name
        self.description = description
        self.genre = genre
        self.language = language
        self.url = url
        self.link = link
        self.img_url = img_url

    def __repr__(self):
        return '<id {}>'.format(self.id)


class RelPlaylistItem(db.Model):
    __tablename__ = 'rel_playlists_items'

    playlist_id     = db.Column(db.Integer, db.ForeignKey('playlists.id'), primary_key=True)
    item_id         = db.Column(db.Integer, db.ForeignKey('items.id'), primary_key=True)
    rank            = db.Column(db.Integer)
    item            = db.relationship('Item')
    __table_args__  = (db.UniqueConstraint('playlist_id', 'item_id', name='_playlist_item_uc'),
                     )

    def __init__(self, playlist_id, item_id, rank):
        self.playlist_id    = playlist_id
        self.item_id        = item_id
        self.rank           = rank

    def __repr__(self):
        return '<playlist_id %s><item_id %s><rank %s>' % (self.playlist_id,
            self.item_id, self.rank)

class Item(db.Model):
    __tablename__ = 'items'

    id              = db.Column(db.Integer, primary_key=True)
    created         = db.Column(db.DateTime)
    channel_id      = db.Column(db.Integer)
    name            = db.Column(db.String())
    description     = db.Column(db.String())
    duration        = db.Column(db.Integer)
    cat_time        = db.Column(db.Integer)
    cat_name        = db.Column(db.String())
    audio_url       = db.Column(db.String())
    published       = db.Column(db.DateTime)
    genre           = db.Column(db.String())

    def __init__(self, name, description, channel_id, duration_str, audio_url, published):
        self.name           = name
        self.description    = description
        self.channel_id     = channel_id
        self.audio_url      = audio_url
        self.published      = published
        self.duration, self.cat_time, self.cat_name = PodTime().getDurationCat(duration_str)

    def __repr__(self):
        return 'Item<id {}>'.format(self.id)


class Playlist(db.Model):
    __tablename__ = 'playlists'

    id              = db.Column(db.Integer, primary_key=True)
    created         = db.Column(db.DateTime)
    name            = db.Column(db.String())
    description     = db.Column(db.String())
    items           = db.relationship('RelPlaylistItem')

    def __init__(self, name, description):
        self.name = name
        self.description = description

    def __repr__(self):
        return 'Playlist<id {}>'.format(self.id)

    @property
    def ranked_items(self):
        return sorted(self.items, key=lambda x: x.rank)

roles_users = db.Table('roles_users',
        db.Column('user_id', db.Integer(), db.ForeignKey('users.id')),
        db.Column('role_id', db.Integer(), db.ForeignKey('roles.id')))

class Role(db.Model, RoleMixin):
    __tablename__ = 'roles'
    
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id              = db.Column(db.Integer, primary_key=True)
    created         = db.Column(db.DateTime)
    email           = db.Column(db.String(255), unique=True)
    password        = db.Column(db.String(255))
    active          = db.Column(db.Boolean())
    confirmed_at    = db.Column(db.DateTime)
    roles           = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))
