
import os
import sys

from appPublic.jsonConfig import getConfig
from appPublic.folderUtils import ProgramPath

from kivy.config import Config
from kivy.metrics import sp,dp,mm
from kivy.core.window import WindowBase
from kivy.clock import Clock

import kivy
from kivy.resources import resource_add_path
resource_add_path(os.path.join(os.path.dirname(__file__),'./ttf'))
Config.set('kivy', 'default_font', [
	'msgothic',
	'DroidSansFallback.ttf'])

from kivy.app import App
# from .baseWidget import baseWidgets
# from .widgetExt import Messager
# from .externalwidgetmanager import ExternalWidgetManager
from .threadcall import HttpClient,Workers
from .derivedWidget import buildWidget, loadUserDefinedWidget
from .utils import *
from .pagescontainer import PageContainer
from .widgetExt.messager import Messager

class BlocksApp(App):
	def urlwidget(self,**kw):
		url = kw.get('url')
		if url is None:
			raise ArgumentError('url','urlwidget miss a url argument')
		parenturl = kw.get('parenturl')
		url = absurl(url,parenturl)
		x = None
		dic = App.get_running_app().hc.get(url)
		if dic is not None:
			ancestor = kw.get('ancestor')
			x = buildWidget(dic, ancestor=ancestor,parenturl=url)
		
		return x

	def filewidget(self,**kw):
		filename = kw.get('filename')
		if filename is None:
			raise ArgumentError('filename','filewidget miss a filename argument')
		b = ''
		with codecs.open(filename,'r','utf-8') as f:
			b = f.read()
		if b == '':
			return None
		dic = json.loads(b)
		ancestor = kw.get('ancestor')
		x = buildwidget(dic,ancestor)
		return x

	def build(self):
		x = PageContainer()
		config = getConfig()
		self.config = config
		self.workers = Workers(maxworkers=config.maxworkers or 80)
		self.workers.start()
		self.hc = HttpClient()
		WindowBase.softinput_mode='below_target'
		Clock.schedule_once(self.build1)
		return x

	def build1(self,t):
		x = None
		loadUserDefinedWidget()
		if self.config.root:
			x = buildWidget(self.config.root)
			self.root.add(x)
		else:
			msgr = Messager()
			msgr.show_error('config.root is None')
			
	def __del__(self):
		self.workers.running = False		
