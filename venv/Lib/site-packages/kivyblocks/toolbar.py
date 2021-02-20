from kivy.graphics import Color, Rectangle
from kivy.uix.button import ButtonBehavior
from kivy.uix.image import AsyncImage
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.app import App
from kivy.clock import Clock

from appPublic.dictObject import DictObject

from .widgetExt.scrollwidget import ScrollWidget
from .utils import *
from .kivysize import KivySizes

"""
tool options
{
	img_size=1.5,	
	text_size=0.7,
	text='',
	img_src=''
	id = 'me'
}
"""
class Tool(ButtonBehavior, BoxLayout):
	def __init__(self,**opts):
		super().__init__(orientation='vertical',size_hint=(None,None))
		self.opts = DictObject(**opts)
		app = App.get_running_app()
		ks = KivySizes()
		size = ks.unitedSize(self.opts.img_size)
		img = AsyncImage(source=self.opts.img_src,size_hint=(None,None),
			size=(size,size))
		tsize = ks.unitedSize(self.opts.text_size)
		lbl = Label(text=self.opts.text,font_size=int(tsize))
		lbl.text_size = (size, 2* tsize)
		self.add_widget(img)
		self.add_widget(lbl)
		self.size = (size * 1.1, (size + 2 * tsize)*1.1)
		
	def on_size(self,obj,size):
		if self.parent:
			print('********center***********')
			self.center = self.parent.center

	def on_press(self):
		print('Tool(). pressed ...............')

"""
toolbar options
{
	img_size=1.5,	
	text_size=0.7,
	tools:[
		{
			"name":"myid",
			"img_src":"gggggg",
			"text":"gggggg"
			"url":"ggggggggg"
		},
		...
	]
}
"""
class Toolbar(GridLayout):
	def __init__(self, callback,**opts):
		self.opts = DictObject(**opts)
		self.tool_widgets={}
		super().__init__(cols = len(self.opts.tools))
		self.size_hint = (1,None)
		for opt in self.opts.tools:
			opt.img_size = self.opts.img_size
			opt.text_size = self.opts.text_size
			tool = Tool(**opt)
			self.tool_widgets[opt.name] = tool
			box = BoxLayout()
			box.add_widget(tool)
			self.add_widget(box)
			tool.bind(on_press=callback)
		self.height = tool.height * 1.1

	def on_size(self,obj,size):
		with self.canvas.before:
			Color(0.3,0.3,0.3,1)
			Rectangle(pos=self.pos,size=self.size)

"""
Toolpage options
{
	img_size=1.5,	
	text_size=0.7,
	tool_at:"left","right","top","bottom",
	tools:[
		{
			"name":"myid",
			"img_src":"gggggg",
			"text":"gggggg"
			"url":"ggggggggg"
		},
		...
	]
	
"""
class ToolPage(BoxLayout):
	def __init__(self,**opts):
		self.opts = DictObject(**opts)
		if self.opts.tool_at in [ 'top','bottom']:
			orient = 'vertical'
		else:
			orient = 'horizontal'

		super().__init__(orientation=orient)
		self.content = None
		self.toolbar = None
		Clock.schedule_once(self.show_firstpage)
	
	def on_size(self,obj,size):
		if self.content is None:
			return
		x,y = size
		self.toolbar.width = x
		self.content.width = x
		self.content.height = y - self.toolbar.height

	def showPage(self,obj):
		self._show_page(obj.opts)

	def show_firstpage(self,t):
		self.mywidgets = {}
		self.content = BoxLayout()
		for t in self.opts.tools:	
			t.url = absurl(t.url,self.parenturl)
			t.img_src = absurl(t.img_src,self.parenturl)

		self.toolbar = Toolbar(self.showPage, **self.opts)
		if self.opts.tool_at in ['top','left']:
			self.add_widget(self.toolbar)
			self.add_widget(self.content)
		else:
			self.add_widget(self.content)
			self.add_widget(self.toolbar)
		return self._show_page(self.opts.tools[0])

	def _show_page(self,opts):
		x = self.mywidgets.get(opts.name)
		if x is None:
			purl = ''
			if hasattr(self,'parenturl'):
				purl = self.parenturl
				print('#########parenturl=',purl,'##########')
			kw = {
				'url' : opts.url,
				'parenturl':purl
			}
			x = App.get_running_app().urlwidget(**kw)
			# x.bind(minimux_width=x.setter('width'))
			# x.bind(minimux_height=x.setter('height'))
			self.mywidgets[opts.name] = x
		self.content.clear_widgets()
		self.content.add_widget(x)
		
		
if __name__ == '__main__':
	from blocksapp import BlocksApp
	app = BlocksApp()
	app.run()
