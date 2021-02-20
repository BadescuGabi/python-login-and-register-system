
def dictExtend(s,addon):
	ret = {}
	ret.update(s)
	skeys = ret.keys()
	for k,v in addon.items():
		if k not in skeys:
			ret[k] = v
			continue
		if type(v)!=type(ret[k]):
			ret[k] = v
			continue
		if type(v)==type({}):
			ret[k] = dictExtend(ret[k],v)
			continue
		if type(v)==type([]):
			ret[k] = ret[k] + v
			continue
		ret[k] = v
	return ret
