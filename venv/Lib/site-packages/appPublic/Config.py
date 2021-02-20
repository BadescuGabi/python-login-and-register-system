# Config.py
# Copyright (c) 2009 longtop Co.
# See LICENSE for details.
# author: yumoqing@gmail.com
# created date: 2009-02-01
# last modified date: 2009-02-05

import os,sys
from appPublic.ExecFile import ExecFile
from appPublic.dictObject import DictObject
from appPublic.Singleton import Singleton
from zope.interface import implements
CONFIG_FILE = 'conf/config.ini'
from folderUtils import ProgramPath
class Node(object) :
    pass

class Config:

    __metaclass = Singleton
    def __init__(self,configpath=None):
        if configpath is None:
            ps = CONFIG_FILE.split('/')
            configpath = os.path.join(ProgramPath(),*ps)
        self.configfile = configpath
        self.__execfile = ExecFile(self,path=configpath)
        self.__execfile.set('Node',Node)
        self.__execfile.set('DictObject',DictObject)
        self.__execfile.set('dict',DictObject)
        r,msg = self.__execfile.run()
        if not r:
            print(r,msg)

def getConfig(path=None):
    conf = Config(path)
    return conf
    
