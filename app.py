from flask import Flask, render_template, request, redirect
import psycopg2
import json
import datetime

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

enco = lambda obj: (
    obj.isoformat()
    if isinstance(obj, datetime.datetime)
    or isinstance(obj, datetime.date)
    else None
)

conn = psycopg2.connect("dbname=%s user=%s" % ('spaces','spaces'))


@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/signin', methods=['POST'])
def sign_in():
    user = request.form['login']
    pwd  = request.form['password']
    print("is %s %s" % (user, pwd))
    return redirect('/api/channels')

@app.route('/api/channels')
def get_channels():
    cur = conn.cursor()

    cur.execute("SELECT * FROM channels LIMIT 3");
    res = cur.fetchall()
    cur.close()
    conn.close()

    for ch in res:
        print(str(ch))

    return json.dumps(res, default=enco)

# @app.route('/api/register', methods=['POST'])
# def register():
#     json_data = request.json
#     user = {
#         user:json_data['user'],
#         password:json_data['password']
#     }
#     try:
#         cur = conn.cursor()
#         cur.execute('INSERT INTO users (login, password) VALUES (%s, %s)', 
#             (user['login'], user['password']))
#         conn.commit()
#         cur.close()
#         conn.close()
#         status = 'success'
#     except:
#         status = 'this user is already registered'
#     db.session.close()
#     return jsonify({'result': status})

# @app.route('/api/login', methods=['POST'])
# def login():
#     json_data = request.json
#     user = {
#         login:json_data['user'],
#         password:json_data['password']
#     }
#     cur = conn.cursor()
#     cur.execute('SELECT * FROM users WHERE login = %s', (user['login'],))
#     res = cur.fetchone()
#     if res and bcrypt.check_password_hash(
#             res[1], user['password']):
#         session['logged_in'] = True
#         status = True
#     else:
#         status = False
#     return jsonify({'result': status})