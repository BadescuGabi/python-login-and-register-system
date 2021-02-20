import ujson as json
import codecs

def loadf(fn,coding='utf8'):
	f = codecs.open(fn,'r',coding)
	d = json.load(f)
	f.close()
	return d
	
def dumpf(obj,fn,coding='utf8'):
	f = codecs.open(fn,'w',coding)
	json.dump(obj,f)
	f.close()

load = json.load
dump = json.dump
loads = json.loads
dumps = json.dumps