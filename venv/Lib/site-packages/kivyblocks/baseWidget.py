import sys
from kivy.uix.button import Button
from kivy.uix.accordion import Accordion,AccordionItem
from kivy.uix.label import Label

from kivy.uix.actionbar import ActionBar,ActionView,ActionPrevious,ActionItem,ActionButton
from kivy.uix.actionbar import ActionToggleButton, ActionCheck,ActionSeparator,ActionGroup

from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.pagelayout import PageLayout
from kivy.uix.scatterlayout import ScatterLayout
from kivy.uix.recycleboxlayout import RecycleBoxLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.stacklayout import StackLayout

from kivy.uix.checkbox import CheckBox
from kivy.uix.switch import Switch
from kivy.uix.textinput import TextInput
from kivy.uix.dropdown import DropDown
from kivy.uix.tabbedpanel import TabbedPanel,TabbedPanelContent,TabbedPanelHeader,TabbedPanelItem
from kivy.uix.treeview import TreeView
from kivy.uix.image import AsyncImage,Image
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.scrollview import ScrollView
from kivy.uix.splitter import Splitter
from kivy.uix.spinner import Spinner
from kivy.uix.slider import Slider

from kivy.uix.screenmanager import ScreenManager
from kivy.uix.sandbox import Sandbox
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.uix.filechooser import FileChooser
from kivy.uix.effectwidget import EffectWidget
from kivy.uix.colorpicker import ColorPicker
from kivy.uix.carousel import Carousel
from kivy.uix.camera import Camera
from kivy.uix.bubble import Bubble
from kivy.uix.codeinput import CodeInput

from kivycalendar3 import DatePicker

from .widgetExt.scrollwidget import ScrollWidget
from .widgetExt.binstateimage import BinStateImage
from .widgetExt.jsoncodeinput import JsonCodeInput
from .widgetExt.inputext import FloatInput,IntegerInput, \
		StrInput,SelectInput, BoolInput, AmountInput
from .widgetExt.messager import Messager
import platform
osname = platform.system()
if osname == 'android':
	from .widgetExt.phonebutton import PhoneButton
	from .widgetExt.androidwebview import AWebView

class Text(Label):
	def __init__(self,**kw):
		super().__init__(**kw)

	def on_size(self,t,v):
		self.text_size = v

