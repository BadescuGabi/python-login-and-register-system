import os,sys
import time
import datetime

leapMonthDays = [0,31,29,31,30,31,30,31,31,30,31,30,31]
unleapMonthDays = [0,31,28,31,30,31,30,31,31,30,31,30,31]

def curDatetime():
	return datetime.datetime.now()

def curDateString():
	d = curDatetime()
	return '%04d-%02d-%02d' %(d.year,d.month,d.day)
	
def timestampstr():
	d = curDatetime()
	return '%04d-%02d-%02d %02d:%02d:%02d.%03d' % (d.year,
			d.month,
			d.day,
			d.hour,
			d.minute,
			d.second,
			d.microsecond/1000)
	
def isMonthLastDay(d):
    dd = datetime.timedelta(1)
    d1 = d + dd
    if d1.month != d.month:
        return True
    return False

def isLearYear(year):
    if year % 4 == 0 and year % 100 == 0 and not (year % 400 == 0):
	    return True
    return False
	    
def timestamp(dt):
    return int(time.mktime((dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second,dt.microsecond,0,0)))

def timeStampSecond(dt):
    return int(time.mktime((dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second,0,0,0)))

def addSeconds(dt,s):
	ndt = dt + datetime.timedelta(0,s)
	return ndt
	
def monthMaxDay(y,m):
    dt = ymdDate(y,m,1)
    if isLeapYear(dt):
        return leapMonthDays[m]
    return unleapMonthDays[m]

def date2str(dt=None):
	if dt is None:
		dt = curDatetime()
	return '%04d-%02d-%02d' % (dt.year,dt.month,dt.day)

def time2str(dt):
	return '%02d:%02d:%02d' % (dt.hour,dt,minute,dt.second)
	
def str2Date(dstr):
	try:
		haha = dstr.split(' ')
		y,m,d = haha[0].split('-')
		H = M = S = 0
		if len(haha) > 1:
			H,M,S = haha[1].split(':')
		return ymdDate(int(y),int(m),int(d),int(H),int(M),int(S))
	except Exception as e:
		print(e)
		return None
		
def ymdDate(y,m,d,H=0,M=0,S=0):
    return datetime.datetime(y,m,d,H,M,S)
    
def str2Datetime(dstr):
	d,t = dstr.split(' ')
	y,m,d = d.split('-')
	H,M,S = t.split(':')
	return datetime.datetime(int(y),int(m),int(d),int(H),int(M),int(S))
	
def addMonths(dt,months):
    y = dt.year()
    m = dt.month()
    d = dt.day()
    mm = m % 12
    md = m / 12
    if md != 0:
        y += md
    m = mm
    maxd = monthMaxDay(y,m)
    if d > maxd:
        d = maxd
    return ymdDate(y,m,d)

def addYears(dt,years):
    y = dt.year() + years
    m = dt.month()
    d = dt.day()
    maxd = monthMaxDay(y,m)
    if d > maxd:
        d = maxd
    return ymdDate(y,m,d)

def dateAdd(dt,days=0,months=0,years=0):
    if days != 0:
        dd = datetime.timedelta(days)
        dt = dt + dd    
    if months != 0:
        dt = addMonths(dt,months)
    if years != 0:
        dt = addYears(dt,years)
    return dt

def firstSunday(dt):
    f = dt.weekday()
    if f<6:
        return dt + datetime.timedelta(7 - f)
    return dt

DTFORMAT = '%Y%m%d %H%M%S'
def getCurrentTimeStamp() :
	t = time.localtime()
	return TimeStamp(t)
	
def TimeStamp(t) :
	return time.strftime(DTFORMAT,t)

def StepedTimestamp(baseTs,ts,step) :
	if step<2 :
		return ts
	offs = int(timestampSub(ts,baseTs))
	step = int(step)
	r,m = divmod(offs,step)
	if m < step/2 :
		return timestampAdd(baseTs,step * r)
	else :
		return timestampAdd(baseTs,step * (r+1))
		
def timestampAdd(ts1,ts2) :
	t1 = time.strptime(ts1,DTFORMAT)
	tf = time.mktime(t1)
	if type(ts2)=='' :
		t2 = time.strptime(ts2,DTFORMAT)
		ts2 = time.mktime(t2)
	tf += ts2
	t = time.localtime(tf)
	return TimeStamp(t)

def timestampSub(ts1,ts2) :
	t1 = time.strptime(ts1,DTFORMAT)
	t2 = time.strptime(ts2,DTFORMAT)
	ret = time.mktime(t1) - time.mktime(t2)
	return int(ret)

def timestamp2dt(t):
	return datetime.datetime.fromtimestamp(t)
