from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import serialization
from cryptography.exceptions import InvalidSignature
import base64

class RSA:
	def __init__(self):
		pass
	
	def write_privatekey(self,private_key,fname,password=None):
		pwd = password
		pem = ''
		if pwd is not None:
			pwd = bytes(pwd,encoding='utf8')  if not isinstance(pwd, bytes) else pwd
			pem = private_key.private_bytes(
				encoding=serialization.Encoding.PEM,
				format=serialization.PrivateFormat.PKCS8,
				encryption_algorithm=serialization.BestAvailableEncryption(pwd)
			)
		else:
			pem = private_key.private_bytes(
				encoding=serialization.Encoding.PEM,
				format=serialization.PrivateFormat.TraditionalOpenSSL,
				encryption_algorithm=serialization.NoEncryption()
			)
		

		with open(fname,'w') as f:
			text = pem.decode('utf8')
			f.write(text)

	def write_publickey(self,public_key,fname):
		pem = public_key.public_bytes(
			encoding=serialization.Encoding.PEM,
			format=serialization.PublicFormat.SubjectPublicKeyInfo
		)

		with open(fname,'w') as f:
			text = pem.decode('utf8')
			f.write(text)
		
	def read_privatekey(self,fname,password=None):
		pwd = password
		if password is not None:
			pwd = bytes(password,encoding='utf8')  if not isinstance(password, bytes) else password
		with open(fname, "rb") as key_file:
			key = serialization.load_pem_private_key(
				key_file.read(),
				password=pwd,
				backend=default_backend()
			)
			return key
	
	def read_publickey(self,fname):
		with open(fname,'r') as f:
			public_key_pem_export = f.read()
			public_key_pem_export = bytes(public_key_pem_export,encoding='utf8') if not isinstance(public_key_pem_export, bytes) else public_key_pem_export
			return serialization.load_pem_public_key(data=public_key_pem_export,backend=default_backend())
			
	def create_privatekey(self):
		return rsa.generate_private_key(
			public_exponent=65537,
			key_size=2048,
			backend=default_backend()
			)
	
	def create_publickey(self,private_key):
		return private_key.public_key()
		
	def encode(self,public_key,text):
		message_bytes = bytes(text, encoding='utf8') if not isinstance(text, bytes) else text
		return str(base64.b64encode(public_key.encrypt(message_bytes,
			padding.OAEP(
				mgf=padding.MGF1(algorithm=hashes.SHA256()),
				algorithm=hashes.SHA256(),
				label=None
			)
		)), encoding='utf-8')
		
	def decode(self,private_key,cipher):
		cipher = cipher.encode('utf8') if not isinstance(cipher, bytes) else cipher
		ciphertext_decoded = base64.b64decode(cipher)
		plain_text = private_key.decrypt(
			ciphertext_decoded,padding.OAEP(
				mgf=padding.MGF1(algorithm=hashes.SHA256()),
				algorithm=hashes.SHA256(),
				label=None
			)
		)
		return str(plain_text, encoding='utf8')
		
	def sign(self,private_key,message):
		data_to_sign = bytes(message, encoding='utf8') if not isinstance(
			message, 
			bytes
		) else message
		signer = private_key.signer(
			padding.PSS(
				mgf=padding.MGF1(hashes.SHA256()),
				salt_length=padding.PSS.MAX_LENGTH
			),
			hashes.SHA256()
		)
		signer.update(data_to_sign)
		signature = str(
			base64.b64encode(signer.finalize()),
			encoding='utf8'
		)
		return signature
	
	def check_sign(self,public_key,plain_text,signature):
		try:
			plain_text_bytes = bytes(
				plain_text, 
				encoding='utf8'
			) if not isinstance(plain_text, bytes) else plain_text
			signature = base64.b64decode(
				signature
			) if not isinstance(signature, bytes) else signature
			verifier = public_key.verifier(
			  signature,
			  padding.PSS(
				  mgf=padding.MGF1(hashes.SHA256()),
				  salt_length=padding.PSS.MAX_LENGTH
			  ),
			  hashes.SHA256()
			)
			verifier.update(plain_text_bytes)
			verifier.verify()
			return True
		except InvalidSignature as e:
			return False
			
if __name__ == '__main__':
	Recv_cipher=b'JHHDhjaHLeLRopobfiJvWtVn8Bu3/3AsV6Xr8MwHBBEli7v+oHRNH2dcAfVa7VcdBlKlr7W+hDDAxlex3/OzwyRp4R5DcDsepTLPaG+nKK6zj0MGkvEJ6iNpABO9uohskFXPBuO6t3+G6cKRMMeIU7g7oSJqlbKHJyRmd9j8OHS2fFYL331oRhJvyuJe5zrdxHEOez+XEt2AbuYi7WFFVlM/DvX/tjAG3SHXr14GlJYGbuNR2LNIapAMBSt7GDQ/LrzLv54ysE3OZpVFnOszVt5ythiDPoImnpJ990Fb/1yd7goPZ5NA8cSKCu7dDV42JWcj44JHrIfNsMR7aG9QxQ=='
	r = RSA()
	mpri = r.create_privatekey()
	mpub = r.create_publickey(mpri)
	
	zpri = r.create_privatekey()
	zpub = r.create_publickey(zpri)
	
	text = 'this is a test data, aaa'
	cipher = r.encode(mpub,text)
	signature = r.sign(zpri,text)
	
	ntext = r.decode(mpri,cipher)
	check = r.check_sign(zpub,ntext,signature)
	print(text,ntext,check)
	
	ypri = r.read_privatekey('d:/dev/mecp/conf/RSA.private.key','ymq123')
	ypub = r.read_publickey('d:/dev/mecp/conf/RSA.public.key')
	
	x = r.encode(ypub,'root:ymq123')
	print('root:ymq123 encode=',x,len(x),len(Recv_cipher))
	orgtext=r.decode(ypri,Recv_cipher)
	print(orgtext)
	
	r.write_publickey(ypub,'./test.public.key')
	r.write_privatekey(ypri,'./test.private.key','ymq123')
	ypri = r.read_privatekey('./test.private.key','ymq123')
	ypub = r.read_publickey('./test.public.key')
	
	x = r.encode(ypub,text)
	ntext = r.decode(ypri,x)
	print(text,'<==>',ntext)
	