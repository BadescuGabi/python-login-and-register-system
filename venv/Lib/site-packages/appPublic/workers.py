import os
import sys
import time
import pyodbc as db
from multiprocessing import Process, Queue,Pipe,freeze_support,cpu_count
from threading import Thread
import logging

from appPublic.folderUtils import ProgramPath
FINISH_JOB=0
EXIT=4
ABORT_JOB=5
COMMIT_JOB=6
DO_JOB=1
ERROR=2

OK=0
def debug(s):
	fn = os.path.join(ProgramPath(),"worker_child.log")
	f = open(fn,"a")
	f.write("%s\n" % s)
	f.close()
	pass #print s

logger = logging.getLogger(__name__)
	
class Worker(Process):
	def __init__(self,inQ,outQ):
		Process.__init__(self)
		self.inQ = inQ
		self.outQ = outQ
		self.done = False
		self.aborted = False
		self.task_no = 0
	
	def abort_task(self):
		pass
		
	def finish_task(self):
		pass
		
	def job_begin(self):
		pass
	
	def job_end(self):
		pass
		
	def abort(self):
		self.aborted = True
		
	def run(self):
		self.job_begin()
		self.job()
		if self.aborted:
			self.abort_task()
			self.outQ.put([ABORT_JOB,self.name,self.task_no,None])
			debug("process=%s,aborted at task_no=%d" % (self.name,self.task_no))
			#self.inQ.cancel_join_thread()
		else:
			self.finish_task()
			self.outQ.put([FINISH_JOB,self.name,self.task_no,None])
			debug("process=%s,end at task_no=%d" % (self.name,self.task_no))
		self.job_end()
		debug("process %s end" % self.name)
		sys.exit(0)
		
	def job(self):
		debug("process %s running" % (self.name))
		while not self.done:
			cmd,task_no,args = self.inQ.get()
			self.task_no = task_no
			debug("process=%s,cmd=%d,task_no=%d" % (self.name,cmd,self.task_no))
			if cmd==ABORT_JOB:
				logger.info("process %s aborted" % self.name)
				self.aborted = True
				self.done = True
				continue
			if cmd==FINISH_JOB:
				logger.info("process %s finished" % self.name)
				self.done = True
				continue
			if cmd!=DO_JOB:
				continue
			try:
				d = self.task(args)
				self.outQ.put([cmd,self.name,self.task_no,d])
				debug("process=%s,cmd=%d,task_no=%d,responed" % (self.name,cmd,self.task_no))
			except Exception as e:
				debug("ERROR:%s" % e)
				self.outQ.put([ERROR,self.name,self.task_no,"Error"])
				debug("process=%s,cmd=%d,task_no=%d,error" % (self.name,cmd,self.task_no))
				self.abort()

	def task(self,args):
		return None

class Workers(Thread):
	def __init__(self,worker_cnt,Wklass,argv):
		Thread.__init__(self)
		self.worker_cnt = worker_cnt
		self.aborted = False
		self.workers = []
		self.taskQ = Queue()
		self.doneQ = Queue()
		self.follows = []
		self.task_cnt = 0
		self.resp_cnt = 0
		self.task_no = 0
		self.max_task_no_resp = 0
		
		i = 0
		while i < self.worker_cnt:
			w =  Wklass(self.taskQ,self.doneQ,*argv)
			self.workers.append(w)
			w.start()
			i += 1
	
	def __del__(self):
		self.cleanTaskQ()
		self.cleanDoneQ()
		self.taskQ.close()
		self.doneQ.close()
		
	def eraseDeadProcess(self):
		d = [ p for p in self.workers if p.is_alive() ]
		self.workers = d
		self.worker_cnt = len(d)
		
	def addFollowWorkers(self,workers):
		self.follows.append(workers)
	
	def isFollowDone(self):
		for w in self.follows:
			if not w.isDone():
				#logger.info("%s, follow %s still alive" % (self.name,w.name))
				return False
		return True

	def isFinished(self):
		for w in self.workers:
			if w.is_alive():
				#logger.info("%s, process %s still alive" % (self.name,w.name))
				return False
		return True
	
	def isDone(self):
		if not self.isFollowDone():
			return False
		if not self.isFinished():
			return False
		return True
	
	def isAborted(self):
		return self.aborted
					
	def run(self):
		while not self.isFinished():
			#logger.info("thread %s, task_cnt=%d,resp_cnt = %d,aborted=%s" % (self.name,self.task_cnt,self.resp_cnt,str(self.aborted)))
			status,proName,task_no,data = self.getResult()
			if status is not None:
				self.handleResult(status,proName,data)
			for w in self.follows:
				if w.isAborted():
					self.abortTask()
			self.eraseDeadProcess()
			#time.sleep(0.01)
		logger.info("thread %s end .................." % (self.name))
			
	def handleResult(self,status,proName,data):
		#logger.info("thread=%s,status=%s,proName=%s" % (self.name,str(status),proName))
		if status == FINISH_JOB or status == ABORT_JOB:
			for p in self.workers:
				if p.name == proName and p.is_alive():
					p.join()
			#logger.info("%s,finished job,status=%d" % (self.name,status))
			return
		if status == ERROR and not self.aborted:
			#logger.info("thread %s, error" % (self.name))
			self.abortTask()
			logger.info("%s,error job,status=%d" % (self.name,status))
			return
		if status == DO_JOB:
			self.resp_cnt += 1
			for i in self.follows:
				#logger.info("task hand to %s" % (i.name))
				i.addTask(data,waitting=True)
						
	def done(self):
		while self.max_task_no_resp < self.task_no:
			self.eraseDeadProcess()
			if self.worker_cnt == 0:
				return
			time.sleep(0.01)
			
		for w in self.workers:
			self.task_no += 1
			self.taskQ.put([FINISH_JOB,self.task_no,None],False)
			
		for w in self.follows:
			w.done()
			
	def addTask(self,args,waitting=False):
		try:
			if self.isAborted():
				return False
			self.task_no += 1
			self.taskQ.put([DO_JOB,self.task_no,args],waitting)
			self.task_cnt += 1
			return True
		except Exception as e:
			logger.info("thread (%s)error:%s" % (self.name,mstr(e)))
			return False
	
	def abortTask(self):
		if self.aborted:
			return
		self.aborted = True
		self.cleanTaskQ()
		for w in self.workers:
			self.task_no += 1
			self.taskQ.put([ABORT_JOB,self.task_no,None],False)
		for w in self.follows:
			w.abortTask()
	
	def cleanTaskQ(self):
		r = True
		while r:
			try:
				self.taskQ.get(False)
			except:
				r = False

	def cleanDoneQ(self):
		r = True
		while r:
			try:
				self.doneQ.get(False)
			except:
				r = False
		
	def getResult(self,waitting=True):
		try:
			status,proName,task_no,data = self.doneQ.get(waitting)
			if task_no > self.max_task_no_resp:
				self.max_task_no_resp = task_no
			#logger.info("%s status=%s,%s,%d" % (self.name,str(status),proName,task_no))
			return (status,proName,task_no,data)
		except Exception as e:
			logger.info("thread %s error:%s" % (self.name,str(e)))
			return None,None,None,None
