"""
{
	dataurl:url,
	fields:[
		field, field, ...
	]
}
field:
{
	name:"ttt",
	label:"ffff",
	datatype:one of str, text, short, long, float, date, time, ...
	freeze:True of False
	hidden:True of False
	width: default is 100
	cols:default is 1
}
"""
from kivy.clock import Clock
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.app import App
from appPublic.dictObject import DictObject
from .datagrid.Datagrid import DataGrid
from .utils import absurl
from .kivysize import KivySizes

class ScrollDataGrid(ScrollView):
	def __init__(self,**kw):
		super().__init__()
		self.grid = DataGrid()
		self.grid.size_hint = (None,1)
		# self.grid.width = 1500
		self.grid.bind(minimum_width=self.grid.setter('width'))
		self.do_scroll_y = False
		self.do_scroll_x = True
		self.add_widget(self.grid)
	
	def setupGrid(self, headers, width, height):
		r =  self.grid.setupGrid(headers,width,height)
		self.grid.width = width
		self.body = self.grid.body
		self.body.bind(on_touch_down=self.synchronizeMove)

	def synchronizeMove(self,obj,touch):
		x,y = touch.pos
		self.grid.headerRow.on_touch_down(touch)

	def  addRow(self, rowsData, **kwargs):
		return self.grid.addRow(rowsData,**kwargs)

	def removeRowAtIndex(self, index):
		return self.grid.removeRowAtIndex(index)

	def changeCellValueAtRow(self, rowIndex, cellIndex, cellValue):
		return self.grid.changeCellValueAtRow(rowIndex, cellIndex, cellValue)
	def removeRowById(self, widget_id):
		return self.grid.removeRowById(widget_id)
	def removeAllContent(self):
		return self.grid.removeAllContent()
	def changeRowColor(self, rowIndex, changedColor):
		return self.grid.changeRowColor(rowIndex, changedColor)
	def changeRowColorByID(self, widget_id, changedColor):
		return self.grid.changeRowColorByID(widget_id, changeColor)
		
	
class DataList(BoxLayout):
	def widthc2p(self,options):

		ks = KivySizes()
		for f in options.fields:
                    if f.width:
                            f.width = ks.CSize(f.width)
                    else:
                            f.width = ks.CSize(12)
		return options

	def __init__(self,**options):
		def scrollfreeze(x,b):
			if self.freeze_grid:
				self.freeze_grid.body.scroll_y = \
					self.normal_grid.body.scroll_y
			if self.normal_grid.body.scroll_y < 0.01:
				if self.total_cnt <= self.max_row:
					return
				if self.loading == True:
					return 
				self.loading = True
				self.loadData(self.curpage + 1)
					
		def scrollnormal(x,b):
			return
			if self.normal_grid:
				self.normal_grid.body.scroll_y = \
					self.freeze_grid.body.scroll_y
		super().__init__()
		self.options = DictObject(**options)
		self.options = self.widthc2p(self.options)
		self.total_cnt = 0
		self.loading = False
		self.page_rows = self.options.rows or 60
		self.curpage = 0 # page start from 1
		self.min_row = -1
		self.max_row = -1
		self.freeze_grid = None
		self.normal_grid = None
		self.freeze_fields = [ f for f in self.options.fields if  f.freeze and not f.hidden ]
		self.normal_fields = [ f for f in self.options.fields if not f.freeze and not f.hidden ]
		if len(self.freeze_fields) > 0:
			self.freeze_grid = self.buildGrid(self.freeze_fields,freeze=True)
			self.freeze_grid.body.bar_width = 0
			self.add_widget(self.freeze_grid)

		if len(self.normal_fields) > 0:
			self.normal_grid = self.buildGrid(self.normal_fields,freeze=False)
			self.normal_grid.body.bar_width = 4
			self.add_widget(self.normal_grid)
		Clock.schedule_once(self.loadData, 1)
		if self.freeze_grid:
			self.freeze_grid.body.scroll_y = 1
			self.freeze_grid.body.bind(on_scroll_stop=scrollnormal)
		if self.normal_grid:
			self.normal_grid.body.scroll_y = 1
			self.normal_grid.body.bind(on_scroll_stop=scrollfreeze)
	
	def buildGrid(self,fields,freeze=False):
		if freeze:
			grid = DataGrid()
		else:
			grid = ScrollDataGrid()
		fielddescs = []
		width = 0
		height = 40
		for f in fields:
			x = {
				'text':f.label,
				'type':'Label',
				'width':f.width or 100
			}
			width = width + x['width']
			fielddescs.append(x)
		grid.setupGrid(fielddescs,width,height)
		if freeze:
			grid.size_hint_x = None
			grid.width = width + len(fields) * 4
		return grid

	def addRow(self,grid,r,freeze=False):
		fds = [] 
		fields = self.freeze_fields if freeze else self.normal_fields
		for f in fields:
			v = r[f.name]
			if v is None:
				v = ''
			else:
				v = str(v)
			x = {
				'text':v,
				'type':'Label'
				}
			fds.append(x)
		grid.addRow(fds)

	def deleteRows(self,side):
		"""
		side<0:delete bottom lines
		else: delete top lines
		"""
		pass

	def loadData(self,page):
		def showData(obj,d):
			d = DictObject(**d)
			if d is None:
				raise Exception
			self.total_cnt = d.total
			if self.curpage > page:
				v = self.min_row
				self.min_row = self.min_row - len(d.rows)
				
			else:
				v = self.max_row
				self.max_row = self.max_row + len(d.rows)
			if self.max_row - self.min_row > self.page_rows * 3:
				self.deleteRows(self.curpage - page)
			self.curpage = page
			for r in d.rows:
				if self.freeze_grid is not None:	
					self.addRow(self.freeze_grid,r,freeze=True)
				self.addRow(self.normal_grid,r)
			self.normal_grid.body.scroll_y = 1.0 - float(v-self.min_row)/float(self.max_row - self.min_row)
			self.loading = False
		
		url = self.options.get('dataurl') + '?page=%d&rows=%d' % (page,self.page_rows)
		parenturl = None
		if hasattr(self,'parenturl'):
			parenturl = self.parenturl
		url = absurl(url,parenturl)
		d = App.get_running_app().hc.get(url,callback=showData)

