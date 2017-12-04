#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    代理模块
"""
from bottle import *
from admin import admin_app
from config.consts import  STATIC_LAYUI_PATH,STATIC_ADMIN_PATH,BACK_PRE,RES_VERSION
from common.utilt import *
from common.log import *
from datetime import datetime
from web_db_define import *
from model.agentModel import *
from model.userModel import *
from model.protoclModel import *
from access_module import *
import hashlib
import json

GET_FORMS = "%s = request.GET.get('%s','').strip()"
POST_FORMS = "%s = request.forms.get('%s','').strip()"

@admin_app.get('/agent/list')
@checkAccess
def getAgentList(redis,session):
    """
        代理列表
    """
    lang    = getLang()
    isList  = request.GET.get('list','').strip()
    agentId = request.GET.get('id','').strip()
    searchId = request.GET.get('searchId','').strip()
    start_date = request.GET.get('start_date','').strip()
    end_date = request.GET.get('end_date','').strip()

    if not agentId:
        agentId = session['id']
    log_debug('[try get_agent_list] agentId[%s] '%(agentId))

    adminTable = AGENT_TABLE%(agentId)
    creatAgUrl = BACK_PRE + '/agent/create'
    #搜索条件
    condition = {'start_date':start_date,'end_date':end_date,'searchId':searchId}
    create_auth,aType = redis.hmget(adminTable,('create_auth','type'))
    try:
        create_auth = int(create_auth)
    except:
        create_auth = 0

    if creatAgUrl in redis.smembers(AGENT2ACCESSBAN%(agentId)):
        createAg = '0'
    else:
        createAg = '1'

    if isList:
        res = getAgListInfos(redis,session,agentId,condition,lang)
        return json.dumps(res)
    else:
        info = {
                'title'                  :       '下线代理列表(%s)'%(lang.TYPE_2_ADMINTYPE[str(int(aType)+1)]),
                'showPlus'               :       'true' if aType in ['0','1'] else 'false',
                'createAccess'           :       createAg,
                'atype'                  :       aType,
                'searchTxt'              :       '公会/代理ID',
                'createUrl'              :       BACK_PRE+'/agent/create',
                'listUrl'                :       BACK_PRE+'/agent/list?list=1',
                'create_auth'            :       create_auth,
                'show_date_search'       :       True,
                'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH
        }
        return template('admin_agent_list',PAGE_LIST=PAGE_LIST,info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/agent/info')
@checkAccess
def get_agent_info(redis,session):
    """
        代理信息查看
    """
    curTime = datetime.now()
    lang    = getLang()
    agentId = request.GET.get('id','').strip()
    if not agentId:
        return {'code':'1','msg':'非法操作!'}

    adminTable = AGENT_TABLE%(agentId)
    account,aid,name,roomCard,regDate,regIp,valid,aType = \
                redis.hmget(adminTable,('account','id','name','roomcard','regDate','regIp','valid','type'))

    agentInfo = {
            'title'         :       '代理(%s)详细信息'%(account),
            'backUrl'       :       BACK_PRE+'/agent/list',
            'name'          :        name,
            'account'       :        account,
            'roomCard'      :        '无限制' if aType == '0' else roomCard,
            'regDate'       :        regDate,
            'regIp'         :        regIp,
            'valid'         :        '有效' if valid == '1' else '冻结',
            'aType'         :        lang.TYPE_2_ADMINTYPE[aType],
            'aid'           :        aid,
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH
    }

    log_debug('[try getAgInfo] agent[%s] detail info [%s]'%(account,agentInfo))
    return template('admin_agent_info',info=agentInfo,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/agent/create')
@checkAccess
def getAgentCreate(redis,session):
    """
        创建代理
    """
    curTime = datetime.now()
    agentId =  request.GET.get('id','').strip()
    lang    = getLang()

    if not agentId:
        agentId = session['id']

    adminTable = AGENT_TABLE%(agentId)
    aType,shareRate = redis.hmget(adminTable,('type','shareRate'))
    log_debug('[%s][admin][ag][info] create ag.parentId[%s]'%(curTime,agentId))
    createAgentType = int(aType)+ 1
    access = getListAccess(createAgentType,lang)

    info = {
            'title'                  :       '创建代理（上级代理:%s）'%(agentId),
            'parentAg'               :       agentId,
            'aType'                  :       aType,
            'backUrl'                :       BACK_PRE+'/agent/list',
            'submitUrl'              :       BACK_PRE+'/agent/create',
            'games'                  :       getCreatAgentGames(redis,agentId),
            'defaultGames'           :       redis.smembers(GAME_DEFAULT_BIND),
            'shareRate'              :       shareRate,
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH
    }

    return template('agent_create',Access=access,info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/agent/create')
@checkAccess
def do_agCreate(redis,session):
    """
        创建代理操作
    """
    curTime = datetime.now()
    now_date = curTime.strftime('%Y-%m-%d')
    selfUid = session['id']
    lang = getLang()
    for fields in AGENT_FIELDS:
        log_debug('---------------[%s]'%(POST_FORMS%(fields,fields)))
        exec(POST_FORMS%(fields,fields))

    if not parentAg:
        return {'code':1,'msg':'非法创建代理!'}

    #当前创建的是
    aType,aName,aIsTrail = redis.hmget(AGENT_TABLE%(parentAg),('type','name','isTrail'))
    if not aIsTrail:
        aIsTrail = '0'
    log_debug('[%s][try do_agCreate] agent.parentAg[%s] account[%s] passwd[%s] comfirmPasswd[%s]'\
                    %(curTime,parentAg,account,passwd,comfirPasswd))

    checkFields = [
        {'field':account,'msg':'代理账号不能为空'},
        {'field':passwd,'msg':'密码不能为空'},
        {'field':comfirPasswd,'msg':'密码不能为空'}
    ]

    for field in checkFields:
        if not field['field']:
            return {'code':1,'msg':field['msg']}

    if unitPrice and shareRate:
        if float(shareRate) > float(unitPrice):
            return {'code':1,'msg':'给下级分成不能大于钻石单价!'}

    if myRate and shareRate:
        if float(shareRate) > float(myRate):
            return {'code':1,'msg':'给下级分成不能大于自己的分成!'}

    agent_table = AGENT_TABLE%(agentId)
    if redis.exists(agent_table):
        return {'code':1,'msg':'代理ID[%s]已存在'%(agentId)}

    parentSetTable  =  AGENT_CHILD_TABLE%(parentAg)
    if int(parentAg) == 1:
        recharge,create_auth,open_auth ='1','0','0'
    else:
        topAgentId = getTopAgentId(redis,parentAg)
        recharge,create_auth = redis.hmget(AGENT_TABLE%(topAgentId),('recharge','create_auth'))
        open_auth = '0'
        if not recharge:
            recharge = '1'
        if not create_auth:
            create_auth = '0'

    admimtoIdTalbel = AGENT_ACCOUNT_TO_ID%(account)
    pipe = redis.pipeline()

    if not redis.exists(admimtoIdTalbel):
        if not agentId:
            agentId = getAgentIdNo(redis)
        else:
            pipe.sadd(AGENT_ID_TABLE,agentId)

        agentType = int(aType)+1
        agentInfo = {
                'id'                    :           agentId,
                'account'               :           account,
                'passwd'                :           hashlib.sha256(passwd).hexdigest(),
                'name'                  :           '',
                'shareRate'             :           shareRate,
                'valid'                 :            1,
                'roomcard_id'           :           0,
                'parent_id'             :           parentAg,
                'roomcard'              :           0,
                'regIp'                 :           '127.0.0.1',
                'regDate'               :           curTime.strftime("%Y-%m-%d %H:%M:%S"),
                'lastLoginIP'           :           1,
                'lastLoginDate'         :           1,
                'isTrail'               :           aIsTrail,
                'unitPrice'             :           unitPrice,
                'recharge'              :           recharge,
                'isCreate'              :           '1',
                'create_auth'           :           create_auth,
                'open_auth'             :           open_auth,
                'type'                  :           agentType,
                'defaultRoomCard'       :           defaultRoomCard,
        }

        adminTable  =  AGENT_TABLE%(agentId)
        if unitPrice:
            pipe.sadd(AGENT_ROOMCARD_PER_PRICE%(agentId),unitPrice)

        if shareRate:
            pipe.sadd(AGENT_RATE_SET%(agentId),shareRate)
            
        #创建日期索引
        pipe.sadd(AGENT_CREATE_DATE%(now_date),agentId)
        pipe.hmset(adminTable,agentInfo)
        #创建代理账号映射id
        pipe.set(admimtoIdTalbel,agentId)
        #将该代理添加进父代理集合
        pipe.set(AGENT2PARENT%(agentId),parentAg)
        #创建代理账号的父Id映射
        pipe.sadd(parentSetTable,agentId)
        # 为该代理绑定拥有的游戏
        setAgentGames(request,redis,parentAg,agentId)
        # 为该代理绑定拥有的权限(通过type)
        setAgentAccess(redis,agentType,agentId)
        # 禁止改代理的列表权限
        banAgentAccess(redis,request,agentType,agentId)
        pipe.execute()
    else:
        log_debug('[%s][agent][create][error] agent account[%s] is exists!'%(curTime,account))
        return {'code':1,'msg':'代理账号(%s)已经存在.'%(account)}

    #创建成功日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['openAgent']%(agentId)}

    writeAgentOpLog(redis,selfUid,logInfo)
    log_debug('[%s][agent][create][success] agent create success! info[%s]'%(curTime,agentInfo))
    return {'code':0,'msg':'创建代理(%s)成功'%(account),'jumpUrl':'/admin/agent/list'}

@admin_app.get('/agent/modify')
@checkAccess
def getAgentModify(redis,session):
    """
        代理修改
    """
    curTime = datetime.now()
    agentId =  request.GET.get('id','').strip()
    lang    = getLang()

    adminTable = AGENT_TABLE%(agentId)
    Type,rate,parentId,account,unitPrice,name,defaultRoomCard = \
                                redis.hmget(adminTable,('type','shareRate','parent_id','account','unitPrice','name','defaultRoomCard'))
    parentAdminTable = AGENT_TABLE%(parentId)
    #  父代理的属性
    aType,shareRate = redis.hmget(parentAdminTable,('type','shareRate'))
    log_debug('[%s][admin][ag][info] modify ag.parentId[%s]'%(curTime,agentId))
    ownGames = getAgentOwnGames(redis,agentId)

    access = getListAccess(Type,lang)
    banAccess = getListBanAccess(redis,agentId)

    info = {
            'title'                  :       '修改代理（上级代理:%s）'%(parentId),
            'agentId'                :       agentId,
            'aType'                  :       aType,
            'backUrl'                :       BACK_PRE+'/agent/list',
            'submitUrl'              :       BACK_PRE+'/agent/modify',
            'games'                  :       getAgentGames(redis,parentId,agentId),
            'ownGames'               :       ownGames,
            'shareRate'              :       shareRate,
            'unitPrice'              :       unitPrice,
            'rate'                   :       rate,
            'account'                :       account,
            'name'                   :       name,
            'defaultRoomCard'        :       defaultRoomCard if defaultRoomCard else 0,
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH
    }

    return template('admin_agent_modify',Access=access,banAccess=banAccess,info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/agent/modify')
@checkAccess
def do_agModify(redis,session):
    """
        修改代理操作
    """
    curTime = datetime.now()
    agentId = request.forms.get('agentId','').strip()
    account = request.forms.get('account','').strip()
    unitPrice = request.forms.get('unitPrice','').strip()
    shareRate = request.forms.get('shareRate','').strip()
    myRate = request.forms.get('myRate','').strip()
    name = request.forms.get('name','').strip()
    defaultRoomCard = request.forms.get('defaultRoomCard','').strip()
    if not agentId:
        return {'code':1,'msg':'非法修改代理!'}

    # agentparentId = redis.get(AGENT_ACCOUNT_TO_ID%(parentAg))
    #当前修改的是

    aType,aName = redis.hmget(AGENT_TABLE%(agentId),('type','name'))
    log_debug('[%s][agent][modify][info] try to modify agent.agentId[%s] account[%s]'\
                    %(curTime,agentId,account))

    # checkFields = [
    #     {'field':account,'msg':'代理账号不能为空'},
    #     {'field':passwd,'msg':'密码不能为空'},
    #     {'field':comfirPasswd,'msg':'密码不能为空'}
    # ]


    # for field in checkFields:
    #     if not field['field']:
    #         return {'code':1,'msg':field['msg']}

    if unitPrice and shareRate:
        if float(shareRate) > float(unitPrice):
            return {'code':1,'msg':'给下级分成不能大于钻石单价!'}
    if myRate and shareRate:
        if float(shareRate) > float(myRate):
            return {'code':1,'msg':'给下级分成不能大于父代理的分成!'}
    pipe = redis.pipeline()
    adminTable  =  AGENT_TABLE%(agentId)
    agentInfo = {
                'shareRate'             :           shareRate,
                'unitPrice'             :           unitPrice,
                'name'                  :           name,
                'defaultRoomCard'       :           defaultRoomCard,
        }
    if unitPrice:
        pipe.sadd(AGENT_ROOMCARD_PER_PRICE%(agentId),unitPrice)
    if shareRate:
        pipe.sadd(AGENT_RATE_SET%(agentId),shareRate)
    pipe.hmset(adminTable,agentInfo)
        # 为该代理重新绑定拥有的游戏
    modifyAgentGames(request,redis,agentId)
    # 修改代理的禁用列表权限
    banAgentAccessModify(redis,request,aType,agentId)
    pipe.execute()

    #创建成功日志
    log_debug('[%s][agent][modify][success] agent create success! info[%s]'%(curTime,agentInfo))
    return {'code':0,'msg':'修改代理(%s)成功'%(account),'jumpUrl':'/admin/agent/list'}

@admin_app.get('/agent/freeze')
@checkAccess
def do_agFreeze(redis,session):
    """
        代理冻结
    """
    curTime = datetime.now()
    lang    = getLang()
    selfAccount,selfUid = session['account'],session['id']

    agentId = request.GET.get('id','').strip()

    adminTable = AGENT_TABLE%(agentId)
    if not redis.exists(adminTable):
        log_debug('[%s][agent][freeze][error] agent[%s] is not exists!'%(curTime,agentId))
        return abort(403)

    if redis.hget(adminTable,'valid') == '1':
        agentFreeze(redis,agentId)
        #记录操作日志
        logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['freezeAgent']%(agentId)}
    else:
        redis.hset(adminTable,'valid','1')
        #记录操作日志
        logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['unfreezeAgent']%(agentId)}

    writeAgentOpLog(redis,selfUid,logInfo)
    return {'code':0,'msg':'(%s)状态更改成功!'%(agentId),'jumpUrl':'/admin/agent/list'}

@admin_app.get('/agent/trail')
@checkAccess
def do_agTrail(redis,session):
    """
    设置公会为试玩
    """
    curTime = datetime.now()
    lang    = getLang()
    selfAccount,selfUid = session['account'],session['id']

    agentId = request.GET.get('id','').strip()

    adminTable = AGENT_TABLE%(agentId)
    if not redis.exists(adminTable):
        log_debug('[%s][agent][trail][error] agent[%s] is not exists!'%(curTime,agentId))
        return {'code':1,'msg':lang.GROUP_NOT_EXISTS_TXT%(agentId)}

    if redis.hget(adminTable,'isTrail') == '0':
        doAgentChange(redis,agentId,'isTrail',1)
        #记录操作日志
        logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['trailAgent']%(agentId)}
    else:
        doAgentChange(redis,agentId,'isTrail',0)
        #记录操作日志
        logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                        'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['unTrailAgent']%(agentId)}

    writeAgentOpLog(redis,selfUid,logInfo)
    return {'code':0,'msg':lang.GROUP_STATUS_SETTING_SUCCESS%(agentId),'jumpUrl':BACK_PRE+'/agent/list'}

@admin_app.get('/agent/recharge')
@checkAccess
def do_agRecharge(redis,session):
    """
    设置公会是否能给会员充卡接口
    """
    curTime = datetime.now()
    lang    = getLang()
    selfAccount,selfUid = session['account'],session['id']
    agentId = request.GET.get('id','').strip()

    login_info_dict = {
            '0'             :       'rechargeAg',
            '1'             :       'unRechargeAg'
    }

    adminTable = AGENT_TABLE%(agentId)
    if not redis.exists(adminTable):
        log_debug('[%s][agent][trail][error] agent[%s] is not exists!'%(curTime,agentId))
        return {'code':1,'msg':lang.GROUP_NOT_EXISTS_TXT%(agentId)}

    re_status = redis.hget(adminTable,'recharge')
    if not re_status:
        re_status = '1'

    if re_status == '0':
        doAgentChange(redis,agentId,'recharge',1)
    else:
        doAgentChange(redis,agentId,'recharge',0)

    #记录操作日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                    'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE[login_info_dict[re_status]]%(agentId)}
    writeAgentOpLog(redis,selfUid,logInfo)
    return {'code':0,'msg':lang.GROUP_RECHARGE_SETTING_SUCCESS%(agentId),'jumpUrl':BACK_PRE+'/agent/list'}

@admin_app.get('/agent/auto_check')
@checkAccess
def do_Auto(redis,session):
    """
    设置公会是否能给会员充卡接口
    """
    curTime = datetime.now()
    lang    = getLang()
    selfAccount,selfUid = session['account'],session['id']
    agentId = request.GET.get('id','').strip()

    login_info_dict = {
            '0'             :       'autocheck',
            '1'             :       'unAutocheck'
    }

    adminTable = AGENT_TABLE%(agentId)
    if not redis.exists(adminTable):
        log_debug('[%s][agent][trail][error] agent[%s] is not exists!'%(curTime,agentId))
        return {'code':1,'msg':lang.GROUP_NOT_EXISTS_TXT%(agentId)}

    auto_check = redis.hget(adminTable,'auto_check')
    if not auto_check:
        auto_check = '1'

    if auto_check == '0':
        doAgentChange(redis,agentId,'auto_check',1)
    else:
        doAgentChange(redis,agentId,'auto_check',0)

    #记录操作日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                    'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE[login_info_dict[auto_check]]%(agentId)}
    writeAgentOpLog(redis,selfUid,logInfo)
    return {'code':0,'msg':lang.GROUP_CHECK_SETTING_SUCCESS,'jumpUrl':BACK_PRE+'/agent/list'}

@admin_app.get('/agent/create_auth')
@checkAccess
def do_createAuth(redis,session):
    """
    是否允许公会创建三级公会
    """
    curTime = datetime.now()
    lang    = getLang()
    selfAccount,selfUid = session['account'],session['id']
    agentId = request.GET.get('id','').strip()

    login_info_dict = {
            '0'             :       'createAuth',
            '1'             :       'unCreateAuth'
    }

    adminTable = AGENT_TABLE%(agentId)
    if not redis.exists(adminTable):
        log_debug('[%s][agent][trail][error] agent[%s] is not exists!'%(curTime,agentId))
        return {'code':1,'msg':lang.GROUP_NOT_EXISTS_TXT%(agentId)}

    create_auth = redis.hget(adminTable,'create_auth')
    if not create_auth:
        create_auth = '0'

    if create_auth == '0':
        doAgentChange(redis,agentId,'create_auth',1)
    else:
        doAgentChange(redis,agentId,'create_auth',0)

    #记录操作日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                    'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE[login_info_dict[create_auth]]%(agentId)}
    writeAgentOpLog(redis,selfUid,logInfo)
    return {'code':0,'msg':lang.GROUP_CHECK_SETTING_SUCCESS,'jumpUrl':BACK_PRE+'/agent/list'}

@admin_app.get('/agent/open_auth')
@checkAccess
def do_openAuth(redis,session):
    """
    是否允许有权限的玩家代开房
    """
    curTime = datetime.now()
    lang    = getLang()
    selfAccount,selfUid = session['account'],session['id']
    agentId = request.GET.get('id','').strip()

    login_info_dict = {
            '0'             :       'openAuth',
            '1'             :       'unOpenAuth'
    }

    adminTable = AGENT_TABLE%(agentId)
    if not redis.exists(adminTable):
        log_debug('[%s][agent][trail][error] agent[%s] is not exists!'%(curTime,agentId))
        return {'code':1,'msg':lang.GROUP_NOT_EXISTS_TXT%(agentId)}

    open_auth = redis.hget(adminTable,'open_auth')
    if not open_auth:
        open_auth = '0'

    if open_auth == '0':
        redis.hset(adminTable,'open_auth',1)
        #doAgentChange(redis,agentId,'open_auth',1)
    else:
        redis.hset(adminTable,'open_auth',0)

    #记录操作日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                    'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE[login_info_dict[open_auth]]%(agentId)}
    writeAgentOpLog(redis,selfUid,logInfo)
    return {'code':0,'msg':lang.GROUP_CHECK_SETTING_SUCCESS,'jumpUrl':BACK_PRE+'/agent/list'}

@admin_app.get('/agent/member/curOnline')
@checkAccess
def getCurOnline(redis,session):
    """
        获取在线用户
    """
    lang    =  getLang()
    curTime =  datetime.now()
    isList  =  request.GET.get('list','').strip()

    if isList:
        onlineInfos = getMemberOnlineList(redis,lang,session['id'])
        return json.dumps(onlineInfos)
    else:
        info = {
                'title'                  :           '会员实时在线',
                'listUrl'                :           BACK_PRE+'/agent/member/curOnline?list=1',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }

        return template('admin_member_online',info=info,lang=lang,RES_VERSION=RES_VERSION)


@admin_app.get('/agent/checkBuyCard')
def getAgentCardRefresh(redis,session):
    """
    轮询检查下级代理向自己是否购买钻石
    """
    curTime = datetime.now()
    selfUid = session['id']
    if selfUid == '1':
        pass
    number = request.GET.get('number','').strip()
    buyOrderTable = AGENT_SALEPENDING_ORDER_LIST%(selfUid,curTime.strftime('%Y-%m-%d'))
    if not redis.exists(buyOrderTable):
        return {'code':2,'orderNo':0}
    orderNo = redis.llen(buyOrderTable)

    if int(number) > orderNo:
        return {'code':2,'orderNo':orderNo}
    elif int(number) < orderNo:
        return {'code':0,'msg':'您有%s笔未处理的订单'%(orderNo),'orderNo':orderNo,'jumpUrl':BACK_PRE+'/order/sale/record'}
    else :
        return {'code':3}

@admin_app.get('/agent/cardRefresh')
def getAgentCardRefresh(redis,session):
    """
    会员钻石刷新
    """
    curTime = datetime.now()
    selfAccount,selfUid = session['account'],session['id']

    adminTable = AGENT_TABLE%(selfUid)

    roomCards,aType = redis.hmget(adminTable,('roomcard','type'))
    if not aType:
        return {'roomCard':'会话信息超时'}

    if int(aType) in [SYSTEM_ADMIN]:
        return {'roomCard':'无限制'}

    return {'roomCard':roomCards}

@admin_app.get('/agent/comfirmJoin')
def getComfirmJoin(redis,session):
    """
    确认加入
    """
    curTime = datetime.now()

    selfAccount,selfUid = session['account'],session['id']

    memberIds = redis.lrange(JOIN_GROUP_LIST%(selfUid),0,-1)
    pipe = redis.pipeline()
    for memberId in memberIds:
        if int(memberId) <= 0:
            continue
        status = redis.get(JOIN_GROUP_RESULT%(memberId)).split(':')[1]
        if int(status) == 0:
            status = 1
            pipe.set(JOIN_GROUP_RESULT%(memberId),"%s:%s"%(selfUid,status))
            pipe.sadd(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(selfUid), memberId)
            pipe.hset(FORMAT_USER_TABLE%(memberId),'parentAg',selfUid)
            pipe.lrem(JOIN_GROUP_LIST%(selfUid),memberId)
            pipe.execute()
            return {'code':0,'msg':'会员[%s]审核成功.'%(memberId)}

    return {'code':1}


@admin_app.get('/agent/room/list')
@checkAccess
def getAgentRoomList(redis,session):
    """
        代理直属玩家房间列表
    """
    curTime = datetime.now()
    lang    = getLang()
    isList  = request.GET.get('list','').strip()
    agentId = session['id']

    if isList:
        res = getAgRoomListInfos(redis,session,agentId,lang)
        log_debug('res[%s]'%(res))
        return json.dumps(res)
    else:
        info = {
                'title'                  :       '玩家房间列表',
                'listUrl'                :       BACK_PRE+'/agent/room/list?list=1',
                'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH
        }
        return template('admin_agent_room_list',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/agent/room/kick')
@checkAccess
def getAgentRoomList(redis,session):
    """
        代理直属玩家房间列表 - 强制解散房间
    """
    curTime = datetime.now()
    lang    = getLang()
    roomId  = request.GET.get('id','').strip()
    print 'roomId',roomId
    roomTable = ROOM2SERVER%(roomId)
    try:
        gameId = redis.hget(roomTable,'gameid')
    except:
        return {'code':1,'msg':'房间已解散'}

    sendProtocol2GameService(redis, gameId,HEAD_SERVICE_PROTOCOL_DISSOLVE_ROOM%(roomId))

    return {'code':0,'msg':lang.GAME_DISSOLVE_ROOM_SUCCESS,'jumpUrl':BACK_PRE+'/agent/room/list'}


@admin_app.get('/agent/active')
@checkAccess
def getAgentActive(redis,session):
    """
    下线代理活跃数统计
    """
    curTime  = datetime.now()
    lang     = getLang()
    isList = request.GET.get('list','').strip()
    selfUid  = request.GET.get('id','').strip()
    startDate = request.GET.get('startDate','').strip()
    endDate  =  request.GET.get('endDate','').strip()
    date     =  request.GET.get('date','').strip()

    if date:
        endDate = date

    if not selfUid:
        selfUid = session['id']

    openList = True
    if int(session['type']) in [1,2]:
        openList = False

    if isList:
        report = getAgentActiveReport(redis,selfUid,startDate,endDate)
        return json.dumps(report)
    else:
        info = {
                    'title'         :       '下线代理活跃',
                    'listUrl'                :       BACK_PRE+'/agent/active?list=1',
                    'searchTxt'              :       '请输入公会号',
                    'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH

        }

    return template('admin_agent_active',openList=openList,info=info,lang=lang,RES_VERSION=RES_VERSION)
