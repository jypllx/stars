from flask import Flask, url_for, redirect
from flask import request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from config import BaseConfig
import logging
from logging.handlers import RotatingFileHandler
from flask.ext.security import Security, SQLAlchemyUserDatastore, \
    login_required
from flask.ext.login import logout_user
from werkzeug import secure_filename
import os
import re
import sys
import json


app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)

from models import *
from forms  import *
user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

# @app.before_first_request
# def create_user():
#     user_datastore.create_user(email='admin@stars.com', password='1234')
#     db.session.commit()


# JINJA2 formatter
@app.template_filter('duration')
def format_duration(value):
    duration=int(value)
    seconds = duration % 60
    hours = int(duration/3600)
    minutes = int(duration / 60) - hours*60
    return '%02d:%02d:%02d' % (hours, minutes, seconds)

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
    search_source=''
    search_country=''
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
        if request.form['search_source']:
            search_source=request.form['search_source']
            q=q.filter_by(source=search_source)
        if request.form['search_country']:
            search_country=request.form['search_country']
            q=q.filter_by(country=search_country)

    channels = q.all()
    results = db.engine.execute("Select DISTINCT itunes_category_ FROM channels ORDER BY itunes_category_")
    iTunes_categories=[]
    for result in results:
        iTunes_categories.append(result[0])

    results = db.engine.execute("Select DISTINCT mood FROM channels ORDER BY mood")
    moods=[]
    for result in results:
        moods.append(result[0])

    results = db.engine.execute("Select DISTINCT source FROM channels ORDER BY source")
    sources=[]
    for result in results:
        sources.append(result[0])

    results = db.engine.execute("Select DISTINCT country FROM channels ORDER BY country")
    countries=[]
    for result in results:
        countries.append(result[0])

    return render_template('bo/channels/index.html',
        channels=channels,
        iTunes_categories=iTunes_categories, moods= moods, sources=sources, countries=countries,
        search_title=search_title, search_desc=search_desc, search_iCat=search_iCat, search_mood=search_mood,
        search_source=search_source,search_country=search_country)


@app.route('/bo/channels/<int:id>', methods=['POST', 'GET'])
@login_required
def channels_get(id):
    form = ChannelForm(request.form)
    channel=db.session.query(Channel).get(id)

    if form.validate_on_submit():
        channel.title=form.title.data
        channel.description=form.description.data
        channel.mood=form.mood.data
        channel.image=form.image.data
        channel.source=form.source.data
        channel.country=form.country.data
        app.logger.info("UPDATED !!! "+channel.country)
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
    results = db.engine.execute("Select DISTINCT mood FROM channels ORDER BY mood")
    moods=[]
    for result in results:
        moods.append(result[0])

    form=PlaylistForm(request.form)
    form.set_moods(moods)

    playlist=None
    if id is not None:
        playlist=db.session.query(Playlist).get(id)

    if request.method=='POST' and form.validate():
        if id is not None:
            playlist.name=form.name.data
            playlist.description=form.description.data
            playlist.mood=form.mood.data
        else:
            playlist=Playlist(form.name.data,
                form.description.data, form.mood.data)
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
    search_source=''
    search_country=''

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
        if request.form['search_source']:
            search_source=request.form['search_source']
            q=q.filter_by(source=search_source)
        if request.form['search_country']:
            search_country=request.form['search_country']
            q=q.filter_by(country=search_country)
        if request.form['search_date']:
            search_date=request.form['search_date']
            q=q.filter(Item.pubdate_ >= search_date)

    items = q.order_by(Item.pubdate_.desc()).limit(25).all()

    playlists = Playlist.query.all()
    
    results = db.engine.execute("Select DISTINCT itunes_category_ FROM items ORDER BY itunes_category_")
    iTunes_categories=[]
    for result in results:
        iTunes_categories.append(result[0])

    results = db.engine.execute("Select DISTINCT mood FROM items ORDER BY mood")
    moods=[]
    for result in results:
        moods.append(result[0])

    results = db.engine.execute("Select DISTINCT source FROM items ORDER BY source")
    sources=[]
    for result in results:
        sources.append(result[0])

    results = db.engine.execute("Select DISTINCT country FROM items ORDER BY country")
    countries=[]
    for result in results:
        countries.append(result[0])

    return render_template('bo/items/index.html',
        items=items, playlists=playlists,
        iTunes_categories=iTunes_categories, moods=moods, time_categories=PodTime().CATEGORIES,
        sources=sources, countries=countries,
        search_title=search_title, search_desc=search_desc, search_date=search_date,
        search_iCat=search_iCat, search_mood=search_mood, search_length=search_length,
        search_source=search_source,search_country=search_country)

