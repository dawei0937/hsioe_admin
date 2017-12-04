#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    DB初始化
"""

import sys
sys.path.insert(0, 'server_common')
sys.path.insert(0, 'mahjong')
from web_db_define import *
from datetime import datetime,time
from admin import access_module
from config.consts import *
import redis
import hashlib

def getInst(dbNum):
    global redisdb
    redisdb = redis.ConnectionPool(host="192.168.0.99", port=6379, db='1', password='Fkkg65NbRwQOnq01OGMPy5ZREsNUeURm')
    return redis.Redis(connection_pool=redisdb)

redis = getInst(1)

#初始化管理账号
curTime = datetime.now()
pipe = redis.pipeline()

sysid = 1
# id


"""
    配置代理名称和房卡
    代理名称            ：       房卡数
"""
print 'clean login pool...............'
print redis.sadd(FORMAT_LOGIN_POOL_SET,'test')
print redis.smembers(FORMAT_LOGIN_POOL_SET)
print redis.srem(FORMAT_LOGIN_POOL_SET,'test')
print redis.smembers(FORMAT_LOGIN_POOL_SET)
#redis.delete(FORMAT_LOGIN_POOL_SET)
print 'clean success.......'
