#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    this is Description
"""

from bottle import *
from admin import admin_app
from config.consts import STATIC_LAYUI_PATH,STATIC_ADMIN_PATH,BACK_PRE,RES_VERSION
import access_module
from model.agentModel import *
from common.utilt import *
from common.log import *
import subprocess



#后台首页
import time
import os
import md5

CREATE_PAGE_TIME = 60*10
@admin_app.get('/')
@checkLogin
def getAdminPage(redis,session):

    #是否第一次登录
    #log_debug('[INDEX][url:/] compare time_stamp[%s] sessionTime[%s]'%(time_stamp,session['time_stamp']))
    lang = getLang()
    curTime = datetime.now()
    myAccesses = eval(session['access'])
    agentInfo = redis.hgetall(AGENT_TABLE%(session['id']))
    mainModules = []
    # 一级菜单定位
    i= -1
    # 二级菜单定位
    j= -1
    for accessObj in access_module.MENU_MODULES:
        test = {}
        test['1'] = accessObj.url

        if accessObj.check and (accessObj.url in myAccesses):
            i+=1
            # 重置二级菜单定位
            j=-1
            mainModule = {}
            mainModule['url'] = accessObj.url
            mainModule['txt'] = accessObj.getTxt(lang)
            mainModule['subModules'] = []
            mainModules.append(mainModule)

        elif len(accessObj.tree) != 2 and (accessObj.url in myAccesses):
            j+=1
            subModule = {}
            subModule['url'] = accessObj.url
            subModule['txt'] = accessObj.getTxt(lang)
            subModule['subsubModules'] = []
            mainModules[i]['subModules'].append(subModule)
        elif len(accessObj.tree) == 2 and (accessObj.url in myAccesses):
            if j==-1:
                subModule = {}
                subModule['url'] = accessObj.url
                subModule['txt'] = accessObj.getTxt(lang)
                subModule['subsubModules'] = []
                mainModules[i]['subModules'].append(subModule)
            else:
                subsubModule = {}
                subsubModule['url'] = accessObj.url
                subsubModule['txt'] = accessObj.getTxt(lang)
                mainModules[i]['subModules'][j]['subsubModules'].append(subsubModule)

    if int(agentInfo['type']) in [SYSTEM_ADMIN]:
        roomcard = '无限制'
    else:
        roomcard = agentInfo['roomcard']

    try:
        open_auth = int(agentInfo['open_auth'])
    except:
        open_auth = 0

    open_auth_text = OPENAUTH_2_TXT[open_auth]
    if int(agentInfo['type']) != 0:
        parentId = agentInfo['parent_id']
        parentAccount = redis.hget(AGENT_TABLE%(parentId),'account')
    else:
        parentId=''
        parentAccount=''

    info = {
        'STATIC_ADMIN_PATH'     :   STATIC_ADMIN_PATH,
        'ADMIN_DEFAULT_PAGE'    :   '/admin/home',
        'agentType'             :   int(agentInfo['type']),
        'parentId'              :   parentId,
        'parentAccount'         :   parentAccount,
        'open_auth_text'        :   open_auth_text,
        'link_fish_url'         :   '/admin/fish',
        'link_fish_txt'         :   '捕鱼管理',
        'show_card_bar'         :   True
    }

    index_tpl = template('admin_base',info=info,roomcard=roomcard,RES_VERSION=RES_VERSION,lang=lang,\
                          session=session,agentInfo=agentInfo,TYPE2TXT=lang.TYPE_2_ADMINTYPE,mainModules=mainModules)

    return index_tpl

@admin_app.get('/home')
def getSystemInfoPage(redis,session):
    """
        系统配置信息页面
    """
    lang = getLang()
    selfUid = session['id']
    curTime = datetime.now()
    # 当日注册人数
    registByday =  redis.scard(FORMAT_REG_DATE_TABLE%(curTime.strftime('%Y-%m-%d')))
    if selfUid == 1:
        # 总注册人数
        memberTotal = redis.scard(ACCOUNT4WEIXIN_SET)
        # 当日活跃数
        loginByday = redis.get(DAY_ALL_LOGIN_COUNT%(curTime.strftime('%Y-%m-%d')))
        # 当日耗卡数
        playRoomByday = redis.get(DAY_ALL_PLAY_ROOM_CARD%(curTime.strftime('%Y-%m-%d')))

    else:
        memberTotal = getAgentMemberTotal(redis,session['id'])
        # 当日注册人数
        #registByday =  redis.scard(FORMAT_REG_DATE_TABLE%(curTime.strftime('%Y-%m-%d')))
        # 当日活跃数
        loginByday = getAgentMemberLogin(redis,session['id'],curTime.strftime('%Y-%m-%d'))
        # 当日耗卡数
        playRoomByday = getAgentRoomByDay(redis,session['id'],curTime.strftime('%Y-%m-%d'))

    info    =   {
                    'title'                  :           '首页',
                    'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH,
                    'memberTotal'            :           memberTotal,
                    'loginByday'             :           loginByday if loginByday else 0,
                    'registByday'            :           registByday if registByday else 0,
                    'playRoomByday'          :           playRoomByday if playRoomByday else 0,
    }

    return template('admin_home',info=info,lang=lang,session=session,RES_VERSION=RES_VERSION)

@admin_app.get('/showDetail')
def get_show_detail(redis,session):
    """
    获取7日的数据变化
    """
    week_date_lists = get_week_date_list()
    login_count_list,take_count_list,reg_count_list = [],[],[]
    for week_date in week_date_lists:
        reg_count_list.append(redis.scard(FORMAT_REG_DATE_TABLE%(week_date)))
        take_count = redis.get(DAY_ALL_PLAY_ROOM_CARD%(week_date))
        if not take_count:
            take_count = 0
        take_count = int(take_count)
        take_count_list.append(take_count)
        login_count = redis.get(DAY_ALL_LOGIN_COUNT%(week_date))
        if not login_count:
            login_count = 0
        login_count = int(login_count)
        login_count_list.append(login_count)

    return {'code':1,'week':week_date_lists,'reg_list':reg_count_list,'login_list':login_count_list,'take_list':take_count_list}



@admin_app.get('/checkAdminOL')
def checkAdminOl(redis,session):
    """
    检测是否超时
    """
    if session.get('account',None):
        return {'code':1}

    return {'code':0,'msg':'长时间未操作或该账号在其他地方登陆'}

@admin_app.get('/logout')
def getLogout(redis,session):
    """
    后台管理登出
    """
    curTime = datetime.now()
    agent_account = session['account']
    agent_id      = session['id']

    session['account'],session['id'],session['time_stamp'],session['index_path'] = '','',None,None

    log_debug('[%s][logout][info] user[%s] has logout.'%(curTime,agent_account))

    return redirect(BACK_PRE+'/login')
