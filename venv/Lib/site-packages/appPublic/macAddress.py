#! /usr/bin/env python
import locale
import psutil
import socket


def getAllAddress():
	iocounts = psutil.net_io_counters(pernic=True)
	ns = [ k for k in iocounts.keys() if iocounts[k].bytes_sent>0 and iocounts[k].bytes_recv>0 ]
	stats = psutil.net_if_stats()
	stat = [ i for i in stats.keys() if i in ns ]
	hds = psutil.net_if_addrs()
	for n,v in hds.items():
		if n not in stat:
			continue
		for i in v:
			if i.family == socket.AF_INET:
				yield n,i.address
	
def getAllMacAddress():
	coding = locale.getdefaultlocale()[1]
	iocounts = psutil.net_io_counters(pernic=True)
	ns = [ k for k in iocounts.keys() if iocounts[k].bytes_sent>0 and iocounts[k].bytes_recv>0 ]
	stats = psutil.net_if_stats()
	stat = [ i for i in stats.keys() if i in ns ]
	hds = psutil.net_if_addrs()
	for n,v in hds.items():
		if n not in stat:
			continue
		for i in v:
			if i.family == socket.AF_PACKET:
				yield n,i.address

if __name__ == '__main__':
	def test():
		for i in getAllAddress():
			print("mac=",i)
	test()
