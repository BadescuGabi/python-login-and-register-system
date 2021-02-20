from kivy.app import App
from appPublic.jsonConfig import getConfig
from .kivysize import KivySizes

def StrConvert(s):
	if not s.startswith('py::'):
		return s
	s = s[4:]
	try:
		ns = {}
		exec('_n_=' + s,globals(),ns)
		return ns['_n_']
	except Exception as e:
		print('----e=',e,'------------s=',s)
		return s

def ArrayConvert(a):
	s = []
	for i in a:
		s.append(JDConvert(i))
	return s

def DictConvert(dic):
	d = {}
	for k,v in dic.items():
		if k == 'widgettype':
			d[k] = v
		else:
			d[k] = JDConvert(v)
	return d

def JDConvert(dic):
	nd = {}
	if type(dic) == type(''):
		return StrConvert(dic)
	if type(dic) == type([]):
		return ArrayConvert(dic)
	if type(dic) == type({}):
		return DictConvert(dic)
	return dic
				
def getWidgetById(w,id):
	if id[0] == '/':
		app = App.get_running_ap()
		if not hasattr('ids'):
			return None
		return app.ids.get(id[1:])
	if id in ['self', '.' ]:
		return w
	if not hasattr(w,'ids'):
		return None
	return w.ids.get(id)
		
def CSize(x,y=None,name=None):
    ks = KivySizes()
    return ks.CSize(x,y=y,name=name)

def screenSize():
    ks = KivySizes()
    return ks.getScreenSize()

def screenPhysicalSize():
    ks = KivySizes()
    return ks.getScreenPhysicalSize()

def absurl(url,parent):
	config = getConfig()
	if url.startswith('/'):
		return config.uihome + url
	if url.startswith(config.uihome):
		return url
	if parent == '':
		raise Exception('related url need a parent url')

	if parent.startswith(config.uihome):
		parent = parent[len(config.uihome):]
	paths = parent.split('/')
	paths.pop()
	for i in url.split('/'):
		if i in [ '.', '' ]:
			continue
		if i == '..':
			if len(paths) > 1:
				paths.pop()
			continue
		paths.append(i)
	return config.uihome + '/'.join(paths)

