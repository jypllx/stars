from app import db
from parser.podtime import PodTime
from parser.podmood import PodMood
from flask.ext.security import UserMixin, RoleMixin


podmood=PodMood('./moods.xlsx')


"""
Channel and items are a proper refleciton of the RSS file of the podcast.
Columns ending with an underscore are information pulled from the RSS file 
and should not be modified. These information are eventually duplicated in
fields with the same name but no underscore. These fields can be edited
and are displayed on Tootak UI.
"""
class Channel(db.Model):
    __tablename__ = 'channels'

    id              = db.Column(db.Integer, primary_key=True)
    
    title_          = db.Column(db.String())
    link_           = db.Column(db.String())
    description_    = db.Column(db.String())
    itunes_category_= db.Column(db.String())
    language_       = db.Column(db.String())
    author_         = db.Column(db.String())
    image_          = db.Column(db.String())
    last_build_date_= db.Column(db.DateTime)

    title           = db.Column(db.String())
    description     = db.Column(db.String())    
    mood            = db.Column(db.String())
    image           = db.Column(db.String())
    created         = db.Column(db.DateTime)


    def __init__(self, title_, link_, description_, itunes_category_,
                language_, author_, image_, last_build_date_):
        self.title_ = title_.strip()
        self.link_ = link_.strip()
        self.description_ = description_.strip()
        self.itunes_category_ = itunes_category_.strip()
        self.language_ = language_.strip()
        self.author_ = author_.strip()
        self.image_ = image_.strip()
        self.last_build_date_ = last_build_date_
    
        self.title  = self.title_
        self.description  = self.description_
        self.mood = podmood.get_mood(self.itunes_category_)
        self.image = self.image_

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
    channel_id      = db.Column(db.Integer)
    
    title_          = db.Column(db.String())
    description_    = db.Column(db.String())
    itunes_category_= db.Column(db.String()) # copied from the channel
    pubdate_        = db.Column(db.DateTime)
    duration_       = db.Column(db.Integer) # in seconds
    audio_url_      = db.Column(db.String())

    title           = db.Column(db.String())
    description     = db.Column(db.String())
    mood            = db.Column(db.String())
    cat_time        = db.Column(db.Integer)
    cat_name        = db.Column(db.String())
    created         = db.Column(db.DateTime)

    def __init__(self, title_, description_, channel_id, duration_str, audio_url_, pubdate_, itunes_category_):
        self.title_         = title_.strip()
        self.description_   = description_.strip()
        self.channel_id     = channel_id
        self.audio_url_     = audio_url.strip()
        self.pubdate_       = pubdate_
        self.duration_, self.cat_time, self.cat_name = PodTime().getDurationCat(duration_str)
        self.itunes_category_= itunes_category_.strip()
        self.mood           = podmood.get_mood(self.itunes_category_)

    @property
    def duration_str(self):
        if self.duration is None:
            return ''
        m, s = divmod(int(self.duration), 60)
        h, m = divmod(m, 60)
        if h == 0:
            return "%s:%s" % (m, s)
        else:
            return "%s:%s:%s" % (h, m, s)

    def __repr__(self):
        return 'Item<id {}>'.format(self.id)

class Tag(db.Model):
    __tablename__ = 'tags'

    id              = db.Column(db.Integer, primary_key=True)
    name            = db.Column(db.String())
    description     = db.Column(db.String())
    playlists       = db.relationship('Playlist', backref='tag', lazy='joined')

    def __init__(self, name, description):
        self.name           = name
        self.description    = description

class Playlist(db.Model):
    __tablename__ = 'playlists'

    id              = db.Column(db.Integer, primary_key=True)
    created         = db.Column(db.DateTime)
    name            = db.Column(db.String())
    description     = db.Column(db.String())
    tag_id          = db.Column(db.Integer, db.ForeignKey('tags.id'))
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
