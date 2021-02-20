# -*- coding:utf8 -*-
import re
class ConvertException(Exception):
	pass
	
class ArgsConvert(object):
	def __init__(self,preString,subfixString,coding='utf-8'):
		self.preString = preString
		self.subfixString = subfixString
		self.coding=coding
		sl1 = [ u'\\' + c for c in self.preString ]
		sl2 = [ u'\\' + c for c in self.subfixString ]
		ps = u''.join(sl1)
		ss = u''.join(sl2)
		re1 = ps + r"[_a-zA-Z_\u4e00-\u9fa5][a-zA-Z_0-9\u4e00-\u9fa5\,\.\'\{\}\[\]\(\)\-\+\*\/]*" + ss
		self.re1 = re1
		# print( self.re1,len(self.re1),len(re1),type(self.re1))
		
	def convert(self,obj,namespace,default=''):
		""" obj can be a string,[],or dictionary """
		if type(obj) == type(u''):
			return self.convertUnicode(obj,namespace,default)
		if type(obj) == type(''):
			return self.convertString(obj,namespace,default)
		if type(obj) == type([]):
			ret = []
			for o in obj:
				ret.append(self.convert(o,namespace,default))
			return ret
		if type(obj) == type({}):
			ret = {}
			for k in obj.keys():
				ret.update({k:self.convert(obj.get(k),namespace,default)})
			return ret
		# print( type(obj),"not converted")
		return obj
	
	def findAllVariables(self,src):
		r = []
		for ph in re.findall(self.re1,src):
			dl = self.getVarName(ph)
			r.append(dl)
		return r
		
	def getVarName(self,vs):
		return vs[len(self.preString):-len(self.subfixString)]
	
	def getVarValue(self,var,namespace,default):
		v = default
		try:
			v = eval(var,namespace)
		except Exception as e:
			v = namespace.get(var,default)
		return v 
			
	def convertUnicode(self,s,namespace,default):
		args = re.findall(self.re1,s)
		for arg in args:
			dl = s.split(arg)
			var = self.getVarName(arg)
			v = self.getVarValue(var,namespace,default)				
			if type(v) != type(u''):
				v = str(v)
			s = v.join(dl)
		return s
		
	def convertString(self,s,namespace,default):
		ret = self.convertUnicode(s,namespace,default)
		return ret

class ConditionConvert(object):
	def __init__(self,pString = u'$<',sString=u'>$',coding='utf-8'):
		self.coding = coding
		self.pString = pString
		self.sString = sString
		pS = ''.join([u'\\'+i for i in self.pString ])
		sS = ''.join([u'\\'+i for i in self.sString ])
		self.re1 = re.compile(u'(' + pS + '/?' + u'[_a-zA-Z_\u4e00-\u9fa5][a-zA-Z_0-9\u4e00-\u9fa5\,\.\'\{\}\[\]\(\)\-\+\*\/]*' + sS + u')')
		self.buffer1 = []
	def convert(self,obj,namespace):
		""" obj can be a string,[],or dictionary """
		if type(obj) == type(u''):
			return self.convertUnicode(obj,namespace)
		if type(obj) == type(''):
			return self.convertString(obj,namespace)
		if type(obj) == type([]):
			ret = []
			for o in obj:
				ret.append(self.convert(o,namespace))
			return ret
		if type(obj) == type({}):
			ret = {}
			for k in obj.keys():
				ret.update({k:self.convert(obj.get(k),namespace)})
			return ret
		# print( type(obj),"not converted")
		return obj
	
	def getVarName(self,vs):
		return vs[len(self.pString):-len(self.sString)]
	
	def getVarValue(self,var,namespace):
		v = None
		try:
			v = eval(var,namespace)
		except Exception as e:
			v = namespace.get(var,None)
		return v 
			
	def convertList(self,alist,namespace):
		ret = []
		handleList = alist
		while len(handleList) > 0:
			i = handleList[0]
			handleList = handleList[1:]
			if len(self.re1.findall(i)) < 1:
				ret.append(i)
			else:
				name = self.getVarName(i)

				if name[0] == u'/':
					name = name[1:]
					if len(self.buffer1) < 1:
						raise ConvertException('name(%s) not match' % name)
					if self.buffer1[-1] != name:
						raise ConvertException('name(%s) not match(%s)' % (self.buffer1[-1],name))
					val = self.getVarValue(name,namespace)
					self.buffer1 = self.buffer1[:-1]
					if val is not None:
						return u''.join(ret),handleList
					else:
						return u'',handleList
				else:
					self.buffer1.append(name)
					subStr,handleList = self.convertList(handleList,namespace)
					ret.append(subStr)
		if len(self.buffer1)>0:
			raise ConvertException('name(s)(%s) not closed' % ','.join(self.buffer1))
		return u''.join(ret),[]
		
	def convertUnicode(self,s,namespace):
		ret = []
		parts = self.re1.split(s)
		s,b = self.convertList(parts,namespace)
		return s
		
	def convertString(self,s,namespace):
		ret = self.convertUnicode(s,namespace)
		return ret

		
if __name__ == '__main__':
	"""
	ns = {
		'a':12,
		'b':'of',
		'c':'abc',
		u'是':'is',
		'd':{
			'a':'doc',
			'b':'gg',
		}
	}
	AC = ArgsConvert('%{','}%')
	s1 = u"%{a}% is a number,%{d['b']}% is %{是}% undefined,%{c}% is %{d['a']+'(rr)'}% string"
	arglist=['this is a descrciption %{b}% selling book',123,'ereg%{a}%,%{c}%']
	argdict={
		'my':arglist,
		'b':s1
	}
	print(f(s1,'<=>',AC.convert(s1,ns)))
	print(f(argdict,'<=>',AC.convert(argdict,ns)))
	"""
	cc = ConditionConvert()
	s2 = u"Begin $<abc>$this is $<ba>$ba = 100 $</ba>$condition out$</abc>$ end"
	s3 = """select * from RPT_BONDRATINGS
where 1=1
$<rtype>$and ratingtype=${rtype}$$</rtype>$
$<bond>$and bond_id = ${bond}$$</bond>$"""
	print(f("result=",cc.convert(s2,{'ba':23})))
	print(f("result = ",cc.convert(s3,{'bond':'943','rtype':'1'})))
	
