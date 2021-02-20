import poplib,pdb,email,re,time
from email import header
import datetime
import os

POP_ADDR = r'pop.126.com'
USER = ''
PASS = ''
CONFIG = ''

def getYear(date):
	rslt = re.search(r'\b2\d{3}\b', date)
	return int(rslt.group())

def getMonth(date):
	monthMap = {'Jan':1,'Feb':2,'Mar':3,'Apr':4,'May':5,'Jun':6,
				'Jul':7,'Aug':8,'Sep':9,'Oct':10,'Nov':11,'Dec':12,}

	rslt = re.findall(r'\b\w{3}\b', date)
	for i in range(len(rslt)):
		month = monthMap.get(rslt[i])
		if None != month:
			break

	return month

def getDay(date):
	rslt = re.search(r'\b\d{1,2}\b', date)
	return int(rslt.group())

def getTime(date):
	rslt = re.search(r'\b\d{2}:\d{2}:\d{2}\b', date)
	timeList = rslt.group().split(':')

	for i in range(len(timeList)):
		timeList[i] = int(timeList[i])

	return timeList

def transformDate(date):
	rslt = getYear(date)
	rslt = rslt * 100
	rslt = rslt + getMonth(date)
	rslt = rslt * 100
	rslt = rslt + getDay(date)
	   

	timeList = getTime(date)
	for i in range(len(timeList)):
		rslt = rslt * 100
		rslt = rslt + timeList[i]

	return rslt

def getRecentReadMailTime():
	fp = open(CONFIG, 'r')
	rrTime = fp.read()
	fp.close()
	return rrTime

def setRecentReadMailTime():
	fp = open(CONFIG, 'w')
	fp.write(time.ctime())
	fp.close()
	return

def getTimeEarly(period):
	def years(n):
		return datetime.timedelta(years=n)
	def months(n):
		return datetime.timedelta(years=n)
	def days(n):
		return datetime.timedelta(days=n)
	def hours(n):
		return datetime.timedelta(hours=n)
	def minutes(n):
		return datetime.timedelta(minutes=n)
	def seconds(n):
		return datetime.timedelta(seconds=n)
	
	funcs={
		'y':years,
		'm':months,
		'd':days,
		'H':hours,
		'M':minutes,
		'S':seconds,
	}
	pattern='(\d*)([ymdHMS])'
	r=re.compile(pattern)
	s = r.findall(period)
	t = datetime.datetime.now()
	for v,ty in s:
		td = funcs[ty](int(v))
		t = t - td
	return time.ctime(t.timestamp())
	

def parseMailContent(msg):
	if msg.is_multipart():
		for part in msg.get_payload():
			parseMailContent(part)
	else:
		bMsgStr = msg.get_payload(decode=True)
		charset = msg.get_param('charset')
		msgStr = 'Decode Failed'
		try:
			if None == charset:
				msgStr = bMsgStr.decode()
			else:
				msgStr = bMsgStr.decode(charset)
		except:
			pass
		
		print(msgStr)

def recvEmail(POP_ADDR,USER,PASS,PERIOD,callback):
	server = poplib.POP3(POP_ADDR)
	server.user(USER)
	server.pass_(PASS)

	mailCount,size = server.stat()
	mailNoList = list(range(mailCount))
	mailNoList.reverse()
	FROMTIME = getTimeEarly(PERIOD)
	hisTime = transformDate(FROMTIME)
	#pdb.set_trace()
	for i in mailNoList:
		message = server.retr(i+1)[1]
		mail = email.message_from_bytes(b'\n'.join(message))

		if transformDate(mail.get('Date')) > hisTime:
			if not callback(mail):
				break
			#parseMailContent(mail)
		else:
			break
