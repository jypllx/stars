from flask import Flask, url_for, redirect
from flask import request, render_template
from flask.ext.sqlalchemy import SQLAlchemy

import logging
from logging.handlers import RotatingFileHandler

# from flask.ext.login import LoginManager, login_required
# from flask.ext.openid import OpenID

from config import BaseConfig
import os
import re
import sys

app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)
# login_manager = LoginManager()
# login_manager.init_app(app)
# login_manager.login_view = 'login'

from models import *


# @login_manager.user_loader
# def user_loader(id):
#     return User.query.get(int(id))


@app.route('/')
def home():
    return redirect(url_for('channels_index'))


@app.route('/channels/', methods=['GET','POST'])
#@login_required
def channels_index():
    search=''
    q = Channel.query
    if request.method == 'POST':
        search=request.form['search']
        q=q.filter(Channel.name.ilike('%'+search+'%'))
    channels = q.all()
    #limit(25).
    return render_template('channels/index.html', channels=channels, search=search)
    

@app.route('/channels/<int:id>')
def get_channel(id):
    channel=db.session.query(Channel).get(id)
    items=Item.query.filter_by(channel_id=id).limit(25).all()
    return render_template('channels/view.html', channel=channel, items=items)


@app.route('/playlists/', methods=['POST', 'GET'])
def playlists_index():
    search=''
    q=Playlist.query
    if request.method == 'POST':
        playlists=[]
        q.filter(Playlist.name.ilike('%'+request.form['search']+'%'))
        search=request.form['search']
    
    playlists=q.all()
    return render_template('playlists/index.html', playlists=playlists, search=search)


@app.route('/playlists/<int:id>')
def get_playlist(id):
    playlist=db.session.query(Playlist).get(id)
    return render_template('playlists/view.html', playlist=playlist)


@app.route('/playlists/add', methods=['POST'])
def playlists_add():
    p = Playlist(request.form['name'], request.form['description'])
    db.session.add(p)
    db.session.commit()
    return redirect(url_for('playlists_index'))


@app.route('/items/move/<way>/<int:playlist_id>/<int:item_id>')
def item_move(way, playlist_id, item_id):
    app.logger.info(way +' '+str(playlist_id)+' '+str(item_id))
    p = db.session.query(Playlist).get(playlist_id)

    for idx, item in enumerate(p.items):
        if item_id == item.id:
            break

    if way == 'up':
        if idx > 0:
            i_up   = p.items[idx]
            i_down = p.items[idx-1]

    elif way == 'down':
        if idx < len(p.items):
            i_down = p.items[idx]
            i_up   = p.items[idx+1]


    app.logger.info(str(idx))
    pass


@app.route('/items/', methods=['POST', 'GET'])
def items_index():
    search=''
    q = Item.query
    if request.method == 'POST':
        search = request.form['search']

        elts = search.split(' ')
        for elt in elts:

            m = re.match('^(\d*)([mh])$', elt)
            if m is not None:
                # from min to secs
                dur = int(m.groups()[0])*60
                if m.groups()[1] == 'h':
                    dur = dur*60

                cat = PodTime().getCat(dur)

                q = q.filter(Item.cat_time == cat)
            else:
                q = q.filter(Item.name.ilike('%'+elt+"%"))

    items = q.limit(25).all()
    playlists = Playlist.query.all()
    return render_template('items/index.html', items=items, search=search, playlists=playlists)


@app.route('/items/add_to_playlist', methods=['POST'])
def add_item_to_playlist():
    nb_items = RelPlaylistItem.query.filter(RelPlaylistItem.playlist_id == request.form['playlist_id']).count()

    r = RelPlaylistItem(request.form['playlist_id'], request.form['item_id'], nb_items)
    db.session.add(r)
    db.session.commit()

    return redirect(url_for('playlists_index'))


# @app.route('/login', methods=['GET', 'POST'])
# # @oid.loginhandler
# def login():
#     form = LoginForm()
#     if form.validate_on_submit():
#         user = User.query.get(form.email.data)
#         if user:
#             if bcrypt.check_password_hash(user.password, form.password.data):
#                 user.authenticated = True
#                 db.session.add(user)
#                 db.session.commit()
#                 login_user(user, remember=True)
#                 return redirect(url_for("/"))
#     return render_template("login.html", form=form)


# @app.route('/logout', methods=['GET'])
# @login_required
# def logout():
#     user = current_user
#     user.authenticated=False
#     db.session.add(user)
#     db.session.commit()
#     logout_user()
#     return render_template('logout.html')


if __name__ == '__main__':
    handler = RotatingFileHandler('./logs.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run()
