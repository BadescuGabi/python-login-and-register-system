import os,re,sys
import codecs
from appPublic.folderUtils import _mkdir
from appPublic.Singleton import SingletonDecorator
from appPublic.folderUtils import ProgramPath
import threading
import time

import locale

comment_re = re.compile(r'\s*#.*')
msg_re = re.compile(r'\s*([^:]*)\s*:\s*([^\s].*)')

def dictModify(d, md) :
	for i in md.keys() :
		if md[i]!=None :
			d[i] = md[i]
	return d

convert_pairs = 	{':':'\\x3A',
	'\n':'\\x0A',
	'\r':'\\x0D',
}

def charEncode(s) :
	r = ''
	v = s.split('\\')
	s = '\\\\'.join(v)
	for i in convert_pairs.keys() :
		v = s.split(i)
		s = convert_pairs[i].join(v)
		# print 'i=',i,'iv=',convert_pairs[i],'s=',s
	return s
 
def charDecode(s) :
	for i in convert_pairs.items() :
		v = s.split(i[1])
		s = i[0].join(v)
	v = s.split('\\\\')
	s = '\\'.join(v)
	return s
     
def getTextDictFromLines(lines) :
	d = {}
	for l in lines :
		l = ''.join(l.split('\r'))
		if comment_re.match(l) :
			continue
		m = msg_re.match(l)
		if m :
			grp = m.groups()
			d[charDecode(grp[0])] = charDecode(grp[1])
	return d

def getFirstLang(lang) :
	s = lang.split(',')
	return s[0]

@SingletonDecorator
class MiniI18N:
	"""
	"""
	def __init__(self,path,lang=None,coding='utf8') :
		self.path = path
		l = locale.getdefaultlocale()
		self.curLang = l[0]
		self.coding = coding
		self.id = 'i18n'
		self.langTextDict = {}
		self.messages = {}
		self.setupMiniI18N()
		self.missed_pt = None
		self.translated_pt = None
		self.header_pt = None
		self.footer_pt = None
		self.show_pt=None
		self.clientLangs = {}
		self.languageMapping = {}
		self.timeout = 600
	
	def __call__(self,msg,lang=None) :
		"""
		"""
		if type(msg) == type(b''):
			msg = msg.decode(self.coding)
		return self.getLangText(msg,lang)
		
	def setLangMapping(self,lang,path):
		self.languageMapping[lang] = path
		
	def getLangMapping(self,lang):
		return self.languageMapping.get(lang,lang)

	def setTimeout(self,timeout=600):
		self.timeout = timeout
	
	def delClientLangs(self):
		t = threading.currentThread()
		tim = time.time() - self.timeout
		[ self.clientLangs.pop(k,None) for k in self.clientLangs.keys() if self.clientLangs[k]['timestamp'] < tim ]
				
	def getLangDict(self,lang):
		return self.langTextDict.get('lang',{})
		
	def getLangText(self,msg,lang=None) :
		"""
		"""
		if lang==None :
			lang = self.getCurrentLang()
		if lang not in self.langTextDict.keys() :
			self.langTextDict[lang] = {}
		if msg not in self.messages.keys() :
			self.messages[msg] = ''
		dict = self.langTextDict[lang]
		if msg not in dict.keys() :
			return msg
		return dict[msg]

	def getMissTextList(self,lang=None) :
		"""
		"""
		if lang==None :
			lang = self.getCurrentLang()
		if lang not in self.langTextDict.keys() :
			self.langTextDict[lang] = {}
		texts = []

		keys = list(self.messages.keys())
		keys.sort()
		for i in keys :
			if i not in self.langTextDict[lang].keys() :
				texts.append(charEncode(i) + ':' )

		s =  '\n'.join(texts)
		return s

	def getTranslatedTextList(self,lang=None) :
		"""
		"""
		if lang==None :
			lang = self.getCurrentLang()
		if lang not in self.langTextDict.keys() :
			self.langTextDict[lang] = {}
		texts = []
		keys = list(self.langTextDict[lang].keys())
		keys.sort()
		for i in keys :
			texts.append(charEncode(i) + ':' + charEncode(self.langTextDict[lang][i]))

		s =  '\n'.join(texts)
		return s

	def I18nTranslating(self,newtexts,lang=None,submit='') :
		"""
		"""
		if lang==None :
			lang = self.getCurrentLang()
		if lang not in self.langTextDict.keys() :
			self.langTextDict[lang] = {}

		textDict = getTextDictFromLines(newtexts.split('\n'))
		d = {}
		if lang in self.langTextDict :
			d = self.langTextDict[lang]
		self.langTextDict[lang].update(textDict)
		for i in textDict.keys() :
			self.messages[i] = ''
		self.writeTranslateMessage()

	def writeUntranslatedMessages(self) :
		p = os.path.join(self.path,'i18n')
		langs = []
		
		for f in os.listdir(p) :
			if os.path.isdir(os.path.join(p,f)) :
				langs.append(f)
		for lang in langs:
			p1 = os.path.join(self.path,'i18n',lang)
			if not os.path.exists(p1) :
				_mkdir(p1)
			p2 = os.path.join(p1,'unmsg.txt')
			f = codecs.open(p2,'w',self.coding)
			f.write(self.getMissTextList(lang))
			f.close()


	def writeTranslateMessage(self) :
		p1 = os.path.join(self.path,'i18n',self.getCurrentLang())
		if not os.path.exists(p1) :
			_mkdir(p1)
		p2 = os.path.join(p1,'msg.txt')
		f = codecs.open(p2,'w',self.ccoding)
		f.write(self.getTranslatedTextList())
		f.close()

	def setupMiniI18N(self) :
		"""
		"""

		p = os.path.join(self.path,'i18n')
		langs = []
		
		for f in os.listdir(p) :
			if os.path.isdir(os.path.join(p,f)) :
				langs.append(f)
		for dir in langs :
			p1 = os.path.join(p,dir,'msg.txt')
			if os.path.exists(p1) :
				f = codecs.open(p1,'r',self.coding)
				textDict = getTextDictFromLines(f.readlines())
				f.close()
				d = {}
				if dir in self.langTextDict :
					d = self.langTextDict[dir]
				self.langTextDict[dir] = textDict
				for i in textDict.keys() :
					self.messages[i] = ''
				
		self._p_changed = 1
		
	def setCurrentLang(self,lang):
		lang = self.getLangMapping(lang)
		t = time.time()
		threadid = threading.currentThread()
		a = dict(timestamp=t,lang=lang)
		self.clientLangs[threadid] = a

	def getCurrentLang(self) :
		"""
		"""
		threadid = threading.currentThread()
		return self.clientLangs[threadid]['lang']

def getI18N(coding='utf8'):
	path = ProgramPath()
	i18n = MiniI18N(path,coding)
	return i18n

