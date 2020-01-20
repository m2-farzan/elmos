#!/usr/bin/python3

from flask import Flask, render_template, send_from_directory, request, session, redirect, url_for
from flask_mysqldb import MySQL

app = Flask(__name__, static_url_path='')
app.secret_key = 'CHANGE_ME_2'

app.config['MYSQL_HOST'] = '127.0.0.1'
app.config['MYSQL_USER'] = 'elmos_vahed'
app.config['MYSQL_PASSWORD'] = 'CHANGE_ME'
app.config['MYSQL_DB'] = 'elmos_units'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)


@app.route('/')
def home():
  return render_template('home.html')
  
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
  cur.execute("INSERT INTO users(email, password, department_id, gender) VALUES (%s, %s, %s, %s)", (email, password, user_dep_id, gender))
  mysql.connection.commit()
  cur.close()
  return render_template('sign-up-good.html')
  
@app.route('/login', methods=['GET','POST'])
def login():
  if request.method == 'POST':
    email = request.form['email']
    password = request.form['password']
    return login_as(email, password)
  else:
    return render_template('login.html')

def login_as(email, password):
  cur = mysql.connection.cursor()
  users = cur.execute("SELECT * FROM users WHERE email = %s AND password = %s" , (email, password))
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
  return redirect(url_for('schedule'))
  
@app.route('/logout')
def logout():
  session.clear();
  return home()

@app.route('/schedule')
def schedule():
  if not session.get('logged_in', False):
    return render_template('log-in-dude.html')
  else:
    return render_template('schedule.html', departments_list=departments_list(), user_department=current_user_department(), user_units=user_units(), departments_by_key=departments_by_key())

def parse_dep(dep, cur):
  rr = {}
  rr['name'] = dep['name']
  rr['units'] = []
  cur.execute("SELECT * FROM units WHERE department=%s AND gender IN(0,%s) ORDER BY name ASC",(dep['id'], session['gender']))
  units = cur.fetchall()
  for unit in units:
    rr['units'].append({'name':unit['name'], 'id':unit['id'], 'time_start_1':unit['time_start_1'], 'time_end_1':unit['time_end_1'], 'weekday_1':unit['weekday_1'], 'time_start_2':unit['time_start_2'], 'time_end_2':unit['time_end_2'], 'weekday_2':unit['weekday_2'], 'instructor':unit['instructor']})
  return rr
  
def get_dep(dep_id):
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM departments WHERE id = %s", [dep_id])
  dep = cur.fetchone()
  r = parse_dep(dep, cur)
  cur.close()
  return r
    
    
def departments_list():
  cur = mysql.connection.cursor()
  cur.execute("SELECT * FROM departments ORDER BY name ASC")
  r = []
  deps = cur.fetchall()
  for dep in deps:
    r.append( parse_dep(dep, cur) )
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
    r.append({'name':unit['name'], 'id':unit['id'], 'time_start_1':unit['time_start_1'], 'time_end_1':unit['time_end_1'], 'weekday_1':unit['weekday_1'], 'time_start_2':unit['time_start_2'], 'time_end_2':unit['time_end_2'], 'weekday_2':unit['weekday_2'], 'instructor':unit['instructor']})
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
    r.append( {'id':unit['id'], 'name':unit['name'], 'instructor':unit['instructor'], 'weight':unit['weight']} )
    total_w = total_w + int(unit['weight'])
  cur.close()
  return r, total_w

if __name__ == '__main__':
  app.run(host="0.0.0.0", port=90, debug=True)
