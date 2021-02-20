#dataMapping
from appPublic.dictObject import DictObject

def keyMapping(dic,mappingtab,keepmiss=True):
	ret = {}
	keys = [ k for k in dic.keys()]
	if not keepmiss:
		keys = [ k for k in dic.keys() if k in mappingtab.keys() ]
	[ ret.update({mappingtab.get(k,k):dic[k]}) for k in keys ]
	return DictObject(**ret)


def valueMapping(dic,mappingtab):
	"""
	mappingtab format:
	{
		"field1":{
			"a":"1",
			"b":"2",
			"__default__":"5"
		},
		"field2":{
			"a":"3",
			"b":"4"
		}
	}
	field1,field2 is in dic.keys()
	"""
	ret = {}
	for k in dic.keys():
		mt = mappingtab.get(k,None)
		if mt is None:
			ret[k] = dic[k]
		else:
			dv = mt.get('__default__',dic[k])
			v = mt.get(dic[k],dv)
			ret[k] = v

	return DictObject(**ret)
	