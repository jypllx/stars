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
from forms  import *

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
    search_iCat=''
    search_mood=''
    q = Channel.query
    if request.method == 'POST':
        # TODO : replace by WTForms
        if request.form['search_title']:
            search_title = request.form['search_title']
            for elt in search_title.split(' '):
                q = q.filter(Channel.title_.ilike('%'+elt+"%"))
        if request.form['search_desc']:
            search_desc = request.form['search_desc']
            for elt in search_desc.split(' '):
                q = q.filter(Channel.description_.ilike('%'+elt+"%"))
        if request.form['search_iCat']:
            search_iCat=request.form['search_iCat']
            q=q.filter_by(itunes_category_=search_iCat)
        if request.form['search_mood']:
            search_mood=request.form['search_mood']
            q=q.filter_by(mood=search_mood)

    channels = q.all()
    results = db.engine.execute("Select DISTINCT itunes_category_ FROM channels ORDER BY itunes_category_")
    iTunes_categories=[]
    for result in results:
        iTunes_categories.append(result[0])

    results = db.engine.execute("Select DISTINCT mood FROM channels ORDER BY mood")
    moods=[]
    for result in results:
        moods.append(result[0])

    return render_template('bo/channels/index.html',
        channels=channels,
        iTunes_categories=iTunes_categories, moods= moods,
        search_title=search_title, search_desc=search_desc, search_iCat=search_iCat, search_mood=search_mood)


@app.route('/bo/channels/<int:id>', methods=['POST', 'GET'])
@login_required
def channels_get(id):
    form = ChannelForm(request.form)
    channel=db.session.query(Channel).get(id)
    if request.method == 'POST' and form.validate():
        channel.title=form.title.data
        channel.description=form.description.data
        channel.mood=form.mood.data
        channel.image=form.image.data
        db.session.commit()
        return redirect(url_for('channels_get', id=id))

    channel=db.session.query(Channel).get(id)
    form.populate(channel)
    items=Item.query.filter_by(channel_id=id).limit(25).all()
    return render_template('bo/channels/view.html', form=form, items=items)


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
    return render_template('bo/playlists/index.html', playlists=playlists, search=search, tag_id=tag_id, tags=tags)

@app.route('/bo/playlists/edit', methods=['POST', 'GET'])
@app.route('/bo/playlists/edit/<int:id>', methods=['POST', 'GET'])
@login_required
def playlists_edit(id=None):
    form=PlaylistForm(request.form)
    playlist=None
    if id is not None:
        playlist=db.session.query(Playlist).get(id)

    if request.method=='POST' and form.validate():
        if id is not None:
            playlist.name=form.name.data
            playlist.description=form.description.data
        else:
            playlist=Playlist(form.name.data,
                form.description.data)
            db.session.add(playlist)
        db.session.commit()
        return redirect(url_for('playlists_edit', id=playlist.id))

    items=[]
    if id is not None:
        form.populate(playlist)
        items=playlist.ranked_items
    return render_template('bo/playlists/edit.html', form=form,
        items=items)


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
def items_move(way, playlist_id, item_id):
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

    return redirect(url_for('playlists_edit', id=playlist_id))

@app.route('/bo/items/remove/<int:playlist_id>/<int:item_id>')
@login_required
def items_remove(playlist_id, item_id):
    r=RelPlaylistItem.query.filter_by(playlist_id=playlist_id).filter_by(item_id=item_id).first()
    rank=r.rank

    others=RelPlaylistItem.query.filter_by(playlist_id=playlist_id).filter(RelPlaylistItem.rank>rank).all()
    for other in others:
        other.rank=other.rank-1
    db.session.delete(r)
    db.session.commit()
    return redirect(url_for('playlists_edit', id=playlist_id))


