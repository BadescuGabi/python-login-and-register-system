#
from appPublic.dictObject import DictObject

class SingletonDecorator:
    def __init__(self,klass):
        self.klass = klass
        self.instance = None
    def __call__(self,*args,**kwds):
        if self.instance == None:
            self.instance = self.klass(*args,**kwds)
        return self.instance

@SingletonDecorator
class GlobalEnv(DictObject):
	pass

if __name__ == '__main__':
	@SingletonDecorator
	class Child(object):
		def __init__(self,name):
			print("clild.init")
			self.name = name
		def __str__(self):
			return 'HAHA：' + self.name
		def __expr__(self):
			print(self.name)
        
	@SingletonDecorator
	class Handle(object):
		def __init__(self,name):
			self.name = name
		def __expr__(self):
			print(self.name)
  
	c = Child('me')
	d = Child('he')
	
	print(str(c),str(d))
	e = Handle('hammer')
	f = Handle('nail');
	print(str(e),str(f))
	
