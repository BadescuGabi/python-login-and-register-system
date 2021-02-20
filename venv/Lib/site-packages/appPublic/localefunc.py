# this function will fix a bug for open a file with a not english name.
#

import sys
import locale

language, local_encoding = locale.getdefaultlocale()
if sys.platform == 'win32':
     import locale, codecs
     local_encoding = locale.getdefaultlocale()[1]
     if local_encoding.startswith('cp'):            # "cp***" ?
         try:
             codecs.lookup(local_encoding)
         except LookupError:
             import encodings
             encodings._cache[local_encoding] = encodings._unknown
             encodings.aliases.aliases[local_encoding] = 'mbcs'
    
def locale_open(filename,mode='rb') :
    return open(filename.encode(local_encoding),mode)

def localeString(s) :
	try :
		return unicode(s,'utf-8').encode(local_encoding)
		
	except :
		return s

def utf8String(s) :
	try :
		return unicode(s,local_encoding).encode('utf-8')
	except :
		return s

def charsetString(s,charset) :
	try :
		return unicode(s,local_encoding).encode(charset)
	except :
		try :
			return unicode(s,'utf-8').encode(charset)
		except :
			return s

