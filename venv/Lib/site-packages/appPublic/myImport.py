def myImport(modulename):
	modules = modulename.split('.')
	if len(modules) > 1:
		a = __import__(modules[0])
		return eval('a.' + '.'.join(modules[1:]))
	return __import__(modulename)