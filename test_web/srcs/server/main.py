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
from create_server import makeHsioeServer
from i18n.i18n import initializeWeb
#实例化语言包
initializeWeb()
#初始化应用
hsioe = makeHsioeServer(bottle.default_app())#bottle.default_app()
#设置bottle的最大文件上传内容
hsioe.set_memfile_max(1024*1024*2)
hsioe.set_template_path('server/template/%s'%('default'))
#初始化app
hsioe._init_app()

@hsioe.app.error(404)
def get_error_404(code):
    """ 返回404 """
    return 'not found'

@hsioe.app.error(500)
def get_error_500(code):
    """ 返回500 """
    return "Server Error"

@hsioe.app.get('/<res_path:path>')
def content_path(res_path):
    '''
     @description: 设置资源文件路径
    '''
    #支持跨域请求
    bottle.response.add_header('Conten-Type','application/octet-stream')
    return bottle.static_file(res_path,root='server/static/')

if hsioe.app.config.get('download_view', 1):
    """ 是否开放下载 """
    @hsioe.app.get('/download/<res_path:path>')
    def download_path(res_path):
        '''
        @description:               是否允许下载
        '''
        return bottle.static_file(res_path,root='server/static/download', download=True)
