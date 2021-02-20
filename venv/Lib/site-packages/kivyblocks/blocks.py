import os
import sys
import codecs
import importlib
import json

from appPublic.dictExt import dictExtend
from appPublic.jsonConfig import getConfig
from appPublic.folderUtils import ProgramPath

from kivy.config import Config
from kivy.metrics import sp,dp
from kivy.core.window import WindowBase

import kivy
from kivy.resources import resource_add_path
resource_add_path(os.path.join(os.path.dirname(__file__),'./ttf'))
Config.set('kivy', 'default_font', [
    'msgothic',
    'DroidSansFallback.ttf'])

from kivy.app import App
from .baseWidget import baseWidgets
from .widgetExt import Messager
from .externalwidgetmanager import ExternalWidgetManager
from .threadcall import HttpClient

def showError(e):
	print('error',e)
class Blocks:
	def __init__(self):
		self.registedWidget = {}
		self.namedWidgets = {}
		self.descLoader = ExternalWidgetManager()
		self.register({'widgettype':'FloatLayout'})
		self.register({'widgettype':'BoxLayout'})
		self.register({
						'widgettype':'Button',
						'options':{
							'size_hint_y':None,
							'height':2
						}
					})
		self.register({'widgettype':'AsyncImage'})
		self.register({'widgettype':'Image'})
		self.register({'widgettype':'TreeView'})
		self.register({
						'widgettype':'TextInput'
					})
		self.register({'widgettype':'DropDown'})
		self.register({'widgettype':'TabbedPanel'})
		self.register({'widgettype':'TabbedPanelContent'})
		self.register({'widgettype':'TabbedPanelHeader'})
		self.register({'widgettype':'TabbedPanelItem'})
		self.register({'widgettype':'Switch'})
		self.register({'widgettype':'CheckBox'})
		self.register({'widgettype':'StackLayout'})
		self.register({'widgettype':'RelativeLayout'})
		self.register({'widgettype':'RecycleBoxLayout'})
		self.register({'widgettype':'ScatterLayout'})
		self.register({'widgettype':'PageLayout'})
		self.register({'widgettype':'GridLayout'})
		self.register({'widgettype':'AnchorLayout'})
		self.register({'widgettype':'ActionBar'})
		#self.register({'widgettype':'ActionOverflow'})
		self.register({'widgettype':'ActionView'})
		#self.register({'widgettype':'ContextualActionViews'})
		self.register({'widgettype':'ActionPrevious'})
		self.register({'widgettype':'ActionItem'})
		self.register({'widgettype':'ActionButton'})
		self.register({'widgettype':'ActionToggleButton'})
		self.register({'widgettype':'ActionCheck'})
		self.register({'widgettype':'ActionSeparator'})
		self.register({'widgettype':'ActionGroup'})
		self.register({'widgettype':'Label'})
		self.register({'widgettype':'AccordionItem'})
		self.register({'widgettype':'Accordion'})
		self.register({'widgettype':'BinStateImage'})
		self.register({'widgettype':'ScrollView'})
		self.register({'widgettype':'ScrollWidget'})
		self.register({'widgettype':'Splitter'})
		self.register({'widgettype':'Spinner'})
		self.register({'widgettype':'Slider'})
		self.register({'widgettype':'ScreenManager'})
		self.register({'widgettype':'Sandbox'})
		self.register({'widgettype':'ProgressBar'})
		self.register({'widgettype':'Popup'})
		self.register({'widgettype':'ModalView'})
		self.register({'widgettype':'FileChooser'})
		self.register({'widgettype':'EffectWidget'})
		self.register({'widgettype':'ColorPicker'})
		self.register({'widgettype':'Carousel'})
		self.register({'widgettype':'Camera'})
		self.register({'widgettype':'Bubble'})
		self.register({'widgettype':'CodeInput'})
		self.register({'widgettype':'JsonCodeInput'})
		self.register({'widgettype':'BoolInput'})
		self.register({'widgettype':'AmountInput'})
		self.register({'widgettype':'FloatInput'})
		self.register({'widgettype':'IntegerInput'})
		self.register({'widgettype':'StrInput'})
		self.register({'widgettype':'SelectInput'})
		#self.register({'widgettype':'AWebView'})
		self.register({'widgettype':'DatePicker'})
		self.register({'widgettype':'PhoneButton'})
		self.register({'widgettype':'Text'})
					
		self.descLoader.travalRegisterDesc(self.register)
	
	def register(self,options):
		"""
		options format:
		{
			"widgettype":name,
			"basetype":"fefefe", 
			"options":opts,
			"subwidgets":[],
			"binds":[]
		}
		"""
		name = options['widgettype']
		if not options.get('basetype'):
			try:
				klass = baseWidgets[name]
				options['klass'] = klass
			except:
				raise Exception('class(%s) import error' % name)
		
		self.registedWidget[name] = options
			
	def isWidegetDesc(self,obj):
		return type(obj)==type({}) and obj.get('widgettype',None) is not None
	
	def setBinds(self,widget,binddesc):
		"""
		"""
		pass
		
	def getRegisterdConfig(self,widgettype):
		conf = self.registedWidget[widgettype]
		if not conf.get('basetype',False):
			return conf
		conf1 = self.getRegisterdConfig(conf.get('basetype'))
		return dictExtend(conf1,conf)
				
	def valueBuild(self,options):
		app = App.get_running_app()
		if type(options) != type({}):
			return options
		opts = {}
		for k,v in options.items():
			if self.isWidegetDesc(v):
				opts[k] = self.build(v)
				continue
			if type(v) == type({}):
				opts[k] = self.valueBuild(v)
				continue
			if type(v) == type([]):
				opts[k] = [ self.valueBuild(i) for i in v ]
				continue
			if k in ['width','height','text_size']:
				v = sp(int(app.font_size * v))
			if k in ['font_size']:
				v = sp(app.myFontSizes.get(v,self.font_size))
			opts[k] = v
		return opts
		
	def __build(self,desc,parent):
		ids = {}
		name = desc['widgettype']
		desc = dictExtend(self.getRegisterdConfig(name),desc)
		options = desc.get('options',{})
		options = self.valueBuild(options)
		if name in ['Button','Label']:
			if options.get('font_size',None) is None:
				options['font_size'] = sp(App.get_running_app().font_size)
		
		# events = self.getEvents(options)
		Klass = desc['klass']
		widget = None
		try:
			widget = Klass(**options)
		except Exception as e:
			print('options=',options,'class=',name,e)
			raise e
			
		if desc.get('id',False):
			ids.update({desc['id']:widget})
		if desc.get('subwidgets',False):
			for d in desc['subwidgets']:
				w,ids1 = self.build(d,widget)
				ids.update(ids1)
				if not d.get('topwidget',False):
					widget.add_widget(w)
		if desc.get('binds',False):
			self.setBinds(widget,desc['binds'])

		#for e in events:
		#	pass
		return widget,ids

	def build(self,desc,parent=None):
		"""
		desc format:
		{
			type:<registered widget>,
			id:widget id,
			options:
			subwidgets:[
			]
			binds:[
			]
		}
		"""
		name = desc['widgettype']
		if name == 'externalwidget':
			desc = self.descLoader.loadWidgetDesc(desc)
			
		widget,ids = self.__build(desc,parent=parent)
		if parent is None:
			widget.ids = ids
			return widget
		else:
			return widget,ids
	
