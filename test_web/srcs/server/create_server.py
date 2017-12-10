#-*- coding:utf-8 -*-
#!/usr/bin/env python

"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
     server初始化
"""
from bottle import request,response,abort,hook
import bottle
from common.install_plugin import install_redis_plugin,install_session_plugin
from i18n.i18n import initializeWeb
from config import consts
import json
import logging
import os
import sys

class makeHsioeServer(object):
    """ 创建server应用类 """
    def __init__(self,app):
        self.app = app
        self.modules = (
            #可以配置的模块
        )

    def _init_app(self):
        self._install_plugin()
        self._init_config()
        self._init_log()
        self._init_before()
        self._init_all_modules()

    def _install_plugin(self):
        """ 初始化插件 """
        install_redis_plugin(self.app)
        install_session_plugin(self.app)

    def _init_config(self):
        """ 初始化配置 """
        with open(consts.CONFIG_FILE) as f:
            self.app.config.load_dict(json.load(f))

    def _init_log(self):
        """ 初始化日志文件 """
        #获取当前main.py文件所在服务器的绝对路径
        program_path = os.path.split(os.path.realpath(__file__))[0]
        #将路径添加的bottle变量中
        sys.path.append(program_path)
        #初始化日志目录路径
        log_path = os.path.join(program_path, 'log')
        #############################################
        # 如果日志目录log文件夹不存在，则创建日志目录
        if not os.path.exists(log_path):
            print 'xxxxxxxxx'
            os.mkdir(log_path,0755)

        logging.basicConfig(
               level=logging.DEBUG,
               format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
               filename="%s/ds_info.log" % log_path,
               filemode='w+'
        )

    def _init_before(self):
        @hook('before_request')
        def request_before():
            """ 访问前的钩子 """
            pass

    def _init_all_modules(self):
        """ 初始化所有模块 """
        if not self.modules:
            return
        pass

    def set_memfile_max(self,value):
        """ 设置bottle的上传文件大小 """
        if value and isinstance(value,int):
            bottle.BaseRequest.MEMFILE_MAX = value

    def set_template_path(self,path):
        """ 添加bottle的模版路径 """
        if path:
            bottle.TEMPLATE_PATH.append(path)
