#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    系统会员模块
"""
from bottle import *
from admin import admin_app
from config.consts import  STATIC_LAYUI_PATH,STATIC_ADMIN_PATH,BACK_PRE,PLAYER_BASE_SCORE,DEFAULT_BASE_SCORE,RES_VERSION
from common.utilt import *
from common.log import *
from datetime import datetime
from web_db_define import *
from model.agentModel import *
from model.protoclModel import *
from model.userModel import *
from model.orderModel import *
import hashlib
import json


#LANG = getLang()

@admin_app.get('/member/curOnline')
@checkAccess
def getCurOnline(redis,session):
    """
        获取在线用户
    """
    lang    =  getLang()
    curTime =  datetime.now()
    isList  =  request.GET.get('list','').strip()

    if isList:
        pass
    else:
        info = {
                'title'                  :           lang.MEMBER_ONLINE_TITLE_TXT,
                'listUrl'                :           BACK_PRE+'/member/curOnline?list=1',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }

        return template('admin_member_online',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/member/list')
def getDirectMemberList(redis,session):
    """
        获取会员列表
    """
    lang    =  getLang()
    curTime =  datetime.now()
    isList  =  request.GET.get('list','').strip()
    startDate = request.GET.get('startDate','').strip()
    endDate   = request.GET.get('endDate','').strip()
    pageSize = request.GET.get('pageSize','').strip()
    pageNumber = request.GET.get('pageNumber','').strip()
    searchId   = request.GET.get('searchId','').strip()
    sort_name  = request.GET.get('sort_name','').strip()
    sort_method = request.GET.get('sort_method','')
    selfUid  = session['id']

    if isList:
        res = getMemberList(redis,session,selfUid,searchId,lang,int(pageSize),int(pageNumber),sort_name,sort_method)
        return json.dumps(res)
    else:
        info = {
                'title'                  :           lang.MEMBER_LIST_TITLE_TXT,
                'listUrl'                :           BACK_PRE+'/member/list?list=1',
                'searchTxt'              :           lang.MEMBER_INPUT_TXT,
                'sort_bar'               :           True,#开启排序
                'member_page'            :           True,#开启排序
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }

        return template('admin_member_list',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/member/kick')
def do_kickDirectMember(redis,session):
    """
        踢出直属会员
    """
    lang    =  getLang()
    curTime =  datetime.now()
    selfUid  = session['id']
    memberId = request.GET.get('id','').strip()

    userTable = FORMAT_USER_TABLE%(memberId)
    userParent = redis.hget(userTable,'parentAg')
    userParentTable = FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(userParent)
    if not userParent:
        return {'code':1,'msg':'会员ID[%s]的公会不存在.'%(memberId)}
    #print userTable
    pipe = redis.pipeline()
    try:
        pipe.srem(userParentTable, memberId) #上线代理需要获得
        pipe.hset(userTable, 'parentAg', '')
    except Exception,e:
        log_debug('[%s][member][kick][error] agentId[%s] member[%s] kick error,reason[%s]'%(curTime,selfUid,memberId,e))

    pipe.execute()
    #记录操作日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['uncheckMember']%(memberId)}
    writeAgentOpLog(redis,selfUid,logInfo)

    return {'code':0,'msg':'移除会员[%s]成功'%(memberId),'jumpUrl':BACK_PRE+'/member/list'}

@admin_app.get('/member/removeCard')
def get_removeCard(redis,session):
    """
        移除会员的钻石
    """
    curTime = datetime.now()
    lang    = getLang()
    memberId =  request.GET.get('id','').strip()
    if not memberId:
        return {'code':'1','msg':'非法操作!'}
    parentAg =  redis.hget(FORMAT_USER_TABLE%(memberId),'parentAg')
    roomcard = redis.get(USER4AGENT_CARD%(parentAg, memberId))
    memberInfo = {
            'title'         :       '移除会员(%s)钻石'%(memberId),
            'backUrl'       :       BACK_PRE+'/member/list',
            'agentId'       :       parentAg,
            'memberId'      :       memberId,
            'submitUrl'     :       BACK_PRE+'/member/removeCard',
            'roomcard'      :       roomcard,
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH
    }

    return template('admin_member_removeCard',info=memberInfo,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/member/removeCard')
def do_removeCard(redis,session):
    """
        移除会员的钻石逻辑
    """
    curTime = datetime.now()
    lang    = getLang()
    roomcard = request.forms.get('roomcard','').strip()
    agentId = request.forms.get('agentId','').strip()
    remove  = request.forms.get('remove','').strip()
    memberId = request.forms.get('memberId','').strip()

    if not remove:
        return {'code':1,'msg':lang.MEMBER_DIOMAN_INPUT_TXT}

    if type(remove) == type(0.1):
        return {'code':1,'msg':lang.MEMBER_DIOMAN_INPUT_NUM_TXT}

    try :
        if int(remove) <= 0 :
            return {'code':1,'msg':lang.MEMBER_DIOMAN_LT_TXT}

        if int(remove) > int(roomcard):
            return {'code':1,'msg':lang.MEMBER_DIOMAN_GT_TXT}
    except :
        return {'code':1,'msg':lang.MEMBER_DIOMAN_INPUT_NUM_TXT}

    NewRemove = '-'+remove
    redis.incrby(USER4AGENT_CARD%(agentId, memberId),int(NewRemove))
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['removeRoomCard']%(memberId,remove)}
    writeAgentOpLog(redis,agentId,logInfo)

    return {'code':0,'msg':lang.MEMBER_DIOMAN_REMOVE_SUCCESS%(memberId,remove),'jumpUrl':'/admin/member/list'}


@admin_app.get('/member/addCard')
def get_addCard(redis,session):
    """
        移除会员的钻石
    """
    curTime = datetime.now()
    lang    = getLang()
    memberId =  request.GET.get('id','').strip()
    if not memberId:
        return {'code':'1','msg':'非法操作!'}

    parentAg =  redis.hget(FORMAT_USER_TABLE%(memberId),'parentAg')
    memberTable = FORMAT_USER_TABLE%(memberId)
    name,headImgUrl = redis.hmget(memberTable,('nickname','headImgUrl'))
    roomcard = redis.get(USER4AGENT_CARD%(parentAg, memberId))

    memberInfo = {
            'title'         :       '补会员[%s]钻石'%(memberId),
            'backUrl'       :       BACK_PRE+'/member/list',
            'agentId'       :       parentAg,
            'memberId'      :       memberId,
            'submitUrl'     :       BACK_PRE+'/member/addCard',
            'roomcard'      :       roomcard,
            'name'          :       name,
            'headImgUrl'    :       headImgUrl,
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH
    }

    return template('admin_member_addCard',info=memberInfo,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/member/addCard')
def do_addCard(redis,session):
    """
        移除会员的钻石逻辑
    """
    curTime = datetime.now()
    lang    = getLang()
    roomcard = request.forms.get('roomcard','').strip()
    agentId = request.forms.get('agentId','').strip()
    add  = request.forms.get('add','').strip()
    memberId = request.forms.get('memberId','').strip()
    selfUid = session['id']

    if not add:
        return {'code':1,'msg':lang.MEMBER_DIOMAN_INPUT_TXT}

    if type(add) == type(0.1):
        return {'code':1,'msg':lang.MEMBER_DIOMAN_INPUT_NUM_TXT}

    try :
        if int(add) <= 0 :
            return {'code':1,'msg':lang.MEMBER_DIOMAN_LT_TXT}
    except :
        return {'code':1,'msg':lang.MEMBER_DIOMAN_INPUT_NUM_TXT}

    NewRemove = '+'+add
    redis.incrby(USER4AGENT_CARD%(agentId, memberId),int(NewRemove))
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['addRoomCard']%(memberId,add)}
    #写入操作人ID
    writeAgentOpLog(redis,selfUid,logInfo)

    return {'code':0,'msg':lang.MEMBER_DIOMAN_ADD_SUCCESS%(memberId,add),'jumpUrl':'/admin/member/list'}

@admin_app.get('/member/modify')
def get_modifyMember(redis,session):
    """
        修改代理下属玩家信息
    """
    curTime = datetime.now()
    lang    = getLang()
    memberId =   request.GET.get('id','').strip()
    if not memberId:
        return {'code':'1','msg':'非法操作!'}

    memberTable = FORMAT_USER_TABLE%(memberId)
    maxScore,baseScore   = redis.hmget(memberTable,('maxScore','baseScore'))

    memberInfo = {
            'title'         :       '会员[%s]信息修改'%(memberId),
            'backUrl'       :       BACK_PRE+'/member/list',
            'memberId'      :       memberId,
            'submitUrl'     :       BACK_PRE+'/member/modify',
            'maxScore'      :       maxScore if maxScore else 1,
            'baseScore'     :       baseScore if baseScore else DEFAULT_BASE_SCORE,
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH
    }

    return template('admin_member_modify',baseScore=PLAYER_BASE_SCORE,info=memberInfo,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/member/modify')
def do_modifyMember(redis,session):
    """
        修改代理操作
    """
    curTime = datetime.now()
    lang     = getLang()
    selfUid  = session['id']
    memberId = request.forms.get('memberId','').strip()
    maxScore = request.forms.get('maxScore','').strip()
    score1   = request.forms.get('score1','').strip()
    score2   = request.forms.get('score2','').strip()
    score3   = request.forms.get('score3','').strip()
    score4   = request.forms.get('score4','').strip()
    score5   = request.forms.get('score5','').strip()
    score6   = request.forms.get('score6','').strip()
    score7   = request.forms.get('score7','').strip()
    score8   = request.forms.get('score8','').strip()
    score9   = request.forms.get('score9','').strip()
    score10   = request.forms.get('score10','').strip()
    score11   = request.forms.get('score11','').strip()
    score12   = request.forms.get('score12','').strip()
    score13   = request.forms.get('score13','').strip()
    score14   = request.forms.get('score14','').strip()
    score15   = request.forms.get('score15','').strip()
    score16   = request.forms.get('score16','').strip()
    score17   = request.forms.get('score17','').strip()
    score18   = request.forms.get('score18','').strip()
    score19   = request.forms.get('score19','').strip()
    score20   = request.forms.get('score20','').strip()

    if not memberId:
        return {'code':1,'msg':'非法修改会员!'}

    baseScoreList = []
    scoreList = [score1,score2,score3,score4,score5,score6,score7,score8,score9,\
                        score10,score11,score12,score13,score14,score15,score16,score17,score18,score19,score20]

    for score in scoreList:
        if score:
            baseScoreList.append(score)

    print baseScoreList

    pipe = redis.pipeline()
    try:
        memebrTable  =  FORMAT_USER_TABLE%(memberId)
        pipe.hmset(memebrTable,{'maxScore':max(scoreList)})
        pipe.hmset(memebrTable,{'baseScore':baseScoreList})
    except Exception,e:
        log_debug('[%s][try ModifyMember][error] memberId[%s] modify info error. reason[%s]'%(curTime,memberId,e))
        return {'code':1,'msg':'修改会员[%s]信息失败'%(memberId)}

    #修改成功日志
    log_debug('[%s][memebr][modify][success] memebr Id is [%s] ！'%(curTime,memberId))
    pipe.execute()

    #记录操作日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['modifyMember']%(memberId)}
    writeAgentOpLog(redis,selfUid,logInfo)

    return {'code':0,'msg':'修改会员(%s)成功'%(memberId),'jumpUrl':'/admin/member/list'}


@admin_app.get('/member/search')
@checkAccess
def getMemberSearch(redis,session):
    """
    会员查询充卡
    """
    curTime = datetime.now()
    lang    = getLang()
    memberId = request.GET.get('memberId','').strip()

    info = {
                'title'             :               lang.MENU_MEMBER_SEARCH_TXT,
                'memberId'          :               memberId,
                'searchUrl'         :               BACK_PRE+'/member/recharge',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
    }

    return template('admin_member_search',info=info,message=None,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/member/recharge')
def getMemberRecharge(redis,session):
    """
    会员充卡
    """
    curTime = datetime.now()
    lang    = getLang()
    dateStr = curTime.strftime('%Y-%m-%d')

    selfAccount,selfUid = session['account'],session['id']

    memberId = request.GET.get('memberId','').strip()

    memberTable = FORMAT_USER_TABLE%(memberId)
    memberChildIds = redis.smembers(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(selfUid))

    if not redis.exists(memberTable) or (memberId not in memberChildIds):
        info = {
                'title'             :                lang.MENU_MEMBER_SEARCH_TXT,
                'memberId'          :                memberId,
                'searchUrl'         :                BACK_PRE+'/member/recharge',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }
        log_debug('[%s][roomCard][member recharge] memberId[%s] is not exists.'%(curTime,memberId))
        return template('admin_member_search',info=info,message='会员[%s]不存在'%(memberId),lang=lang,RES_VERSION=RES_VERSION)

    account,name,openID,headImgUrl = redis.hmget(memberTable,('account','nickname','openid','headImgUrl'))
    if not redis.exists(USER4AGENT_CARD%(selfUid,memberId)):
        redis.set(USER4AGENT_CARD%(selfUid,memberId),0)

    roomcard = redis.get(USER4AGENT_CARD%(selfUid,memberId))

    print '[%s][member recharge][info] account[%s] name[%s] roomcard[%s] openid[%s]'\
                            %(curTime,account,name,roomcard,openID)
    info = {
                'title'             :           '钻石充值 [当前会员:%s]'%(account),
                'submitUrl'         :           '/admin/member/recharge',
                'backUrl'           :           '/admin/member/list',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH,
                'memberId'          :           memberId,
                'account'           :           account,
                'name'              :           name,
                'roomCard'          :           roomcard,
                'headImgUrl'        :           headImgUrl,
                'rechargeTypes'     :           ROOMCARD2TYPE['member'],
                'openId'            :           openID
    }

    return template('admin_member_recharge',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/member/recharge')
def do_memberRecharge(redis,session):
    """
    会员充卡逻辑
    """
    curTime  =  datetime.now()
    lang     =  getLang()
    dateStr  =  curTime.strftime('%Y-%m-%d')
    selfAccount,selfUid = session['account'],session['id']

    userId = request.forms.get('memberId','').strip()
    cardNum = request.forms.get('cardNums','').strip()
    passwd  = request.forms.get('passwd','').strip()

    userTable  = FORMAT_USER_TABLE%(userId)
    roomCard2AgentTable = USER4AGENT_CARD%(selfUid,userId)
    agentTable = AGENT_TABLE%(selfUid)

    roomcard,name,selfPasswd,type,parent_id = redis.hmget(agentTable,('roomcard','name','passwd','type','parentAg'))
    print roomcard,name,selfPasswd,type
    info  =  {
                'title'             :       '会员钻石充值',
                'backUrl'           :       BACK_PRE+'/member/list'
    }

    checkNullFields = [
        {'field':cardNum,'msg':'充值钻石数不能为空'},
        {'field':passwd,'msg':'请输入你的密码'}
    ]

    for check in checkNullFields:
        if not check['field']:
            return {'code':1,'msg':check['msg']}

    if selfPasswd != hashlib.sha256(passwd).hexdigest():
        return {'code':1,'msg':'您的密码不正确'}

    pipe  =  redis.pipeline()
    if int(type) not in [0,1]:
        if int(roomcard) < int(cardNum):
            return {'code':4,'msg':lang.CARD_NOT_ENGOUGHT_TXT,'jumpUrl':BACK_PRE+'/order/buy'}
        pipe.hincrby(agentTable,'roomcard',-int(cardNum))

    pipe.incrby(roomCard2AgentTable,cardNum)

    print '[%s][recharge roomcard][info] memberId[%s] cards[%s]'%(curTime,userId,cardNum)

    orderNo = getOrderNo(selfUid)

    orderInfo = {
            'orderNo'                :       orderNo,
            'cardNums'               :       cardNum,
            'applyAccount'           :       userId+"(玩家)",
            'status'                 :       1,
            'apply_date'             :       curTime.strftime('%Y-%m-%d %H:%M:%S'),
            'finish_date'            :       curTime.strftime('%Y-%m-%d %H:%M:%S'),
            'type'                   :       0,
            'note'                   :       '',
            'saleAccount'            :       selfAccount
    }

    if createOrder(redis,orderInfo):
        #创建订单
        pipe.lpush(AGENT_SALE_ORDER_LIST%(selfUid,dateStr),orderNo)
        pipe.lpush(AGENT_SALESUCCESS_ORDER_LIST%(selfUid,dateStr),orderNo)

        #统计代理售卡
        if redis.exists(AGENT_SALE_CARD_DATE%(selfUid,dateStr)):
            pipe.hincrby(AGENT_SALE_CARD_DATE%(selfUid,dateStr),'cardNums',int(cardNum))
        else:
            pipe.hmset(AGENT_SALE_CARD_DATE%(selfUid,dateStr),{'cardNums':int(cardNum),'date':dateStr})

        pipe.execute()
        #通知服务端
        #sendProtocol2GameService(redis,MAHJONG_GAMEID,HEAD_SERVICE_PROTOCOL_MEMBER_REFRESH%(account))
        return {'code':0,'msg':'成功向[%s]充值了钻石[%s]张'%(userId,cardNum),'jumpUrl':BACK_PRE+'/member/search'}

    return {'code':1,'msg':'充值失败'}

@admin_app.get('/member/joinList')
def getMemberApplyList(redis,session):
    """
    获取下线代理申请列表
    """
    curTime = datetime.now()
    lang    = getLang()
    selfAccount,selfUid  =  session['account'],session['id']

    isList = request.GET.get('list','').strip()

    if isList:
        applyLists = getmemberApplyList(redis,selfUid)
        return json.dumps(applyLists)
    else:
        info = {
                    'title'                  :          '玩家申请列表',
                    'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH,
                    'listUrl'                :           BACK_PRE+'/member/joinList?list=1'
        }

        return template('admin_member_apply_list',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/member/join/comfirm')
def do_memberJoinComfirm(redis,session):
    """
    审核会员加入公会
    """
    curTime = datetime.now()
    lang    = getLang()
    selfAccount,selfUid   =   session['account'],session['id']

    memberId  =  request.forms.get('id','').strip()
    if not memberId:
        return {'code':1,'msg':'会员ID[%s]错误'%(memberId)}

    try:
        memberJoinComfirm(redis,selfUid,memberId)
    except Exception,e:
        print '[%s][join Comfirm][error] reason[%s]'%(curTime,e)
        return {'code':1,'msg':'审核会员异常'}

    #记录操作日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['checkMember']%(memberId)}
    writeAgentOpLog(redis,selfUid,logInfo)
    return {'code':0,'msg':'会员[%s]审核通过.'%(memberId),'jumpUrl':BACK_PRE+'/member/modify?id=%s'%(memberId)}

@admin_app.post('/member/join/reject')
def do_memberJoinReject(redis,session):
    """
    拒绝会员加入公会
    """
    curTime = datetime.now()
    lang = getLang()
    selfAccount,selfUid  =  session['account'],session['id']

    memberId   =   request.forms.get('id','').strip()
    if not memberId:
        return {'code':1,'msg':'会员ID[%s]错误'%(memberId)}

    pipe = redis.pipeline()
    try:
        log_debug('[%s][reject Member][info] agentId[%s] reject memberId[%s]'%(curTime,selfUid,memberId))
        pipe.lrem(JOIN_GROUP_LIST%(selfUid),memberId)
    except Exception,e:
        log_debug('[%s][reject member][error] memberId[%s] reject error. reason[%s]'%(curTime,memberId,e))
        return {'code':1,'msg':'会员[%s]拒绝失败'%(memberId)}

    pipe.execute()
    #记录操作日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['rejectMember']%(memberId)}
    writeAgentOpLog(redis,selfUid,logInfo)
    return {'code':0,'msg':'会员[%s]已拒绝加入公会'%(memberId),'jumpUrl':BACK_PRE+'/member/joinList'}

@admin_app.get('/member/kicks')
def do_memberKick(redis,session):
    """
    踢出会员
    """
    account = request.GET.get('account','').strip()

    account2user_table = FORMAT_ACCOUNT2USER_TABLE%(account)
    memberTable = redis.get(account2user_table)
    if not redis.exists(memberTable):
        return {'code':1,'msg':'会员[%s]不存在'%(account)}

    #发送提出玩家协议给服务端
    sendProtocol2AllGameService(redis,HEAD_SERVICE_PROTOCOL_KICK_MEMBER%(account))

    return {'code':0,'msg':'会员(%s)已被踢出游戏!'%(account),'jumpUrl':BACK_PRE+'/agent/member/curOnline'}

@admin_app.get('/member/gm/list')
def getGmsList(redis,session):
    """
        获取gm列表
    """
    lang    =  getLang()
    curTime =  datetime.now()
    #接收的值
    fileds = ('show_list','pageSize','pageNumber','searchId')
    for filed in fileds:#动态定义
        exec("%s = request.GET.get('%s','').strip()"%(filed,filed))

    if show_list:
        res = getGmList(redis,session,searchId,int(pageSize),int(pageNumber))
        return json.dumps(res)
    else:
        info = {
                'title'                  :           'GM玩家列表',
                'listUrl'                :           BACK_PRE+'/member/gm/list?show_list=1',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH,
                'searchTxt'              :               '输入玩家ID',
                'removeUrl'              :           BACK_PRE + '/member/gm/kick',
                'addGMUrl'               :           BACK_PRE + '/member/gm/add'
        }

        return template('admin_member_gm_list',PAGE_LIST=PAGE_LIST,info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/member/gm/kick')
def do_kickGmMember(redis,session):
    """
        踢出会员gm权限
    """
    lang    =  getLang()
    curTime =  datetime.now()
    selfUid  = session['id']
    gm_ids = request.GET.get('id','').strip()

    if not gm_ids:
        log_debug('[try do_kickGmMember] gm_ids[%s] is not illegs.'%(gm_ids))
        return {'code':1,'msg':'GM_IDS参数错误.'}

    gm_ids = gm_ids.split(",")
    gm_table = 'GMAccount:set'

    pipe = redis.pipeline()

    for gm_id in gm_ids:
        if not redis.sismember(gm_table,gm_id):
            continue
        pipe.srem(gm_table, gm_id) #上线代理需要获得

    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['kickGm']%(gm_ids)}
    writeAgentOpLog(redis,selfUid,logInfo)
    pipe.execute()
    return {'code':0,'msg':'移除玩家[%s]GM权限成功'%(gm_ids),'jumpUrl':BACK_PRE+'/member/gm/list'}

@admin_app.get('/member/gm/add')
def get_addGmMember(redis,session):
    curTime = datetime.now()
    lang    = getLang()
    info = {
                'title'             :               '添加GM权限',
                'addUrl'            :               BACK_PRE+'/member/gm/add',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
    }

    return template('admin_member_gm_add',info=info,message=None,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/member/gm/showHis')
def get_addGmMember(redis,session):
    curTime = datetime.now()
    lang    = getLang()
    userId  = request.GET.get('userId','').strip()
    isList  = request.GET.get('list','').strip()

    log_debug('[try get_addGmMember] userId[%s]'%(userId))
    if not userId:
        return

    if isList:
        gm_his = get_gm_op_list(redis,userId)
        return json.dumps(gm_his)
    else:
        info = {
                    'title'             :               '玩家[%s]GM历史'%(userId),
                    'addUrl'            :               BACK_PRE+'/member/gm/list',
                    'dataUrl'           :               BACK_PRE+'/member/gm/showHis?list=1&userId=%s'%(userId),
                    'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }

        return template('admin_member_gm_his',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/member/gm/add')
def do_addGmMember(redis,session):
    curTime = datetime.now()
    lang    = getLang()
    memberId = request.forms.get('memberId','').strip()
    memberTable = FORMAT_USER_TABLE%(memberId)
    selfUid = session['id']
    if not redis.exists(memberTable):
        return {'code':1,'msg':'会员[%s]不存在'%(memberId)}
    account = redis.hget(memberTable,'account')
    gmTable = 'GMAccount:set'
    if redis.sismember(gmTable,account):
        return {'code':1,'msg':'会员[%s]已经拥有gm权限'%(memberId)}
    try:
        redis.sadd(gmTable,account) #上线代理需要获得
    except Exception,e:
        log_debug('[%s][member][gm][add][error] gmAccount[%s]  add error,reason[%s]'%(curTime,account,e))
        return {'code':1,'msg':'添加会员[%s] gm权限失败'%(account)}

    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['addGm']%(account)}
    writeAgentOpLog(redis,selfUid,logInfo)
    return {'code':0,'msg':'给会员[%s]设置gm权限成功'%(memberId),'jumpUrl':BACK_PRE+'/member/gm/list'}

@admin_app.get('/member/freeze')
def do_freezeMember(redis,session):
    """
    冻结玩家操作接口
    """
    curTime = datetime.now()
    lang    = getLang()
    memberId = request.GET.get('id','').strip()

    freezeDesc = {
            '1'     :     '冻结成功',
            '0'     :     '解冻成功'
    }

    if not memberId:
        return {'code':1,'msg':'memberId请求错误'}


    memberTable = FORMAT_USER_TABLE%(memberId)
    if not redis.exists(memberTable):
        return {'code':1,'msg':'会员[%s]不存在'%(memberId)}

    valid = redis.hget(memberTable,'valid')
    pipe = redis.pipeline()
    if valid == '1':
        pipe.hset(memberTable,'valid','0')
    else:
        pipe.hset(memberTable,'valid','1')

    pipe.execute()
    return {'code':0,'msg':'会员[%s] %s'%(memberId,freezeDesc[valid]),'jumpUrl':BACK_PRE+'/member/list'}

@admin_app.get('/member/dayUseCard')
def get_member_day_useCard(redis,session):
    """
    玩家每日消耗房卡数统计
    """
    curTime = datetime.now()
    lang = getLang()
    isList = request.GET.get('list','').strip()
    startDate = request.GET.get('startDate','').strip()
    endDate = request.GET.get('endDate','').strip()
    memberId = request.GET.get('searchId','').strip()

    if isList:
        if not memberId:
            return []
        res = getMemberUseCardsByDay(redis,startDate,endDate,memberId)
        return json.dumps(res)
    else:
        info = {
                'title'     :       '玩家每日消耗钻石数',
                'listUrl'                :           BACK_PRE+'/member/dayUseCard?list=1&searchId=0',
                'searchTxt'              :           '会员ID',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }

        return template('admin_member_dayuser',PAGE_LIST=PAGE_LIST,info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/member/open_auth')
def do_openAuth(redis,session):
    """
    开启玩家的代开房间权限
    """
    curTime = datetime.now()
    lang    = getLang()
    selfAccount,selfUid = session['account'],session['id']
    memberId = request.forms.get('id','').strip()

    login_info_dict = {
            '0'             :       'openMemberAuth',
            '1'             :       'unOpenMemberAuth'
    }

    memberTable = FORMAT_USER_TABLE%(memberId)
    if not redis.exists(memberTable):
        log_debug('[try do_openAuth][error] member[%s] is not exists!'%(memberId))
        return {'code':1,'msg':lang.MEMBER_NOT_EXISTES_TXT%(memberId)}

    open_auth = redis.hget(memberTable,'open_auth')
    if not open_auth:
        open_auth = '0'

    if open_auth == '0':
        redis.hset(memberTable,'open_auth',1)
        #doAgentChange(redis,agentId,'open_auth',1)
    else:
        redis.hset(memberTable,'open_auth',0)

    #记录操作日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                    'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE[login_info_dict[open_auth]]%(memberId)}
    writeAgentOpLog(redis,selfUid,logInfo)
    return {'code':0,'msg':lang.GROUP_CHECK_SETTING_SUCCESS,'jumpUrl':BACK_PRE+'/member/list'}
