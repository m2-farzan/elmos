#!/usr/bin/python3

from flask import Flask, render_template, send_from_directory, request, session, redirect, url_for, flash, abort, make_response
from flask_mysqldb import MySQL
from flask_caching import Cache
from hashlib import md5
from os import environ
from random import randint
import re
from redis import Redis
import decimal
import flask.json

class MyJSONEncoder(flask.json.JSONEncoder):
    def __init__(self, **kwargs):
        kwargs['ensure_ascii'] = False
        kwargs['sort_keys'] = False
        super(MyJSONEncoder, self).__init__(**kwargs)
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            # Convert decimal instances to strings.
            return str(obj)
        return super(MyJSONEncoder, self).default(obj)


app = Flask(__name__, static_url_path='')
app.secret_key = environ['SECRET_KEY']

app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = environ['DB_USER']
app.config['MYSQL_PASSWORD'] = environ['DB_PASS']
app.config['MYSQL_DB'] = environ['DB_DATABASE']
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 50

SUPPORT_PROMPT = False
CAPTCHA_LOGIN_PROMPT = True
CAPTCHA_MAINPAGE_PROMPT = True
CAPTCHA_MAINPAGE_RAND_COEFF = 3

cache = Cache(app)
mysql = MySQL(app)

redis = Redis('redis', decode_responses=True)

app.json_encoder = MyJSONEncoder

@app.route('/')
def index():
  if session.get('logged_in', False):
    return redirect(url_for('schedule'))
  return render_template('home.html')
  
@app.route('/home')
def home():
  return render_template('home.html')

@app.route('/cheers')
def cheers():
  set_supporter()
  return render_template('cheers.html')

def set_supporter():
  try:
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO supporters(id) VALUES (%s)", [session['user_id']])
    mysql.connection.commit()
    cur.close()
  except:
    pass

def is_supporter():
  try:
    cur = mysql.connection.cursor()
    users = cur.execute("SELECT * FROM supporters WHERE id = %s" , [session['user_id']])
    r = users > 0
    cur.close()
    return r
  except:
    return False

@app.route('/css/<path:path>')
def send_css(path):
    return send_from_directory('css', path)
  
@app.route('/scripts/<path:path>')
def send_scripts(path):
    return send_from_directory('scripts', path)
    
@app.route('/images/<path:path>')
def send_img(path):
    return send_from_directory('images', path)
    
@app.route('/fonts/<path:path>')
def send_font(path):
    return send_from_directory('fonts', path)

@app.route('/favicon.ico')
def send_icon():
    return send_from_directory('images', 'favicon.ico')
    
@app.route('/sign-up', methods=['GET','POST'])
def signup():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']
    gender = 1 if request.form['gender'] == 'پسر' else 2
    user_dep_id = user_department_name_to_id( request.form['user_department'] )
    return create_user(email, password, user_dep_id, gender)
  else:
    return render_template('sign-up.html', departments=user_departments())
    
def create_user(email, password, user_dep_id, gender):
  cur = mysql.connection.cursor()
  users = cur.execute("SELECT * FROM users WHERE email = %s" , [email])
  if users > 0:
    cur.close()
    return render_template('sign-up-clash.html')
  password_hash = md5(password.encode('utf-8')).hexdigest()
  cur.execute("INSERT INTO users(email, password, department_id, gender) VALUES (%s, %s, %s, %s)", (email, password_hash, user_dep_id, gender))
  mysql.connection.commit()
  cur.close()
  return render_template('sign-up-good.html')
  
@app.route('/login', methods=['GET','POST'])
def login():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']
    if 'captcha' in request.form:
      captcha_code_set(request.form['captcha'])
    return login_as(email, password)
  else:
    captcha_required = (redis.get('captcha') == 'waiting') and CAPTCHA_LOGIN_PROMPT
    return render_template('login.html', captcha_required=captcha_required)