@app.route('/bo/items/', methods=['POST', 'GET'])
@login_required
def items_index():
    search_title=''
    search_desc=''
    search_iCat=''
    search_mood=''
    search_length='-1'
    search_date=''

    q = Item.query
    if request.method == 'POST':
        if request.form['search_title']:
            search_title = request.form['search_title']
            for elt in search_title.split(' '):
                q = q.filter(Item.title.ilike('%'+elt+"%"))
        if request.form['search_desc']:
            search_desc = request.form['search_desc']
            for elt in search_desc.split(' '):
                q = q.filter(Item.description.ilike('%'+elt+"%"))
        if request.form['search_iCat']:
            search_iCat=request.form['search_iCat']
            q=q.filter_by(itunes_category_=search_iCat)
        if request.form['search_mood']:
            search_mood=request.form['search_mood']
            q=q.filter_by(mood=search_mood)
        if request.form['search_length']:
            search_length=request.form['search_length']
            q=q.filter_by(cat_time=search_length)
        if request.form['search_date']:
            search_date=request.form['search_date']
            q=q.filter(Item.pubdate_ >= search_date)

    else:
        q=q.order_by(Item.pubdate_.desc()).limit(25)
    items = q.all()
    playlists = Playlist.query.all()
    
    results = db.engine.execute("Select DISTINCT itunes_category_ FROM items ORDER BY itunes_category_")
    iTunes_categories=[]
    for result in results:
        iTunes_categories.append(result[0])

    results = db.engine.execute("Select DISTINCT mood FROM items ORDER BY mood")
    moods=[]
    for result in results:
        moods.append(result[0])

    return render_template('bo/items/index.html',
        items=items, playlists=playlists,
        iTunes_categories=iTunes_categories, moods=moods, time_categories=PodTime().CATEGORIES,
        search_title=search_title, search_desc=search_desc, search_date=search_date,
        search_iCat=search_iCat, search_mood=search_mood, search_length=search_length)

@app.route('/bo/items/<int:id>', methods=['POST', 'GET'])
@login_required
def items_edit(id):
    form = ItemForm(request.form)
    item=db.session.query(Item).get(id)
    if request.method == 'POST' and form.validate():
        item.title      =form.title.data
        item.description=form.description.data
        item.mood       =form.mood.data if form.mood.data != '' else None
        
        db.session.commit()
        return redirect(url_for('items_index'))

    channel=db.session.query(Channel).get(item.channel_id)
    form.populate(item, channel)
    return render_template('bo/items/edit.html',
        form=form)

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
    return render_template('bo/tags/index.html', tags=tags)

@app.route('/bo/tags/edit',  methods=['POST', 'GET'])
@app.route('/bo/tags/edit/<id>', methods=['POST', 'GET'])
@login_required
def tags_edit(id=None):
    form = TagForm(request.form)
    tag=None
    if id is not None:
        tag = db.session.query(Tag).get(id)
    
    if request.method=='POST' and form.validate():
        if id is not None:
            tag.name=form.name.data
            tag.description=form.description.data
        else:
            tag=Tag(form.name.data, form.description.data)
            db.session.add(tag)
        db.session.commit()
        return redirect(url_for('tags_index'))

    if id is not None:
        form.populate(tag)
    return render_template('bo/tags/edit.html', form=form)

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
    return render_template('mobile/home.html', playlists=playlists, time_categories=PodTime().CATEGORIES)

@app.route('/ajax/items', methods=['POST'])
@login_required
def mob_home_ajax():
    q = Item.query

    cat_time = request.form['cat_time']
    itunes_category_ = request.form['itunes_cat']
    page = int(request.form['page'])
    if cat_time != '':
        q = q.filter(Item.cat_time == cat_time)

    if itunes_category_ == 'Comedy':
        q = q.filter_by(itunes_category_ = 'Comedy')
    elif itunes_category_ == 'Culture':
        q = q.filter_by(itunes_category_ = 'Society & Culture')
    elif itunes_category_ == 'Sports':
        q = q.filter_by(itunes_category_ = 'Sports & Recreation')
    else:
        q = q.filter_by(itunes_category_ = 'News & Politics')
    
    nb   = q.count()
    if page == nb and nb != 0:
        page = nb-1
    item = q.order_by(Item.pubdate_.desc()).offset(int(page)).first()

    data = {'item':
        {
            'name':'Aucun résultat' if item is None else item.title[:30]+'...', 
            'description': '' if item is None else item.description[:100]+'...',
            'duration':'' if item is None else item.duration_
        }, 
        'cat_time':cat_time, 'itunes_category_':itunes_category_, 'page':page}


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
            time_categories=PodTime().CATEGORIES,
            tags=tags, channels=channels)
    if request.method=='POST':
        search=''
        cat_time='-1'
        playlist_id=''
        channel_id=''
        
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
            q=q.filter_by(channel_id=channel_id)
        if request.form['itunes_category']:
            q=q.filter_by(itunes_category_=request.form['itunes_category'])

        items = q.limit(10).all()
        return render_template('mobile/resultats.html', 
            items=items, time_categories=PodTime().CATEGORIES,
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
