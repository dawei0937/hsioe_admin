#-*- coding:utf-8 -*-
#!/usr/bin/env python

"""
Author : $Author$
Date   : $Date$
Revision:$Revision$

Description:
    后台用户验证模块
"""
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from bottle import request,abort,template,response,redirect
from admin import admin_app
from config.consts import *
from common.utilt import *
from common import web_util
from common.validcode import create_validate_code
from common import web_util,encrypt_util
from datetime import datetime
import hashlib
import md5
from web_db_define import *
from model.agentModel import *

@admin_app.get('/login')
def getLoginPage(redis,session):
    """ 后台登录接口 """
    lang = getLang()

    info = {
                    'vcodeUrl'               :           BACK_PRE+'/vcode',
                    'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH,
                    'submitUrl'              :           BACK_PRE+'/login',
                    'account'                :       '',
                    'passwd'                 :       '',
    }
    return template('admin_login',info=info,lang=lang,message='',RES_VERSION=RES_VERSION)

@admin_app.post('/login')
def do_login(redis,session):
    lang = getLang()
    fields = {
        ('userName','用户名','is_strip=True,is_check_null=True'),
        ('password','密码','is_strip=True,is_check_null=True'),
        ('code','验证码','is_strip=True,is_check_null=True')
    }

    for field in fields:
        exec('%s = web_util.get_form("%s","%s","%s")'%(field[0],field[0],field[1],field[2]))

    info = {
            'title'                  :           '管理员登录',
            'submitUrl'              :           BACK_PRE+'/login',
            'account'                :           userName,
            'passwd'                 :           password,
            'vcodeUrl'               :           BACK_PRE+'/vcode',
            'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH,
    }

    try:
        if code.upper() != session['maj_vcode'].upper():
            return web_util.return_msg(-1011,'验证码不正确',{})
    except:
        return web_util.return_msg(-1012,'验证码已过期,请刷新验证码重试',{})

    agentId = getAgentId(redis,userName)
    adminTable = AGENT_TABLE%(agentId)

    # log_debug('[Try login] account[%s] password[%s] adminTable[%s]'%(account,passwd,adminTable))
    if not redis.exists(adminTable):
        return web_util.return_msg(-1000,'帐号或密码错误,请重新尝试.',{})

    adminPasswd,valid,agent_type = redis.hmget(adminTable,('passwd','valid','type'))

    if  adminPasswd != encrypt_util.to_sha256(password):
        #记录登录日志
        agentOpLog(redis,userName,2,web_util.get_ip())
        return web_util.return_msg(-1001,'密码错误,请重新输入',{})

    if valid != '1':
        return web_util.return_msg(-1002,'该帐号已被冻结,请联系管理员.',{})

    if agent_type == '1':
        redis.sadd(AGENT2ACCESS%(agentId),'/admin/agent/open_auth')

    #更新登录IP和登陆日期
    session['lastLoginIp'], session['lastLoginDate'],session['type'] = \
        redis.hmget(adminTable, ('lastLoginIp', 'lastLoginDate','type'))

    curTime = datetime.now()
    redis.hmset(adminTable, {
        'lastLoginIp'     :   request.remote_addr,
        'lastLoginDate'   :   curTime.strftime("%Y-%m-%d %H:%M:%S")
    })

    #记录session信息
    session['account'] = userName
    session['id'] = agentId
    #重新生成权限
    getNewAccess(redis,agentId)
    session['access'] = str(redis.smembers(AGENT2ACCESS%(agentId)))
    #记录登录日志
    agentOpLog(redis,userName,1,request.remote_addr)
    return {'code':0,'msg':'登录成功','jumpUrl':BACK_PRE}

@admin_app.get('/vcode')
def changeVerfiyCode(session):
    """ 验证码接口 """
    # if checkServiceOutDate(redis):
    #     return ''
    img, vcode = create_validate_code()
    session['maj_vcode'] = vcode.upper()

    mstream = StringIO()
    img.save(mstream, "GIF")
    response.set_header('Content-Type', 'image/gif')
    return mstream.getvalue()
