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
    return redirect(url_for('mob_home'))

@app.route('/bo/')
@login_required
def home_bo():
    return redirect(url_for('channels_index'))

@app.route('/bo/channels/', methods=['GET','POST'])
@login_required
def channels_index():
    search_title=''
    search_desc=''
    search_genre=''
    q = Channel.query
    if request.method == 'POST':
        # TODO : replace by WTForms
        if request.form['search_title']:
            search_title = request.form['search_title']
            for elt in search_title.split(' '):
                q = q.filter(Channel.name.ilike('%'+elt+"%"))
        if request.form['search_desc']:
            search_desc = request.form['search_desc']
            for elt in search_desc.split(' '):
                q = q.filter(Channel.description.ilike('%'+elt+"%"))
        if request.form['search_genre']:
            search_genre=request.form['search_genre']
            q=q.filter_by(genre=search_genre)

    channels = q.all()
    results = db.engine.execute("Select DISTINCT genre FROM channels ORDER BY genre")
    genres=[]
    for result in results:
        genres.append(result[0])

    return render_template('channels/index.html', 
        channels=channels, 
        genres=genres,
        search_title=search_title, search_desc=search_desc, search_genre=search_genre)
    

@app.route('/bo/channels/<int:id>')
@login_required
def channels_get(id):
    channel=db.session.query(Channel).get(id)
    items=Item.query.filter_by(channel_id=id).limit(25).all()
    return render_template('channels/view.html', channel=channel, items=items)

@app.route('/bo/channels/edit/<int:id>', methods=['POST'])
def channels_edit(id):
    pass


@app.route('/bo/playlists/', methods=['POST', 'GET'])
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


@app.route('/bo/playlists/<int:id>')
@login_required
def playlists_get(id):
    playlist=db.session.query(Playlist).get(id)
    return render_template('playlists/view.html', playlist=playlist)


@app.route('/bo/playlists/add', methods=['POST'])
@login_required
def playlists_add():
    p = Playlist(request.form['name'], request.form['description'])
    db.session.add(p)
    db.session.commit()
    return redirect(url_for('playlists_index'))

@app.route('/bo/playlists/delete/<int:id>', methods=['GET'])
@login_required
def playlists_delete(id):
    rels=RelPlaylistItem.query.filter_by(playlist_id=id).all()
    for rel in rels:
        db.session.delete(rel)
    playlist=db.session.query(Playlist).get(id)
    db.session.delete(playlist)
    db.session.commit()

    return redirect(url_for('playlists_index'))

@app.route('/bo/playlists/add_tag', methods=['POST'])
@login_required
def playlists_add_tag():
    p=db.session.query(Playlist).get(request.form['tag_playlist_id'])
    p.tag_id = request.form['tag_id']
    db.session.add(p)
    db.session.commit()
    return redirect(url_for('playlists_index'))


@app.route('/bo/items/move/<way>/<int:playlist_id>/<int:item_id>')
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


@app.route('/bo/items/', methods=['POST', 'GET'])
@login_required
def items_index():
    search_title=''
    search_desc=''
    search_genre=''
    search_length=''

    q = Item.query
    if request.method == 'POST':
        if request.form['search_title']:
            search_title = request.form['search_title']
            for elt in search_title.split(' '):
                q = q.filter(Item.name.ilike('%'+elt+"%"))
        if request.form['search_desc']:
            search_desc = request.form['search_desc']
            for elt in search_desc.split(' '):
                q = q.filter(Item.description.ilike('%'+elt+"%"))
        if request.form['search_genre']:
            q=q.filter_by(genre=search_genre)
        if request.form['search_length']:
            search_length=request.form['search_length']
            q=q.filter_by(cat_time=search_length)
    else:
        q=q.order_by(Item.created.desc()).limit(25)
    items = q.all()
    playlists = Playlist.query.all()
    
    results = db.engine.execute("Select DISTINCT genre FROM items ORDER BY genre")
    genres=[]
    for result in results:
        genres.append(result[0])

    return render_template('items/index.html', 
        items=items, playlists=playlists, genres=genres,
        search_title=search_title, search_desc=search_desc, search_genre=search_genre, search_length='')


@app.route('/bo/items/add_to_playlist', methods=['POST'])
@login_required
def add_item_to_playlist():
    nb_items = RelPlaylistItem.query.filter(RelPlaylistItem.playlist_id == request.form['playlist_id']).count()

    r = RelPlaylistItem(request.form['playlist_id'], request.form['item_id'], nb_items)
    db.session.add(r)
    db.session.commit()

    return redirect(url_for('playlists_index'))

@app.route('/bo/tags/')
@login_required
def tags_index():
    tags = Tag.query.all()
    return render_template('tags/index.html', tags=tags)

@app.route('/bo/tags/add', methods=['POST'])
@login_required
def tags_add():
    t = Tag(request.form['name'], request.form['description'])
    db.session.add(t)
    db.session.commit()
    return redirect(url_for('tags_index'))

@app.route('/bo/tags/delete/<int:id>')
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

@app.route('/home', methods=['GET'])
@login_required
def mob_home():
    playlists = Playlist.query.order_by(Playlist.created.desc()).limit(4).all()
    return render_template('mobile/home.html', playlists=playlists)

@app.route('/ajax/items', methods=['POST'])
@login_required
def mob_home_ajax():
    q = Item.query
    #app.logger.info("%s , %s" % (request.form['cat_time'], request.form['genre']))    

    cat_time = request.form['cat_time']
    genre = request.form['genre']
    page = int(request.form['page'])
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
    
    nb   = q.count()
    app.logger.info(nb)
    if page == nb and nb != 0:
        page = nb-1
    item = q.order_by(Item.published.desc()).offset(int(page)).first()

    data = {'item':
        {
            'name':'Aucun résultat' if item is None else item.name[:30]+'...', 
            'description': '' if item is None else item.description[:100]+'...',
            'duration':'' if item is None else item.duration_str
        }, 
        'cat_time':cat_time, 'genre':genre, 'page':page}


    return json.dumps(data)

@app.route('/ajax/playlist/', methods=['POST'])
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

@app.route('/search/', methods=['POST', 'GET'])
@login_required
def mob_search():
    if request.method=='GET':
        tags=Tag.query.limit(2).all()
        channels=Channel.query.limit(4).all()
        return render_template('mobile/recherche.html',
            tags=tags, channels=channels)
    if request.method=='POST':
        search=''
        cat_time=''
        playlist_id=''
        channel_id='-1'
        
        q = Item.query
        if request.form['search'] :
            search = request.form['search']
            q = q.filter(Item.name.ilike('%'+search+'%'))
        if request.form['cat_time']:
            cat_time=request.form['cat_time']
            q = q.filter_by(cat_time=cat_time)

        if request.form['playlist_id']:
            playlist_id=request.form['playlist_id']
            rels=RelPlaylistItem.query.filter_by(playlist_id=playlist_id)
            item_ids=[]
            for rel in rels:
                item_ids.append(rel.item_id)
            if item_ids:
                q=q.filter(Item.id.in_(item_ids))
        if request.form['channel_id']:
            channel_id=request.form['channel_id']
            app.logger.info(channel_id)
            q=q.filter_by(channel_id=channel_id)

        items = q.limit(10).all()
        app.logger.info(items)
        return render_template('mobile/resultats.html', 
            items=items, 
            search=search, cat_time=cat_time, playlist_id=playlist_id, channel_id=channel_id)


@app.route('/library/')
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
