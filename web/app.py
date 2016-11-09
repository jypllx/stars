from flask import Flask, url_for, redirect
from flask import request, render_template
from flask.ext.sqlalchemy import SQLAlchemy
# from flask.ext.login import LoginManager, login_required
# from flask.ext.openid import OpenID
from config import BaseConfig
import os

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
    if request.method == 'POST':
        search=request.form['search']
        channels=Channel.query.filter(Channel.name.ilike('%'+search+'%')).all()
    else:
        channels=db.session.query(Channel).all()
    return render_template('index.html', channels=channels, search=search)
    

@app.route('/channels/<int:id>')
def get_channel(id):
    channel=db.session.query(Channel).get(id)
    items=Item.query.filter_by(channel_id=id).all()
    return render_template('channel.html', channel=channel, items=items)


@app.route('/playlists/', methods=['POST', 'GET'])
def playlists_index():
    search=''
    if request.method == 'POST':
        playlists=[]
        # playlists=Playlist.query.filter(Playlist.name.ilike('%'+request.form['search']+'%')).all()
        # search=request.form['search']
    else:
        playlists=db.session.query(Playlist).all()
    return render_template('index.html', playlists=playlists, search=search)


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
