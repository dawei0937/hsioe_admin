#-*- coding:utf-8 -*-
#!/usr/bin/env python

"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    平台入口
"""
import bottle
import json
import random
import subprocess
import redis
import os
import sys
import logging
from i18n.i18n import initializeWeb
from config.consts import *
from common import web_util,log_util
from common.install_plugin import install_redis_plugin,install_session_plugin

#############################################
# 初始化bottle框架相关参数
#############################################
# 获取当前main.py文件所在服务器的绝对路径
program_path = os.path.split(os.path.realpath(__file__))[0]
#将路径添加的bottle变量中
sys.path.append(program_path)
# 让提交数据最大改为2M（如果想上传更多的文件，可以在这里进行修改）
bottle.BaseRequest.MEMFILE_MAX = 1024 * 1024 * 2
#############################################
# 初始化日志相关参数
#############################################
# 如果日志目录log文件夹不存在，则创建日志目录
if not os.path.exists('log'):
    os.mkdir('log')
# 初始化日志目录路径
log_path = os.path.join(program_path, 'log')
# 定义日志输出格式与路径
logging.basicConfig(level=logging.INFO,
                     format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                     filename="%s/ds_info.log" % log_path,
                     filemode='w+')
#实例化语言包
initializeWeb()

#############################################
# 初始化模版相关
#############################################
bottle.TEMPLATE_PATH.append('server/template/%s'%('default'))
random.seed()
#主应用
main_app = bottle.default_app()
# #从json中读取配置文件
with open(CONFIG_FILE) as f:
    main_app.config.load_dict(json.load(f))

#安装插件
install_redis_plugin(main_app)
install_session_plugin(main_app)

@main_app.get('/<res_path:path>')
def content_path(res_path):
    '''
     @description: 设置资源文件路径
    '''
    #支持跨域请求
    bottle.response.add_header('Conten-Type','application/octet-stream')
    return bottle.static_file(res_path,root='server/static/')

if main_app.config.get('download_view', 1):
    """ 是否开放下载 """
    @main_app.get('/download/<res_path:path>')
    def download_path(res_path):
        '''
        @description:               是否允许下载
        '''
        return bottle.static_file(res_path,root='server/static/download', download=True)
