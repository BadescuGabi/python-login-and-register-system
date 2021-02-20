
from kivy.logger import Logger
import asyncio

from kivy.app import App
import kivy.base

from kivy.config import Config
from kivy.utils import platform
from kivy.clock import Clock
from kivy.event import EventDispatcher
from kivy.lang import Builder
from kivy.context import register_context

from kivy.base import EventLoopBase, ExceptionManager
from kivy.base import EventLoop, stopTouchApp
from kivy.config import ConfigParser
from kivy.uix.widget import Widget
from kivy.core.window.window_pygame import WindowPygame,  pygame
from kivy.core.window.window_sdl2 import WindowSDL  
# from kivy.core.window.window_x11 import WindowX11
# from kivy.core.window.window_egl_rpi import WindowEglRpi

def eventloopbase_run(self):
	def _run():
		if not self.quit:
			self.loop.call_later(0.01,_run)
		self.idle()
	_run()

			
def _run_mainloop():
	def timing_loop():
		if not EventLoop.quit and EventLoop.status == 'started':
			EventLoop.loop.call_later(0.01,timing_loop)
		else:
			stopTouchApp()
		try:
			EventLoop.run()
		except BaseException as inst:
			# use exception manager first
			print(f'{__file__}:_run_mainloop() error-----')
			r = ExceptionManager.handle_exception(inst)
			if r == ExceptionManager.RAISE:
				stopTouchApp()
				raise
			else:
				pass

	timing_loop()


def pygame_mainloop(self):
	def timing_loop():
		if not EventLoop.quit and EventLoop.status == 'started':
			EventLoop.loop.call_later(0.01,timing_loop)
		try:
			self._mainloop()
			if not pygame.display.get_active():
				pygame.time.wait(100)
		except BaseException as inst:
			# use exception manager first
			print('-------error here------- ')
			r = ExceptionManager.handle_exception(inst)
			if r == ExceptionManager.RAISE:
				stopTouchApp()
				raise
			else:
				pass

	timing_loop()		
		
def uni_mainloop(self):
	def timing_loop():
		if not EventLoop.quit and EventLoop.status == 'started':
			EventLoop.loop.call_later(0.01,timing_loop)
		else:
			Logger.info("WindowSDL: exiting mainloop and closing.")
			self.close()
		try:
			self._mainloop()
		except BaseException as inst:
			# use exception manager first
			r = ExceptionManager.handle_exception(inst)
			if r == ExceptionManager.RAISE:
				stopTouchApp()
				raise
			else:
				pass

	timing_loop()

def runTouchApp(widget=None, slave=False):
	'''Static main function that starts the application loop.
	You can access some magic via the following arguments:

	:Parameters:
		`<empty>`
			To make dispatching work, you need at least one
			input listener. If not, application will leave.
			(MTWindow act as an input listener)

		`widget`
			If you pass only a widget, a MTWindow will be created
			and your widget will be added to the window as the root
			widget.

		`slave`
			No event dispatching is done. This will be your job.

		`widget + slave`
			No event dispatching is done. This will be your job but
			we try to get the window (must be created by you beforehand)
			and add the widget to it. Very useful for embedding Kivy
			in another toolkit. (like Qt, check kivy-designed)

	'''

	from kivy.input import MotionEventFactory, kivy_postproc_modules

	# Ok, we got one widget, and we are not in slave mode
	# so, user don't create the window, let's create it for him !
	if widget:
		EventLoop.ensure_window()

	# Instance all configured input
	for key, value in Config.items('input'):
		Logger.debug('Base: Create provider from %s' % (str(value)))

		# split value
		args = str(value).split(',', 1)
		if len(args) == 1:
			args.append('')
		provider_id, args = args
		provider = MotionEventFactory.get(provider_id)
		if provider is None:
			Logger.warning('Base: Unknown <%s> provider' % str(provider_id))
			continue

		# create provider
		p = provider(key, args)
		if p:
			EventLoop.add_input_provider(p, True)

	# add postproc modules
	for mod in list(kivy_postproc_modules.values()):
		EventLoop.add_postproc_module(mod)

	# add main widget
	if widget and EventLoop.window:
		if widget not in EventLoop.window.children:
			EventLoop.window.add_widget(widget)

	# start event loop
	Logger.info('async Base: Start application main loop')
	EventLoop.start()

	# remove presplash on the next frame
	if platform == 'android':
		Clock.schedule_once(EventLoop.remove_android_splash)

	# we are in a slave mode, don't do dispatching.
	if slave:
		return

	# in non-slave mode, they are 2 issues
	#
	# 1. if user created a window, call the mainloop from window.
	#	This is due to glut, it need to be called with
	#	glutMainLoop(). Only FreeGLUT got a gluMainLoopEvent().
	#	So, we are executing the dispatching function inside
	#	a redisplay event.
	#
	# 2. if no window is created, we are dispatching event loop
	#	ourself (previous behavior.)
	#
	try:
		if EventLoop.window is None:
			Logger.info('async:_run_mainloop() calling..')
			_run_mainloop()
			Logger.info('async:_run_mainloop() finished..')
		else:
			Logger.info('async:mainloop() calling..')
			EventLoop.window.mainloop()
			Logger.info('async:mainloop() finished..')
	finally:
		pass

def asyncPatch(loop=None):
	kivy.base.EventLoop.loop = asyncio.get_event_loop() if loop is None else loop
	kivy.base.runTouchApp = runTouchApp
	EventLoopBase.run = eventloopbase_run
	kivy.base._run_mainloop = _run_mainloop
	WindowPygame.mainloop = pygame_mainloop
	WindowSDL.mainloop = uni_mainloop
	# WindowX11.mainloop = uni_mainloop
	# WindowEglRpi.mainloop = uni_mainloop

def wait_coro(func,*args,**kw):
	task = asyncio.Task(func(*args,**kw))
	ret = asyncio.wait(task)
	return ret

class AsyncApp(App):
	def __init__(self,loop=None,**kw):
		super(AsyncApp,self).__init__(**kw)
		self.loop = asyncio.get_event_loop() if loop is None else loop

	def run(self):
		def check_stop():
			if not EventLoop.quit and EventLoop.status == 'started':
				self.loop.call_later(0.01,check_stop)
			else:
				self.stop()
				self.loop.stop()

		asyncPatch(loop=self.loop)
		if not self.built:
			self.load_config()
			self.load_kv(filename=self.kv_file)
			root = self.build()
			if root:
				self.root = root
		if self.root:
			if not isinstance(self.root, Widget):
				Logger.critical('App.root must be an _instance_ of Widget')
				raise Exception('Invalid instance in App.root')
			from kivy.core.window import Window
			Window.add_widget(self.root)

		# Check if the window is already created
		from kivy.base import EventLoop
		window = EventLoop.window
		if window:
			self._app_window = window
			window.set_title(self.get_application_name())
			icon = self.get_application_icon()
			if icon:
				window.set_icon(icon)
			self._install_settings_keys(window)
		else:
			Logger.critical("Application: No window is created."
							" Terminating application run.")
			return

		self.dispatch('on_start')
		runTouchApp()
		check_stop()
		self.loop.run_forever()
