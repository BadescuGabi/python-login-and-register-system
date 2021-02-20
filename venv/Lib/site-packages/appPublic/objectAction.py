from appPublic.Singleton import SingletonDecorator

@SingletonDecorator
class ObjectAction(object):
	def __init__(self):
		self.actionList = {}
	
	def init(self,id,action):
		idA = self.actionList.get(id,None)
		if idA is None:
			idA = self.actionList[id] = {}
		self.actionList[id][action] = []
		
	def add(self,id,action,func):
		idA = self.actionList.get(id,None)
		if idA is None:
			idA = self.actionList[id] = {}
		fL = idA.get(action,None)
		if fL is None:
			fL = self.actionList[id][action] = []
		self.actionList[id][action].append(func)

	def execute(self,id,action,data,callback=None):
		if action in ['#','*']:
			return data
		idA = self.actionList.get(id,None)
		if idA is None:
			return data
		fL = idA.get(action,[])
		fL += idA.get('*',[])
		for f in fL:
			data = f(id,action,data)
		if len(fL)==0:
			for f in idA.get('#',[]):
				data = f(id,action,data)
		if callback is not None:
			callback(data)
		return data

if __name__ == '__main__':
	def f(id,act,data):
		return data

	def f1(id,act,data):
		return data

	def f2(id,act,data):
		return data
		
	def add():
		oa = ObjectAction()
		oa.add('test','b',f)
		#oa.add('test','*',f1)
		oa.add('test','#',f2)

	def exe():
		oa = ObjectAction()
		oa.execute('test','a','data1')

	add()
	exe()
	
