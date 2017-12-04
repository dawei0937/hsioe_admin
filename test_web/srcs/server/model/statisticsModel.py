#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    统计模型
"""
from web_db_define import *
from config.consts import *
from common.log import *
from admin import access_module
import agentModel
from model.userModel import *
from datetime import timedelta,datetime
from operator import itemgetter
#from model.userModel import getAgentAllMemberIds


ACTIVE_OP_LIST = [
        {'url':'/admin/statistics/active/showDay','txt':'查看详细','method':'GET'}
]

def getAllChildAgentId(redis,agentId):
    """
    返回所有下级代理ID
    """
    agentIdList = []
    pipe = redis.pipeline()
    downLines = redis.smembers(AGENT_CHILD_TABLE%(agentId))
    log_debug('[agentModel][Func][getAllChildAgentId] agentId[%s] downlines[%s]'%(agentId,downLines))

    if downLines:
        for downline in downLines:
            agentIdList.append(downline)
            subDownlines = redis.smembers(AGENT_CHILD_TABLE%(downline))
            if subDownlines:
                for subDownline in subDownlines:
                    agentIdList.append(subDownline)

    log_debug('[agentModel][Func][getAllChildAgentId] agentId[%s] allChildIds[%s]'%(agentId,agentIdList))
    return agentIdList

def getDateTotal(redis,agentId,agentIds,endDate,startDate):
    """
    获取某段时间内的总数
    """
    deltaTime = timedelta(1)
    count = 0
    for aid in agentIds:
        nums = redis.get(DAY_ALL_PLAY_COUNT%(endDate,aid))
        if not nums:
            nums = 0
        count+=int(nums)
    #log_debug('[getDateTotal] startDate[%s],endDate[%s] agentIds[%s] count[%s]'%(startDate,endDate,agentIds,count))
    return count

def getCountTotal(redis,agentId,dateStr):
    """
    获取总局数统计数据
    """

    #返回所有下级ID

    parentTable = AGENT_CHILD_TABLE%(agentId)
    agentIds = redis.smembers(parentTable)
    if not agentIds:
        agentIds = [agentId]

    deltaTime = timedelta(1)
    res = []
    totalCount = 0
    for agent_id in agentIds:
        agentDetail = redis.hgetall(AGENT_TABLE%(agent_id))
        count = redis.get(DAY_ALL_PLAY_COUNT%(dateStr,agent_id))
        if not count:
            count = 0
        count = int(count)
        parentTable = AGENT_CHILD_TABLE%(agent_id)
        agent_ids = redis.smembers(parentTable)
        count+=getDateTotal(redis,agent_id,agent_ids,dateStr,dateStr)
        totalCount+=count
        #log_debug('[getAgentActiveReport][FUNC] agentIds[%s] list[%s]'%(agent_id,DAY_AG_LOGIN_COUNT%(agent_id,agentInfo['date'])))

    return int(totalCount)

def get_login_count(redis,selfUid,dateStr,agentIds):
    """
    获取代理当天登录人数统计
    """
    log_debug('--------------------------[%s][%s]'%(selfUid,dateStr))
    login_count = 0
    if int(selfUid) == 1:
        login_count = redis.scard(FORMAT_LOGIN_DATE_TABLE%(dateStr))
    else:
        for _agentId in agentIds:
            count = redis.get(DAY_AG_LOGIN_COUNT%(_agentId,dateStr))
            if not count:
                count = 1
            login_count+=int(count)
    if not login_count:
        login_count = 0
    log_debug('[try get_login_count] agentIds[%s] login_count[%s]'%(agentIds,login_count))
    return int(login_count)

def get_take_count(redis,selfUid,dateStr):
    """
    获取代理日消耗砖石统计
    """
    if selfUid == '1':
        regTable = DAY_ALL_PLAY_ROOM_CARD%(dateStr)
        take_count = redis.get(regTable)
    else:
        take_count = agentModel.getAgentRoomByDay(redis,selfUid,dateStr)
    if not take_count:
        take_count = 0
    log_debug('[try get_take_count] agentIds[%s] take_count[%s]'%(selfUid,take_count))
    return int(take_count)

def get_active_reports(redis,startDate,endDate,selfUid):
    """
    获取活跃人数数据
    """
    try:
        startDate = datetime.strptime(startDate,'%Y-%m-%d')
        endDate   = datetime.strptime(endDate,'%Y-%m-%d')
    except:
        weekDelTime = timedelta(7)
        weekBefore = datetime.now()-weekDelTime
        startDate = weekBefore
        endDate   = datetime.now()

    deltaTime = timedelta(1)
    if int(selfUid) == 1:
        agentIds = []
    else:
        agentIds = getAllChildAgentId(redis,selfUid)

    res = []
    now_time = datetime.now()
    while endDate >= startDate:
        active_info = {}
        if endDate >= now_time:
            endDate -= deltaTime
            continue
        dateStr = endDate.strftime('%Y-%m-%d')
        login_count = get_login_count(redis,selfUid,dateStr,agentIds)
        take_card  = get_take_count(redis,selfUid,dateStr)
        take_count  = getCountTotal(redis,selfUid,dateStr)
        active_info['login_count'] = login_count
        active_info['take_count'] = take_count
        active_info['take_card'] = take_card
        active_info['date'] = dateStr
        active_info['op'] = ACTIVE_OP_LIST

        res.append(active_info)
        endDate -= deltaTime

    return {'data':res,'count':len(res)}

def get_login_list(redis,agentId,reg_date):
    """
        获取某个时间段注册人数详情
        params:
            [ reg_date ] : 某一天

    """

    registMemberList =  redis.smembers(FORMAT_LOGIN_DATE_TABLE%(reg_date))

    adminTable = AGENT_TABLE % (agentId)
    aType, aId =redis.hmget(adminTable, ('type', 'id'))

    type2getMemberIds = {
            0     :       getSystemMemberIds,
            1     :       getAgentAllMemberIds
    }

    memberIds = None
    if int(aType) == 1:
        memberIds = type2getMemberIds[int(aType)](redis,agentId)
    elif int(aType) > 1 :
        memberTable = FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(agentId)
        memberIds = redis.smembers(memberTable)

    res = []
    member_id_keys = []
    for member in registMemberList:
        account2user_table = FORMAT_ACCOUNT2USER_TABLE%(member)
        member_id_keys.append(account2user_table)

    #获取会员ID
    member_id_lists = [user_id.split(":")[1] for user_id in redis.mget(member_id_keys)]
    for member_id in member_id_lists:
        if memberIds and member_id not in memberIds:
            continue
        memberInfo = {}
        use_count = redis.hget(PLAYER_DAY_DATA%(member_id,reg_date),'roomCard')
        if not use_count:
            use_count = 0
        table = FORMAT_USER_TABLE%(member_id) #从账号获得账号信息，和旧系统一样
        name,nickname,regIp,parentAg = \
        redis.hmget(table,('name','nickname','regIp','parentAg'))
        memberInfo['name'] = name
        memberInfo['nickname'] = nickname
        memberInfo['id'] = member_id
        memberInfo['parentAg'] = parentAg
        memberInfo['use_count'] = use_count

        res.append(memberInfo)
    return res
