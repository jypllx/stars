from flask import Flask, url_for, redirect
from flask import request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from config import BaseConfig
import logging
from logging.handlers import RotatingFileHandler
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    login_required
from flask.ext.login import logout_user

app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)

import os
import re
import sys
import json

from models import *

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# @app.before_first_request
# def create_user():
#     user_datastore.create_user(email='admin@stars.com', password='1234')
#     db.session.commit()


@app.route('/')
@login_required
def home():
    # return redirect(url_for('channels_index'))
    return render_template('choice.html')


@app.route('/channels/', methods=['GET','POST'])
@login_required
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
@login_required
def get_channel(id):
    channel=db.session.query(Channel).get(id)
    items=Item.query.filter_by(channel_id=id).limit(25).all()
    return render_template('channels/view.html', channel=channel, items=items)


@app.route('/playlists/', methods=['POST', 'GET'])
@login_required
def playlists_index():
    search=''
    tag_id=''
    q=Playlist.query
    if request.method == 'POST':

        if request.form['search'] is not None and request.form['search'] != '':
            search=request.form['search']
            q=q.filter(Playlist.name.ilike('%'+search+'%'))
            
        if request.form['tag_id'] is not None and request.form['tag_id'] != '':
            tag_id=request.form['tag_id']
            q=q.filter_by(tag_id=tag_id)

    playlists=q.all()
    tags=Tag.query.all()
    return render_template('playlists/index.html', playlists=playlists, search=search, tag_id=tag_id, tags=tags)


@app.route('/playlists/<int:id>')
@login_required
def get_playlist(id):
    playlist=db.session.query(Playlist).get(id)
    return render_template('playlists/view.html', playlist=playlist)


@app.route('/playlists/add', methods=['POST'])
@login_required
def playlists_add():
    p = Playlist(request.form['name'], request.form['description'])
    db.session.add(p)
    db.session.commit()
    return redirect(url_for('playlists_index'))

@app.route('/playlists/delete/<int:id>', methods=['GET'])
@login_required
def playlists_delete(id):
    rels=RelPlaylistItem.query.filter_by(playlist_id=id).all()
    for rel in rels:
        db.session.delete(rel)
    playlist=db.session.query(Playlist).get(id)
    db.session.delete(playlist)
    db.session.commit()

    return redirect(url_for('playlists_index'))

@app.route('/playlists/add_tag', methods=['POST'])
@login_required
def playlists_add_tag():
    p=db.session.query(Playlist).get(request.form['tag_playlist_id'])
    p.tag_id = request.form['tag_id']
    db.session.add(p)
    db.session.commit()
    return redirect(url_for('playlists_index'))



@app.route('/items/move/<way>/<int:playlist_id>/<int:item_id>')
@login_required
def item_move(way, playlist_id, item_id):
    #app.logger.info(way +' '+str(playlist_id)+' '+str(item_id))

    r = RelPlaylistItem.query.filter(RelPlaylistItem.playlist_id==playlist_id,
            RelPlaylistItem.item_id==item_id).first()
    rank = r.rank
    if way == 'up':
        new_rank = rank - 1
    elif way == 'down':
        new_rank = rank + 1

    rm = RelPlaylistItem.query.filter(RelPlaylistItem.playlist_id==playlist_id,
            RelPlaylistItem.rank==new_rank).first()

    rm.rank=rank
    r.rank=new_rank
    db.session.commit()

    return redirect(url_for('get_playlist', id=playlist_id))


@app.route('/items/', methods=['POST', 'GET'])
@login_required
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
@login_required
def add_item_to_playlist():
    nb_items = RelPlaylistItem.query.filter(RelPlaylistItem.playlist_id == request.form['playlist_id']).count()

    r = RelPlaylistItem(request.form['playlist_id'], request.form['item_id'], nb_items)
    db.session.add(r)
    db.session.commit()

    return redirect(url_for('playlists_index'))

