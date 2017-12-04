#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    系统设置模块
"""
from bottle import *
from admin import admin_app
from config.consts import  STATIC_LAYUI_PATH,STATIC_ADMIN_PATH,BACK_PRE,PARTY_PLAYER_COUNT,RES_VERSION
from common.utilt import *
from common.log import *
from datetime import datetime
from web_db_define import ORDER2WEIXIN_SWITCH
from model.hallModel import *
import json


@admin_app.get('/setting/system')
def getSysSetting(redis,session):
    """
    系统设置页面
    """
    curTime = datetime.now()
    lang    = getLang()

    info = {
                'title'                  :           lang.SYSTEM_SETTING_TITLE_TXT,
                'settingUrl'             :           BACK_PRE+'/setting/system',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
    }

    """
    系统设置的参数列表
    [
        {'name':xxxx,'value':xxx,'desc':xxxx},
        {'name':xxxx,'value':xxx,'desc':xxxx},
        {'name':xxxx,'value':xxx,'desc':xxxx},
    ]
    """
    wechatSwitch = redis.get(ORDER2WEIXIN_SWITCH)
    if not wechatSwitch:
        wechatSwitch = 0
    gameServerUrl = redis.get(GAME_SERVER_URL)
    if not gameServerUrl:
        gameServerUrl = ''

    settings = [
    
         {'name':'wechatSwitch','title':'支付设置','value':wechatSwitch,'desc':'微信支付开关'},
         {'name':'gameServerUrl','title':'游戏服务域名','value':gameServerUrl,'desc':'游戏服务地址'}

    ]

    return template('admin_setting_system',info=info,lang=lang,settings=settings,RES_VERSION=RES_VERSION)

@admin_app.post('/setting/system')
def do_settingSystem(redis,session):
    """
    系统设置页面
    """
    curTime = datetime.now()

    #微信支付开关
    wechatSwitch = request.forms.get('wechatSwitch','').strip()
    gameServerUrl = request.forms.get('gameServerUrl','').strip()

    #print
    log_debug('[%s][settingSystem][info] wechatSwitch[%s]'%(curTime,wechatSwitch))

    pipe = redis.pipeline()
    try:
        if int(wechatSwitch) not in [0,1]:
            return {'code':1,'msg':'微信支付开关值只能为0或1'}
    except:
        wechatSwitch = 1
    
    try:
        pipe.set(ORDER2WEIXIN_SWITCH,int(wechatSwitch))
        pipe.set(GAME_SERVER_URL,gameServerUrl)
    except Exception,e:
        log_debug('[%s][settingSystem][error] setting error[%s]'%(curTime,e))
        return {'code':0,'msg':'设置配置失败'}

    pipe.execute()
    return {'code':1,'msg':'保存配置成功'}


@admin_app.get('/setting/hotUpDateSetting')
def getHotUpDataSetting(redis,session):
    """
    热更新设置配置
    """
    curTime = datetime.now()
    lang    = getLang()
    info = {
            'title'             :       '大厅热更新配置',
            'submitUrl'         :       BACK_PRE+'/setting/hotUpDateSetting',                
            'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
    }

    settingInfo = getHotSettingAll(redis)

    return template('admin_hotUpdate_setting',settingInfo=settingInfo,info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/setting/hotUpDateSetting')
def do_HotUpdate(redis,session):
    """
    热更新配置
    """
    curTime = datetime.now()

    lang = getLang()

    resVersion = request.forms.get('resVersion','').strip()
    minVersion = request.forms.get('minVersion','').strip()
    iosMinVersion = request.forms.get('iosMinVersion','').strip()
    downloadUrl = request.forms.get('downloadURL','').strip()
    IPAURL = request.forms.get('IPAURL','').strip()
    apkSize = request.forms.get('apkSize','').strip()
    apkMD5 = request.forms.get('apkMD5','').strip()
    hotUpdateURL = request.forms.get('hotUpdateURL','').strip()
    hotUpdateScriptsURL = request.forms.get('hotUpdateScriptsURL','').strip()
    updateAppStore1 = request.forms.get('updateAppStore1','').strip()
    updateAppStore2 = request.forms.get('updateAppStore2','').strip()
    updateAndroid = request.forms.get('updateAndroid','').strip()
    updateYYB = request.forms.get('updateYYB','').strip()
    packName = request.forms.get('packName','').strip()

    #log_debug
    log_debug('[%s][hotUpDateSetting][info] resVersion[%s] minVersion[%s] iosMinVersion[%s] downloadUrl[%s]'\
                    %(curTime,resVersion,minVersion,iosMinVersion,downloadUrl))

    checkNullField = [
            {'field':resVersion,'msg':'resVersion不能为空'},
            {'field':minVersion,'msg':'minVersion不能为空'},
            {'field':iosMinVersion,'msg':'iosMinVersion不能为空'},
            {'field':downloadUrl,'msg':'downloadUrl不能为空'},
            {'field':IPAURL,'msg':'IPAURL不能为空'},
            {'field':downloadUrl,'msg':'downloadUrl不能为空'},
            {'field':hotUpdateURL,'msg':'hotUpdateURL不能为空'},
            {'field':hotUpdateScriptsURL,'msg':'hotUpdateScriptsURL不能为空'}
    ]

    for check in checkNullField:
        if not check['field']:
            return {'code':1,'msg':check['msg']}

    updateHostSettingInfo = {

                'resVersion'        :       resVersion,
                'minVersion'        :       minVersion,
                'iosMinVersion'     :       iosMinVersion,
                'downloadURL'       :       downloadUrl,
                'IPAURL'            :       IPAURL,
                'apkSize'           :       apkSize,
                'hotUpdateURL'      :       hotUpdateURL,
                'hotUpdateScriptsURL'   :   hotUpdateScriptsURL,
                'updateAppStore1'    :       updateAppStore1,
                'updateAppStore2'    :       updateAppStore2,
                'updateAndroid'     :       updateAndroid,
                'updateYYB'         :       updateYYB,
                'packName'          :       packName,
                'lastUpTime'        :       curTime.strftime('%Y-%m-%d %H:%M:%S')
    }

    try:
        saveHotUpDateSetting(redis,updateHostSettingInfo)
    except:
        log_debug('[%s][hotUpDateSetting][error] hotUpdateError reason[%s]'%(curTime,e))

    return {'code':0,'msg':'热更新配置成功','jumpUrl':BACK_PRE+'/setting/hotUpDateSetting'}
