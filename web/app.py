from flask import Flask, url_for, redirect
from flask import request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
# from flask.ext.login import LoginManager, login_required
# from flask.ext.openid import OpenID
from config import BaseConfig
import os
import re

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
    channels = q.limit(25).all()
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


@app.route('/playlists/add', methods=['POST'])
def playlists_add():
    p = Playlist(request.form['name'], request.form['description'])
    db.session.add(p)
    db.session.commit()
    return redirect(url_for('playlists_index'))

@app.route('/items/', methods=['POST', 'GET'])
def items_index():
    p = re.compile('(\d*)([mh])')
    search=''
    if request.method == 'POST':
        search = request.form['search']
        q = Item.query

        elts = search.split(' ')
        for elt in elts:
            m = p.match(elt)
            if m is not None:
                if m.group()[1] == 'm':
                    q = q.filter(Item.cat_time == int(m.group()[0])*60)
            else:
                q = q.filter(Item.name.ilike('%'+elt+"%"))
    else:
        q=Item.query

    items = q.limit(25).all()
    return render_template('items/index.html', items=items, search=search)


# @app.route('/playlists/add', methods=['POST', 'GET'])
# def playlists_add():
#     pass


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
    app.run()
