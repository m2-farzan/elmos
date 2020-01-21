#!/usr/bin/python3
import string
import mysql.connector
mydb = mysql.connector.connect(
  host="localhost",
  user="elmos_vahed",
  passwd="CHANGE_ME",
  database="elmos_units"
)

def filter_farsi(txt):
  return txt.replace( 'ي', 'ی').replace('ك', 'ک').replace('<br>','،')
  
def extract_weekdays(txt):
  dd = [0,0,0,0,0,0]
  d = txt.count('شنبه')
  dd[1] = txt.count('يك شنبه')
  dd[2] = txt.count('دو شنبه')
  dd[3] = txt.count('سه شنبه')
  dd[4] = txt.count('چهار شنبه')
  dd[5] = txt.count('پنج شنبه')
  dd[0] = d - (dd[1] + dd[2] + dd[3] + dd[4] + dd[5])
  weekdays = []
  for i in range(0, 6):
    if dd[i] == 2:
      return [i,i]
    elif dd[i] == 1:
      weekdays.append(i)
  return weekdays
  
def extract_week_times(txt, no):
  if no == 1:
    cursor = txt.find('شنبه')
  else:
    cursor = txt.rfind('شنبه')
  cursor = min(txt.find('0', cursor), txt.find('1', cursor))
  time_text = txt[cursor:(cursor+11)]
  start = int(time_text[0:2]) + int(time_text[3:5])/60.0
  end = int(time_text[6:8]) + int(time_text[9:11])/60.0
  return (start, end)
  
def get_exam_datetime(txt):
  if len(txt) < 5:
    return 0,0
  first_slash = txt.find('/')
  mon = int( txt[(first_slash+1):(first_slash+3)] )
  day = int( txt[(first_slash+4):(first_slash+6)] )
  date = (mon-1)*31 - max(mon-7,0)*1 + day
  first_colon = txt.find('-') - 3
  time = int(txt[(first_colon-2):first_colon]) + int(txt[(first_colon+1):(first_colon+3)]) / 60.0
  return date, time
  

mycursor = mydb.cursor()
mycursor.execute("DELETE FROM units")
mydb.commit()

duty = 1500

def fetch_data(f):
  return (f.readline())[4:-6]

def fetch_file(f, prefix = ""):
  # drop first 31 lines
  for i in range(0, 31):
    f.readline()
  errors = []
  for j in range(0,duty):
    if (j%100 == 0):
      print("progress: %d/%d"%(j,duty))
    try:
      term = fetch_data(f)
      dep_id = fetch_data(f) # !
      dep = fetch_data(f)
      group_id = fetch_data(f)
      group = fetch_data(f)
      id_raw = fetch_data(f) # !
      name = fetch_data(f) # !
      weight = (fetch_data(f))[16:-7] # !
      amali = fetch_data(f)
      capacity = fetch_data(f) #!
      registered = fetch_data(f) #!
      waiting_list = fetch_data(f)
      gender = fetch_data(f) #!
      instructor = fetch_data(f) #!
      schedule_time = fetch_data(f) #!
      exam_time_x = fetch_data(f) #!
      limit = fetch_data(f) #~
      for i in range(0,6):
        f.readline()
      desc = fetch_data(f) #~
      f.readline()
      f.readline()
      
      id_f = id_raw[:7] + id_raw[8:10]
      name_f = prefix + filter_farsi(name)
      gender_f = 0
      if gender == 'مرد':
        gender_f = 1
      if gender == 'زن':
        gender_f = 2
      instructor_f = filter_farsi(instructor)[:-1]
      exam_day, exam_time = get_exam_datetime(exam_time_x)
      
      
      if (dep_id == '90' and ('ورزش' in name)):
        instructor_f = instructor_f + " - " + desc
      
      if (dep_id == '28' and ('تخصصی' in name_f)):
        instructor_f = instructor_f + " - " + limit[23:23+30]
      
      # az mabani bargh
      if len(id_raw) > 7 and id_raw[0:7] == '1211320':
        instructor_f = "(" + "مخصوص " + filter_farsi( limit.split('،')[1][8:] ) + ") - " + instructor_f

      days = extract_weekdays(schedule_time)
      day_1 = days[0]
      if len(days) > 1:
        day_2 = days[1]
      else:
        day_2 = -1
      start_1 = extract_week_times(schedule_time,1)[0]
      end_1 = extract_week_times(schedule_time,1)[1]
      if len(days) > 1:
        start_2 = extract_week_times(schedule_time,2)[0]
        end_2 = extract_week_times(schedule_time,2)[1]
      else:
        start_2 = -1
        end_2 = -1
    except :
      print("parse error at %d [%f, %f]"%(j,exam_day, exam_time))
      errors.append(name_f)
      continue
    #print("INSERT INTO units(id,department,name,instructor,weekday_1,time_start_1,time_end_1,weekday_2,time_start_2,time_end_2,exam_day,exam_time,capacity,registered_count,weight,gender) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"% (id_f,dep_id,name_f,instructor_f,day_1,start_1,end_1,day_2,start_2,end_2,1,8.0,30,0,2,0))
    try:
      mycursor.execute("INSERT INTO units(id,department,name,instructor,weekday_1,time_start_1,time_end_1,weekday_2,time_start_2,time_end_2,exam_day,exam_time,capacity,registered_count,weight,gender) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)", (id_f,dep_id,name_f,instructor_f,day_1,start_1,end_1,day_2,start_2,end_2,exam_day,exam_time,capacity,registered,weight,gender_f))
      mydb.commit()
    except:
      print("commit error at %d"%(j))
  print(errors)

f = open("data_avail.txt")
fetch_file(f)
g = open("data_na.txt")
fetch_file(g, "غ‌.ق.اخذ - ")
