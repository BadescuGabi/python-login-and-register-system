import os
import sys
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.video import Video
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.app import App
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, \
    NumericProperty, DictProperty, OptionProperty
from .utils import *

class VPlayer(FloatLayout):
	fullscreen = BooleanProperty(False)
	exit = BooleanProperty(False)
	stoped_play = BooleanProperty(False)
	paused_play = BooleanProperty(False)
	
	def __init__(self,vfile=None,loop=False,
			openfile_img=None,
			exit_img = None,
			pause_imgs = None,
			mute_imgs = None,
			track_img = None,
			next_img = None,
			replay_img = None):
		super().__init__()
		self.vp = Video(allow_stretch=True,pos_hint={'x': 0, 'y': 0},size_hint=(1,1))
		self.add_widget(self.vp)
		self.loop = loop
		self.openfile_img = openfile_img
		self.exit_img = exit_img
		self.pause_imgs = pause_imgs
		self.mute_imgs = mute_imgs
		self.track_img = track_img
		self.next_img = next_img
		self.replay_img = replay_img
		self.ffplayer = None
		self.menubar = None
		self._popup = None
		self.manualMode = False
		self.old_path = os.getcwd()
		self.pb = None
		if vfile:
			if type(vfile) == type([]):
				self.playlist = vfile
			else:
				self.playlist = [vfile]
			self.curplay = 0
			self.vp.source = self.playlist[self.curplay]
			self.vp.state = 'play'
		else:
			self.playlist = []
			self.curplay = -1
		self.vp.bind(eos=self.video_end)
		self.vp.bind(state=self.on_state)
		self.vp.bind(loaded=self.createProgressbar)
		self.vp.bind(on_touch_down=self.buildMenu)

	def addPlaylist(self,lst):
		self.playlist += lst

	def video_end(self,t,v):
		self.curplay += 1
		if not self.loop and self.curplay >= len(self.playlist):
			self.parent.remove_widget(self)
			return
		self.curplay = self.curplay % len(self.playlist)
		self.vp.source = self.playlist[self.curplay]
		self.vp.state = 'play'

	def totime(self,dur):
		h = dur / 3600
		m = dur % 3600 / 60
		s = dur % 60
		return '%02d:%02d:%02d' % (h,m,s)
		
	def createProgressbar(self,obj,v):
		if hasattr(self.vp._video, '_ffplayer'):
			self.ffplayer = self.vp._video._ffplayer

		if self.pb is None:
			self.pb = BoxLayout(orientation='horizontal',
				size_hint = (0.99,None),height=CSize(1.4))
			btn_menu=Button(text='M',size_hint=(None,None),text_size=CSize(1,1),size=CSize(1.2,1,2))
			btn_menu.bind(on_press=self.buildMenu)
			btn_volume=Button(text='V',size_hint=(None,None),text_size=CSize(1,1),size=CSize(1.2,1,2))
			btn_volume.bind(on_press=self.volumeControl)
			self.curposition = Label(text='0',width=CSize(4),
				size_hint_x=None)
			self.curposition.align='right'
			self.maxposition = Label(text=self.totime(self.vp.duration),
				width=CSize(4),size_hint_x=None)
			self.maxposition.align = 'left'
			# self.slider = ProgressBar(value=0,max=max)
			self.slider = Slider(min=0, 
				max=self.vp.duration, 
				value=0, 
				orientation='horizontal', 
				step=0.01)
			self.slider.bind(on_touch_down=self.enterManualMode)
			self.slider.bind(on_touch_up=self.endManualMode)
			self.manual_mode=False

			self.add_widget(self.pb)
			self.pb.add_widget(btn_menu)
			self.pb.add_widget(self.curposition)
			self.pb.add_widget(self.slider)
			self.pb.add_widget(self.maxposition)
			self.pb.add_widget(self.btn_volume)
			self.pb.pos = (0,0)
			Clock.schedule_interval(self.update_slider,1)

	def volumeControl(self,obj,v):
		self.volumeCtrl = BoxLayout(orientation='vertical',size_hint=(None,None),size=CSize(1.4,10))
		self.pos = self.width - self.volumeCtrl.width,CSize(1.4)
		self.add_widget(self.volumeCtrl)
		btn_mute = Button(text='Mute',size_hint_y=None,height=CSize(1.4))
		if self.vp.volume <= 0.001:
			btn_mute.text = 'Sound'
		btn_menu.bind(on_press=self.mute)
		self.volumeCtrl.add_widget(btn_mute)
		slider = Slider(min=0,
                                max=1,
                                value=self.vp.volume,
                                orientation='vertical',
                                step=0.01)
		slider.bind(on_value=self.setVolume)
		self.volumeCtrl.add_widegt(slider)
		btn_audioswitch = Button(text='track',size_hint_y=None,height=CSize(1.4))
		btn_audioswitch.bind(on_press=self.audioswitch)
		self.volumeCtrl.add_widget(btn_audioswitch)

	def enterManualMode(self,obj,touch):
		if not self.slider.collide_point(*touch.pos):
			return
		self.manualMode = True

	def endManualMode(self,obj,touch):
		if not self.manualMode:
			return
		self.vp.seek(self.slider.value/self.vp.duration)
		self.manualMode = False

	def update_slider(self,t):
		self.curposition.text = self.totime(self.vp.position)
		if not self.manualMode:
			self.slider.value = self.vp.position
			self.slider.max = self.vp.duration
		self.maxposition.text = self.totime(self.vp.duration)

	def on_state(self,o,v):
		print('onstate()',o,v,self.vp.state)

	def on_fullscreen(self, instance, value):
		window = self.get_parent_window()
		print('window.size=',window.size)
		if not window:
			Logger.warning('VideoPlayer: Cannot switch to fullscreen, '
						   'window not found.')
			if value:
				self.fullscreen = False
			return
		if not self.parent:
			Logger.warning('VideoPlayer: Cannot switch to fullscreen, '
						   'no parent.')
			if value:
				self.fullscreen = False
			return

		if value:
			self._fullscreen_state = state = {
				'parent': self.parent,
				'pos': self.pos,
				'size': self.size,
				'pos_hint': self.pos_hint,
				'size_hint': self.size_hint,
				'window_children': window.children[:]}

			# remove all window children
			for child in window.children[:]:
				window.remove_widget(child)

			# put the video in fullscreen
			if state['parent'] is not window:
				state['parent'].remove_widget(self)
			window.add_widget(self)

			# ensure the video widget is in 0, 0, and the size will be
			# readjusted
			self.pos = (0, 0)
			self.size = (100, 100)
			self.pos_hint = {}
			self.size_hint = (1, 1)
		else:
			state = self._fullscreen_state
			window.remove_widget(self)
			for child in state['window_children']:
				window.add_widget(child)
			self.pos_hint = state['pos_hint']
			self.size_hint = state['size_hint']
			self.pos = state['pos']
			self.size = state['size']
			if state['parent'] is not window:
				state['parent'].add_widget(self)

	def buildMenu(self,obj,touch):
		if not self.collide_point(*touch.pos):
			print('not inside the player')
			return 

		if touch.is_double_tap:
			self.fullscreen = False if self.fullscreen else True
			if self.menubar:
				self.remove_widget(self.menubar)
				self.menubar = None
			print('doube_tap')
			return 

		if self.menubar:
			print('delete menubar')
			self.remove_widget(self.menubar)
			self.menubar = None
			return 

		self.menubar = BoxLayout(orientation='horizontal',
			size_hint_y=None,height=CSize(1.4))
		self.btn_pause = Button(text='pause')
		if self.vp.state == 'pause':
			self.btn_pause.text = 'play'
		self.btn_pause.bind(on_press=self.pause)

		self.menubar.add_widget(self.btn_pause)
		self.menubar.add_widget(self.btn_mute)
		if self.can_openfile:
			btn_open = Button(text='open')
			btn_open.bind(on_press=self.openfile)
			self.menubar.add_widget(btn_open)
		if self.can_cut:
			btn_cut = Button(text='>>|')
			btn_cut.bind(on_press=self.endplay)
			self.menubar.add_widget(btn_cut)
		if self.can_replay:
			btn_replay = Button(text='replay')
			btn_replay.bind(on_press=self.replay)
			self.menubar.add_widget(btn_replay)
		self.menubar.pos = CSize(0,1.4)
		self.add_widget(self.menubar)

	def endplay(self,btn):
		self.vp.seek(1.0,precise=True)

	def replay(self,btn):
		self.vp.seek(0.0,precise=True)

	def hideMenu(self):
		self._popup.dismiss()
		self.remove_widget(self.menubar)
		self.menubar = None

	def audioswitch(self,btn):
		if self.ffplayer is not None:
			self.ffplayer.request_channel('audio')

	def setVolume(self,obj,v):
		self.vp.volume = v

	def mute(self,btn):
		if self.vp.volume > 0.001:
			self.old_volume = self.vp.volume
			self.vp.volume = 0.0
			btn.text = 'sound'
		else:
			self.vp.volume = self.old_volume
			btn.text = 'mute'

	def pause(self,t):
		if self.vp.state == 'play':
			self.vp.state = 'pause'
			self.btn_pause.text = 'play'
		else:
			self.vp.state = 'play'
			self.btn_pause.text = 'pause'

	def openfile(self,t):
		if self._popup is None:
			def vfilter(path,filename):
				vexts = ['.avi',
                                        '.mpg',
                                        '.mpe',
                                        '.mpeg',
                                        '.mlv',
                                        '.dat',
                                        '.mp4',
                                        '.flv',
                                        '.mov',
                                        '.rm',
                                        '.mkv',
                                        '.rmvb',
                                        '.asf',
                                        '.3gp'
				]
				for ext in vexts:
					if filename.endswith(ext):
						return True
				return False
			c = BoxLayout(orientation='vertical')
			self.file_chooser = FileChooserListView()
			self.file_chooser.filters = [vfilter]
			self.file_chooser.multiselect = True
			self.file_chooser.path = self.old_path
			self.file_chooser.bind(on_submit=self.loadFilepath)
			c.add_widget(self.file_chooser)
			b = BoxLayout(size_hint_y=None,height=35)
			c.add_widget(b)
			cancel = Button(text='Cancel')
			cancel.bind(on_press=self.cancelopen)
			load = Button(text='load')
			load.bind(on_press=self.playfile)
			b.add_widget(load)
			b.add_widget(cancel)
			self._popup = Popup(title='Open file',content=c,size_hint=(0.9,0.9))
		self._popup.open()

	def cancelopen(self,obj):
		self.hideMenu()

	def loadFilepath(self,obj,fpaths,evt):
		print('fp=',fpaths,type(fpaths),'evt=',evt)
		self.hideMenu()
		self.playlist = fpaths
		self.curplay = 0
		self.vp.source = self.playlist[self.curplay]
		self.vp.state = 'play'

	def playfile(self,obj):
		print('obj')
		self.hideMenu()
		self.playlist = []
		for f in self.file_chooser.selection:
			fp = os.path.join(self.file_chooser.path,f)
			self.playlist.append(fp)
		self.curplay = 0
		self.vp.source = self.playlist[self.curplay]
		self.vp.state = 'play'
			
if __name__ == '__main__':
	class MyApp(App):
		def build(self):
			vf = None
			if len(sys.argv) > 1:
				vf = sys.argv[1:]
			self.player = VPlayer(vfile=vf,
				loop=True,
				can_openfile=True,
				can_move = True,
				can_cut=True,
				can_replay=True,
				can_changevolume = True
			)
			return self.player

	MyApp().run()
