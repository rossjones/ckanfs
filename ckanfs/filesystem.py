import logging
import requests

from os import getuid, getgid

from stat import S_IFDIR, S_IFREG
from errno import ENOENT
from time import time
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn

from .proxies import Factory


class CKANFilesystem(LoggingMixIn, Operations):
    def __init__(self, ckan_host):
        self.uid = getuid()
        self.gid = getgid()
        self.factory = Factory(ckan_host)

    def getattr(self, path, fh=None):
        p = self.factory.build_proxy(path)
        return p.attributes()

    def statfs(self, path):
        return {
            "f_namemax": 255,
            "f_frsize": 2048,
            "f_bsize": 4096,
            "f_flag": 1,  # ST_RDONLY
        }

    def read(self, path, size, offset, fh):
        p = self.factory.build_proxy(path)
        return p.data(offset, size)

    def readdir(self, path, fh):
        p = self.factory.build_proxy(path)
        return [".", ".."] + p.names()

