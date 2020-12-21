# Gregorian & Jalali ( Hijri_Shamsi , Solar ) Date Converter Functions
# Author: JDF.SCR.IR =>> Download Full Version : http://jdf.scr.ir/jdf
# License: GNU/LGPL _ Open Source & Free _ Version: 2.72 : [2017=1396]
# --------------------------------------------------------------------
# 1461 = 365*4 + 4/4   &  146097 = 365*400 + 400/4 - 400/100 + 400/400
# 12053 = 365*33 + 32/4      &       36524 = 365*100 + 100/4 - 100/100
from datetime import datetime, timezone, timedelta

def gregorian_to_jalali(gy,gm,gd):
 g_d_m=[0,31,59,90,120,151,181,212,243,273,304,334]
 if(gy>1600):
  jy=979
  gy-=1600
 else:
  jy=0
  gy-=621
 if(gm>2):
  gy2=gy+1
 else:
  gy2=gy
 days=(365*gy) +(int((gy2+3)/4)) -(int((gy2+99)/100)) +(int((gy2+399)/400)) -80 +gd +g_d_m[gm-1]
 jy+=33*(int(days/12053))
 days%=12053
 jy+=4*(int(days/1461))
 days%=1461
 if(days > 365):
  jy+=int((days-1)/365)
  days=(days-1)%365
 if(days < 186):
  jm=1+int(days/31)
  jd=1+(days%31)
 else:
  jm=7+int((days-186)/30)
  jd=1+((days-186)%30)
 return jy,jm,jd

def now_to_str():
  tz_ = timezone( timedelta( minutes=210 ) )
  now = datetime.now(tz=tz_)
  y,m,d = gregorian_to_jalali(now.year, now.month, now.day)
  hh = str(now.hour).zfill(2)
  mm = str(now.minute).zfill(2)
  return "%d/%d/%d - %s:%s"%(y,m,d,hh,mm)
