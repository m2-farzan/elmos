#!/usr/bin/python3
import mysql.connector
from persian_datetime import now_to_str
from flask import Flask, request
from os import environ, uname
from redis import Redis
from utils import extract_weekdays, extract_week_times, filter_farsi, get_exam_datetime, simplify_dep_name, limit_warning, xml_preprocess
import xml.etree.ElementTree as XMLET

DATA_AVAIL_PATH = "data_avail.xml"
DATA_NA_PATH = "data_na.xml"

db_config = {
    'host': 'db',
    'user': environ['DB_USER'],
    'passwd': environ['DB_PASS'],
    'database': environ['DB_DATABASE']
}
mydb = mysql.connector.connect(**db_config)

redis = Redis('redis', db=0)

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def http_entry():
    if request.method == 'GET':
        return 'Service Up. Hostname is: ' + uname()[1]
    request.files['data_avail'].save(DATA_AVAIL_PATH)
    request.files['data_na'].save(DATA_NA_PATH)
    main()
    return 'Files received.'


def fetch_file(f, mycursor, prefix = ""):
  root = XMLET.fromstring(
    xml_preprocess(
      f.read()
    )
  )

  errors = []
  for j in range(len(root)):
    if (j%100 == 0):
      print("progress: %d/%d" % (j, len(root)), flush=True)
    try:
      data = root[j].attrib

      dep_id = data['B2'] + data['B4'] # !
      id_raw = data['C1'] # !
      name = data['C2'] # !
      weight = data['C3'] # !
      capacity = data['C7'] #!
      registered = data['C8'] #!
      gender = data['C10'] #!
      instructor = data['C11'] #!
      schedule_time = data['C12'] #!
      exam_time_x = data['C13'] #!
      limit = data['C15'] #~
      desc = data['C25'] #~


      id_f = id_raw[:7] + id_raw[8:10]
      name_f = prefix + filter_farsi(name)
      if name_f[0:9] == 'آزمایشگاه':
        name_f = name_f.replace('آزمایشگاه', 'آز')
      gender_f = 0
      if gender == 'مرد':
        gender_f = 1
      if gender == 'زن':
        gender_f = 2
      instructor_f = filter_farsi(instructor)[:-1]
      exam_day, exam_time = get_exam_datetime(exam_time_x)
      
      
      if (dep_id == '90' and ('ورزش' in name)):
        instructor_f = instructor_f + " - " + desc

      # general limit parser
      warnings = limit_warning(id_raw, limit)
      if len(warnings) > 0:
        instructor_f = '(' + limit_warning(id_raw, limit) + ') - ' + instructor_f

      # nime-1 exactly repeated as nime-2:
      if 'نيمه2' in schedule_time:
        cursor = schedule_time.rfind('نيمه1')
        comma = schedule_time.find('،', cursor)
        n1 = schedule_time[0:comma]
        n2 = schedule_time[comma+2:]
        n2 = n2.replace('نيمه2', 'نيمه1')
        n1.replace('حل تمرين', 'درس')
        n2.replace('حل تمرين', 'درس')
        n1.replace('ت', 'ع')
        n2.replace('ت', 'ع')
        if n1 == n2:
          schedule_time = n1
        elif n1 in n2:
          schedule_time = n2
        elif n2 in n1:
          schedule_time = n1
        else:
          print(id_raw)
          print (n1)
          print(n2)
      
      # ravesh tolid:
      if id_raw == '1911395_01':
        days = [2]
      else:
        days = extract_weekdays(schedule_time)
      day_1 = days[0]
      day_2 = -1
      day_3 = -1
      if len(days) > 1:
        day_2 = days[1]
      if len(days) > 2:
        day_3 = days[2]
      start_1 = extract_week_times(schedule_time,1)[0]
      end_1 = extract_week_times(schedule_time,1)[1]
      start_2 = -1
      end_2 = -1
      start_3 = -1
      end_3 = -1
      if len(days) > 1:
        start_2 = extract_week_times(schedule_time,2)[0]
        end_2 = extract_week_times(schedule_time,2)[1]
      if len(days) > 2:
        start_3 = extract_week_times(schedule_time,3)[0]
        end_3 = extract_week_times(schedule_time,3)[1]
    except Exception as e:
      # raise e
      print("parse error at %d [%f, %f]"%(j,exam_day, exam_time))
      errors.append(('PE', id_raw, name_f, str(e)))
      continue
    try:
      mycursor.execute("REPLACE INTO units(id,department,name,instructor,weekday_1,time_start_1,time_end_1,weekday_2,time_start_2,time_end_2,weekday_3,time_start_3,time_end_3,exam_day,exam_time,capacity,registered_count,weight,gender,obsolete) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,0)", (id_f,dep_id,name_f,instructor_f,day_1,start_1,end_1,day_2,start_2,end_2,day_3,start_3,end_3,exam_day,exam_time,capacity,registered,weight,gender_f))
    except Exception as e:
      # raise e
      print("insert error at %d"%(j))
      errors.append(('DbE', id_raw, name_f, str(e)))
      print(instructor_f)
  for er in errors:
      redis.append("database_errors", "-- %s: %s | %s ................ %s\n"%er)

def main():
    global mydb
    try:
        mycursor = mydb.cursor()
    except mysql.connector.errors.OperationalError: # Timed out
        mydb = mysql.connector.connect(**db_config)
        mycursor = mydb.cursor()

    mycursor.execute("UPDATE units SET obsolete = 1")

    redis.set("database_errors", '')
    redis.append("database_errors", 'ق.اخذ: \n\n')
    with open(DATA_AVAIL_PATH, 'r') as f:
      fetch_file(f, mycursor)
    
    redis.append("database_errors", '\n\nغ.ق.اخذ: \n\n')
    with open(DATA_NA_PATH, 'r') as g:
      fetch_file(g, "غ.ق.اخذ ")

    try:
      mydb.commit()
      redis.set("last_db_update", now_to_str())
    except:
      print("commit error at the end")
    
    print("End of duty.", flush=True)

# main()
if __name__ == '__main__':
	app.run(port=80, host="0.0.0.0")
