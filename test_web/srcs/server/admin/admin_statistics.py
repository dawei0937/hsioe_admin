#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    数据统计模块
"""
from bottle import *
from admin import admin_app
from config.consts import  STATIC_LAYUI_PATH,STATIC_ADMIN_PATH,BACK_PRE,RES_VERSION
from common.utilt import *
from common.log import *
from datetime import datetime
from web_db_define import *
from model.orderModel import *
from model.agentModel import *
from model.statisticsModel import *
from model.userModel import *
import json


@admin_app.get('/statistics/buyReport')
@checkAccess
def getBuyReport(redis,session):
    """
    获取代理的订单报表
    """
    lang      = getLang()

    isList = request.GET.get('list','').strip()
    startDate = request.GET.get('startDate','').strip()
    endDate = request.GET.get('endDate','').strip()

    selfAccount,selfUid = session['account'],session['id']

    if not startDate or not endDate:
        #默认显示一周时间
        startDate,endDate = getDaya4Week()

    if isList:
        reports = getBuyCardReport(redis,selfUid,startDate,endDate)
        return json.dumps(reports)
    else:
        info = {
                'title'         :    '[%s]购钻报表'%(selfAccount),
                'searchStr'     :    '',
                'showLogType'   :    '',
                'startDate'     :    startDate,
                'endDate'       :    endDate,
                'listUrl'       :    BACK_PRE+'/statistics/buyReport?list=1',
                'STATIC_LAYUI_PATH'      :   STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :   STATIC_ADMIN_PATH
        }

        return template('admin_report_buy',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/statistics/saleReport')
@checkAccess
def getSaleReport(redis,session):
    """
    获取代理的订单报表
    """
    lang      = getLang()

    isList = request.GET.get('list','').strip()
    startDate = request.GET.get('startDate','').strip()
    endDate = request.GET.get('endDate','').strip()

    selfAccount,selfUid = session['account'],session['id']

    if not startDate or not endDate:
        #默认显示一周时间
        startDate,endDate = getDaya4Week()

    if isList:
        reports = getSaleCardReport(redis,selfUid,startDate,endDate)
        return json.dumps(reports)
    else:
        info = {
                'title'         :    '[%s]售钻报表'%(selfAccount),
                'searchStr'     :    '',
                'showLogType'   :    '',
                'startDate'     :    startDate,
                'endDate'       :    endDate,
                'listUrl'       :    BACK_PRE+'/statistics/saleReport?list=1',
                'STATIC_LAYUI_PATH'      :   STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :   STATIC_ADMIN_PATH
        }

        return template('admin_report_sale',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/statistics/allAgentSaleReport')
@checkAccess
def getAgentSaleReport(redis,session):
    """
    获取下线代理的售钻订单报表
    """
    lang      = getLang()

    isList = request.GET.get('list','').strip()
    startDate = request.GET.get('startDate','').strip()
    endDate = request.GET.get('endDate','').strip()
    group_id = request.GET.get('group_id','').strip()

    selfAccount,selfUid = session['account'],session['id']

    if not startDate or not endDate:
        #默认显示一周时间
        startDate,endDate = getDaya4Week()

    if isList:
        reports = getAgentSaleCardReport(redis,selfUid,startDate,endDate,group_id)
        return json.dumps(reports)
    else:
        info = {
                'title'         :    '[%s]的下线代理售钻报表'%(selfAccount),
                'searchStr'     :    '',
                'showLogType'   :    '',
                'startDate'     :    startDate,
                'endDate'       :    endDate,
                'group_search'  :    True,#开启代理查询
                'listUrl'       :    BACK_PRE+'/statistics/allAgentSaleReport?list=1',
                'STATIC_LAYUI_PATH'      :   STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :   STATIC_ADMIN_PATH
        }

        return template('admin_report_agent_sale',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/statistics/allAgentBuyReport')
@checkAccess
def getAgentBuyReport(redis,session):
    """
    获取下线代理的购钻订单报表
    """
    lang      = getLang()

    isList = request.GET.get('list','').strip()
    startDate = request.GET.get('startDate','').strip()
    endDate = request.GET.get('endDate','').strip()
    group_id = request.GET.get('group_id','').strip()

    selfAccount,selfUid = session['account'],session['id']

    if not startDate or not endDate:
        #默认显示一周时间
        startDate,endDate = getDaya4Week()

    if isList:
        reports = getAgentBuyCardReport(redis,selfUid,startDate,endDate,group_id)
        return json.dumps(reports)
    else:
        info = {
                'title'         :    '[%s]的下线代理购钻报表'%(selfAccount),
                'searchStr'     :    '',
                'showLogType'   :    '',
                'startDate'     :    startDate,
                'endDate'       :    endDate,
                'group_search'  :    True,#开启代理查询
                'listUrl'       :    BACK_PRE+'/statistics/allAgentBuyReport?list=1',
                'STATIC_LAYUI_PATH'      :   STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :   STATIC_ADMIN_PATH
        }

        return template('admin_report_agent_buy',info=info,lang=lang,RES_VERSION=RES_VERSION)



def getTimeList(begin_date,end_date):
    date_list = []
    begin_date = datetime.strptime(begin_date, "%Y-%m-%d")
    end_date = datetime.strptime(end_date, "%Y-%m-%d")
    while begin_date <= end_date:
        date_str = begin_date.strftime("%Y-%m-%d")
        date_list.append(date_str)
        begin_date += timedelta(days=1)
    return date_list


def getNextRateReportInfo(redis,selfUid,date,unitPrice):
    """
    获取下线抽成的列表(循环查询)
    """
    NextAgentIds=redis.smembers(AGENT_CHILD_TABLE%(selfUid))
    log_debug('NextAgentIds[%s]'%(NextAgentIds))
    RateReportList = []
    for NextAgentId in NextAgentIds:
        agentTable = AGENT_TABLE%(NextAgentId)
        aType,parentId = redis.hmget(agentTable,('type','parent_id'))
        log_debug('NextAgentId[%s] aType[%s] parentId[%s]'%(NextAgentId,aType,parentId))
        if aType == '2':
            agentPerPriceList  =  redis.smembers(AGENT_ROOMCARD_PER_PRICE%(parentId))
        else:
            agentPerPriceList  =  redis.smembers(AGENT_ROOMCARD_PER_PRICE%(NextAgentId))
        agentRateList =  redis.smembers(AGENT_RATE_SET%(NextAgentId))
        for price in agentPerPriceList:
            log_debug('price[%s]'%(price))
            for rate in agentRateList:
                agentRateTable = AGENT_RATE_DATE%(NextAgentId,rate,price,date)
                if redis.exists(agentRateTable):
                    agentRate = redis.hgetall(agentRateTable)
                    agentRate['date'] = date
                    agentRate['id'] = NextAgentId
                    RateReportList.append(agentRate)

    log_debug('[RateReportList] selfUid[%s] RateReportList[%s]'%(selfUid,RateReportList))
    return RateReportList


def getRateReportInfo(redis,selfUid,startDate,endDate):
    """
    获取抽成的列表
    """
    date_list = getTimeList(startDate,endDate)
    RateReportList = []
    agentTable = AGENT_TABLE%(selfUid)
    aType,parentId = redis.hmget(agentTable,('type','parent_id'))
    numberTotal = 0
    rateTotal = 0
    superTotal = 0
    for date in date_list:
        if aType == '0':
            agentRateTable = AGENT_COMPAY_RATE_DATE%(selfUid,date)
            if redis.exists(agentRateTable):
                agentRate = redis.hgetall(agentRateTable)
                agentRate['date'] = date
                agentRate['id'] = selfUid
                RateReportList.append(agentRate)
                numberTotal += int(agentRate['number'])
                rateTotal += round(float(agentRate['rateTotal']),2) if 'rateTotal' in agentRate.keys() else 0.00
        else:
            if aType == '2':
                agentPerPriceList  =  redis.smembers(AGENT_ROOMCARD_PER_PRICE%(parentId))
            else:
                agentPerPriceList  =  redis.smembers(AGENT_ROOMCARD_PER_PRICE%(selfUid))

            log_debug('[agentPerList][%s]'%(agentPerPriceList))
            agentRateList =  redis.smembers(AGENT_RATE_SET%(selfUid))
            for price in agentPerPriceList:
                for rate in agentRateList:
                    agentRateTable = AGENT_RATE_DATE%(selfUid,rate,price,date)
                    log_debug('[agentRateTable] selfUid[%s] agentRateTable[%s]'%(selfUid,agentRateTable))
                    if redis.exists(agentRateTable):
                        agentRate = redis.hgetall(agentRateTable)
                        agentRate['date'] = date
                        agentRate['id'] = selfUid
                        RateReportList.append(agentRate)
                        numberTotal += int(agentRate['number'])
                        rateTotal += round(float(agentRate['rateTotal']),2)
                        superTotal += round(float(agentRate['superRateTotal']),2)

    log_debug('[agentRateTable] selfUid[%s] agentRateTable[%s]'%(selfUid,agentRateTable))
    return {'date':RateReportList,'numberTotal':numberTotal,'rateTotal':rateTotal,'superTotal':superTotal}

@admin_app.get('/statistics/rateReport')
@checkAccess
def getRateReport(redis,session):
    """
    获取代理的利润分成报表
    """
    lang  =  getLang()
    isList = request.GET.get('list','').strip()

    startDate = request.GET.get('startDate','').strip()
    endDate = request.GET.get('endDate','').strip()
    selfUid = request.GET.get('id','').strip()
    date = request.GET.get('date','').strip()
    unitPrice = request.GET.get('unitPrice','').strip()


    log_debug('[STATISTICS][rateReport][info] selfUid[%s] date[%s]'%(selfUid,date))
    if selfUid and date and unitPrice:
        reports = getNextRateReportInfo(redis,selfUid,date,unitPrice)
        return json.dumps(reports)

    if not selfUid:
        selfUid  =  session['id']

    selfAccount = session['account']
    agentTable = AGENT_TABLE%(selfUid)
    aType = redis.hget(agentTable,('type'))
    if isList:
        reports = getRateReportInfo(redis,selfUid,startDate,endDate)
        return json.dumps(reports)
    else:
        info = {
                    'title'         :       '[%s]销售利润报表'%(selfAccount),
                    'startDate'     :       startDate,
                    'endDate'       :       endDate,
                    'listUrl'       :       BACK_PRE+'/statistics/rateReport?list=1',
                    'STATIC_LAYUI_PATH'  :   STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'  :   STATIC_ADMIN_PATH,
                    'aType'              :  aType
        }

        return template('admin_report_rate',info=info,lang=lang,RES_VERSION=RES_VERSION)



def getRegCountList(redis,startDate,endDate):
    """
        获取某个时间段注册人数列表
        params:
            [ startDate ] : 开始日期
            [ endDate ]   : 结束日期

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

    res = []
    now_time = datetime.now()
    while startDate <= endDate:
        if startDate>now_time:
            startDate += deltaTime
            continue
        regInfo = {}
        dateStr = startDate.strftime('%Y-%m-%d')
        regTable = FORMAT_REG_DATE_TABLE%(dateStr)
        regCount = redis.scard(regTable)
        regInfo['reg_date'] = dateStr
        regInfo['reg_count'] = regCount
        regInfo['op'] = []
        regInfo['op'].append({'url':'/admin/statistics/reg/list','method':'GET','txt':'查看详情'})
        res.append(regInfo)

        startDate += deltaTime

    res.reverse()
    return res

