# coding=utf-8
"""
Automation client for automatesocket.py
=======================================

"""

import socket
import struct
import json
import base64
import sys
from time import time, sleep
from os.path import join
from os import getcwd

_connect_info = ("localhost", 7777)


def _dprint(msg):
    sys.stdout.write(msg)
    sys.stdout.flush()


def _recvall(sock, size):
    msg = ""
    while len(msg) < size:
        packet = sock.recv(size - len(msg))
        if not packet:
            return None
        msg += packet
    return msg


def interact(*args):
    """Manually send a command to the connected socket
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(_connect_info)
    try:
        msg = json.dumps(args)
        size = len(msg)
        sock.sendall(struct.pack("I", size))
        sock.sendall(msg)
        msgsize = _recvall(sock, struct.calcsize("I"))
        if not msgsize:
            return None
        size = struct.unpack("I", msgsize)[0]
        msgdata = _recvall(sock, size)
        return json.loads(msgdata)
    finally:
        sock.close()


def connect(host="localhost", port=7777, timeout=10):
    global _connect_info
    _dprint("Connecting to {}:{}... ".format(host, port))
    _connect_info = (host, port)
    start = time()
    while True:
        try:
            if interact("ping") is True:
                _dprint("ok\n")
                return
            if time() - start > timeout:
                _dprint("timeout\n", fatal=True)
                raise Exception("Connection timeout")
        except:
            sleep(.1)


def wait(cond="True", timeout=-1):
    _dprint("Wait condition '{}'... ".format(cond))
    ret = interact("wait", cond, timeout)
    _dprint("ok (result={})\n".format(ret))
    return ret


def screenshot(name="screenshot", suffix=None, outdir=None):
    filename = u"{name}{suffix}.png".format(
        name=name, suffix=u"-{}".format(suffix) if suffix else "")
    filename = join(outdir or getcwd(), filename)
    _dprint(u"Screenshot ({})... ".format(filename))
    width, height, data = interact("screenshot")
    data = base64.decodestring(data)
    with open(filename, "wb") as fd:
        fd.write(data)
    _dprint("ok\n")


def quit():
    _dprint("Quit the application... ")
    interact("quit")
    _dprint("ok\n")


def execute(cmd):
    return interact("execute", cmd)


class spawn(object):
    def __init__(self, *args):
        self.args = args

    def __enter__(self):
        import subprocess
        self.process = subprocess.Popen(self.args)

    def __exit__(self, *args):
        self.process.terminate()
        self.process.wait()


if __name__ == "__main__":
    connect()
    wait("app.screen_manager.current == 'welcome'")
    wait("app.screen_manager.current_screen.transition_progress == 1")
    screenshot()
    quit()
