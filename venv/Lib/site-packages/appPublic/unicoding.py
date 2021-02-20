#unidict.py
import locale

def unicoding(d,coding='utf8'):
	if type(d) == type(''):
		return d
	if type(d) == type(b''):
		try:
			if coding is not Noene:
				return d.decode(coding)
			else:
				return d.decode(locale.getdefaultlocale()[1])
		except:
			try:
				return d.decode(locale.getdefaultlocale()[1])
			except:
				try:
					return d.decode('utf8')
				except:
					return d
	return d

def uObject(obj,coding='utf8'):
	otype = type(obj)
	if otype == type(u''):
		return obj
	if otype == type({}):
		return uDict(obj,coding)
	if otype == type([]):
		return [uObject(i,coding) for i in obj ]
	if hasattr(obj,'decode'):
		return obj.decode(coding)
	return obj
	
def uDict(dict,coding='utf8'):
	d = {}
	for k,v in dict.items():
		d[uObject(k)] = uObject(v)
	return d
