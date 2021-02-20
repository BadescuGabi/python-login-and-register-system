import uuid

node = None

def setNode(n='ff001122334455'):
	global node
	if len(n)>12:
		return
	for c in n:
		if c not in ['0','1','2','3','4','5','6','7','8','9','a','b','c','d','e','f']:
			return
	node = eval('0x' + n + 'L')

def getID():
	global node
	if node is None:
		node = uuid.getnode()
	u = uuid.uuid1(node)
	return u.hex

