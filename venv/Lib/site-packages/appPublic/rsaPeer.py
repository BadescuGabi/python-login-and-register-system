from appPublic.rsa import RSA
from appPublic.rc4 import RC4
try:
	import ujson as json
except:
	import json
import random

class DeliverPacket:
	def __init__(self,sender,c,k,s):
		self.sender = sender
		self.c = c
		self.k = k
		self.s = s
	
	def pack(self):
		d = {
			"sender":self.sender,
			"c":self.c,
			"k":self.k,
			"s":self.s,
		}
		return json.dumps(d)
	
	def unpack(self,body):
		d = json.loads(body)
		self.sender = d.sender
		self.c = d['c']
		self.k = d['k']
		self.s = d['s']

class RSAPeer:
	def __init__(self,myid,myPrikey,pearPubKey=None):
		self.myid = myid
		self.mypri = myPrikey
		self.peerpub = pearPubKey
		self.rsa = RSA()
	
	def getPeerPublicKey(self,id):
		pass
		
	def _genSystematicKey(self):
		t = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890~!@#$%^&*'
		kl = random.randint(10,15)
		ky = []
		klen = len(t) - 1
		for k in range(kl):
			i = random.randint(0,klen)
			# print(k,klen,i)
			ky.append(t[i])
		return ''.join(ky)
		
	def encode(self,text):
		"""
		return a json text
		json ojbect have three addt:
		k:encrypted rc4 key
		s:signature
		c:ciphertext encrypted by key
		"""
		d = {"id":self.myid,"data":text}
		text = json.dumps(d)
		sk = self._genSystematicKey()
		rc4 = RC4(sk)
		c = rc4.encode(text)
		s = self.rsa.sign(self.mypri,sk)
		if self.peerpub is None:
			return None
		k = self.rsa.encode(self.peerpub,sk)
		d = {
			'c':c,
			'k':k,
			's':s
		}
		return json.dumps(d)
		
	def decode(self,body):
		"""
		cipher a json text
		json ojbect have three addt:
		k:encrypted rc4 key
		s:signature
		c:ciphertext encrypted by key
		"""
		d = json.loads(body)
		signature = d['s']
		sk = self.rsa.decode(self.mypri,d['k'])
		# print('sk=',sk,'k=',d['k'],type(d['k']))
		rc4 = RC4(sk)
		t = rc4.decode(d['c'])
		d = json.loads(t)
		ret = d['data']
		if self.peerpub is not None and not self.rsa.check_sign(self.peerpub,sk,signature):
			return None
		if self.peerpub is None:
			peerpub = self.getPeerPublicKey(d['id'])
			if peerpub is None:
				return None
			if  not self.rsa.check_sign(peerpub,sk,signature):
				return None
		return ret

if __name__ == '__main__':
	r = RSA()
	mary_pri = r.create_privatekey()
	mary_pub = r.create_publickey(mary_pri)
	
	john_pri = r.create_privatekey()
	john_pub = r.create_publickey(john_pri)
	
	john_rp = RSAPeer(john_pri,mary_pub)
	mary_rp = RSAPeer(mary_pri,john_pub)
	txt = '''hello python 爱的实打实大师大师大师的发送到发送到而非个人格个二哥而而二哥而个人各位,UDP是一种无连接对等通信协议，没有服务器和客户端概念，通信的任何一方均可通过通信原语直接和其他方通信
	
HOME FAQ DOCS DOWNLOAD 
 

index
next |
previous |
Twisted 18.9.0 documentation » Twisted Names (DNS) » Developer Guides » '''
	c = john_rp.encode(txt)
	newtxt = mary_rp.decode(c)
	print(txt)
	print('<===>')
	print(c)
	print('<===>')
	print(newtxt)