@app.route('/tags/')
@login_required
def tags_index():
    tags = Tag.query.all()
    return render_template('tags/index.html', tags=tags)

@app.route('/tags/add', methods=['POST'])
@login_required
def tags_add():
    t = Tag(request.form['name'], request.form['description'])
    db.session.add(t)
    db.session.commit()
    return redirect(url_for('tags_index'))

@app.route('/tags/delete/<int:id>')
@login_required
def tags_delete(id):
    playlists = Playlist.query.filter_by(tag_id=id).all()
    for playlist in playlists:
        playlist.tag_id = None
    db.session.commit()
    
    t = db.session.query(Tag).get(id)
    db.session.delete(t)
    db.session.commit()
    return redirect(url_for('tags_index'))

@app.route('/mob/home/', methods=['GET'])
@login_required
def mob_home():
    playlists = Playlist.query.order_by(Playlist.created.desc()).limit(4).all()
    return render_template('mobile/home.html', playlists=playlists)

@app.route('/mob/home/ajax', methods=['POST'])
@login_required
def mob_home_ajax():
    q = Item.query
    #app.logger.info("%s , %s" % (request.form['cat_time'], request.form['genre']))    

    cat_time = request.form['cat_time']
    genre = request.form['genre']
    if cat_time != '':
        q = q.filter(Item.cat_time == cat_time)

    if genre == 'Comedy':
        q = q.filter(Item.genre == 'Comedy')
    elif genre == 'Culture':
        q = q.filter(Item.genre == 'Society & Culture')
    elif genre == 'Sports':
        q = q.filter(Item.genre == 'Sports & Recreation')
    else:
        q = q.filter(Item.genre == 'News & Politics')
    
    item = q.order_by(Item.published.desc()).first()
    data = {'item':
        {
            'name':'' if item is None else item.name[:30]+'...', 
            'description': '' if item is None else item.description[:100]+'...',
            'duration':'' if item is None else item.duration_str
        }, 
        'cat_time':cat_time, 'genre':genre}


    return json.dumps(data)

@app.route('/mob/playlist/', methods=['POST'])
@login_required
def mob_playlist_ajax():
    playlist=db.session.query(Playlist).get(request.form['playlistId'])
    item = None
    if len(playlist.ranked_items) != 0:
        item = playlist.ranked_items[0].item

    data = {'item':
        {
            'name':'No podcast found!!!' if item is None else item.name[:30]+'...', 
            'description': '' if item is None else item.description[:100]+'...',
            'duration':'' if item is None else item.duration_str
        }, 
        'playlistId':request.form['playlistId']}

    return json.dumps(data)

@app.route('/mob/search/', methods=['POST', 'GET'])
@login_required
def mob_search():
    if request.method=='GET':
        tags=Tag.query.limit(2).all()
        channels=Channel.query.limit(4).all()
        return render_template('mobile/recherche.html', tags=tags, channels=channels)
    if request.method=='POST':
        search=''
        cat_time=''
        
        q = Item.query
        if request.form['search'] :
            app.logger.info('BOUYA')
            q = q.filter(Item.name.ilike('%'+request.form['search']+'%'))
        if request.form['cat-time']:
            q = q.filter_by(cat_time=cat_time)

        if request.form['playlist_id']:
            rels=RelPlaylistItem.query.filter_by(playlist_id=request.form['playlist_id'])
            item_ids=[]
            for rel in rels:
                item_ids.append(rel.item_id)
            if item_ids:
                q=q.filter(Item.id.in_(item_ids))
        if request.form['channel_id']:
            q=q.filter_by(channel_id=request.form['channel_id'])

        items = q.limit(10).all()
        app.logger.info(items)
        return render_template('mobile/resultats.html', items=items, search=search, cat_time=cat_time)


@app.route('/mob/library/')
@login_required
def mob_library():
    return render_template('mobile/home.html')


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


if __name__ == '__main__':
    handler = RotatingFileHandler('./logs.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run()
