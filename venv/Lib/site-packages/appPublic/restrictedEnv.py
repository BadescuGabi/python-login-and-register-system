import appPublic.timeUtils as tu 
import datetime as dt

class RestrictedEnv:
	def __init__(self):
		self.reg('today',self.today)
		self.reg('date',self.date)
		self.reg('datetime',self.datetime)
		self.reg('now',dt.datetime.now)
		
	def reg(self,k,v):
		self.__dict__[k] = v
		
	def run(self,dstr):
		dstr = '__tempkey__ = %s' % dstr
		exec(dstr,globals(),self.__dict__)
		return self.__tempkey__
		
	def today(self):
		now = dt.datetime.now()
		return tu.ymdDate(now.year,now.month,now.day)
		
	def date(self,dstr):
		return tu.str2Date(dstr)
	
	def datetime(self,dstr):
		return tu.str2Datetime(dstr)

if __name__ == '__main__':
	ns = RestrictedEnv()
	a = ns.run('today()')
	b = ns.run("date('2011-10-31')")
	c = ns.run('datetime("2012-03-12 10:22:22")')
	d = ns.run('now()')
