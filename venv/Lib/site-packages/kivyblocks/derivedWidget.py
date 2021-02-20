import json
from kivy.uix.button import ButtonBehavior
from kivy.properties import *
from kivy.app import App
from appPublic.myTE import MyTemplateEngine
from appPublic.jsonConfig import getConfig
from .baseWidget import *
from .datalist import DataList
from .utils import *
from .vplayer import VPlayer
from .aplayer import APlayer
from .toolbar import ToolPage

"""
dic format
{
	"widgettype":"xx",
	"bases":[
		{
			"base":"Button",
			"options":{}
		}
	],
	"properties":[
		{
			"name":"kef",
			"type":"NumericProperty()"
		}
	],
	"binds":[
		[[id,sock],[id,method]]
	],
	"methods":{
		"xxxx":"code ....."
	},
	"subwidgets":[
	]
}
"""

widgettmpl="""
{% set init=False %}
{% for b in bases %}
{% if b.options %}
{% set init=True %}
{% endif %}
{% endfor %}
{% if subwidgets %}
{% set init=True %}
{% endif %}
{% if binds %}
{% set init=True %}
{% endif %}
class {{widgettype}}({% for b in bases %}{{b.base}}{% if not loop.last %},{% endif %}{% endfor %}):
{% if properties %}
{% for name,value in properties.items() %}
	{{name}} = {{value}}
{% endfor %}
{% endif %}
{% if init %}
	def __init__(self,**kw):
	{% for b in bases %}
		{% if b.options %}
		kwargs = {}
		bopts={{json.dumps(b.options)}}
		kwargs.update(kw)
		kwargs.update(JDConvert(bopts))
		{{b.base}}.__init__(self,**kwargs)
		{% else %}
		{{b.base}}.__init__(self,**kw)
		{% endif %}
	{% endfor %}
	{% if subwidgets %}
		self.subwidgets()
	{% endif %}
	{% if binds %}
		{% for b in binds %}
		w1 = getWidgetById(self,'{{b[0][0]}}')
		w2 = getWidgetById(self,'{{b[1][0]}}')
		w1.bind({{b[0][1]}}=w2.{{b[1][1]}})
		{% endfor %}
	{% endif %}
{% else %}
	pass
{% endif %}
{% if subwidgets %}
	def subwidgets(self):
		if not hasattr(self,'ids'):
			self.ids = {}
		app = App.get_running_app()
		if not hasattr(app,'ids'):
			app.ids = {}
		jsonstr = '''{{json.dumps(subwidgets)}}'''
		sws =  json.loads(jsonstr)
		for o in sws:
			w = buildWidget(o,ancestor=self,parenturl='{{parenturl}}')
			self.add_widget(w)
{% endif %}

{% if methods %}
{% for name,code in methods.items() %}
m = {}
exec('''{{code}}''',globals(),m)
for k,v in m.items():
	{{widgettype}}.{{name}} = v
{% endfor %}
{% endif %}
		
"""

"""
instance dic format
{
	"widgettype":"iconbutton",
	"options":{
	},
	"subwidgets":[
	],
	"binds":[
		[[id,evt],[id,evt]]
	]
}
"""

instancetmpl = """
{% if options %}
jsonstr='''{{json.dumps(options)}}'''
options = json.loads(jsonstr)
options = JDConvert(options)
{% if widgettype in ['urlwidget','filewidget'] %}
options['ancestor'] = ancestor
options['parenturl'] = '{{parenturl}}'
__target__ = App.get_running_app().{{widgettype}}(**options)
{% else %}
__target__ = {{widgettype}}(**options)
{% endif %}
{% else %}
__target__ = {{widgettype}}()
{% endif %}
{% if id %}
{% if id[0] == '/' %}
app = App.get_running_app()
if not hasattr(app,'ids'):
	app.ids = {}
app.ids['{{id[1:]}}'] = __target__
{% else %}
if not hasattr(ancestor,'ids'):
	ancestor.ids = {}
ancestor.ids['{{id}}'] = __target__
{% endif %}
{% endif %}
{% if subwidgets %}
{% for desc in subwidgets %}
jsonstr = '''{{json.dumps(desc)}}'''
desc = json.loads(jsonstr)
# desc = JDConvert(desc)
sw = buildWidget(desc,ancestor=__target__,parenturl='{{parenturl}}')
__target__.add_widget(sw)
{% endfor %}
{% endif %}
{% if binds %}
{% for b in binds %}
w1 = getWidgetById(__target__,'{{b[0][0]}}')
w2 = getWidgetById(__target__,'{{b[1][0]}}')
w1.bind({{b[0][1]}}=w2.{{b[1][1]}})
{% endfor %}
{% endif %}
"""

def loadUserDefinedWidget():
	config = getConfig()
	if config.udws:
		for udw in config.udws:
			udw = absurl(udw,'')
			udwdescs = App.get_running_app().hc.get(udw)
			for desc in udwdescs:
				buildClass(desc)
def buildClass(dic):
	te = MyTemplateEngine([])
	try:
		code = te.renders(widgettmpl,dic)
	except Exception as e:
		print(dic,e)
		raise e
	print(code)
	g = {}
	try:
		exec(code,globals(),g)
	except Exception as e:
		print(code,'-error-',e)
		raise
	globals().update(g)
	for k,v in g.items():
		return v
	return None

def buildWidget(dic,ancestor=None,parenturl=''):
	if ancestor is None:
		ancestor = App.get_running_app()
	te = MyTemplateEngine([])
	te.set('ancestor',ancestor)
	te.set('parenturl',parenturl)
	try:
		code = te.renders(instancetmpl,dic)
	except Exception as e:
		print(dic,e)
		raise e
	g = {}
	g['ancestor'] = ancestor
	# print(code)
	try:
		exec(code,globals(),g)
	except Exception as e:
		print('CODE****',code,'****CODE','-error-',e,'-error-')
		raise e
	for k,v in g.items():
		if k=='__target__':
			if dic['widgettype'] in ['urlwidget', 'filewidget' ]:
				return v
			if parenturl == '' and hasattr(ancestor,'parenturl'):
				parenturl = ancestor.parenturl
			v.parenturl = parenturl
			return v
	return None

class ArgumentError(Exception):
	def __init__(self,p,msg):
		super().__init__()
		self.argument=p
		self.msg = msg
	def __str__(self):
		return "Arguments(%s) error:%s" % (self.argument, self.msg)


if __name__ == '__main__':
	from kivy.app import App
	dic = {
		"widgettype":"iconbutton",
		"bases":[
			{
			
				"base":"ButtonBehavior"
			},
			{
				"base":"Image"
			}
		],
		"methods":[
			{
				"name":"on_press",
				"code":"def on_press(self): print('pressed ')"
			}
		]
	}
	class MyApp(App):
		def build(self):
			buildClass(dic)
			
			return buildWidget({'widgettype':'iconbutton',
					'options':{
						'source':"/tmp/image.jpeg"
					}
			})
	MyApp().run()
