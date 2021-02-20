# ExecFile.py
# usage :
# r = ExecFile()
# r.set('a','bbbb')
# r.run('test/cards.ini')
# r.cards
# 
import os,sys

class DictConfig(dict):
	def __init__(self,dic=None,path=None,str=None,namespace={}):
		dict.__init__(self)
		self.namespace=namespace
		if dic is not None and type(dic) == dict:
			self.__dict__.update(dic)
			self.__subConfig()
		if path is not None:
			self.__path = path
			self.__load(path)
		if str is not None:
			self.__confstr = str
			try:
				exec(str,self.namespace,self.__dict__)
				self.__subConfig()
			except:
				pass
	def keys(self):
		return self.__dict__.keys()
	
	def __getitem__(self,n):
		return self.__dict__[n]
		
	def __getattr__(self,name):
		if self.__dict__.has_key(name):
			return self.__dict__[name]
		raise AttributeError(name)
	
	def __subConfig(self):
		for n in self.__dict__.keys():
			if type(self.__dict__[n]) == dict:
				self.__dict__[n] = DictConfig(dic=self.__dict__[n])
			elif type(self.__dict__[n]) == type([]):
				a = []
				for i in self.__dict__[n]:
					if type(i) == dict:
						a.append(DictConfig(dic=i))
					else:
						a.append(i)
				self.__dict__[n] = a
			elif type(self.__dict__[n]) == type(()):
				a = []
				for i in self.__dict__[n]:
					if type(i) == dict:
						a.append(DictConfig(dic=i))
					else:
						a.append(i)
				self.__dict__[n] = tuple(a)

	def __load(self,path):
		d = {}
		c = {}
		f = open(path,'r')
		buf = f.read()
		f.close()
		try:
			exec(buf,self.namespace,namespace)
			#print d
			#print "c=",c
			self.__dict__.update(c)
			#print self.__dict__
			self.__subConfig()
			return True
		except Exception as e:
			print(self.__path,e)
			return False
			
class ExecFile(object) :
	def __init__(self,obj=None,path=None,namespace={}):
		self.namespace = namespace
		if obj == None:
			obj = self
		self.__object = obj
		#self.namespace.update(self.__object.__dict__)
		self.__file = path
		
	def set(self,name,v) :
		setattr(self.__object,name,v)

	def get(self,name,default=None) :
		return getattr(self.__object,name,default)
	
	def run(self,path=None) :
		if path!=None:
			self.__file = path
		if self.__file is None:
			raise Exception('exec file is none')
		f = open(self.__file,'r')
		buf = f.read()
		f.close()
		try :
			exec(buf,globals(),self.__object.__dict__)
		except Exception as e:
			print("ExecFile()",e)
			return (False,e)
		return (True,'')
						

