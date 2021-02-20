
import asyncio
from collections.abc import Coroutine
# from asyncio.coroutines import iscoroutine

import zmq
import zmq.asyncio
import json

class Publisher:
	def __init__(self,port,coding='utf-8',msgid=1000):
		self.port = port
		self.socket = None
		self.coding = coding
		self.msgid = msgid
		context = zmq.asyncio.Context()
		self.socket = context.socket(zmq.PUB)
		self.socket.bind('tcp://*:%d' % self.port)

	async def publish(self,msg,msgtype='text',msgid=-1):
		print(msg,msgtype)
		if msgid == -1:
			msgid = self.msgid
		if msgtype != 'text':
			msg = json.dumps(msg)
			msgtype = 'json'
		s = '%d %s %s' % (msgid,msgtype,msg)
		print(s,msgtype,msgid)
		b = s.encode(self.coding)
		await self.socket.send(b)

	def __del__(self):
		self.socket.close()

class Subscriber:
	def __init__(self,host,ports,msgid,coding='utf-8'):
		self.host = host
		self.ports = ports
		self.msgid = msgid
		self.coding = coding
		context = zmq.asyncio.Context()  
		self.socket = context.socket(zmq.SUB)  
		f = b'%d' % self.msgid
		self.socket.setsockopt(zmq.SUBSCRIBE, f)  
		for p in self.ports:
			self.socket.connect("tcp://%s:%d" % (self.host,p))
	
	def addPort(self,port):
		self.socket.connect("tcp://%s:%d" % (self.host,port))
		#f = b'%d' % self.msgid
		#self.socket.setsockopt(zmq.SUBSCRIBE, f)  
		
	async def subscribe(self):
		ret = await self.socket.recv()
		ret = ret.decode(self.coding)
		msgid, msgtype, body = ret.split(' ',2)
		print('msgid=',msgid,'msgtype=',msgtype,'body=',body)
		if msgtype == 'json':
			return json.loads(body)
		return body

	def __del__(self):
		self.socket.close()

class RRServer:
	"""
	a request / response mode server
	"""
	def __init__(self,port,handler=None):
		self.port = port
		self.handler = handler
		print(type(self.handler))
		
	async def run(self):
		running = True
		context = zmq.asyncio.Context()
		socket = context.socket(zmq.REP)
		socket.bind('tcp://*:%s' % self.port)
		while running:
			rmsg = await socket.recv()
			wmsg = rmsg
			if self.handler is not None:
				wmsg = self.handler(rmsg)
				if isinstance(wmsg,Coroutine):
					wmsg = await wmsg
			await socket.send(wmsg)
		socket.close()

class RRClient:
	"""
	a request / response mode client
	"""
	def __init__(self,host,port):
		self.host = host
		self.port = port
		context = zmq.asyncio.Context()
		self.socket = context.socket(zmq.REQ)
		self.socket.connect('tcp://%s:%d' % (self.host,self.port))
	
	async def request(self,msg):
		await self.socket.send(msg)
		return await self.socket.recv()


class PPPusher:
	"""
	pusher of Push / Pull mode
	"""
	def __init__(self,host,port):
		self.host = host
		self.port = port
		context = zmq.asyncio.Context()
		self.socket = context.socket(zmq.PUSH)
		self.socket.bind('tcp://%s:%d' % (self.host,self.port))

	async def push(self,msg):
		await self.socket.send(msg)

class PPPuller:
	"""
	puller of Push / Pull mode
	"""
	def __init__(self,host,port,handler=None):
		self.host = host
		self.port = port
		self.handler = handler
		
	async def run(self):
		self.running = True
		context = zmq.asyncio.Context()
		socket = context.socket(zmq.PULL)
		socket.bind('tcp://%s:%d' % (self.host,self.port))
		while self.running:
			msg = await self.socket.recv()
			if self.handler is not None:
				x = self.handler(msg)
				if isinstance(x,Coroutine):
					await x

class PairClient:
	"""
	client of Pair mode 
	"""
	def __init__(self,host,port):
		self.host = host
		self.port = port
		context = zmq.asyncio.Context()
		self.socket = context.socket(zmq.PAIR)
		self.socket.bind('tcp://%s:%d' % (self.host,self.port))

	async def request(self,msg):
		await self.socket.send(msg)
		return await self.socket.recv()

class PairServer:
	"""
	server of Pair mode
	"""
	def __init__(self,port,handler=None):
		self.port = port
		self.handler = handler
		self.running = True

	async def run(self):
		self.running = True
		context = zmq.asyncio.Context()
		socket = context.socket(zmq.PAIR)
		socket.bind('tcp://*:%d' % self.port)
		while self.running:
			msg = await socket.recv()
			ret = msg
			if self.handler is not None:
				ret = self.handler()
				if isinstance(ret,Coroutine):
					ret = await ret
			await socket.send(ret)
