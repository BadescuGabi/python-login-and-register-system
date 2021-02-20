import sys
import threading
from threading import Thread
from queue import Queue, Empty

class Worker(Thread):
	def __init__(self, rqueue, timeout=1):
		Thread.__init__(self)
		self.timeout = timeout
		self.setDaemon(False)
		self.r_queue = rqueue
		self.start()

	def run(self):
		emptyQueue = False
		while True:
			try:
				callable,args,kw = self.r_queue.get(timeout=self.timeout)
				if callable is None:
					break
				callable(*args,**kw)

			except Empty:
				time.sleep(1)

	def resulthandler(self,rez):
		pass

class ThreadWorkers:
	def __init__(self,num_workers=20):
		self.workQueue = Queue()
		self.worker_cnt = num_workers
		self.workers = []
		self.__createThreadPool(num_workers)

	def __createThreadPool(self,num):
		for i in range(num):
			thread = Worker(self.workQueue)
			self.workers.append(thread)
	
	def wait_for_complete(self):
		for i in range(self.worker_cnt):
			self.add_job(None,None,None)

		while len(self.workers):
			thread = self.workers.pop()
			if thread.isAlive():
				thread.join()
	
	def add_job(self,callable,args=[],kw={}):
		self.workQueue.put([callable,args,kw])
if __name__ == '__main__':
	import requests
	def get(url):
		x = requests.get(url)
		print(x.status_code)

	tw = ThreadWorkers()
	for i in range(10000):
		tw.add_job(get,['http://www.baidu.com'])
	tw.wait_for_complete()
	print('finished')
