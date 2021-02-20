# coding=utf-8

import automate
from os.path import dirname, join, exists, realpath
from os import getcwd

# install or replace a automateserver.py in the current directory
server_fn = realpath(join(automate.__path__[0], "server.py"))
automateserver_fn = realpath(join(getcwd(), "automateserver.py"))
print("Install automateserver.py in {}".format(automateserver_fn))
with open(server_fn, "r") as fd:
    server_content = fd.read()
with open(automateserver_fn, "w") as fd:
    fd.write(server_content)
