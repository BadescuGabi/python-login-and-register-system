import codecs
import csv
class Reader:
	def __init__(self,f,delimiter):
		self.f = f
		self.delimiter = delimiter
		self.line = 0

	def __iter__(self):
		return self
	
	def next(self):
		l = self.f.readline()
		if l == '':
			raise StopIteration()
		while l[-1] in [ '\n','\r']:
			l = l[:-1]
		r = [ i if i != '' else None for i in l.split(self.delimiter) ]
		self.line = self.line + 1
		return r

class CSVData:
	def __init__(self,filename,coding='utf8',delimiter=','):
		self.filename = filename
		self.coding = coding
		self.f = codecs.open(filename,'rb',self.coding)
		self.reader = Reader(self.f,delimiter)
		self.fields = self.reader.next()
	
	def __del__(self):
		self.f.close()
	
	def __iter__(self):
		return self
	
	def next(self):
		try:
			r = self.reader.next()
			if len(r) != len(self.fields):
				print("length diff",len(r),len(self.fields),"at line %d" % self.reader.line)
				raise StopIteration()
			d = {}
			[d.update({self.fields[i]:r[i]}) for i in range(len(self.fields))]
			return d
		except:
			raise StopIteration()

if __name__ == '__main__':
	import sys
	cd = CSVData(sys.argv[1])
	for r in cd:
		print(r)
	