def getCardCountList(redis,agentId,startDate,endDate):
    """
        获取某个时间段注册人数列表
        params:
            [ startDate ] : 开始日期
            [ endDate ]   : 结束日期

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

    res = []

    while startDate <= endDate:
        regInfo = {}
        dateStr = startDate.strftime('%Y-%m-%d')
        if agentId == '1':
            regTable = DAY_ALL_PLAY_ROOM_CARD%(dateStr)
            regCount = redis.get(regTable)
        else:
            regCount = getAgentRoomByDay(redis,agentId,dateStr)
        if not regCount:
            regCount = 0
        regInfo['reg_date'] = dateStr
        regInfo['reg_count'] = regCount
        res.append(regInfo)

        startDate += deltaTime

    res.reverse()
    return res



@admin_app.get('/statistics/reg')
@checkAccess
def getRegStatistics(redis,session):
    lang    =  getLang()
    curTime =  datetime.now()
    isList  =  request.GET.get('list','').strip()
    startDate = request.GET.get('startDate','').strip()
    endDate   = request.GET.get('endDate','').strip()

    if isList:
        res = getRegCountList(redis,startDate,endDate)
        return json.dumps(res)
    else:
        info = {
                'title'                  :           '注册人数统计',
                'listUrl'                :           BACK_PRE+'/statistics/reg?list=1',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH,
        }

        return template('admin_statistics_reg',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/statistics/takeCard')
@checkAccess
def getCardStatistics(redis,session):
    lang    =  getLang()
    curTime =  datetime.now()
    isList  =  request.GET.get('list','').strip()
    startDate = request.GET.get('startDate','').strip()
    endDate   = request.GET.get('endDate','').strip()

    if isList:
        res = getCardCountList(redis,session['id'],startDate,endDate)
        return json.dumps(res)
    else:
        info = {
                'title'                  :           '日耗钻统计',
                'listUrl'                :           BACK_PRE+'/statistics/takeCard?list=1',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH,
        }

        return template('admin_statistics_card',info=info,lang=lang,RES_VERSION=RES_VERSION)


def getRegListByRegDate(redis,reg_date):
    """
        获取某个时间段注册人数详情
        params:
            [ reg_date ] : 某一天

    """
    print 'reg_date',reg_date
    registMemberList =  redis.smembers(FORMAT_REG_DATE_TABLE%(reg_date))
    res = []
    for member in registMemberList:
        memberInfo = {}
        account2user_table = FORMAT_ACCOUNT2USER_TABLE%(member) #从账号获得账号信息，和旧系统一样
        table = redis.get(account2user_table)
        nickname,reg_date,regIp,login_out_date,last_login_date,parentAg,headImgUrl= \
        redis.hmget(table,('nickname','regDate','regIp','last_logout_date','last_login_date','parentAg','headImgUrl'))
        memberInfo['nickname'] = nickname
        memberInfo['reg_date'] = reg_date
        memberInfo['regIp'] = regIp
        memberInfo['parentAg'] = regIp
        memberInfo['last_login_date'] = last_login_date if last_login_date else '-'
        memberInfo['login_out_date'] = login_out_date if login_out_date else '-'
        memberInfo['parentAg'] = parentAg if parentAg else '未加入任何公会'
        memberInfo['headImgUrl'] = headImgUrl
        memberInfo['account'] = member

        res.append(memberInfo)
    return res



@admin_app.get('/statistics/reg/list')
def getRegStatisticsList(redis,session):
    lang    =  getLang()
    curTime =  datetime.now()
    isList  =  request.GET.get('list','').strip()
    reg_date = request.GET.get('reg_date','').strip()

    if isList:
        res = getRegListByRegDate(redis,reg_date)
        return json.dumps(res)
    else:
        info = {
                'title'                  :           '%s 注册列表'%(reg_date),
                'listUrl'                :           BACK_PRE+'/statistics/reg/list?list=1&reg_date=%s'%(reg_date),
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH,
        }

        return template('admin_statistics_reg_list',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/statistics/card/list')
def getRegStatisticsList(redis,session):
    lang    =  getLang()
    curTime =  datetime.now()
    isList  =  request.GET.get('list','').strip()
    reg_date = request.GET.get('reg_date','').strip()

    if isList:
        res = getRegListByRegDate(redis,reg_date)
        return json.dumps(res)
    else:
        info = {
                'title'                  :           '%s 注册列表'%(reg_date),
                'listUrl'                :           BACK_PRE+'/statistics/reg/list?list=1&reg_date=%s'%(reg_date),
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH,
        }

        return template('admin_statistics_reg_list',info=info,lang=lang,RES_VERSION=RES_VERSION)


def getloginCountList(redis,agentId,agentIds,startDate,endDate):
    """
        获取某个时间段注册人数列表
        params:
            [ startDate ] : 开始日期
            [ endDate ]   : 结束日期

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

    res = []

    while startDate <= endDate:
        regInfo = {}
        dateStr = startDate.strftime('%Y-%m-%d')
        if not agentIds and int(agentId) == 1:
            regTable = FORMAT_LOGIN_DATE_TABLE%(dateStr)
            regCount = redis.scard(regTable)
        else:
            if not agentIds:
                agentIds = [agentId]
            regCount = 0
            for _agentId in agentIds:
                count = redis.get(DAY_AG_LOGIN_COUNT%(_agentId,dateStr))
                if not count:
                    count = 0
                regCount+=int(count)

        regInfo['reg_date'] = dateStr
        regInfo['reg_count'] = regCount
        regInfo['op'] = []
        regInfo['op'].append({'url':'/admin/statistics/login/list','method':'GET','txt':'查看详情'})
        res.append(regInfo)

        startDate += deltaTime

    res.reverse()
    return res

