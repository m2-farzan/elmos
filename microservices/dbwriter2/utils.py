import re

def filter_farsi(txt):
  return txt.replace( 'ي', 'ی').replace('ك', 'ک').replace('<br>','،')
  
def extract_schedule(txt):
  r = []
  weekdays = extract_weekdays(txt)
  for i in range(len(weekdays)):
    start, end = extract_week_times(txt, i)
    schedule_tuple = (weekdays[i], start, end)
    if not schedule_tuple in r: # To avoid duplicates.
      r.append(schedule_tuple)
  return r

# returns days e.g. [0, 2, 2] === shanbe, 2shanbe, 2shanbe
def extract_weekdays(txt):
  if txt == "":
    raise Exception("زمان کلاس در گلستان ذکر نشده است ⚪")
  d = txt.count('شنبه')
  if d < 1:
    raise Exception("class time not specified")
  times = re.findall(r"(شنبه)|(يك شنبه)|(دوشنبه)|(سه شنبه)|(چهارشنبه)|(پنج شنبه)", txt)
  def get_day(tup):
    for i in range(0, len(tup)):
      if tup[i] != '':
        return i
  days = [get_day(t) for t in times]
  return days
  
def extract_week_times(txt, no):
  times = re.findall(r"[0-9]{2}:[0-9]{2}-[0-9]{2}:[0-9]{2}", txt)
  time_text = times[no]
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

def simplify_dep_name(txt):
  txt = txt.replace('مهندسی شیمی', 'م. شیمی')
  txt = txt.replace('مهندسی ', '')
  return txt

def limit_warning(id_raw, limit):
  if limit == '':
    return ''
  r = []
  deps = {
    '12': 'برق',
    '13': 'راه آهن',
    '14': 'ریاضی',
    '15': 'صنایع',
    '16': 'فیزیک',
    '17': 'مواد',
    '18': 'معماری',
    '19': 'مکانیک',
    '20': 'مهندسی شیمی',
    '21': 'عمران',
    '22': 'کامپیوتر',
    '26': 'تربیت بدنی',
    '27': 'معارف',
    '28': 'زبان',
    '29': 'شیمی',
    '30': 'خودرو',
    '90': 'عمومی'
  }
  # Marks if:
  # (a) Course is from dep x but is only available for y
  # (b) Course is from dep x and is available for x (only public courses)
  # (c) Course is only unavailable for dep y
  # (d) Course is only available for 99 students
  publics = [
    '1211320', # Az mabani bargh
    '1411155', # Numerical Analysis
    '1611202', # Physics 1
    '1611117', # Physics 2
    '1611202', # Physics 1 [new]
    '1611150', # Physics 2 [new]
    '2211277', # Mabani Comp
    '1611123', # Az phys 1
    '1611124', # Az phys 2
    '1411087', # Mo'adelat Diff
    '1411090', # Math 1
    '1411092', # Math 2
    '1411089', # Rizmo
  ]
  limit = filter_farsi(limit)
  limit = limit.replace('غیرمجاز', '#نجاز')
  limit = limit.replace('مجاز', '#مجاز')
  limit = limit.replace('راه  آهن', 'راه آهن')
  if ('مجاز' in limit) or ('نجاز' in limit):
    first_flag = True
    criteria = limit.split('#')
    cur_dep = deps[id_raw[0:2]]
    for criterion in criteria:
      if 'مجاز' in criterion:
        if ((id_raw[0:7] in publics) and (cur_dep in criterion)) or not (cur_dep in criterion):
          for _, dep in deps.items():
            if dep in criterion:
              if first_flag:
                r.append( 'مخصوص ' + simplify_dep_name(dep) )
                first_flag = False
              else:
                r.append(simplify_dep_name(dep))
      elif 'نجاز' in criterion:
        for _, dep in deps.items():
          if dep in criterion:
            r.append( 'غ.مجاز برای  ' + simplify_dep_name(dep) )
  if 'ظرفیت' in limit and 'ترم ورود' in limit:
    r.append('ظرفیت اختصاصی ترمی')
  else:
    if '3971 تا 3971' in limit:
      r.append('مخصوص ورودی ۹۷')
    if '3981 تا 3981' in limit:
      r.append('مخصوص ورودی ۹۸')
    if '3991 تا 3991' in limit:
      r.append('مخصوص ورودی ۹۹')
    if '4001 تا 4001' in limit:
      r.append('مخصوص ورودی ۱۴۰۰')
    if '4011 تا 4011' in limit:
      r.append('مخصوص ورودی ۱۴۰۱')
    if '4012 تا 4012' in limit:
      r.append('مخصوص ورودی ۱۴۰۲')

  if id_raw == '2811027_03':
    r = [r[0]]

  return '، '.join(r)

def xml_preprocess(raw):
    x = re.sub(r'\&lt;BR\&gt;([^\"])', r'،\1', raw) # Replace a <br> followed by text with comma # TODO: comma+space
    x = re.sub(r'\&\w+;', '', x) # Remove all other url-encoded special characters like &quote; , etc.
    x = re.sub(r'dir\=.{3}', '', x) # Remove all dir=rtl | dir=ltr 's (quotes are already removed from previous line)
    x = re.sub(r'\/?(?:NO)?BR', ' ', x) # Remove any remaining <br>, <nobr>, </nobr>
    # x = re.sub('ي', 'ی', x)
    # x = re.sub('ك', 'ک', x)
    x = re.sub(r'\"\s*(\d+)\s*\"', r'"\1"', x) # Remove any padding whitespace from numeric attributes e.g. "5 " -> "5"
    return x
