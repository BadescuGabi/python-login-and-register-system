import time
from kivy.event import EventDispatcher

from appPublic.dictObject import DictObject

class DataBuffer(EventDispatcher):
	def __init__(self,datagrapper,maxpages=3,pagesize=25):
		self.pages = {}
		self.dataGrapper = dtagrapper
		self.pagesize = pagesize
		self.total_page = None

	async def readPage(self,pageid):
		if pageid < 1:	
			return
		if self.total_page is not None and pageid > self.total_page:
			return

		data = self.getBufferedPage(pageid)
		if data is not None:
			return data

		data = await self.dataGrapper(page=pageid,rows=self.pagesize)
		if self.total_page is None:
			self.total_page = data.total / self.pagesize + 1

		self.bufferPage(pageid,data)
		if self.bufferOverflow():
			self.dropOldest()
		return data

	def bufferPage(self,pageid,data):
		d = DictObject(timestamp=time.time(),page=data)
		self.pages[pageid] = d

	def getBufferedPage(self,pageid):
		d = self.pages.get(pageid,None)
		if d is None:
			return None
		return d.page

	def bufferOverflow(self):
		return len(self.pages.keys())>self.maxpages

	def dropOldest(self):
		pid = -1
		t = time.time()
		for p,d in self.pages.items():
			if d.timestamp < t:
				pid = p
		del self.pages[pid]
		if self.bufferOverflow():
			self.dropOldest()
		