def login_as(email, password):
  cur = mysql.connection.cursor()
  password_hash = md5(password.encode('utf-8')).hexdigest()
  users = cur.execute("SELECT * FROM users WHERE email = %s AND (password = %s OR password = %s)" , (email, password, password_hash))
  if users == 0:
    cur.close()
    return render_template('login-check.html')
  user = cur.fetchone()
  session['logged_in'] = True;
  session['email'] = email;
  session['user_id'] = user['id'];
  session['user_dep_id'] = user['department_id'];
  session['gender'] = user['gender'];
  session.permanent = True
  cur.close()

  if int(session['user_dep_id']) == 15:
    flash(('yellow', 'فعلا نتونستیم درس نقشه کشی صنعتی رشته صنایع رو توی دیتابیس بیاریم. اطلاعات بیشتر در بخش نواقص دیتابیس موجود است.'))

  # If running on subdomain, set a `target_subdomain` cookie for auto-redirect.
  response = make_response( redirect(url_for('schedule')) )
  subdomain_match = re.findall(r"(\w+)\.\w+\.ir+", request.base_url)
  if subdomain_match:
    subdomain_basename, parent_domain = subdomain_match[0]
    response.set_cookie('target_subdomain', subdomain_basename, '.' + parent_domain, expires=2147483647)
  return response
  
@app.route('/logout')
def logout():
  session.clear();
  return redirect(url_for('home'))

def last_db_update():
  return redis.get('last_db_update') or 'N/A'

@app.route('/schedule')
def schedule():
  captcha_required = (redis.get('captcha') == 'waiting') and CAPTCHA_MAINPAGE_PROMPT and (randint(0, CAPTCHA_MAINPAGE_RAND_COEFF) == 0)
  if not session.get('logged_in', False):
    return render_template('log-in-dude.html')
  else:
    if int(session['user_dep_id']) == 18:
        flash(('yellow', 'متاسفانه بعضی از درس‌ها رو نتونستیم به درستی به دیتابیس منتقل کنیم. لطفا از پایین صفحه بخش نواقص دیتابیس را ببینید.'))
    return render_template('schedule.html', user_department=current_user_department, user_units=user_units(), comdeps=comdeps, last_update=last_db_update(), is_supporter=is_supporter(), support_prompt=SUPPORT_PROMPT, captcha_required=captcha_required)

@app.route('/lazy-list')
def lazy_list():
  return render_template('lazy-list.html', departments_list=departments_list, last_update=last_db_update())

def parse_dep(dep):
  cur = mysql.connection.cursor()
  rr = {}
  rr['name'] = dep['name']
  rr['units'] = []
  cur.execute("SELECT * FROM units WHERE department=%s AND gender IN(0,%s) AND obsolete=0 ORDER BY name ASC",(dep['id'], session['gender']))
  units = cur.fetchall()
  for unit in units:
    rr['units'].append(dict(unit))
  cur.close()
  return rr
  
def get_dep(dep_id):
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM departments WHERE id = %s", [dep_id])
  dep = cur.fetchone()
  r = parse_dep(dep)
  cur.close()
  return r
    
def departments_list():
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM departments ORDER BY name ASC")
  r = []
  deps = cur.fetchall()
  for dep in deps:
    r.append(parse_dep(dep))
  cur.close()
  return r

def comdeps():
  r = []
  cur = mysql.connection.cursor()
  cur.execute("SELECT id, dispname FROM comdeps ORDER BY sortorder ASC")
  deps = cur.fetchall()
  for dep in deps:
    dep_data = get_dep(dep['id'])
    dep_data['name'] = dep['dispname']
    r.append(dep_data)
  cur.close()
  return r
  
def current_user_department():
  did = session['user_dep_id']
  return get_dep(did)
  
def user_departments():
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM departments WHERE has_students = 1 ORDER BY name ASC")
  deps = cur.fetchall()
  r = []
  for dep in deps:
    r.append(dep['name'])
  cur.close()
  return r
  
def user_department_name_to_id(name):
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM departments WHERE name = %s", [name])
  dep = cur.fetchone()
  cur.close()
  return dep['id']

  
