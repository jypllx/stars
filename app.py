from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import LoginManager, UserMixin, login_required
import os

app = Flask(__name__)
app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager()

import models

@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)

@app.route('/')
# @login_required
def hello_world():
    return 'Flask Dockerized blouh'

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.get(form.email.data)
        if user:
            if bcrypt.check_password_hash(user.password, form.password.data):
                user.authenticated = True
                db.session.add(user)
                db.session.commit()
                login_user(user, remember=True)
                return redirect(url_for("/"))
    return render_template("login.html", form=form)


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    user = current_user
    user.authenticated=False
    db.session.add(user)
    db.session.commit()
    logout_user()
    return render_template('logout.html')

if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0')
