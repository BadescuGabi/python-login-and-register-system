import csv

class CSVData:
	def __init__(self,csvfile,names = None,headline = 0,dataline = 1):
		self.csvfile = csvfile
		self.names = names
		self.headline = headline
		self.dataline = dataline
	
	def read(self):
		f = open(self.csvfile,'rb')
		reader = csv.reader(f)
		fields = None
		if self.names is not None:
			fields = self.names
		data = []
		lno = 0
		for l in reader:
			if fields is None and lno == self.headline:
				fields = [f for f in l]
			if lno >= self.dataline:
				rec = {}
				for i in range(len(fields)):
					rec[fields[i]] = l[i]
				data.append(rec)
			lno += 1
		f.close()
		return data

	def iterRead(self):
		self.fd = open(self.csvfile,'r')
		try:
			reader = csv.reader(self.fd)
			fields = None
			if self.names is not None:
				fields = self.names
			lno = 0
			self.onBegin()
			for l in reader:
				if fields is None and lno == self.headline:
					fields = [f for f in l]
				if lno >= self.dataline:
					rec = {}
					for i in range(len(fields)):
						rec[fields[i]] = l[i]
					self.onRecord(rec)
				lno += 1
			self.fd.close()
			self.onFinish()
		except exception as e:
			fd.close()
			raise e

	def onReadBegin(self):
		pass
	def onRecord(self,rec):
		print(rec)
	
	def onFinish(self):
		print("onFinish() called")
		
if __name__ == '__main__':
	import sys
	cd = CSVData(sys.argv[1],names = ['st_date','open_price','max_price','min_price','close_price','volume','adj_price'])
	cd.iterRead()
