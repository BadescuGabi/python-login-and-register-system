import codecs

from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from Crypto.Cipher import KPCS1_V1_5 as V1_5
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA512, SHA384, SHA256, SHA, MD5
from Crypto import Random
from base64 import b64encode, b64decode
hash = "SHA-256"

def readPublickey(fname):
	with codecs.open(fname,'r','utf8') as f:
		b = f.read()
		k = RSA.importKey(b)
		return k
	return None

def readPrivatekey(fname,pwd):
	with codecs.open(fname,'r','utf8') as f:
		b = f.read()
		k = RSA.importKey(b,pwd)
		return k
	return None
	
def newkeys(keysize):
	random_generator = Random.new().read
	key = RSA.generate(keysize, random_generator)
	private, public = key, key.publickey()
	return public, private

def importKey(externKey):
	return RSA.importKey(externKey)

def getpublickey(priv_key):
	return priv_key.publickey()

def encrypt(message, pub_key):
	cipher = PKCS1_OAEP.new(pub_key)
	return cipher.encrypt(message)

def decrypt(ciphertext, priv_key):
	try:
		cipher = PKCS1_OAEP.new(priv_key)
		return cipher.decrypt(ciphertext)
	except Exception as e:
		print('e=',e)
		cipher = V1_5.new(priv_key)
		return cipher.decrypt(ciphertext)

def sign(message, priv_key, hashAlg = "SHA-256"):
	global hash
	hash = hashAlg
	signer = PKCS1_v1_5.new(priv_key)

	if (hash == "SHA-512"):
		digest = SHA512.new()
	elif (hash == "SHA-384"):
		digest = SHA384.new()
	elif (hash == "SHA-256"):
		digest = SHA256.new()
	elif (hash == "SHA-1"):
		digest = SHA.new()
	else:
		digest = MD5.new()
	digest.update(message)
	return signer.sign(digest)

def verify(message, signature, pub_key):
	signer = PKCS1_v1_5.new(pub_key)
	if (hash == "SHA-512"):
		digest = SHA512.new()
	elif (hash == "SHA-384"):
		digest = SHA384.new()
	elif (hash == "SHA-256"):
		digest = SHA256.new()
	elif (hash == "SHA-1"):
		digest = SHA.new()
	else:
		digest = MD5.new()
	digest.update(message)
	return signer.verify(digest, signature)

if __name__ == '__main__':
	cipher="""WaMlLEYnhBk+kTDyN/4OJmQf4ccNdk6USgtKpb7eHsYsotq4iyXi3N5hB1E/PqrPSmca1AMDLUcumwIrLeGLT9it3eTBQgl1YQAsmPxa6lF/rDOZoLbwD5sJ6ab/0/fuM4GbotqN5/d0MeuOSELoo8cFWw+7XpRxn9EMYnw5SzsjDQRWxXjZptoaGa/8pBBkDmgLqINif9EWV+8899xqTd0e9w1Gqb7wbt/elRNVBpgsSuSZb+dtBlvNUjuTms8BETSRai5vhXetK26Ms8hrayiy38n7wwEKE8fZ9iFzLtwa6xbhD5KudWbKJFFOZAfpzWttGMwWlISbGQigcW4+Bg=="""
	key = readPrivatekey('d:/dev/mecp/conf/RSA.private.key','ymq123')
	t = decrypt(cipher,key)
	print('t=',t)
	