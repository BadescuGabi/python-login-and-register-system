import time
import datetime

BEGIN=0
END=1

def datetimeStr(t):
	dt = time.localtime(t)
	return time.strftime('%Y-%m-%d %H:%M:%S',dt)
	
class TimeCost:
	def __init__(self):
		self.timerecord = {}
	
	def begin(self,name):
		self.timerecord[name] = {'begin':time.time()}
	
	def end(self,name):
		if name not in self.timerecord.keys():
			self.timerecord[name] = {'begin':time.time()}
		d = self.timerecord[name]
		d['end'] = time.time()
	
	def getTimeCost(self,name):
		return self.timerecord[name]['end'] - self.timerecord[name]['begin']
	
	def getTimeBegin(self,name):
		return self.timerecord[name]['begin']
	
	def getTimeEnd(self,name):
		return self.timerecord[name]['end']
		
	def show(self):
		for name in self.timerecord.keys():
			d = self.timerecord[name]
			cost = d['end'] - d['begin']
			print(name,'begin:',datetimeStr(d['begin']),'end:',datetimeStr(d['end']),'cost:%f seconds' % cost)