class BlocksApp(App):
	myFontSizes = {
		"small":12,
		"normal":16,
		"large":20,
		"huge":24,
	}
	separatorsize = 2
	def build(self):
		b = Blocks()
		self.hc = HttpClient()
		WindowBase.softinput_mode='below_target'
		pp = ProgramPath()
		workdir = pp
		if len(sys.argv)>1:
			workdir = sys.argv[1]
		config = getConfig(workdir,NS={'workdir':workdir,'ProgramPath':pp})
		rooturl = config.rooturl
		if config.font_sizes:
			self.myFontSizes = config.font_sizes

		self.font_size = self.getFontSize(config.font_name)
		x = None
		dic = self.hc.get(rooturl)
		if dic is not None:
			x = b.build(dic)
			return x
		else:
			x = b.build({
				"widgettype":"Label",
				"options":{
					"text":rooturl + ": error"
				}
			})
		return x
			
	def getFontSize(self,fontsizename):
		x = self.myFontSizes.get(fontsizename,None)
		if x == None:
			x = self.myFontSizes.get('normal')
		return x

	def textsize(self,x):
		return (sp(x * self.font_size), sp(self.font_size))

	def buttonsize(self,x):
		m = int(0.6 * self.font_size)
		return (sp(int(self.font_size * x + m),
					sp(self.font_size + m )))
		
if __name__ == '__main__':
	desc = {
		"widgettype":"BoxLayout",
		"options":{
			"orientation":"vertical"
		},
		"subwidgets":[
			{
				"widgettype":"BoxLayout",
				"options":{
					"orientation":"horizontal",
					"size_hint_y":None,
					"height":1
				},
				"subwidgets":[
					{
						"widgettype":"StrInput",
						"id":"ui_url",
						"options":{
							"size_hint":(1,1)
						}
					},
					{
						"widgettype":"Button",
						"id":"go_btn",
						"options":{
							"text":"访问",
							"size_hint":(None,None),
							"height":1,
							"width":2
						}
					}
				]
			},
			{
				"widgettype":"BoxLayout",
				"id":"widgetholder",
				"options":{
					"orientation":"vertical"
				},
			}
		]
	}
		
	class TestApp(App):
		def build(self):
			b = Blocks()
			self.root_widget = b.build(desc)
			self.root_widget.ids['go_btn'].bind(on_release=self.go_test)
			return self.root_widget

		def go_test(self,btn):
			url = self.root_widget.ids['ui_url'].text
			if url != '':
				try:
					desc = {
						"widgettype":"externalwidget",
						"url":url.encode('utf8')
					}
					l = ExternalWidgetManager()
					wdesc = l.loadWidgetDesc(desc)
					b = Blocks()
					w = b.build(wdesc)
					self.root_widget.ids['widgetholder'].clear_widgets()
					self.root_widget.ids['widgetholder'].add_widget(w)
					#print('load ok',wdesc)
				except Exception as e:
					msger = Messager()
					msger.show_error(e)

				
				
	#TestApp().run()
	BlocksApp().run()
