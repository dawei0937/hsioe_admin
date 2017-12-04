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
                     filemode='a')
#实例化语言包
initializeWeb()

#############################################
# 初始化模版相关
#############################################
bottle.TEMPLATE_PATH.append('mahjong/template/%s'%(TEMPLATE_NAME))
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
    return bottle.static_file(res_path,root='mahjong/static/')

if main_app.config.get('download_view', 1):
    """ 是否开放下载 """
    @main_app.get('/download/<res_path:path>')
    def download_path(res_path):
        '''
        @description:               是否允许下载
        '''
        return bottle.static_file(res_path,root=DOWNLOAD_PATH, download=True)

if main_app.config.get('admin_view', 1):
    """ 后台允许访问接口 """
    from admin import admin_app
    main_app.mount('/admin',admin_app)

if main_app.config.get('hall_view',1):
    """ 挂载麻将大厅接口 """
    from hall import hall_app
    main_app.mount('/hall',hall_app)

if main_app.config.get('fish_view',1):
    """ 挂载捕鱼大厅接口 """
    from fish import fish_app
    main_app.mount('/fish',fish_app)

@bottle.hook('before_request')
def validate():
    """使用勾子处理接口访问事件"""
    # 获取当前访问的Url路径
    path_info = bottle.request.environ.get("PATH_INFO")
    # 过滤不用做任何操作的路由（即过滤不用进行判断是否登录和记录日志的url）
    if path_info in ['/favicon.ico', '/', '/api/verify/']:
        return
    ### 记录客户端提交的参数 ###
    # 获取当前访问url路径与ip
    request_log = 'url:' + path_info + ' ip:' + web_util.get_ip()
    try:
        # 添加json方式提交的参数
        if request.json:
            request_log = request_log + ' params(json):' + urllib.parse.unquote(str(request.json))
    except:
        pass
    try:
        # 添加GET方式提交的参数
        if bottle.request.query_string:
            request_log = request_log + ' params(get):' + urllib.parse.unquote(str(request.query_string))
        # 添加POST方式提交的参数
        if request.method == 'POST':
            request_log = request_log + ' params(post):' + urllib.parse.unquote(str(request.params.__dict__))
        # 存储到日志文件中
        log_util.info(request_log)
    except:
        pass

    # 处理ajax提交的put、delete等请求转换为对应的请求路由（由于AJAX不支持RESTful风格提交，所以需要在这里处理一下，对提交方式进行转换）
    if bottle.request.method == 'POST' and bottle.request.POST.get('_method'):
        bottle.request.environ['REQUEST_METHOD'] = bottle.request.POST.get('_method', '')

    # 过滤不用进行登录权限判断的路由（登录与退出登录不用检查是否已经登录）
    url_list = ["/api/login/", "/api/logout/"]