@admin_app.get('/statistics/login')
@checkAccess
def getLoginStatistics(redis,session):

    lang    =  getLang()
    curTime =  datetime.now()
    isList  =  request.GET.get('list','').strip()
    startDate = request.GET.get('startDate','').strip()
    endDate   = request.GET.get('endDate','').strip()

    selfUid  = session['id']
    if int(selfUid) == 1:
        agentIds = []
    else:
        agentIds = getAllChildAgentId(redis,selfUid)

    if isList:
        res = getloginCountList(redis,selfUid,agentIds,startDate,endDate)
        return json.dumps(res)
    else:
        info = {
                'title'                  :           '日登录人数统计',
                'listUrl'                :           BACK_PRE+'/statistics/login?list=1',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }


    return template('admin_statistics_login',info=info,lang=lang,RES_VERSION=RES_VERSION)


@admin_app.get('/statistics/login/list')
def getRegStatisticsList(redis,session):
    lang    =  getLang()
    curTime =  datetime.now()
    isList  =  request.GET.get('list','').strip()
    reg_date = request.GET.get('reg_date','').strip()
    selfUid  = session['id']

    if isList:
        res = getLoginListByRegDate(redis,session['id'],reg_date)
        return json.dumps(res)
    else:
        info = {
                'title'                  :           '%s 登录列表'%(reg_date),
                'listUrl'                :           BACK_PRE+'/statistics/login/list?list=1&reg_date=%s'%(reg_date),
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH,
        }

        return template('admin_statistics_login_list',reg_date=reg_date,info=info,lang=lang,RES_VERSION=RES_VERSION)