@app.route('/bo/items/<int:id>', methods=['POST', 'GET'])
@login_required
def items_edit(id):
    form = ItemForm(request.form)
    item=db.session.query(Item).get(id)
    if request.method == 'POST' and form.validate():
        item.title      =form.title.data
        item.description=form.description.data
        item.mood       =form.mood.data if form.mood.data != '' else None
        item.source     =form.source.data
        item.country    =form.country.data
        
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

    results = db.engine.execute("Select DISTINCT mood FROM channels ORDER BY mood")
    moods=[]
    for result in results:
        moods.append(result[0])
    return render_template('mobile/home.html', playlists=playlists, 
        time_categories=PodTime().CATEGORIES, moods=moods)


@app.route('/ajax/items', methods=['POST'])
@login_required
def mob_home_ajax():
    q = Item.query
    qP = Playlist.query

    cat_time = ''
    mood = ''
    page = int(request.form['page'])
    if request.form['cat_time']:
        cat_time = request.form['cat_time']
        q = q.filter_by(cat_time=cat_time)
    if request.form['mood']:
        mood=request.form['mood']
        q = q.filter_by(mood=mood)
        qP = qP.filter_by(mood=mood)
    
    nb   = q.count()
    if page == nb and nb != 0:
        page = nb-1
    item = q.order_by(Item.pubdate_.desc()).offset(int(page)).first()

    pp = []
    playlists=qP.limit(4).all()
    for playlist in playlists:
        pp.append({'id':playlist.id,'name':playlist.name})

    data = {'item':
        {
            'name':item.title,
            'description':item.description,
            'duration':format_duration(item.duration_),
            'image':item.image,
            'audio_url':item.audio_url_
        }, 
        'cat_time':cat_time, 'mood':mood, 'page':page,
        'playlists':pp}


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
            q = q.filter(Item.title.ilike('%'+search+'%'))
        if request.form['cat_time']:
            cat_time=request.form['cat_time']
            q = q.filter_by(cat_time=cat_time)
        if request.form['playlist_id']:
            playlist_id=request.form['playlist_id']
            rels=RelPlaylistItem.query.filter_by(playlist_id=playlist_id)
            item_ids=[]
            for rel in rels:
                item_ids.append(rel.item_id)
            q=q.filter(Item.id.in_(item_ids))
        if request.form['channel_id']:
            channel_id=request.form['channel_id']
            q=q.filter_by(channel_id=channel_id)
        if request.form['mood']:
            q=q.filter_by(mood=request.form['mood'])

        items = q.order_by(Item.pubdate_.desc()).limit(10).all()

        return render_template('mobile/resultats.html', 
            items=items, time_categories=PodTime().CATEGORIES,
            search=search, cat_time=cat_time, 
            playlist_id=playlist_id, channel_id=channel_id)


@app.route('/library/')
@login_required
def mob_library():
    return render_template('mobile/home.html')


@app.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/moods/', methods=['POST', 'GET'])
@login_required
def moods_index():
    podmood=PodMood()
    form=MoodForm()
    update=False

    if form.validate_on_submit():
        filename = secure_filename(form.mood_file.data.filename)
        form.mood_file.data.save(filename)

        app.logger.info
        # saved file with original title. Need to rename to moods.xlsx
        os.remove(podmood.file)
        os.rename(filename, podmood.file)

        podmood=PodMood()
        update=True
  
    results = db.engine.execute("Select DISTINCT itunes_category_ FROM channels ORDER BY itunes_category_")
    mappings=[]
    for result in results:
        iCat = result[0]
        mood = podmood.get_mood(iCat)
        mappings.append({'itunes_category':iCat, 'mood':mood})

        if update:
            mood = "'"+mood+"'" if mood is not None else "NULL"
            db.engine.execute("UPDATE channels SET mood="+mood+" WHERE itunes_category_='"+iCat+"'")
            db.engine.execute("UPDATE items    SET mood="+mood+" WHERE itunes_category_='"+iCat+"'")
            db.session.commit()

    mood_url = url_for('static', filename='files/'+os.path.basename(podmood.file))

    return render_template('bo/moods/index.html',
        mappings=mappings,
        form=form, 
        mood_file=mood_url)

if __name__ == '__main__':
    handler = RotatingFileHandler('./logs.log', maxBytes=10000, backupCount=1)
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
    app.run(debug=True)
