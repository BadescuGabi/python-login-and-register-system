from kivy.app import App
from kivy.metrics import mm

from appPublic.Singleton import SingletonDecorator
from appPublic.jsonConfig import getConfig

@SingletonDecorator
class KivySizes:
	myFontSizes = {
		"smallest":1.5,
		"small":3,
		"normal":4.5,
		"large":6,
		"huge":7.5,
		"hugest":9,
	}
	separatorsize = 2

	def getFontSize(self,name=None):
		if name is None:
			name = getConfig().font_name
		x = self.myFontSizes.get(name,None)
		if x == None:
			x = self.myFontSizes.get('normal')
		return x

	def namedSize(self,cnt=1,name=None):
		return mm(cnt * self.getFontSize(name=name))

	def unitedSize(self,x,y=None,name=None):
		xr = self.namedSize(cnt=x,name=name)
		if y is None:
			return xr
		return (xr,self.namedSize(cnt=y,name=name))

	def CSize(self,x,y=None,name=None):
		return self.unitedSize(x,y=y,name=name)

	def getScreenSize(self):
		root = App.get_running_app().root
		return root.width, root.height

	def getWindowPhysicalSize(self,w):
		h_phy = float(w.height) / mm(1)
		w_phy = float(w.width) / mm(1)
		return w_phy, h_phy

	def getScreenPhysicalSize(self):
		return self.getWindowPhysicalSize(App.get_running_app().root)

