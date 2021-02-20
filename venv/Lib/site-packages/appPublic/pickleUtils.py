import pickle

def saveData(fn,*args):
  f = open(fn,'wb')
  a = [ pickle.dump(arg,f) for arg in args ]
  f.close()
  
def loadData(fn,cnt):
  a = [None] * cnt
  try:
    f = open(fn,'rb')
    a = [ pickle.load(f) for i in range(cnt) ]
    f.close()
    return a
  except:
    return a