@app.route('/schedule/pick/<unit_id>')
def pick(unit_id):
  cur = mysql.connection.cursor()
  j = cur.execute("SELECT * FROM picks_2 WHERE user_id = %s AND unit_id = %s", (session['user_id'], unit_id))
  if j > 0:
    return 'dup'
  cur.execute("INSERT INTO picks_2(user_id, unit_id) VALUES (%s, %s)", (session['user_id'], unit_id))
  mysql.connection.commit()
  cur.close()
  return "done"
  
@app.route('/schedule/remove/<unit_id>')
def remove(unit_id):
  cur = mysql.connection.cursor()
  cur.execute("DELETE FROM picks_2 WHERE user_id = %s AND unit_id = %s", (session['user_id'], unit_id))
  mysql.connection.commit()
  cur.close()
  return "done"
  
def user_units():
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM picks_2 WHERE user_id = %s", [ session['user_id'] ])
  units = cur.fetchall()
  r = []
  for unit in units:
    unit_id = unit['unit_id']
    cur.execute("SELECT * FROM units WHERE id = %s", [ unit_id ])
    unit = cur.fetchone();
    if unit == None:
      continue
    disp_name = unit['name'] if unit['obsolete'] == 0 else '[حذف شده] - ' + unit['name']
    r.append({**dict(unit), 'name':disp_name})
  cur.execute("UPDATE users SET last_access=NOW() WHERE id = %s", [ session['user_id'] ])
  mysql.connection.commit()
  cur.close()
  return r
  
@app.route('/exams')
def exams():
  return render_template('exams.html', user_exams = user_exams())
  
def user_exams():
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM picks_2 WHERE user_id = %s", [ session['user_id'] ])
  units = cur.fetchall()
  r = []
  for exam in units:
    cur.execute("SELECT * FROM units WHERE id = %s", [ exam['unit_id'] ])
    unit = cur.fetchone()
    if unit == None:
      continue
    r.append( {'id':unit['id'], 'name':unit['name'], 'exam_day':unit['exam_day'], 'exam_time':unit['exam_time']} )
  cur.close()
  return r
  
@app.route('/summary')
def summary():
  s, w = user_summary()
  return render_template('summary.html', summary = s, total_w = w)

def user_summary():
  total_w = 0
  
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM picks_2 WHERE user_id = %s", [ session['user_id'] ])
  units = cur.fetchall()
  r = []
  for exam in units:
    cur.execute("SELECT * FROM units WHERE id = %s", [ exam['unit_id'] ])
    unit = cur.fetchone()
    if unit == None:
      continue
    disp_name = unit['name'] if unit['obsolete'] == 0 else '[حذف شده] - ' + unit['name']
    r.append( {'id':unit['id'], 'name':disp_name, 'instructor':unit['instructor'], 'weight':unit['weight']} )
    total_w = total_w + int(unit['weight'])
  cur.close()
  return r, total_w

@app.route('/database_notes')
def database_notes():
  content = (redis.get('database_errors') or 'Not Available').split('\n')
  return render_template('database_notes.html', content=content)

@app.route('/captcha/img', methods=['GET', 'POST'])
def captcha_img():
  if request.method == 'POST':
    if 'file' not in request.files:
      abort(400)
    img = request.files['file']
    img.save('captcha/captcha.png')
    redis.set('captcha', 'waiting')
    return {}

  elif request.method == 'GET':
    return send_from_directory('captcha', 'captcha.png')

@app.route('/captcha/code/<code>', methods=['POST'])
def captcha_code_set(code):
  if len(code) < 4:
    abort(400)
  cur_code = redis.get('captcha') or 'null'
  if cur_code != 'waiting':
    abort(400)
  redis.set('captcha', code)
  return {}

@app.route('/captcha/code', methods=['GET'])
def captcha_code_get():
  code = redis.get('captcha') or 'null'
  if (code != 'waiting') and (code != 'stale'):
    redis.set('captcha', 'stale')
  return {'code': code}


if __name__ == '__main__':
  app.run(host="0.0.0.0", port=90, debug=True)
