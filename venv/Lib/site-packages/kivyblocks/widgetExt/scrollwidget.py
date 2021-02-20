from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.graphics import Color, Ellipse,Rectangle

class ScrollWidget(ScrollView):
	def __init__(self,**kw):
		super(ScrollWidget,self).__init__(**kw)
		self._inner_layout = GridLayout(cols=1, padding=2, spacing=2,size_hint=(None,None))
		self._inner_layout.bind(minimum_height=self._inner_layout.setter('height'))
		#self._inner_layout.bind(minimum_width=self._inner_layout.setter('width'))
		super(ScrollWidget,self).add_widget(self._inner_layout)
		#self.bind(size=self.on_size)
	
	def on_size(self,t,s):
		print('s=',s)
		x,y = s
		s = x + 5,y + 5
		self._inner_layout.size = s
		"""
		with self.canvas:
			c = Color(1,0,0,1)
			Rectangle(pos=self.pos, size=self.size)
		"""

	def add_widget(self,widget,**kw):
		a = self._inner_layout.add_widget(widget,**kw)
		x,y = widget.pos
		w,h = widget.size
		if x + w > self._inner_layout.width:
			self._inner_layout.width = x + w
		if y + h > self._inner_layout.height:
			self._inner_layout.height = y + h
		return a

	def clear_widgets(self,**kw):
		a = self._inner_layout.clear_widgets(**kw)
		self._inner_layout.width = 0
		self._inner_layout.height = 0

	def remove_widget(self,widget,**kw):
		a = self._inner_layout.remove_widget(widget,**kw)
		return a

if __name__ == '__main__':
	from kivy.app import App
	from kivy.uix.label import Label
	from kivy.uix.button import Button
	import codecs
	
	class MyApp(App):
		def build(self):
			root = ScrollWidget(size=(400,400),pos_hint={'center_x': .5, 'center_y': .5},do_scroll_x=True,do_scroll_y=True)
			with codecs.open(__file__,'r','utf-8') as f:
				txt = f.read()
				lines = txt.split('\n')
				for l in lines:
					root.add_widget(Label(text=l,color=(1,1,1,1),size_hint=(None,None),size=(1200,40)))
			return root

	MyApp().run()
