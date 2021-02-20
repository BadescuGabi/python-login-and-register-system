import os
from datetime import datetime
from PublicData import public_data
from folderUtils import mkdir

myLogPath  = '.'

AllCatelogs=['SYSError',
	'SYSWarn',
	'APPError',
	'APPWarn',
	'APPInfo',
	'DEBUG1',
	'DEBUG2',
	'DEBUG3',
	'DEBUG4',
	'DEBUG5',
]

class MyLog :
	def __init__(self,path) :
		self.setLogPath(path)

	def setLogPath(self,path='.') :
		self.myLogPath = path
	logp=os.path.join(path,'log')
	mkdir(logp)

	def __call__(self,msg='') :
		p = os.path.join(self.myLogPath,'log','my.log')
		f = open(p,'a')
		d = datetime.now()
		f.write('%04d-%02d-%02d %02d:%02d:%02d %s\n' % ( d.year,d.month,d.day,d.hour,d.minute,d.second,msg))
		f.close()

class LogMan :
	def __init__(self) :
		self.logers = {}
		self.catelogs = AllCatelogs
	
	def addCatelog(self,catelog) :
		if catelog not in self.catelogs :
			self.catelogs.append(catelog)
		
	def addLoger(self,name,func,catelog) :
		if type(catelog)!=type([]) :
			catelog = [catelog]
		catelog = [ i for i in catelog if i in self.catelogs ]
		log = {
			'name':name,
			'func':func,
			'catelog':catelog,
			}
		self.logers[name] = log
	
	def delLoger(self,name) :
		if name in self.logers.keys() :
			del self.logers[name]
			
	def setCatelog(self,name,catelog) :
		if type(catelog)!=type([]) :
			catelog = [catelog]
		catelog = [ i for i in catelog if i in self.catelogs ]
		if name in self.logers.keys() :
			log = self.logers[name]
			log['catelog'] = catelog
			self.logers[name] = log
	
	def __call__(self,msg='',catelog='APPInfo') :
		for name,loger in self.logers.items() :
			c = loger['catelog']
			if type(c)!=type([]) :
				c = [c]
			if catelog in c :
				f = loger['func']
				f(msg)
				
def mylog(s,catelog='APPInfo') :
	logman = public_data.get('mylog',None)
	if logman==None :
		path = public_data.get('ProgramPath',None)
		if path==None :
			raise Exception('ProgramPath Not found in "public_data"')
		log = MyLog(path)
		logman = LogMan()
		logman.addLoger('mylog',log,AllCatelogs)
		public_data.set('mylog',logman)
	return logman(s,catelog)

