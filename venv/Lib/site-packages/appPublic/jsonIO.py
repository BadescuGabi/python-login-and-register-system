import json

def uni_str(a, encoding):
    if a is None:
        return None
    if isinstance(a, (list, tuple)):
        s = []
        for i, k in enumerate(a):
            s.append(uni_str(k, encoding))
        return s
    elif isinstance(a, dict):
        s = {}
        for i, k in enumerate(a.items()):
            key, value = k
            s[uni_str(key, encoding)] = uni_str(value, encoding)
        return s
    elif isinstance(a, bool):
        return a
    elif isinstance(a, unicode):
        return a
    elif isinstance(a, str) or (hasattr(a, '__str__') and callable(getattr(a, '__str__'))):
        if getattr(a, '__str__'):
            a = str(a)
        return unicode(a, encoding)
    else:
        return a
        
def success(data):
    return dict(success=True,data=data)

def error(errors):
    return dict(success=False,errors=errors) 
  
def jsonEncode(data,encode='utf-8'):
	return json.dumps(uni_str(data, encode))

def jsonDecode(jsonstring):
  return json.loads(jsonstring)
