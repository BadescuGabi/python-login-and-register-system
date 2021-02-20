# -*- coding: utf-8 -*-  
import random, base64  
from hashlib import sha1  
 
class RC4:
	def __init__(self,data_coding='utf8'):
		self.bcoding = 'iso-8859-1'
		self.dcoding = data_coding
		self.salt = b'AFUqx9WZuI32lnHk'
	
	def _crypt(self,data,key):
		"""RC4 algorithm return bytes"""
		if type(data)==type(''):
			data = data.encode(self.dcoding)
		x = 0  
		box = [i for i in range(256) ]
		for i in range(256):  
			x = (x + box[i] + key[i % len(key)]) % 256  
			box[i], box[x] = box[x], box[i]  
		x = y = 0  
		out = []  
		for char in data:
			x = (x + 1) % 256  
			y = (y + box[x]) % 256  
			box[x], box[y] = box[y], box[x]  
			out.append(chr(char ^ box[(box[x] + box[y]) % 256]))  

		return ''.join(out).encode(self.bcoding) 
  
	def encode(self,data, key,encode=base64.b64encode, salt_length=16):  
		"""RC4 encryption with random salt and final encoding"""  
		akey = key.encode(self.bcoding)
		a = sha1(akey + self.salt)
		k = a.digest()
		data = self.salt + self._crypt(data, k)
		
		if encode:  
			data = encode(data)
		return data.decode(self.dcoding)

	def decode(self,data, key,decode=base64.b64decode, salt_length=16):  
		"""RC4 decryption of encoded data"""  
		akey = key.encode(self.bcoding)
		if decode:  
			data = decode(data)  
		salt = data[:salt_length]
		a = sha1(akey + self.salt)
		k = a.digest() #.decode('iso-8859-1')
		r = self._crypt(data[salt_length:], k)
		return r.decode(self.dcoding)

  
if __name__=='__main__':  
	# 需要加密的数据长度没有限制 
	# 密钥 
	data="231r3 feregrenerjk gkht324g8924gnfw k;ejkvwkjerv"
	key = '123456'  
	rc4 = RC4()
	print(data)
	# 加码  
	encoded_data = rc4.encode(data,key)  
	print(encoded_data,len(encoded_data) )
	# 解码  
	decoded_data = rc4.decode(encoded_data,key)  
	print(decoded_data)
