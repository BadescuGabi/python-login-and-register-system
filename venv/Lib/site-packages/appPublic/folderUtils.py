# -*- coding: utf-8 -*-

import os
import sys
import stat
import os.path
import platform
import time
"""
import win32api
"""
import sys


def startsWith(text,s):
	return text[:len(s)] == s

def endsWith(text,s):
	return text[-len(s):] == s

def ProgramPath():
	filename = sys.argv[0]
	if getattr(sys,'frozen',False):
		filename = sys.executable
	p = os.path.dirname(os.path.abspath(filename))
	return p

def timestamp2datatiemStr(ts):
	t = time.localtime(ts)
	return '%04d-%02d-%-02d %02d:%02d:%02d' % (t.tm_year,t.tm_mon,t.tm_mday,t.tm_hour,t.tm_min,t.tm_sec)
	
"""
def findAllDrives():
    Drives=[]
    # print "Searching for drives..."
    drives=win32api.GetLogicalDriveStrings().split(":")
    for i in drives:
        # print "i=",i,":"
        dr=i[-1].lower()
        if dr.isalpha():
            dr+=":\\"
            inf=None
            try:
                inf=win32api.GetVolumeInformation(dr)
            except:
                pass # Removable drive, not ready
		     # You'll still get the drive letter, but inf will be None
            Drives.append([dr,inf])
    return Drives
"""

## list all folder name under folder named by path
#
def folderList(path) :
	for name in os.listdir(path) :
		full_name = os.path.join(path,name)
		if os.path.isdir(full_name):
			yield full_name

def listFile(folder,suffixs=[],rescursive=False):
    subffixs = [ i.lower() for i in suffixs ]
    for f in os.listdir(folder):
        p = os.path.join(folder,f)
        if rescursive and os.path.isdir(p):
            for p1 in listFile(p,suffixs=suffixs,rescursive=True):
	            yield p1
        if os.path.isfile(p):
            e = p.lower()
            if suffixs == [] :
                yield p
            for s in subffixs:
                if e.endswith(s):
                    yield p

def folderInfo(root,uri=''):
	relpath = uri
	if uri[1]=='/':
		relpath = uri[1:]
	
	path = os.path.join(root,*relpath.split('/'))
	ret = []
	for name in os.listdir(path):
		full_name = os.path.join(path,name)
		s = os.stat(full_name)
		if stat.S_ISDIR(s.st_mode):
			ret.append( {
				'id':relpath + '/' + name,
				'name':name,
				'path':relpath,
				'type':'dir',
				'size':s.st_size,
				'mtime':timestamp2datatiemStr(s.st_mtime),
			})
		if stat.S_ISREG(s.st_mode):
			ret.append( {
				'id':relpath + '/' + name,
				'name':name,
				'path':relpath,
				'type':'file',
				'size':s.st_size,
				'mtime':timestamp2datatiemStr(s.st_mtime),
			})
	return ret
		
		
def rmdir_recursive(dir):
	"""Remove a directory, and all its contents if it is not already empty."""
	for name in os.listdir(dir):
		full_name = os.path.join(dir, name)
		# on Windows, if we don't have write permission we can't remove
		# the file/directory either, so turn that on
		if not os.access(full_name, os.W_OK):
			os.chmod(full_name, 0o600)
		if os.path.isdir(full_name):
			rmdir_recursive(full_name)
		else:
			os.remove(full_name)
	os.rmdir(dir)

def _mkdir(newdir) :
    """works the way a good mkdir should :)
        - already exists, silently complete
        - regular file in the way, raise an exception
        - parent directory(ies) does not exist, make them as well
    """
    if os.path.isdir(newdir):
        pass
    elif os.path.isfile(newdir):
        raise OSError("a file with the same name as the desired " \
                      "dir, '%s', already exists." % newdir)
    else:
        head, tail = os.path.split(newdir)
        if head and not os.path.isdir(head):
            _mkdir(head)
        #print "_mkdir %s" % repr(newdir)
        if tail:
            os.mkdir(newdir)

def _copyfile(fp,dir) :
	fs = open(fp,'rb')
	name = os.path.basename(fp)
	newfp = os.path.join(dir,getFileName(name,dir))
	f = open(newfp,'wb')
	while True :
		data = fs.read(65536)
		if not data :
			break
		f.write(data)
	fs.close()
	f.close()
	return True

def _copydir(fp,dir,topdistinct) :
	name = os.path.basename(fp)
	newname = getFileName(name,dir)
	debug(newname)
	newfp = os.path.join(dir,newname)
	_mkdir(newfp)
	if fp==topdistinct :
		return True

	flist = os.listdir(fp)
	for name in flist :
		full_name = os.path.join(fp,name)
		if os.path.isdir(full_name) :
			p = os.path.join(dir,name)
			_copydir(full_name,newfp,topdistinct)
		else :
			if os.path.isfile(full_name) :
				_copyfile(full_name,newfp)
	return True

mkdir=_mkdir
copyfile = _copyfile
copydir = _copydir
rmdir = rmdir_recursive
