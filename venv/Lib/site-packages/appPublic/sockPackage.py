import os
import time
import threading
import sys
from socket import AF_INET,SOCK_STREAM,socket
from mylog import mylog

def logit(s) :
	mylog(__file__ + ':' + s)

class background(threading.Thread) :
        def __init__(self,func,kw) :
                threading.Thread.__init__(self)
                self.func = func
                self.kw = kw

        def run(self) :
                if self.func!=None :
                        self.func(**self.kw)
                        return

def BackgroundCall(func,datas) :
        b=background(func,datas)
        b.start()
        return

class SocketServerError(Exception) :
	pass

class SocketClientError(Exception) :
	pass

class SocketServer(threading.Thread) :

	def __init__(self,host,port,max_connect=10,callee=None) :
		threading.Thread.__init__(self, name = 'SocketServer')
		self.setDaemon(False)
		self.host = host
		self.port = int(port)
		self.max_c = max_connect
		self.ready = False
		self.keep_running = 0
		self.callee = callee
		self.setSocketServer()

	def setSocketServer(self) :
		try :
			self.sock = socket(AF_INET,SOCK_STREAM)
			self.sock.bind((self.host,self.port))
			self.sock.listen(self.max_c)
			self.ready = True
		except Exception as e:
			logit('setSocketServer() Error:%s\nhost=%s,port=%d' % (e,self.host,self.port))
			pass

	def run(self) :
		if not self.ready :
			raise SocketServerError('not ready')
		callee = self.callee
		if self.callee!=None :
			callee = self.callee
		self.keep_running = 1
		while self.keep_running :
			conn,addr = self.sock.accept()
			BackgroundCall(callee,{'conn':conn,'addr':addr})
			# conn.close()
	
	def stop(self) :
		self.keep_running = 0

	def callee(self,conn,addr) :
		while 1 :
			d = conn.recv(1024)
			if d==None :
				break
			conn.send(d)
		con.close()

class SocketClient :

	def __init__(self,host,port) :
		self.host = host
		self.port = port
		self.ready = False
		self.connect()

	# if tim ==0 not blocking
	def timeout(self,tim) :
		if self.ready :
			self.sock.setblocking(tim>0)
			if tim>0 :
				self.sock.settimeout(tim)

	def connect(self) :
		try :
			self.sock = socket(AF_INET,SOCK_STREAM)
			self.sock.connect((self.host,self.port))
			self.ready = True
		except Exception as e:
			self.ready = False
			logit('Socket connect error,%s\nhost=%s,port=%s' % (e,self.host,self.port))
			raise SocketClientError('connect error')

	def read(self,size) :
		try :
			data = self.sock.recv(size)
			return data
		except Exception as e:
			logit('recv error,%s' % e)
			raise SocketClientError('recv error')

	def write(self,data) :
		try :
			self.sock.send(data)
		except Exception as e:
			logit('recv error,%s' % e)
			raise SocketClientError('send error')
	
	def close(self) :
		self.sock.close()
		self.ready = False

if __name__ == '__main__' :
	s = SocketServer('localhost',12232)
	s.start()
	time.sleep(5)
	while 1 :
		c = SocketClient('localhost',12232)
		msg = 'msg1'
		print("send:",msg)
		c.write(msg)
		d = c.read(1024)
		print("get:",d)
		time.sleep(1)
