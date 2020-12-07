#!/usr/bin/python3

from flask import Flask, render_template, send_from_directory, request, session, redirect, url_for, flash, abort
from flask_mysqldb import MySQL
from flask_caching import Cache
from hashlib import md5
from random import randint

app = Flask(__name__, static_url_path='')
app.secret_key = 'CHANGE_ME_2'

app.config['MYSQL_HOST'] = 'db'
app.config['MYSQL_USER'] = 'elmos_vahed'
app.config['MYSQL_PASSWORD'] = 'CHANGE_ME'
app.config['MYSQL_DB'] = 'elmos_units'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'
app.config['CACHE_TYPE'] = 'simple'
app.config['CACHE_DEFAULT_TIMEOUT'] = 50

RP = '/var/www/elmos/' # root path
SUPPORT_PROMPT = False
CAPTCHA_LOGIN_PROMPT = True
CAPTCHA_MAINPAGE_PROMPT = True
CAPTCHA_MAINPAGE_RAND_COEFF = 3

cache = Cache(app)
mysql = MySQL(app)


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
    with open(RP + 'captcha/captcha.txt') as f:
      captcha_required = (f.readline() == 'waiting') and CAPTCHA_LOGIN_PROMPT
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
  cur.close()

  if int(session['user_dep_id']) == 15:
    flash(('yellow', 'فعلا نتونستیم درس نقشه کشی صنعتی رشته صنایع رو توی دیتابیس بیاریم. اطلاعات بیشتر در بخش نواقص دیتابیس موجود است.'))

  return redirect(url_for('schedule'))
  
@app.route('/logout')
def logout():
  session.clear();
  return redirect(url_for('home'))

def last_db_update():
  return open(RP + 'database/last_db_update', 'r').readline()

def affected_by_gender_mismatch_bug():
  cur = mysql.connection.cursor()
  bugs = cur.execute("select picks_2.user_id, picks_2.unit_id, users.gender, units.gender, units.name from picks_2 join users on picks_2.user_id = users.id join units on picks_2.unit_id=units.id where units.gender!=users.gender and units.gender!=0 and picks_2.user_id=%s;", [session['user_id']])
  if bugs == 0:
    cur.close()
    return []
  errors = cur.fetchall()
  r = []
  for e in errors:
    r.append(e['name'])
  cur.close()
  return r

@app.route('/schedule')
def schedule():
  with open(RP + 'captcha/captcha.txt') as f:
    captcha_required = (f.readline() == 'waiting') and CAPTCHA_MAINPAGE_PROMPT and (randint(0, CAPTCHA_MAINPAGE_RAND_COEFF) == 0)
  if not session.get('logged_in', False):
    return render_template('log-in-dude.html')
  else:
    if len(affected_by_gender_mismatch_bug()) > 0:
      flash(('red', 'سلام. متاسفانه شما یکی از ۱۲ نفری هستین که سایت به اشتباه درس‌هایی که به جنسیتتون نمیخورد رو توی لیستتون آورد و شما اون درس‌ها رو به برنامتون اضافه کردین. این باگ الان برطرف شده ولی اون درس‌ها هنوز توی برنامه شما هستن و باید حذفشون کنین تا همه چیز ردیف بشه. این اتفاق نباید می‌افتاد و ما خیلی خیلی متاسفیم. \n درس‌های مشکل دار این‌ها هستن: ' + '، '.join(affected_by_gender_mismatch_bug())))
    if int(session['user_dep_id']) == 18:
        flash(('yellow', 'متاسفانه بعضی از درس‌ها رو نتونستیم به درستی به دیتابیس منتقل کنیم. لطفا از پایین صفحه بخش نواقص دیتابیس را ببینید.'))
    return render_template('schedule.html', departments_list=departments_list, user_department=current_user_department, user_units=user_units(), departments_by_key=departments_by_key, last_update=last_db_update(), is_supporter=is_supporter(), support_prompt=SUPPORT_PROMPT, captcha_required=captcha_required)

def parse_dep(dep):
  cur = mysql.connection.cursor()
  rr = {}
  rr['name'] = dep['name']
  rr['units'] = []
  cur.execute("SELECT * FROM units WHERE department=%s AND gender IN(0,%s) AND obsolete=0 ORDER BY name ASC",(dep['id'], session['gender']))
  units = cur.fetchall()
  for unit in units:
    rr['units'].append({'name':unit['name'], 'id':unit['id'], 'time_start_1':unit['time_start_1'], 'time_end_1':unit['time_end_1'], 'weekday_1':unit['weekday_1'], 'time_start_2':unit['time_start_2'], 'time_end_2':unit['time_end_2'], 'weekday_2':unit['weekday_2'], 'time_start_3':unit['time_start_3'], 'time_end_3':unit['time_end_3'], 'weekday_3':unit['weekday_3'], 'instructor':unit['instructor'], 'capacity':unit['capacity'], 'registered':unit['registered_count']})
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
  
def departments_by_key():
  r = {}
  r['k90'] = get_dep(90)
  r['k27'] = get_dep(27)
  r['k14'] = get_dep(14)
  r['k16'] = get_dep(16)
  r['k26'] = get_dep(26)
  r['k28'] = get_dep(28)
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
    r.append({'name':disp_name, 'id':unit['id'], 'time_start_1':unit['time_start_1'], 'time_end_1':unit['time_end_1'], 'weekday_1':unit['weekday_1'], 'time_start_2':unit['time_start_2'], 'time_end_2':unit['time_end_2'], 'weekday_2':unit['weekday_2'], 'time_start_3':unit['time_start_3'], 'time_end_3':unit['time_end_3'], 'weekday_3':unit['weekday_3'], 'instructor':unit['instructor'], 'registered':unit['registered_count'], 'capacity':unit['capacity']})
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
  content = open(RP + 'database/errors.txt', 'r', encoding="utf-8").readlines()
  return render_template('database_notes.html', content=content)

@app.route('/captcha/img', methods=['GET', 'POST'])
def captcha_img():
  if request.method == 'POST':
    if 'file' not in request.files:
      abort(400)
    img = request.files['file']
    img.save(RP + 'captcha/captcha.png')
    with open(RP + 'captcha/captcha.txt', 'w') as value_file:
      value_file.write('waiting')
    return {}

  elif request.method == 'GET':
    return send_from_directory('captcha', 'captcha.png')

@app.route('/captcha/code/<code>', methods=['POST'])
def captcha_code_set(code):
  if len(code) < 4:
    abort(400)
  cur_code = 'null'
  with open(RP + 'captcha/captcha.txt', 'r') as value_file:
    cur_code = value_file.readline()
  if cur_code != 'waiting':
    abort(400)
  with open(RP + 'captcha/captcha.txt', 'w') as value_file:
    value_file.write(code)
    return {}

@app.route('/captcha/code', methods=['GET'])
def captcha_code_get():
  code = 'null'
  with open(RP + 'captcha/captcha.txt', 'r') as value_file:
    code = value_file.readline()
  if (code != 'waiting') and (code != 'stale'):
    with open(RP + 'captcha/captcha.txt', 'w') as value_file:
      value_file.write('stale')
  return {'code': code}


if __name__ == '__main__':
  app.run(host="0.0.0.0", port=90, debug=True)
