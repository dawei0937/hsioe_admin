#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    用户模型
"""
from web_db_define import *
from config.consts import *
from common.log import *
from common.utilt import ServerPagination
from admin import access_module
from datetime import timedelta,datetime
from operator import itemgetter

#在线列表要显示的数据
MEMBER_ONLINE_FIELDS = ('nickname','headImgUrl','parentAg','lastLoginClientType','coin')
#玩家信息列表
MEMBER_LIST_FIELDS = ('name','parentAg','roomCard','nickname','headImgUrl','last_login_date','last_logout_date','valid','open_auth')
#消耗钻石描述
USEDIOMTYPE2DESC = {
    '1'     :       '普通房间',
    '2'     :       '代开房间',
    '3'     :       '解散代开房间',
    '4'     :       '新增房卡',
    '5'     :       '苹果支付购买',
    '6'     :       '试玩接口购买'
}

#会员列表要显示的数据
GM_OP_LIST = [
        {'url':'/admin/member/gm/showHis','method':'GET','txt':'操作记录'},
        {'url':'/admin/member/gm/kick','method':'GET','txt':'移除GM权限'}
]

#排序对应编号
SORT_2_INDEX = {
        'id'                :   0,
        'parentAg'          :   2,
        'roomcard'          :   3,
        'last_login_date'   :   6,
        'last_logout_date'  :   7,
        'open_auth'         :   9,
        'rechargeTotal'     :   10
}
#列表数据缓存时间
LIST_CACHE_TTL = 60 * 5
#列表数据缓存阈值
LIST_CACHE_MAXNUM = 10000

def getMemberOnlineList(redis,lang,agentId):
    """
    获取在线会员列表
    """

    #获取在线会员列表
    adminTable = AGENT_TABLE%(agentId)
    aType, aId =redis.hmget(adminTable, ('type', 'id'))
    members = redis.smembers(ONLINE_ACCOUNTS_TABLE)

    childMemberIds = None
    if int(aType) == PROVINCE_AGENT:
        childMemberIds  =  getAgentAllMemberIds(redis,agentId)
    elif int(aType) in [2,3]:
        childMemberIds  =  redis.smembers(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(agentId))

    memberOlList = []
    for member in members:
        if int(aType) != SYSTEM_ADMIN and not childMemberIds:
            break
        onLineTable = FORMAT_CUR_USER_GAME_ONLINE%(member)
        date,roomTag,serviceTag,ip = redis.hmget(onLineTable,\
                                                        ('date','game','serviceTag','ip'))
        account2user_table = FORMAT_ACCOUNT2USER_TABLE%(member) #从账号获得账号信息，和旧系统一样
        table = redis.get(account2user_table)
        #info = redis.hgetall(table)
        userId = table.split(':')[1]
        if childMemberIds and userId not in childMemberIds:
            continue

        name,imgUrl,parentAg,clientKind,coin = redis.hmget(table,MEMBER_ONLINE_FIELDS)
        if not coin:
            coin = 0
        roomcard = redis.get(USER4AGENT_CARD%(parentAg, userId))

        memberOlList.append({
                'id'            :       userId,
                'account'       :       member,
                'name'          :       name,
                'coin'          :       coin,
                'roomTag'       :       roomTag if roomTag else '正在闲逛',
                'roomCard'      :       roomcard if roomcard else 0,
                'date'          :       date,
                'serverTag'     :       serviceTag,
                'clientKind'    :       lang.CLINET_KIND_TXTS[clientKind] if clientKind else '未知设备',
                'login_ip'      :       ip,
                'parentAg'      :       parentAg
        })

    return {
        'count' :   len(memberOlList),   \
        'data'  :   memberOlList
    }

def getAgentAllMemberIds(redis,agentId):
    """
    通过代理Id获取下线代理(直属所有下线会员) 所有会员列表
    """

    adminTable = AGENT_TABLE%(agentId)
    aType, aId =redis.hmget(adminTable, ('type', 'id'))
    parentTable = AGENT_CHILD_TABLE%(aId)
    subIds = redis.smembers(parentTable)
    TotalMember = []
    for subId in subIds:
        members = getAgentAllMemberIds(redis,subId)
        childMemberIds = redis.smembers(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(subId))
        TotalMember += members
        TotalMember += childMemberIds
    return set(TotalMember)

def getSystemMemberIds(redis,selfUid):
    """
    获取所有会员的ID
    采取缓存策略, 如果命中缓存直接返回缓存
                 没命中的话，如果数据量超过阈值，则进行缓存
    """
    memberIdList = []
    if redis.exists('system:memberIds:cache'):#存在缓存ID,直接返回
        memberIdList = redis.get('system:memberIds:cache')
        return eval(memberIdList)
    else:
        userIdKey = []
        memberIds = redis.smembers(ACCOUNT4WEIXIN_SET)
        for memberId in memberIds:
            table = FORMAT_ACCOUNT2USER_TABLE%(memberId) #从账号获得账号信息，和旧系统一样
            userIdKey.append(table)
        memberIdList = [userId.split(":")[1] for userId in redis.mget(userIdKey)]
        if len(memberIdList) >= LIST_CACHE_MAXNUM:
            #如果大于10000条数据做一个ID缓存
            redis.set('system:memberIds:cache',memberIdList)
            #缓存5分钟
            redis.expire('system:memberIds:cache',LIST_CACHE_TTL)
    return memberIdList

def getMemberList(redis,session,selfUid,searchId,lang,pageSize,pageNumber,sort_name,sort_method):
    """
    获取代理的会员列表
    """
    adminTable = AGENT_TABLE%(selfUid)
    aType, aId =redis.hmget(adminTable, ('type', 'id'))

    type2getMemberIds = {
            0     :       getSystemMemberIds,
            1     :       getAgentAllMemberIds
    }

    if searchId and redis.exists(FORMAT_USER_TABLE%(searchId)):#如果搜索的话
        memberIds = [searchId]
    elif int(aType) in type2getMemberIds.keys():#管理员或者1及代理
        memberIds = type2getMemberIds[int(aType)](redis,selfUid)
    else :#二级,三级代理
        memberTable = FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(selfUid)
        memberIds = redis.smembers(memberTable)

    total_records = len(memberIds)
    membersList,user_info_list = [],[]
    selfAccesses = eval(session['access'])
    log_debug('=================startTime[%s]'%(datetime.now()))
    memberInfos = []

    if not searchId and redis.exists("agent:%s:members:cache"%(selfUid)):#直接从缓存读取
        user_info_list = eval(redis.get("agent:%s:members:cache"%(selfUid)))
    else:
        for memberId in memberIds:
            #获取所有用户信息
            table = FORMAT_USER_TABLE%(memberId) #从账号获得账号信息，和旧系统一样
            memberInfos = redis.hmget(table,MEMBER_LIST_FIELDS)
            memberInfos.insert(0,memberId)
            try:
                memberInfos[3] = int(redis.get(USER4AGENT_CARD%(memberInfos[2],memberInfos[0])))
            except:
                memberInfos[3] = 0
            try:
                memberInfos.insert(10,int(get_sum_rechargeInGroup(redis,memberInfos[2],memberInfos[0])))
            except:
                memberInfos.insert(10,0)
            user_info_list.append(memberInfos)

        if total_records >= LIST_CACHE_MAXNUM:#总记录数大于阈值的才需要缓存
            redis.set("agent:%s:members:cache"%(selfUid),user_info_list)
            redis.expire("agent:%s:members:cache"%(selfUid),LIST_CACHE_TTL)

    if sort_name:#如果排序
        log_debug('sorOrder[%s] sortName[%s]'%(sort_name,sort_method))
        user_info_list = sorted(user_info_list, key=itemgetter(SORT_2_INDEX[sort_name]),reverse=FONT_CONFIG['STR_2_SORT'][sort_method])
    #分页渲染
    user_info_list = ServerPagination(user_info_list,pageSize,pageNumber)
    for user_info in user_info_list:
        #MEMBER_LIST_FIELDS = ('name','parentAg','roomCard','nickname','headImgUrl','last_login_date','last_logout_date','valid','open_auth')
        memberInfo = {}
        memberInfo['name'] = user_info[1]
        memberInfo['id'] = user_info[0]
        memberInfo['nickname'] = user_info[4]
        memberInfo['headImgUrl'] = user_info[5]
        memberInfo['last_login_date'] = user_info[6] if user_info[6] else '从未登录'
        memberInfo['last_logout_date'] = user_info[7] if user_info[7] else '从未登录'
        memberInfo['valid'] = user_info[8]
        memberInfo['open_auth'] = user_info[9] if user_info[9] else '0' #默认不开启

        if not user_info[2]:
            memberInfo['roomcard'] = 0
            memberInfo['rechargeTotal'] = 0
            memberInfo['parentAg'] = '无'
        else :
            roomCard = user_info[3]
            memberInfo['roomcard'] = int(roomCard) if roomCard else 0
            memberInfo['parentAg'] = user_info[2]
            memberInfo['rechargeTotal']= user_info[10]
        memberInfo['op'] = []
        for access in access_module.ACCESS_MEMBER_LIST:
            if access.url in selfAccesses:
                if access.url[-4:] == 'kick' and int(aType) == 0 :
                    continue
                elif access.url[-6:] == 'freeze':
                    memberInfo['op'].append({'url':access.url,'txt':'冻结' \
                                if user_info[8] == '1' else '解冻','method':access.method})
                elif access.url[-9:] == 'open_auth':
                    memberInfo['op'].append({'url':access.url,'txt':'关闭代开权限' \
                                if user_info[9] == '1' else '打开代开权限','method':access.method})
                else:
                    memberInfo['op'].append({'url':access.url,'method':access.method,'txt':access.getTxt(lang)})

        membersList.append(memberInfo)
    return {'total':total_records,'result':membersList,}

def getGmList(redis,session,searchId,pageSize,pageNumber):
    """
    获取gm的列表
    """
    gmAccounts = redis.smembers('GMAccount:set')

    if searchId:
        account = redis.hget(FORMAT_USER_TABLE%(searchId),'account')
        gmAccounts = [account]
        gm_list_len = len(gmAccounts)
    else:
        gm_list_len = len(gmAccounts)
        gmAccounts = ServerPagination(gmAccounts,pageSize,pageNumber)

    gm_info_lists = []
    for gmAccount in gmAccounts:
        account2user_table = FORMAT_ACCOUNT2USER_TABLE%(gmAccount) #从账号获得账号信息，和旧系统一样
        table = redis.get(account2user_table)
        if not table :
            aId = '账号未建'
            continue
        else:
            aId = table.split(':')[1]
        name,parentAg = redis.hmget(table,('nickname','parentAg'))
        gmInfo = {}
        gmInfo['id']       =   aId
        gmInfo['name']     =   name
        gmInfo['parentAg'] =   parentAg
        gmInfo['account']  =   gmAccount
        gmInfo['op']       =   GM_OP_LIST
        gm_info_lists.append(gmInfo)

    return {'total':gm_list_len,'result':gm_info_lists}

def getmemberApplyList(redis,agentId):
    """
    获取公会申请列表
    @params:
        redis    :  redis链接实例
        agentId  :  代理ID
    """
    memberIds = redis.lrange(JOIN_GROUP_LIST%(agentId),0,-1)
    applyList = []
    for memberId in memberIds:
        applyInfo = {}
        userJoinInfo = redis.get(JOIN_GROUP_RESULT%(memberId))
        if not userJoinInfo:
            continue
        status = userJoinInfo.split(':')[1]
        try:
            time = redis.get(JOIN_GROUP_RESULT%(memberId)).split(':')[2]
        except:
            time = ''
        if int(status) == 0:
            name,account,headImgUrl = redis.hmget(FORMAT_USER_TABLE%(memberId),('nickname','account','headImgUrl'))
            applyInfo['id'] = memberId
            applyInfo['name'] = name
            applyInfo['time'] = time
            applyInfo['headImgUrl'] = headImgUrl
            applyInfo['op'] = [{'url':'/admin/member/join/comfirm','txt':'审核通过','method':'POST'},\
                               {'url':'/admin/member/join/reject','txt':'拒绝','method':'POST'}]
            applyList.append(applyInfo)

    return applyList

def memberJoinComfirm(redis,agentId,memberId):
    """
    审核会员加入公会
    @params:
        redis    redis链接实例
        agentId  公会ID
        memberId  申请加入公会的会员ID
    """
    pipe = redis.pipeline()
    pipe.set(JOIN_GROUP_RESULT%(memberId),"%s:%s"%(agentId,1))
    pipe.hset(FORMAT_USER_TABLE%(memberId),'parentAg',agentId)
    pipe.sadd(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(agentId), memberId)
    pipe.lrem(JOIN_GROUP_LIST%(agentId),memberId)
    pipe.execute()

def getMemberUseCardsByDay(redis,startDate,endDate,memberId):
    """
    获取会员每日消耗钻石数
    """
    if not memberId:
        return {'data':{},'count':0}

    log_debug('[getMemberUseCardsByDay][FUNC] memberId[%s] startDate[%s] endDate[%s]'%(memberId,startDate,endDate))
    nickname,headImgUrl,parentAg= redis.hmget(FORMAT_USER_TABLE%(memberId),('nickname','headImgUrl','parentAg'))
    try:
        startDate = datetime.strptime(startDate,'%Y-%m-%d')
        endDate   = datetime.strptime(endDate,'%Y-%m-%d')
    except:
        weekDelTime = timedelta(7)
        weekBefore = datetime.now()-weekDelTime
        startDate = weekBefore
        endDate   = datetime.now()

    deltaTime = timedelta(1)
    res = []
    while endDate >= startDate:
        searchData = endDate.strftime('%Y-%m-%d')
        datas = redis.lrange(PLAYER_DAY_USE_CARD%(memberId,searchData),0,-1)
        log_debug('[getMemberUseCardsByDay][FUNC] searchDate[%s] memberId[%s] db[%s] data[%s]'%(searchData,memberId,PLAYER_DAY_USE_CARD%(memberId,searchData),datas))
        for data in datas:
            dataInfo = {}
            typeInfo = data.split(';')
            dataInfo['date'] = searchData
            dataInfo['headImgUrl'] = headImgUrl
            dataInfo['parentAg'] = parentAg
            dataInfo['useCards'] = typeInfo[0]
            dataInfo['useType'] = USEDIOMTYPE2DESC[typeInfo[1]]
            dataInfo['totalCards'] = typeInfo[2]
            dataInfo['roomId'] = typeInfo[len(typeInfo)-1] if len(typeInfo)>=4 else '-'
            res.append(dataInfo)
        endDate -= deltaTime
    #res = sorted(res, key=itemgetter('date','active','id'),reverse=True)
    return {'data':res,'count':len(res),'name':nickname,'headImgUrl':headImgUrl}

def get_sum_rechargeInGroup(redis,group_id,user_id):
    """
    获取会员在改代理下的充值总额
    params: redis,group_id,user_id
    """
    total = redis.get(USER4AGENT_RECHARGE%(group_id,user_id))
    if not total:
        total = 0

    return int(total)

def get_gm_op_list(redis,user_id):
    """
    获取会员的GM记录
    params: reids,user_id
    """
    log_debug('[try get_gm_op_list]  user_id[%s]'%(user_id))
    gm_op_table = GM_CONTROL_DATA%(user_id)
    if not redis.exists(gm_op_table):
        return {'data':[],'count':0}

    op_lists = redis.lrange(gm_op_table,0,-1)
    log_debug('[try get_gm_op_list] op_lists[%s]'%(op_lists))

    res = []
    for op_list in op_lists:
        res.append(eval(op_list))

    return {'data':res,'count':len(res)}

def doMemberFieldChange(redis,memberId,field,change):
    """
    设置会员字段
    """
    log_debug('[try doMemberFieldChange]')
    pipe = redis.pipeline()
    memberTable = FORMAT_USER_TABLE%(memberId)
    pipe.hset(memberTable,field,change)

    pipe.execute()

def get_user_open_auth(redis,user_open_auth,agent_open_auth):
    """
    获取会员的代开房间权限
    """
    if not user_open_auth:
        user_open_auth  = 0
    if not agent_open_auth:
        agent_open_auth = 0

    open_room = 0
    if agent_open_auth == '1':
        #如果代理开启代开房间权限
        #会员必须有权限才能代开
        open_room = int(user_open_auth)
    else:#如果代理没开启,则默认可以代开房间,无论是否有权限
        open_room = 1

    return open_room

def do_user_modify_addr(redis,user_id,addr_info):
    '''
    修改收获地址
    '''
    log_debug('[try do_user_modify_addr]')
    user_addr_table = FORMAT_USER_ADDRESS_TABLE%(user_id)
    return redis.hmset(user_addr_table,addr_info)

def do_user_del_addr(redis,user_id,addr_info):
    '''
    删除收获地址
    '''
    user_addr_table = FORMAT_USER_ADDRESS_TABLE%(user_id)
    if redis.exists(user_addr_table):
        return redis.delete(user_addr_table)
    return

def get_user_exchange_list(redis,user_id,exchange_fields):
    '''
    获取用户兑换奖品记录
    '''
    user_exchange_table = FISH_USER_EXCHANGE_LIST%(user_id)
    if not redis.exists(user_exchange_table):
        return

    user_change_ids = redis.lrange(user_exchange_table,0,-1)
    user_exchange_keys = [FISH_EXCHANGE_TABLE%(user_change_id) for user_change_id in user_change_ids]
    user_exchange_lists = redis.mget(user_exchange_keys)

    user_exchange_info = []
    for user_exchange_list in user_exchange_lists:
        if type(user_exchange_list) in [str,list]:
            exchange_info = eval(user_exchange_list)
            leave_info = {}
            for field in exchange_fields:
                leave_info[field] = exchange_info[field] if field in exchange_info.keys() else ''
            user_exchange_info.append(leave_info)
        else:
            log_debug('[try get_user_exchange_list] get error [%s]'%(user_exchange_list))
    #for tempStartDate
    return user_exchange_info
