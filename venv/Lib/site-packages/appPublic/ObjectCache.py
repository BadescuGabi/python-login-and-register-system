# !/usr/bin/env python
#
# ObjectsCache is a Objects cache
# the Object has to have a method "get_size" to tell 
#   the cacher counting the objects size

class ObjectCache(dict) :
	def __init__(self,maxsize=10000000,*args) :
		super(ObjectsCache,self).__init__(*args) 
		self.maxsize = maxsize
		self.size = 0
		self._shadow = {}

	def __setitem__(self,key,item) :
		try :
			size = item.get_size()
			self.size += size
		except :
			return
		if self.size >= self.maxsize :
			tmp = [(t,key) for key,(t,size) in self._shadow.iteritems() ]
			tmp.sort()
			for i in xrange(len(tmp)//2) :
				del self[tmp[i][i]]
			del tmp
		super(ObjectCache,self).__setitem__(key,item)
		self._shadow[key] = [time.time(),size]

	def __getitem__(self,key) :
		try :
			item = super(ObjectCache,self).__getitem__(key)
		except :
			raise
		else :
			self._shadow[key][0] = time.time()
			return item

	def get(self,key,default=None) :
		if self.has_key(key) :
			return self[key]
		else :
			return default

	def __delitem__(self,key) :
		try :
			super(ObjectCache,self).__delitem__(key)
		except :
			raise
		else :
			self.size -= self._shadow[key][1]
			del self._shadow[key]


