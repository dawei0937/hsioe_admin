#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    邮件公告模块
"""
from bottle import *
from admin import admin_app
from config.consts import  STATIC_LAYUI_PATH,STATIC_ADMIN_PATH,BACK_PRE,PARTY_PLAYER_COUNT
from common.utilt import *
from common.log import *
from datetime import datetime
from model.gameModel import *
from model.agentModel import *
from model.mailModel import *
from model.protoclModel import *
from model.userModel import getAgentAllMemberIds
import json


@admin_app.get('/notic/list')
@checkLogin
def getNoticList(redis,session):
    lang = getLang()
    startDate = request.GET.get('startDate','').strip()
    endDate   = request.GET.get('endDate','').strip()
    isList  = request.GET.get('list','').strip()

    if isList:
        noticList = getNoticsList(redis,session,lang,session['id'])
        return json.dumps(noticList)
    else:
        info = {
                'title'                 :       lang.GAME_NOTIFY_LIST_TXT,
                'tableUrl'              :       BACK_PRE+'/notic/list?list=1',
                'createUrl'             :       BACK_PRE+'/notice/create',
                'STATIC_LAYUI_PATH'     :       STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'     :       STATIC_ADMIN_PATH,
                'back_pre'              :       BACK_PRE,
                'addTitle'              :       lang.GAME_NOTIFY_CREATE_TXT
        }
        return template('admin_notice_list',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/notice/create')
def do_createNotice(redis,session):
    """
        创建新公告
    """
    lang = getLang()
    selfUid = session['id']

    # adminTable = AGENT_TABLE%(selfUid)
    # # adminType  = redis.hget(adminTable,'type')
    info = {
        "title"                 :   lang.GAME_NOTIFY_SEND_TXT,
        "submitUrl"             :   BACK_PRE+"/notice/create",
        'STATIC_LAYUI_PATH'     :   STATIC_LAYUI_PATH,
        'STATIC_ADMIN_PATH'     :   STATIC_ADMIN_PATH,
        'back_pre'              :   BACK_PRE,
        'backUrl'               :   BACK_PRE+"/notic/list"
    }

    return template('admin_game_notice_create',selfUid=selfUid,MAIL_SETTING_INFO=MAIL_SETTING_INFO,info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/notice/create')
def do_createNotice(redis,session):

    for field in FIELDS:
        #賦值
        exec(field)

    lang = getLang()

    log_debug('[NOTIC][url:/notice/create][info] title[%s] validDate[%s] messageType[%s] content[%s]'\
                            %(title,validDate,messageType,content))

    info = {
            'title'         :       lang.GAME_NOTIFY_SEND_TXT,
            'content'       :       content,
            'submitUrl'     :       BACK_PRE+'/notice/create',
            'back_pre'              :   BACK_PRE,
            'STATIC_LAYUI_PATH'     :   STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'     :   STATIC_ADMIN_PATH,
    }

    if not content:
        return {'code':1,'msg':lang.GAME_NOTIFY_REQ_TXT}

    try:
        messageInfo = {
                'title'         :       title,
                'validDate'     :       validDate,
                'messageType'   :       messageType,
                'content'       :       content
        }
        #push2userMsgTable(redis,session['id'],1)
        createNotice(redis,session['id'],messageInfo)
    except Exception,e:
        log_debug('[NOTIC][url:/notice/create][error] reason[%s]'%(e))
        return {'code':1,'msg':'添加新公告失败'}
    
    #记录操作日志
    return {'code':0,'msg':lang.GAME_NOTIFY_SEND_SUCCESS_TXT,'jumpUrl':BACK_PRE+'/notic/list'}

@admin_app.get('/notice/del')
def getGameNoticeDel(redis,session):
    """
    删除公告消息
    """
    noticId = request.GET.get('id','').strip()
    if not noticId:
        return {'code':1,'msg':'noticId[%s]不存在'%(noticId)}

    noticListTable = FORMAT_GAMEHALL_NOTIC_LIST_TABLE
    noticTable = FORMAT_GAMEHALL_NOTIC_TABLE%(noticId)
    if not redis.exists(noticTable):
        return {'code':1,'msg':'noticId[%s]的公告已被删除.'}

    info = {
            'title'         :       lang.GAME_NOTIFY_DEL_TXT,
    }

    pipe = redis.pipeline()
    try:
        pipe.lrem(noticListTable,noticId)
        pipe.delete(noticTable)
    except:
        return {'code':1,'msg':lang.GAME_NOTIFY_DEL_ERR_TXT}

    pipe.execute()
    return {'code':0,'msg':lang.GAME_NOTIFY_DEL_SUCCESS_TXT,'jumpUrl':BACK_PRE+'/notic/list'}

@admin_app.get('/notice/modify')
def getNoticeModify(redis,session):
    lang=getLang()
    curTime = datetime.now()
    noticeId = request.GET.get('id','').strip()

    if not noticeId:
        log_debug('[NOTIC][url:/notice/modify] noticeId[%s] is not pass by Url.'%(noticeId))
        return {'code':'1','msg':'参数不正确.'}

    noticListTable = FORMAT_GAMEHALL_NOTIC_LIST_TABLE
    noticTable = FORMAT_GAMEHALL_NOTIC_TABLE%(noticeId)
    if not noticTable:
        log_debug('[NOTIC][url:/notice/modify] noticeId[%s] is not exists.'%(noticeId))
        return {'code':'1','msg':'公告消息不存在.'}

    noticInfo = redis.hgetall(noticTable)
    info = {
          'title'                 :      lang.GAME_NOTIFY_MODIFY_TXT,
          'noticeId'              :       noticeId,
          'backUrl'               :       BACK_PRE+'/notic/list',
          'submitUrl'             :       BACK_PRE+'/notice/modify',
          'back_pre'              :       BACK_PRE,
          'STATIC_LAYUI_PATH'     :       STATIC_LAYUI_PATH,
          'STATIC_ADMIN_PATH'     :       STATIC_ADMIN_PATH,
    }
    
    return template('admin_game_notice_modify',info=info,MSGTYPE2DESC=MSGTYPE2DESC,noticInfo=noticInfo,MAIL_SETTING_INFO=MAIL_SETTING_INFO,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/notice/modify')
def do_noticModify(redis,session):
    lang     = getLang()

    for field in FIELDS:
        #賦值
        exec(field)

    if not noticeId:
        log_debug('[NOTIC][url:/notice/modify] noticeId[%s] is not pass by Url.'%(noticeId))
        return {'code':'1','msg':'参数不正确.'}

    #判断内容是否为空
    if not content:
        return {'code':1,'msg':lang.GAME_NOTIFY_REQ_TXT}

    noticListTable = FORMAT_GAMEHALL_NOTIC_LIST_TABLE
    noticTable = FORMAT_GAMEHALL_NOTIC_TABLE%(noticeId)
    pipe  =  redis.pipeline()
    try:
        messageInfo = {
                'title'         :       title,
                'validDate'     :       validDate,
                'messageType'   :       DESC2MSGTYPE[messageType],
                'content'       :       content
        }
        log_debug('[NOTICE][MODIFY][info] noticeId[%s] messageInfo[%s]'%(noticeId,messageInfo))
        pipe.hmset(noticTable,messageInfo)
    except Exception,e:
        log_debug('[NOTIC][url:/notice/create][error] reason[%s]'%(e))
        return {'code':1,'msg':'修改公告失败!'}

    pipe.execute()
    return {'code':0,'msg':lang.GAME_NOTIFY_MODIFY_SUC_TXT,'jumpUrl':BACK_PRE+'/notic/list'}

@admin_app.get('/notice/push')
def pushNotices(redis,session):
    """
    将消息放进玩家的信息列表
    """
    type2Msg = {'0':'推送','1':'取消推送'}
    
    curTime = datetime.now()
    timeStr = curTime.strftime("%Y-%m-%d %H:%M")
    agentId  = session['id']
    noticId = request.GET.get('id','').strip()
    pipe = redis.pipeline()
    #超级管理员发的公告需要塞到所有玩家的信息盒子
    noticeTable = FORMAT_GAMEHALL_NOTIC_TABLE%(noticId)
    senderId = redis.hget(noticeTable,'groupId')
    if not senderId:
        senderId = 1
    memberIds = getAgentAllMemberIds(redis,senderId)
    #推送所有公告
    status = redis.hget(noticeTable,'status')
    log_debug('[FUNC][pushNotices][info] agentId[%s] memberIds[%s] status[%s]'%(agentId,memberIds,status))
    try:
        if status == '0':
            for memberId in memberIds:
                log_debug('[FUNC][handle:push][info] agentId[%s] send to memberId[%s] noticId[%s] success'\
                                    %(agentId,memberId,noticId))
                pipe.hset(FORMAT_GAMEHALL_NOTIC_TABLE%(noticId),'time',timeStr)
                pipe.lpush(FORMAT_USER_MESSAGE_LIST%(memberId),noticId)
            pipe.hset(noticeTable,'status','1')            
        else:
            for memberId in memberIds:
                log_debug('[FUNC][handle:unPush][info] agentId[%s] send to memberId[%s] noticId[%s] success'\
                                    %(agentId,memberId,noticId))
                pipe.lrem(FORMAT_USER_MESSAGE_LIST%(memberId),noticId)
                pipe.srem(FORMAT_MSG_READ_SET%(noticId),memberId)
            pipe.hset(noticeTable,'status','0')
    except Exception,e:
        log_debug('[FUNC][push2userMsgTable][Error] agentId[%s] reason[%s]'%(agentId,e))
        return {'code':1,'msg':type2Msg[status]+'失败.'}

    pipe.execute()
    return {'code':0,'msg':type2Msg[status]+'成功.','jumpUrl':BACK_PRE+'/notic/list'}

@admin_app.get('/notice/read')
def getNoticeReadPage(redis,session):
    """
    读取信息
    """
    curTime = datetime.now()
    lang    = getLang()
    msgType = request.GET.get('type','').strip()
    msgId   = request.GET.get('id','').strip()
    agentId = request.GET.get('agentId','').strip()
    memberId = request.GET.get('memberId','').strip()

    #log
    log_debug('[%s][NOTICE][url:/notice/read][info] msgId[%s] msgType[%s] agentId[%s]'%(curTime,msgId,msgType,agentId))

    noticeItem = FORMAT_GAMEHALL_NOTIC_TABLE%(msgId)
    if not redis.exists(noticeItem):
        return template('notice_not_exists')

    noticeReads = FORMAT_MSG_READ_SET%(msgId)
    readList = redis.smembers(noticeReads)
    #log
    log_debug('[%s][NOTICE][url:/notice/read][info] msgId[%s] readList[%s]'%(curTime,msgId,readList))
    #设置消息为已读
    if memberId not in readList:
        redis.sadd(noticeReads,memberId)


    title,content = redis.hmget(noticeItem,('title','content'))

    if msgType == MAIL_TYPE:
        #setReward2User(msgId,userId)
        deleteMsg(redis,msgId,memberId)

    log_debug('[%s][NOTICE][url:/notice/read][return] msgId[%s] title[%s] content[%s]'%(curTime,msgId,title,content))
    return template('notice_content_page',content=content,title=title)