# @admin_app.get('/statistics/count')
# def getCountStatics(redis,session):
#     """
#     获取每日的局数统计
#     """
#     lang = getLang()
#     curTime = datetime.now()
#     isList = request.GET.get('list','').strip()
#     startDate = request.GET.get('startDate','').strip()
#     endDate = request.GET.get('endDate','').strip()
#     selfUid = request.GET.get('id','').strip()
#     date    = request.GET.get('date','').strip()

#     if date:
#         endDate = date

#     log_debug('[count] startDate[%s] endDate[%s]'%(startDate,endDate))

#     if not selfUid:
#         selfUid = session['id']

#     agentType = session['type']
#     openList = 'true'
#     if int(agentType) == 2:
#         openList = 'false'
#     if isList:
#         res = getCountTotal(redis,selfUid,startDate,endDate)
#         return json.dumps(res)
#     else:
#         info = {
#                 'title'         :       '局数统计',
#                 'listUrl'                :           BACK_PRE+'/statistics/count?list=1',
#                 'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
#                 'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH,
#         }

#     return template('admin_statistics_count',openList=openList,info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/statistics/active')
def get_active_page(redis,session):
    """
    活跃人数统计
    """
    curTime = datetime.now()
    lang = getLang()

    isList = request.GET.get('list','').strip()
    start_date = request.GET.get('startDate','').strip()
    end_date = request.GET.get('endDate','').strip()
    selfUid = session['id']
    if isList:
        active_reports = get_active_reports(redis,start_date,end_date,selfUid)
        return json.dumps(active_reports)
    else:
        info = {
                'title'         :       '活跃人数统计',
                'listUrl'                :           BACK_PRE+'/statistics/active?list=1',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }

        return template('admin_statistics_active',PAGE_LIST=PAGE_LIST,info=info,RES_VERSION=RES_VERSION,lang=lang)

@admin_app.get('/statistics/active/showDay')
def get_active_day(redis,session):
    """
    活跃人数统计
    """
    curTime = datetime.now()
    lang = getLang()

    isList = request.GET.get('list','').strip()
    date = request.GET.get('day','').strip()
    selfUid = session['id']
    if isList:
        active_reports = get_login_list(redis,session['id'],date)
        return json.dumps(active_reports)
    else:
        info = {
                'title'                  :          '[%s]统计列表'%(date),
                'listUrl'                :           BACK_PRE+'/statistics/active/showDay?list=1&day=%s'%(date),
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }

        return template('admin_statistics_login_list',PAGE_LIST=PAGE_LIST,date=date,info=info,RES_VERSION=RES_VERSION,lang=lang)
