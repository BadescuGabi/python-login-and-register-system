import os,sys
import json
from appPublic.dictObject import DictObject
from appPublic.Singleton import SingletonDecorator
from appPublic.folderUtils import ProgramPath
from appPublic.argsConvert import ArgsConvert

def key2ansi(dict):
	#print dict
	return dict
	a = {}
	for k,v in dict.items():
		k = k.encode('utf-8')
		#if type(v) == type(u" "):
		#	v = v.encode('utf-8')
		a[k] = v
	
	return a
	
class JsonObject(DictObject):
	"""
	JsonObject class load json from a json file
	"""
	def __init__(self,jsonholder,keytype='ansi',NS=None):
		self.__jsonholder__ = jsonholder
		self.NS = NS
		jhtype = type(jsonholder)
		if jhtype == type("") or jhtype == type(u''):
			f = open(jsonholder,'r')
		else:
			f = jsonholder
		try:
				a = json.load(f)
		except Exception as e:
			print("exception:",self.__jsonholder__,e)
			raise e
		finally:
			if type(jsonholder) == type(""):
				f.close()
		
		if self.NS is not None:
			ac = ArgsConvert('$[',']$')
			a = ac.convert(a,self.NS)
		DictObject.__init__(self,**a)
	
@SingletonDecorator
class JsonConfig(JsonObject):
	pass
def getConfig(path=None,NS=None):
	if path==None:
		path = ProgramPath()
	cfname = os.path.abspath(os.path.join(path,"conf","config.json"))
	# print __name__,cfname
	a = JsonConfig(cfname,NS=NS)
	return a
	
if __name__ == '__main__':
	conf = JsonConfig(sys.argv[1])
	#print conf.db,conf.sql
	#conf1 = JsonConfig(sys.argv[1],keytype='unicode')
	conf1 = JsonConfig(sys.argv[1],keytype='ansi')

	print("conf=",dir(conf))
	print("conf1=",dir(conf1)	)	
