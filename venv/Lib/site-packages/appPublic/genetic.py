class Genetic:
    """
    A Base class for genetical objects,
    all the instances can inherite attributes from its parent. 
    """
    def __init__(self):
        self.__parent__ = None
        self.__children__ = []
        #print dir(self)

    def __getattr__(self,n):
        d = self.__dict__
        if n in d.keys():
            return d[n]
        p = self.__parent__ #d['__parent__']
        if p is not None:
            return getattr(p,n)
        raise AttributeError(n)

    def addChild(self,c):
        self.__children__.append(c)
        c.__parent__ = self
           
    def setParent(self,p):
        p.addChild(self)

if __name__ == '__main__':
    class A(Genetic):
        def __init__(self,a1,a2):
            Genetic.__init__(self)
            self.a1 = a1
            self.a2 = a2
        
    class B(Genetic):
        def __init__(self,b):
            Genetic.__init__(self)
            self.b = b
    gp = A(1,2)
    p = B(3)
    c = A(4,5)
    gc = B(6)
    gc.setParent(c)
    c.setParent(p)
    p.setParent(gp)
