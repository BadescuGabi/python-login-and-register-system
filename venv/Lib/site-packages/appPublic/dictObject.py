def multiDict2Dict(md):
	ns = {}
	for k,v in md.items():
		ov = ns.get(k,None)
		if ov is None:
			ns[k] = v
		elif type(ov) == type([]):
			ov.append(v)
			ns[k] = ov
		else:
			ns[k] = [ov,v]
	return ns

class DictObject(dict):
	def __init__(self,**args):
		try:
			dict.__init__(self,**args)
			for k,v in self.items():
				self.__setattr__(k,self._DOitem(v))
		except Exception as e:
			print("DictObject.__init__()",e,args)
			raise e
	@classmethod
	def isMe(self,name):
		return name == 'DictObject'
		
	def __getattr__(self,name):
		if name in self:
			return self[name]
		return None
	
	def __setattr__(self,name,v):
		self[name] = v
	
	def _DOArray(self,a):
		b = [ self._DOitem(i) for i in a ]
		return b
	
	def _DOitem(self, i):
		if type(i) is type({}):
			return DictObject(**i)
		if type(i) is type([]):
			return self._DOArray(i)
		return i

def dictObjectFactory(_klassName__,**kwargs):
	def findSubclass(_klassName__,klass):
		for k in klass.__subclasses__():
			if k.isMe(_klassName__):
				return k
			k1 = findSubclass(_klassName__,k)
			if k1 is not None:
				return k1
		return None
	try:
		if _klassName__=='DictObject':
			return DictObject(**kwargs)
		k = findSubclass(_klassName__,DictObject)
		if k is None:
			return DictObject(**kwargs)
		return k(**kwargs)
	except Exception as e:
		print("dictObjectFactory()",e,_klassName__)
		raise e
