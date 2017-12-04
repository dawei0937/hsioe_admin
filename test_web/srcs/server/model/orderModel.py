#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    订单模型
"""

from web_db_define import *
from datetime import datetime,timedelta
from common.log import *
import time

def createOrder(redis,orderInfo):
    """
    创建新订单
    @param:
        redis       redis链接实例
        orderInfo   游戏信息
    """

    orderInfo['id']  = redis.incr(ORDER_COUNT)

    orderTable = ORDER_TABLE%(orderInfo['orderNo'])
    pipe = redis.pipeline()

    pipe.hmset(orderTable,orderInfo)
    pipe.lpush(ORDER_LIST,orderInfo['orderNo'])
    return pipe.execute()


def getBuyOrdersById(redis,agentId,startDate,endDate):
    """
    获取代理购卡订单列表
    """
    deltaTime = timedelta(1)

    startDate = datetime.strptime(startDate,'%Y-%m-%d')
    endDate  = datetime.strptime(endDate,'%Y-%m-%d')

    orderList = []
    while endDate >= startDate:

        buyOrderTable = AGENT_BUY_ORDER_LIST%(agentId,endDate.strftime('%Y-%m-%d'))
        if not redis.exists(buyOrderTable):
            endDate-=deltaTime
            continue

        orderNos = redis.lrange(buyOrderTable,0,-1)
        for orderNo in orderNos:
            orderInfo = redis.hgetall(ORDER_TABLE%(orderNo))
            if not orderInfo:
                continue
            orderInfo['op'] = [
                                    {'url':'/admin/order/cancel','txt':'取消订单','method':'post'},
                                    {'url':'/admin/order/info','txt':'查看详情','method':'post'}
                              ]
            orderList.append(orderInfo)

        endDate = endDate-deltaTime
        print endDate

    return orderList

def getSaleOrdersById(redis,agentId,startDate,endDate):
    """
    获取代理售卡订单列表
    """
    deltaTime = timedelta(1)

    startDate = datetime.strptime(startDate,'%Y-%m-%d')
    endDate  = datetime.strptime(endDate,'%Y-%m-%d')

    orderList = []
    while endDate >= startDate:
        buyOrderTable = AGENT_SALE_ORDER_LIST%(agentId,endDate.strftime('%Y-%m-%d'))
        if not redis.exists(buyOrderTable):
            endDate-=deltaTime
            continue
        orderNos = redis.lrange(buyOrderTable,0,-1)
        for orderNo in orderNos:
            orderInfo = redis.hgetall(ORDER_TABLE%(orderNo))
            if not orderInfo:
                continue
            orderInfo['op'] = [{'url':'/admin/order/sale/cancel','txt':'取消订单','method':'post'},{'url':'/admin/order/comfirm','txt':'确认订单','method':'post'}]
            orderList.append(orderInfo)

        endDate-=deltaTime

    return orderList


def getBuyCardReport(redis,agentId,startDate,endDate):
    """
        获取代理购卡报表
        @params:
            redis   :  链接实例
            agentId :  代理ID
            startDate  :  开始日期
            endDate    :  结束日期
    """
    deltaTime = timedelta(1)

    startDate = datetime.strptime(startDate,'%Y-%m-%d')
    endDate  = datetime.strptime(endDate,'%Y-%m-%d')

    reportList = []
    cardNumsTotal = 0

    while endDate >= startDate:
        dateStr = endDate.strftime('%Y-%m-%d')
        buyReportTable = AGENT_BUY_CARD_DATE%(agentId,dateStr)
        if not redis.exists(buyReportTable):
            endDate-=deltaTime
            continue
        reportInfo  =  redis.hgetall(buyReportTable)
        #添加入报表list
        reportList.append(reportInfo)
        endDate-=deltaTime

    return {'cardNumsTotal':cardNumsTotal,'result':reportList}

def getSaleCardReport(redis,agentId,startDate,endDate):
    """
        获取代理售卡报表
        @params:
            redis   :  链接实例
            agentId :  代理ID
            startDate  :  开始日期
            endDate    :  结束日期
    """
    deltaTime = timedelta(1)

    startDate = datetime.strptime(startDate,'%Y-%m-%d')
    endDate   = datetime.strptime(endDate,'%Y-%m-%d')

    reportList = []
    cardNumsTotal = 0

    while endDate >= startDate:
        dateStr = endDate.strftime('%Y-%m-%d')
        saleReportTable = AGENT_SALE_CARD_DATE%(agentId,dateStr)
        if not redis.exists(saleReportTable):
            endDate-=deltaTime
            continue
        reportInfo  =  redis.hgetall(saleReportTable)
        #添加入报表
        reportList.append(reportInfo)

        endDate-=deltaTime

    return {'result':reportList}


def getAgentSaleCardReport(redis,agentId,startDate,endDate,group_id):
    """
        获取该代理的下线代理售卡报表
        @params:
            redis   :  链接实例
            agentId :  代理ID
            startDate  :  开始日期
            endDate    :  结束日期
    """
    deltaTime = timedelta(1)
    startDate = datetime.strptime(startDate,'%Y-%m-%d')
    endDate   = datetime.strptime(endDate,'%Y-%m-%d')

    parentTable = AGENT_CHILD_TABLE%(agentId)
    subIds = []
    if group_id:
        #按代理查询
        subIds = [group_id]
    else:
        subIds = redis.smembers(parentTable)
    reportList = []
    now_time = datetime.now()
    cardNumsTotal = 0
    for subId in subIds:
        agentTable = AGENT_TABLE%(subId)
        account = redis.hget(agentTable,'account')
        endDateCopy = endDate
        while endDateCopy >= startDate:
            if endDateCopy > now_time:
                endDateCopy-=deltaTime
                continue
            dateStr = endDateCopy.strftime('%Y-%m-%d')
            saleReportTable = AGENT_SALE_CARD_DATE%(subId,dateStr)
            log_debug('saleReport[%s]'%(saleReportTable))
            if not redis.exists(saleReportTable):
                endDateCopy-=deltaTime
                continue
            reportInfo = {}
            date,cardNums,totalNums  =  redis.hmget(saleReportTable,('date','cardNums','totalNums'))
            reportInfo['account'] = account
            reportInfo['cards'] = cardNums
            reportInfo['cardNumsTotal'] = totalNums
            reportInfo['date'] = date
            reportInfo['aId'] = subId
            #添加入报表
            reportList.append(reportInfo)
            endDateCopy-=deltaTime

    return {'result':reportList}

def getAgentBuyCardReport(redis,agentId,startDate,endDate,group_id):
    """
        获取该代理的下线代理购卡报表
        @params:
            redis   :  链接实例
            agentId :  代理ID
            startDate  :  开始日期
            endDate    :  结束日期
    """
    deltaTime = timedelta(1)

    startDate = datetime.strptime(startDate,'%Y-%m-%d')
    endDate   = datetime.strptime(endDate,'%Y-%m-%d')

    parentTable = AGENT_CHILD_TABLE%(agentId)
    if group_id:
        #按代理查询
        subIds = [group_id]
    else:
        subIds = redis.smembers(parentTable)

    reportList = []
    cardNumsTotal = 0
    now_time = datetime.now()
    for subId in subIds:
        agentTable = AGENT_TABLE%(subId)
        account = redis.hget(agentTable,'account')
        endDateCopy = endDate
        while endDateCopy >= startDate:
            if endDateCopy > now_time:
                endDateCopy-=deltaTime
                continue
            dateStr = endDateCopy.strftime('%Y-%m-%d')
            buyReportTable = AGENT_BUY_CARD_DATE%(subId,dateStr)
            if not redis.exists(buyReportTable):
                endDateCopy-=deltaTime
                continue
            reportInfo = {}
            date,cardNums,totalNums  =  redis.hmget(buyReportTable,('date','cardNums','totalNums'))

            reportInfo['account'] = account
            reportInfo['cards'] = cardNums
            reportInfo['date'] = date
            reportInfo['cardNumsTotal'] = totalNums
            reportInfo['aId'] = subId
            #添加入报表
            reportList.append(reportInfo)
            endDateCopy-=deltaTime

    return {'cardNumsTotal':cardNumsTotal,'result':reportList}

    return {'result':reportList}

def getWecharRecords(redis,groupId,condition):
    """
    获取微信订单记录
    """
    deltaTime = timedelta(1)
    orderList = []
    roomCardCount,pendingMoney,successMoney,moneyCount = 0,0,0,0
    #orderNos = redis.lrange(ORDER_NUM_LIST,0,-1)

    startDate,endDate = condition['startDate'],condition['endDate']
    startDate = datetime.strptime(startDate,'%Y-%m-%d')
    endDate   = datetime.strptime(endDate,'%Y-%m-%d')

    pipe = redis.pipeline()
    while endDate >= startDate:
        dateStr = endDate.strftime('%Y-%m-%d')
        orders = redis.lrange(DAY_ORDER%(dateStr),0,-1)
        #roomCardCount+=len(orders)
        for order in orders:
            orderInfo = {}
            if not ORDER_TABLE%(order):
                pipe.lrem(ORDER_NUM_LIST,orders)
                pipe.lrem(DAY_ORDER%(dateStr),order)
                continue
            orderDetail = redis.hgetall(ORDER_TABLE%(order))
            if not orderDetail:
                pipe.lrem(ORDER_NUM_LIST,orders)
                pipe.lrem(DAY_ORDER%(dateStr),order)
                continue
            print 'orderWechat[%s] order[%s]'%(orderDetail,order)
            dateStr1 = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(float(orderDetail['time'])))
            moneyCount+=round(float(orderDetail['money']),2)
            if orderDetail['type'] == 'pending':
                pendingMoney+=round(float(orderDetail['money']),2)
            else:
                successMoney+=round(float(orderDetail['money']),2)

            user_table = redis.get(FORMAT_ACCOUNT2USER_TABLE%(orderDetail['account']))
            group_id  = redis.hget(user_table,'parentAg')
            orderInfo['orderNo'] = order
            orderInfo['good_name'] = orderDetail['name']
            orderInfo['good_money'] = round(float(orderDetail['money'])*0.01,2)
            orderInfo['order_paytime'] = dateStr1
            orderInfo['good_count'] = orderDetail['roomCards']
            orderInfo['order_type'] = orderDetail['type']
            orderInfo['group_id'] = group_id if group_id else '-'
            orderInfo['memberId'] = user_table.split(':')[1]
            orderList.append(orderInfo)
        endDate-=deltaTime
    pipe.execute()
    return {'data':orderList,'orderCount':len(orderList),'moneyCount':moneyCount*0.01,'pendingMoney':pendingMoney*0.01,'successMoney':successMoney*0.01}
