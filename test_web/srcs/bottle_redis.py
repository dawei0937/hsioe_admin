# -*-coding:utf8-*-

#!/usr/bin/env python
#-*-coding:utf-8 -*-

"""
@Author: $Author$
@Date: $Date$
@version: $Revision$

Description:
     Description
"""
import redis
import inspect
from bottle import default_app
from common.log import *

class RedisPlugin(object):
    name = 'redis'

    def __init__(self,host="",port="",database="",keyword='redis',pwd=""):
        conf = default_app().config
        self.host = str(conf.get('redis.host', host))
        self.port = conf.get('redis.port', port)
        self.database = conf.get('redis.database', database)
        self.keyword = str(conf.get('redis.keyword', keyword))
        self.pwd  = str(conf.get('redis.passwd',pwd))
        self.redisdb = None

    def setup(self,app):
        for other in app.plugins:
            if not isinstance(other,RedisPlugin): continue
            if other.keyword == self.keyword:
                raise PluginError("Found another redis plugin with "\
                        "conflicting settings (non-unique keyword).")

        if self.redisdb is None:  #主库
            self.redisdb = redis.ConnectionPool(host=self.host, port=self.port, db=self.database, password=self.pwd)


    def apply(self,callback,context):
        args = inspect.getargspec(context['callback'])[0]
        if self.keyword not in args:
            return callback

        def wrapper(*args,**kwargs):
            kwargs[self.keyword] = redis.Redis(connection_pool=self.redisdb)
            #log_debug('[redis][Instance] connection_read_pool[%s]'%(kwargs[self.keyword].connection_read_pool))
            rv = callback(*args, **kwargs)
            return rv
        return wrapper

Plugin = RedisPlugin
