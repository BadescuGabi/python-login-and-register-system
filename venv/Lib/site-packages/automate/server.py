# coding=utf-8
"""
Automation server
=================

Right now, just import this file from your main.py, if you want to use the automateclient.py.
No configuration needed.
"""

import socket
import struct
import threading
import json
import base64
import os
from time import time

COMMAND_SIZE = struct.calcsize("I")
COMMANDS = {}


def command(f):
    COMMANDS[f.__name__] = f


@command
def screenshot(*args):
    """Do a screenshot of the window, and return it as a PNG:
    (width, height, "RGBA", base64-data)
    """
    from kivy.clock import mainthread
    _result = []
    _event = threading.Event()

    @mainthread
    def _real_screenshot():
        import tempfile
        from kivy.core.window import Window
        try:
            fd = tempfile.NamedTemporaryFile(suffix=".png", delete=False)
            # XXX hack, Window.screenshot doesn't respect our filename
            screenshot_fn = fd.name.rsplit(".")[-2] + "0001.png"
            fd.close()
            width, height = Window.size
            Window.screenshot(name=fd.name)
            with open(screenshot_fn, "rb") as fd:
                data = fd.read()
            _result[:] = [width, height, base64.encodestring(data)]
        except:
            import traceback
            traceback.print_exc()
        finally:
            try:
                os.unlink(screenshot_fn)
                os.unlink(fd.name)
            except:
                pass
            _event.set()

    _real_screenshot()
    _event.wait()
    return _result


@command
def execute(cmd):
    """Execute a random string in the app context
    """
    from kivy.clock import mainthread
    _result = [None]
    _event = threading.Event()

    @mainthread
    def _real_execute():
        from kivy.app import App
        app = App.get_running_app()
        idmap = {"app": app}
        try:
            exec cmd in idmap, idmap
        except Exception as e:
            _result[:] = [u"{}".format(e)]
        _event.set()

    _real_execute()
    _event.wait()
    return _result[0]


@command
def wait(cond, timeout=-1):
    """Wait a condition unless timeout happen
    """
    from kivy.app import App
    from kivy.clock import Clock
    _result = [None]
    _event = threading.Event()
    _start = time()

    def _real_wait(*args):
        try:
            app = App.get_running_app()
            idmap = {"app": app}
            if eval(cond, idmap):
                _result[:] = [True]
                _event.set()
                return False
        except:
            pass

        if timeout == -1:
            return

        if time() - _start > timeout:
            _result[:] = [False]
            _event.set()
            return False

    Clock.schedule_interval(_real_wait, .1)
    _event_timeout = None if timeout == -1 else timeout
    try:
        _event.wait(_event_timeout)
    except:
        pass
    Clock.unschedule(_real_wait)
    return _result[0]


@command
def ping():
    return True


@command
def quit():
    from kivy.app import App
    from kivy.clock import Clock

    def _real_quit(*args):
        App.get_running_app().stop()

    Clock.schedule_once(_real_quit, 0)
    return True


def recvall(sock, size):
    msg = ""
    while len(msg) < size:
        print size, len(msg)
        packet = sock.recv(size - len(msg))
        if not packet:
            return None
        msg += packet
    return msg


def run_automate_socket():
    netloc = ("0.0.0.0", 7777)
    servsock = socket.socket()
    servsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, True)
    servsock.bind(netloc)
    servsock.listen(5)

    while True:
        sock, _ = servsock.accept()

        # size of the command
        try:
            size = struct.unpack("I", recvall(sock, struct.calcsize("I")))[0]
            data = recvall(sock, size)
            args = json.loads(data)

            cmd, args = args[0], args[1:]
            result = COMMANDS[cmd](*args)
            data = json.dumps(result)

            sock.sendall(struct.pack("I", len(data)))
            sock.sendall(data)

        except:
            import traceback
            traceback.print_exc()
        finally:
            sock.close()


automate_thread = threading.Thread(target=run_automate_socket)
automate_thread.daemon = True
automate_thread.start()
