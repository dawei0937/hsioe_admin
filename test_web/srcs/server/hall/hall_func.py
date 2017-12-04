#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    this is Description
"""

from bottle import response,request
import inspect
from web_db_define import *
from wechat.wechatData import *
from common.install_plugin import *
from datetime import datetime,timedelta
from config.consts import *
from common.log import *
from model.agentModel import *
import time
import uuid
import xml.dom.minidom
import md5
import hashlib
import urllib2
import urllib
import socket
import redis

#支付配置常量
TYPE_2_CARS = {

    '1'             :           10,
    '2'             :           20,
    '3'             :           30
}

CHECK_WAIT = 0
CHECK_SUCCESS = 1

SHOP_OPEN = 0
SHOP_CLOSE = 1

def getRedisInst(redisHost,dbNum,port=6379,pwd="Fkkg65NbRwQOnq01OGMPy5ZREsNUeURm"):
    """
    获取redis连接实例
    params:
        redisHost   :  redis主机地址
        dbNum        :  数据库编号
        port         :  端口号,默认6379
        pwd          :  密码,默认Fkkg65NbRwQOnq01OGMPy5ZREsNUeURm
    return:
        redis实例
    """
    #global redisdb
    redisdb = redis.ConnectionPool(host=redisHost, port=port, db=dbNum, password=pwd)
    return redis.Redis(connection_pool=redisdb)


def __coinReformat(coin):
    return round(float(coin)/100, 2)

def getGroupIds(redis,groupId):
    """
    获取所有上级代理ID
    """
    Ids = []
    if redis.exists(AGENT_TABLE%(groupId)):
        parentId = redis.get(AGENT2PARENT%(groupId))
        if parentId:
            if int(parentId) == 1:
                return ['1']
            Ids.extend(getGroupIds(redis,parentId))
        else:
            Ids.append(parentId)

    return Ids

def getBroadcasts(redis,groupId,isNew=''):
    """
        获取广播列表
    """
    bIds = redis.lrange(HALL_BROADCAST_LIST,0,-1)
    broadInfos = []
    groupIds = getGroupIds(redis,groupId)
    groupIds.append(groupId)
    log_debug('[groupIds][%s] bids[%s]'%(groupIds,bIds))
    for bid in bIds:
        if redis.exists(FORMAT_BROADCAST_TABLE%(bid)):
            bInfos = redis.hgetall(FORMAT_BROADCAST_TABLE%(bid))
            if bInfos['ag'] in groupIds:
                broadInfos.append(bInfos)
        else:
            redis.lrem(FORMAT_BROADCAST_LIST_TABLE,'1',bid)

    broadcasts = {'broadcasts':broadInfos}

    if isNew:
        broadcasts['isNew'] = isNew

    return broadcasts

def getHallBroadInfo(redis,group_id):
    """
    获取大厅广播列表
    """
    play_set = redis.smembers(HALL_BRO_PLAY_SET)
    broads = redis.lrange(HALL_BRO_CONTAIN_ALL_LIST%(0),0,-1)
    broadList = []
    for broad in broads:
        if broad in play_set:
            broadDetail = {}
            broadInfo = redis.hgetall(HALL_BRO_TABLE%(broad))
            broadDetail['content'] = broadInfo['content']
            broadDetail['repeatInterval'] = int(broadInfo['per_sec'])
            return broadDetail

    broads = redis.lrange(HALL_BRO_CONTAIN_AG_LIST%(2,group_id),0,-1)
    for broad in broads:
        if broad in play_set:
            broadDetail = {}
            broadInfo = redis.hgetall(HALL_BRO_TABLE%(broad))
            broadDetail['content'] = broadInfo['content']
            broadDetail['repeatInterval'] = int(broadInfo['per_sec'])
            return broadDetail

    broads = redis.lrange(HALL_BRO_CONTAIN_AG_LIST%(3,group_id),0,-1)
    for broad in broads:
        if broad in play_set:
            broadDetail = {}
            broadInfo = redis.hgetall(HALL_BRO_TABLE%(broad))
            broadDetail['content'] = broadInfo['content']
            broadDetail['repeatInterval'] = int(broadInfo['per_sec'])
            return broadDetail

    broads = redis.lrange(HALL_BRO_CONTAIN_ALL_LIST%(1),0,-1)
    for broad in broads:
        if broad in play_set:
            broadDetail = {}
            broadInfo = redis.hgetall(HALL_BRO_TABLE%(broad))
            broadDetail['content'] = broadInfo['content']
            broadDetail['repeatInterval'] = int(broadInfo['per_sec'])
            return broadDetail

    return None

def getDefaultRoomCard(redis,groupId,userId,lastGroup=None):
    """
    获取用户的房卡数
    传入参数: redis,groupId(公会ID),userId(玩家ID),lastGroup(是否第一次)
    返回参数:默认房卡
    """
    provinceAgId = getTopAgentId(redis,groupId)
    defaultCard = redis.get(USER4AGENT_CARD%(provinceAgId, userId))
    log_debug('[getDefaultRoomCard] groupId[%s] userId[%s] defaultCards[%s]'%(provinceAgId,userId,defaultCard))
    if not defaultCard:
        if lastGroup:
            #如果不是第一次加公会则返回当前的卡，没有则是0
            defaultCard = redis.get(USER4AGENT_CARD%(groupId, userId))
            if not defaultCard:
                return 0
            return defaultCard
        #如果是第一次则赠送默认房卡
        defaultCard = redis.hget(AGENT_TABLE%(provinceAgId),'defaultRoomCard')
        if not defaultCard:
            defaultCard = 0
    log_debug('[getDefaultRoomCard] return defaultCard[%s] groupId[%s]'%(defaultCard,groupId))
    return defaultCard


def getUserByAccount(redis, account):
    """
    通过account获取玩家数据
    """
    account2user_table = FORMAT_ACCOUNT2USER_TABLE%(account)
    userTable = redis.get(account2user_table)
    return userTable


def getInfoBySid(redis,sid):
    """
    通过Sid获取SessionTable, account, uid, verfiySid信息
    """
    SessionTable = FORMAT_USER_HALL_SESSION%(sid)
    account,uid = redis.hmget(SessionTable, ('account','uid'))
    verfiySid   = redis.get(FORMAT_USER_PLATFORM_SESSION%(uid))
    curTime = getNowTime()
    print '[%s][SessionTable][info] account[%s] sessionKey[%s] verfiyKey[%s]'%(curTime,account,sid,verfiySid)
    return SessionTable, account, uid, verfiySid

def extendSession(redis,session,SessionTable):
    """
    延长session有效时间
    """
    redis.expire(session['session_key'],60*60)
    redis.expire(SessionTable,60*40)
    #session.expire()


def getOrderNonceStr():
    nonceStr = ''
    for count in xrange(MAX_RANDOM_STR_COUNT):
        nonceStr += random.choice(RANDOM_STR_LIST)
    return nonceStr

def getOrderNonceStr4TX():
    nonceStr = ''
    for count in xrange(32):
        nonceStr += random.choice(RANDOM_STR_LIST)
    return nonceStr

def getXMLMessage(url, data): #支付用接口
    socket.setdefaulttimeout(WAIT_WEB_TIME)
    xmlDict = {}
    req = urllib2.Request(url = url, headers={'Content-Type':'text/xml'},data = data )
    Message = urllib2.urlopen(req)
    data = Message.read()

    xmlDict = transXml2Dict(data)
    return xmlDict


def gen_sign(params):
    """
        签名生成函数

        :param params: 参数，dict 对象
        :param key: API 密钥
        :return: sign string
    """

    param_list = []
    for k in sorted(params.keys()):
        v = params.get(k)
        if not v:
            # 参数的值为空不参与签名
            continue
        param_list.append('{0}={1}'.format(k, v))

    # 在最后拼接 key
    param_list.append('key={}'.format(MCH_KEY))
    # 用 & 连接各 k-v 对，然后对字符串进行 MD5 运算
    return md5.new('&'.join(param_list)).hexdigest().upper()

def gen_sign4TX(params):
    """
        签名生成函数

        :param params: 参数，dict 对象
        :param key: API 密钥
        :return: sign string
    """

    param_list = []
    for k in sorted(params.keys()):
        v = params.get(k)
        if not v:
            # 参数的值为空不参与签名
            continue
        param_list.append('{0}={1}'.format(k, v))

    # 在最后拼接 key
    param_list.append('key={}'.format(MCH_KEY_TX))
    # 用 & 连接各 k-v 对，然后对字符串进行 MD5 运算
    return md5.new('&'.join(param_list)).hexdigest().upper()

def gen_sign4WXConfig(params):
    """
        签名生成函数

        :param params: 参数，dict 对象
        :return: sign string
    """

    param_list = []
    for k in sorted(params.keys()):
        v = params.get(k)
        if not v:
            # 参数的值为空不参与签名
            continue
        param_list.append('{0}={1}'.format(k, v))
    # 用 & 连接各 k-v 对，然后对字符串进行 MD5 运算
    return hashlib.sha1('&'.join(param_list)).hexdigest()

def gen_nonce_str():
    """
        生成随机字符串，有效字符a-zA-Z0-9

        :return: 随机字符串
    """
    return ''.join(str(uuid.uuid4()).split('-'))

def transDict2Xml(data):
    """
        将 dict 对象转换成微信支付交互所需的 XML 格式数据
    """

    xml = []
    for k in sorted(data.keys()):
        v = data.get(k)
        if not v.startswith('<![CDATA['):
            v = '<![CDATA[{}]]>'.format(v)
        xml.append('<{key}>{value}</{key}>'.format(key=k, value=v))
    return '<xml>{}</xml>'.format(''.join(xml))

def transXml2Dict(data):
    """
        解析微信返回的xml
    """
    dom = xml.dom.minidom.parseString(data)
    root = dom.documentElement
    xmlDict = {}
    for child in root.childNodes:
        print child
        result = dom.getElementsByTagName(child.nodeName)
        if result == []:
            continue
        result = result[0].childNodes[0].nodeValue
        xmlDict[child.nodeName] = result

    return xmlDict

def para_filter(params):
    """
        过滤参数
    """
    return {key: params[key]
            for key in params
            if key.lower() not in {'sign'} and params[key]}

def checkSign(params):
    """
        验证签名
    """
    if 'sign' not in params:
        return False
    wx_sign = params['sign']
    filter_params = para_filter(params)
    sign = gen_sign(filter_params)
    sign4TX = gen_sign4TX(filter_params)
    return wx_sign == sign or wx_sign == sign4TX

def response2Wechat(resultCode,Msg):
    """
        返回结果给微信
    """

    item = {
        'return_code'       :       resultCode,
        'return_msg'        :       Msg
    }

    return transDict2Xml(item)

def verfiyRcvDatas(redis,params):
    """
        校验支付数据
    """
    curTime = datetime.now()
    orderTable = ORDER_TABLE%(params['out_trade_no'])
    if not redis.exists(orderTable):
        log_debug('[%s][wechatPay][error] orderNo[%s] is not exists.'%(curTime,params['out_trade_no']))
        return False

    updateInfo = {
            'money'         :       params['total_fee'],
            'endTime'       :       params['time_end'],
            'currency'      :       params['fee_type'],
            'orderNum'      :       params['transaction_id'],
            'type'          :       'successful',
    }

    pipe = redis.pipeline()
    try:
        log_debug('[%s][wechatPay][info] update orderInfo[%s] success.'\
                                    %(curTime,updateInfo))
        pipe.hmset(orderTable,updateInfo)
        pipe.srem(PENDING_ORDER,orderTable)
        pipe.sadd(SUCCEED_ORDER,orderTable)
        pipe.persist(orderTable)
        pipe.execute()
    except:
        log_debug('[%s][wechatPay][error] update orderInfo[%s] error.'%(curTime,updateInfo))
        return False

    return True

def countRateOfAgent(redis,agentId,roomcardNumber,unitPrice,lowerRate=0):

    log_debug('[HALLFUNC][countRateOfAgent][info] agentId[%s] roomcard[%s] unitPrice[%s]'%(agentId,roomcardNumber,unitPrice))

    curTime = datetime.now()
    date = curTime.strftime("%Y-%m-%d")
    parentTable = AGENT_TABLE%(agentId)
    parentType,parentrate,parentId = redis.hmget(parentTable,('type','shareRate','parent_id'))

    if parentType == '0':
        AGENT_RATE_TABLE = AGENT_COMPAY_RATE_DATE%(agentId,date)
    else:
        AGENT_RATE_TABLE =AGENT_RATE_DATE%(agentId,parentrate,unitPrice,date)

    log_debug('[HALLFUNC][countRateOfAgent][info] agentId[%s] parentId[%s] parentrate[%s] parentId[%s] agentRateTable[%s]'\
                                %(agentId,parentId,parentrate,parentId,AGENT_RATE_TABLE))

    pipe = redis.pipeline()
    pipe.hincrby(AGENT_RATE_TABLE,'number',amount=roomcardNumber)
    pipe.hset(AGENT_RATE_TABLE,'unitPrice',unitPrice)
    pipe.hset(AGENT_RATE_TABLE,'rate',parentrate)
    if parentType == '0':
        RemainPrice = float(unitPrice) - float(lowerRate)
        if RemainPrice > 0:
            pipe.hincrbyfloat(AGENT_RATE_TABLE, 'rateTotal', amount=RemainPrice * roomcardNumber)
    else:
        remainPrice = float(unitPrice) -  float(lowerRate)
        if remainPrice <= 0:
            countRateOfAgent(redis,parentId,roomcardNumber,unitPrice,lowerRate)
        else:
            parent1Type, parent1Rate = redis.hmget( AGENT_TABLE % (parentId), ('type', 'shareRate'))
            if parent1Type !='0':
                if parentrate > parent1Rate:
                    parentrate = parent1Rate

            if not parentrate:
                parentrate = 0.00

            firstRemainPrice = float(unitPrice) - float(parentrate)
            if firstRemainPrice <=0:
                Rate = float(unitPrice) - float(lowerRate)
                pipe.hincrbyfloat(AGENT_RATE_TABLE,'rateTotal',amount=Rate*roomcardNumber)
                pipe.hincrbyfloat(AGENT_RATE_TABLE, 'meAndNextTotal', amount=float(unitPrice)*roomcardNumber)
                countRateOfAgent(redis,parentId,roomcardNumber,unitPrice,parentrate)
            else :
                Rate = float(parentrate)
                pipe.hincrbyfloat(AGENT_RATE_TABLE,'rateTotal',amount=Rate*roomcardNumber)
                pipe.hincrbyfloat(AGENT_RATE_TABLE, 'meAndNextTotal', amount=float(parentrate) * roomcardNumber)
                pipe.hincrbyfloat(AGENT_RATE_TABLE, 'superRateTotal', amount=firstRemainPrice*roomcardNumber)
                countRateOfAgent(redis,parentId,roomcardNumber,unitPrice,parentrate)
    pipe.execute()

def getCardMoney(redis,groupId):
    """
    会员购卡单价
    """
    AgentTable = AGENT_TABLE%(groupId)
    unitPrice,parentId,atype=redis.hmget(AgentTable,'unitPrice','parent_id','type')
    log_debug('[HALLFUNC][getCardMoney][info] groupId[%s] price[%s]'%(groupId,unitPrice))
    if atype == '2':
        return getCardMoney(redis,parentId)

    return unitPrice

def addRoomCard2Member(redis,transNo):
    """
        会员增加房卡
    """
    curTime = datetime.now()
    orderTable = ORDER_TABLE%(transNo)
    if not redis.exists(orderTable):
        log_debug('[%s][wechatPay][error] orderNo[%s] is not exists.'%(curTime,params['out_trade_no']))
        return False

    cardNums,present_card = redis.hmget(orderTable,('roomCards','presentCards'))
    if not present_card:
        present_card = 0
    try:
        present_card = int(present_card)
    except:
        present_card = 0

    rType,memberAccount= redis.hmget(orderTable,('num','account'))

    #chargeNums = TYPE_2_CARS[rType]
    account2user_table = FORMAT_ACCOUNT2USER_TABLE%(memberAccount) #从账号获得账号信息，和旧系统一样
    userTable = redis.get(account2user_table)
    groupId = redis.hget(userTable, 'parentAg')
    #会员ID
    id = userTable.split(':')[1]

    pipe = redis.pipeline()
    pipe.incrby(USER4AGENT_CARD%(groupId, id),(int(cardNums)+present_card))
    #记录充值卡总额
    if not redis.exists(USER4AGENT_RECHARGE%(groupId,id)):
        pipe.set(USER4AGENT_RECHARGE%(groupId,id),0)
    pipe.incrby(USER4AGENT_RECHARGE%(groupId, id),int(cardNums))
    CardMoney = getCardMoney(redis,groupId)
    log_debug('[%s][wechatPay] recharge CardMoney[%s]'%(curTime,CardMoney))
    #计算分成金额
    countRateOfAgent(redis,groupId,int(cardNums),CardMoney)
    log_debug('[%s][wechatPay] recharge roomcards[%s] to account[%s] success'%(curTime,cardNums,memberAccount))
    roomCards = pipe.execute()[0]

    pipe = redis.pipeline()
    ymd = datetime.now().strftime("%Y-%m-%d")
    useDatas = [int(cardNums), 4, roomCards]
    useStr = ';'.join(map(str, useDatas))
    pipe.lpush(PLAYER_DAY_USE_CARD%(id, ymd), useStr)
    pipe.expire(PLAYER_DAY_USE_CARD%(id, ymd), SAVE_PLAYER_DAY_USE_CARD_TIME)
    pipe.execute()
    #发送消息给服务端
    # sendProtocol2GameService(redis,MAHJONG_GAMEID,HEAD_SERVICE_PROTOCOL_MEMBER_REFRESH%(memberAccount))

def getNowTime():
    """
        获取现在时间
    """
    return datetime.now()

def getRechargeRecords(uid):
    """
        获取充值记录
    """
    FIELD = [
            RechargeLog.order_no,
            RechargeLog.money,
            RechargeLog.recharge_time,
            RechargeLog.status
    ]

    CONDITION = [
            RechargeLog.uid == uid
    ]

    ORDER = [-RechargeLog.id]

    recordList = []
    records = RechargeLog.select(*FIELD).where(*CONDITION).order_by(*ORDER)

    for record in records:
        recordInfo  = {
                'order_no'          :       record.order_no,
                'money'             :       str(record.money),
                'recharge_time'     :       str(record.recharge_time),
                'status'            :       record.status
        }

        recordList.append(recordInfo)

    return recordList

def getWithdrawRecords(uid):
    """
        获取提现记录
    """
    FIELD = [
            WithdrawLog.order_no,
            WithdrawLog.money,
            WithdrawLog.balance_before,
            WithdrawLog.balance,
            WithdrawLog.fee,
            WithdrawLog.time,
            WithdrawLog.status
    ]

    CONDITION = [WithdrawLog.uid == uid]
    ORDER = [-WithdrawLog.id]

    recordList = []
    records = WithdrawLog.select(*FIELD).where(*CONDITION).order_by(*ORDER)

    for record in records:
        recordInfo = {
                'order_no'          :       record.order_no,
                'money'             :       str(record.money),
                'time'              :       str(record.time),
                'balance_before'    :       str(record.balance_before),
                'balance'           :       str(record.balance),
                'fee'               :       str(record.fee),
                'status'            :       str(record.status)
        }

        recordList.append(recordInfo)

    return recordList

def getLoginRecords(uid,sCondition):
    """
        登录记录查询
    """
    FIELD = [
            UserLoginLog.client_kind,
            UserLoginLog.ip,
            UserLoginLog.time,
            UserLoginLog.type
    ]

    CONDITION = [UserLoginLog.user == uid]

    if sCondition['type']:
        CONDITION.append(UserLoginLog.type == sCondition['type'])

    ORDER = [-UserLoginLog.id]

    recordList = []
    records = UserLoginLog.select(*FIELD).where(*CONDITION).order_by(*ORDER)
    for record in records:
        recordInfo = {
                'client_kind'       :       record.client_kind,
                'type'              :       record.type,
                'ip'                :       record.ip,
                'time'              :       str(record.time)
        }

        recordList.append(recordInfo)

    return recordList

def getDaya4Month():
    """
        返回一个星期时间
    """
    weekDelTime = timedelta(30)
    weekBefore = datetime.now()-weekDelTime
    startDate = weekBefore
    endDate   = datetime.now()

    return startDate.strftime('%Y-%m-%d 00:00:00'),endDate.strftime('%Y-%m-%d 23:59:59')
APPIDWEB = 'wx5db7c680fbb8de90'
SECRETWEB = '2e82c680f81b24e62b2612339dcc1d6b'
def getJsapiTicket(redis, account):
    curTime = datetime.now()
    errMsg = ''
    access_token = redis.get(ACCESS_TOKEN_API)
    log_debug('[%s][getJsapiTicket][info] access_token [%s]' % (curTime, access_token))
    if not access_token:
        access_token,errMsg = get_access_token(redis)
        if errMsg:
            return '',errMsg
        jsapi_ticket, errMsg = get_jsapi_ticket(redis, access_token)
        return jsapi_ticket,errMsg
    else:
        jsapi_ticket = redis.get(ACCESS_TOKEN_JSAPI)
        log_debug('[%s][getJsapiTicket][info] jsapi_ticket [%s]' % (curTime, jsapi_ticket))
        if not jsapi_ticket:
            jsapi_ticket, errMsg = get_jsapi_ticket(redis,access_token)
        return jsapi_ticket, errMsg

def get_jsapi_ticket(redis,access_token):
    curTime = datetime.now()
    url = 'https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token=%s&type=jsapi' % (access_token)
    message = getUrlMessage(url)
    log_debug('[%s][getJsapiTicket][info] message [%s]' % (curTime,message))
    errMsg = ''
    jsapi_ticket = ''
    if message['errcode'] !=0:
        log_debug('[%s][getJsapiTicket][info] ACCESS_TOKEN_JSAPI message:%s' % (curTime,message))
        errMsg = message['errmsg']
    else:
        pipe = redis.pipeline()
        pipe.set(ACCESS_TOKEN_JSAPI,message['ticket'])
        # pipe.expire(ACCESS_TOKEN_JSAPI, message['expires_in'])
        pipe.expire(ACCESS_TOKEN_JSAPI, 6000)
        pipe.execute()
        jsapi_ticket = message['ticket']
    return jsapi_ticket,errMsg

def get_access_token(redis):
    curTime = datetime.now()
    url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s' % (APPIDWEB, SECRETWEB)
    message = getUrlMessage(url)
    errMsg = ''
    access_token = ''
    log_debug('[%s][get_access_token][info] ACCESS_TOKEN_API message:%s' % (curTime, message))
    if 'errcode' in message:
        errMsg = message['errmsg']
    else:
        pipe = redis.pipeline()
        pipe.set(ACCESS_TOKEN_API,message['access_token'])
        # pipe.expire(ACCESS_TOKEN_API, message['expires_in'])
        pipe.expire(ACCESS_TOKEN_API, 6000)
        pipe.execute()
        access_token = message['access_token']
    return access_token,errMsg

def del_access_jsapi_token(redis):
    pipe = redis.pipeline()
    pipe.set(ACCESS_TOKEN_API,'')
    pipe.set(ACCESS_TOKEN_JSAPI,'')
    pipe.execute()


def allow_cross(fn):
    def _add_cross(*args,**kw):
        #跨域装饰器
        session = session_plugin.getSession()
        r = redis.Redis(connection_pool=session_plugin.connection_pool)
        argNames = inspect.getargspec(fn)[0]
        if redis_plugin.keyword in argNames:
            kw[redis_plugin.keyword] = session.rdb

        if session_plugin.keyword in argNames:
            kw[session_plugin.keyword] = session

        response.add_header('Access-Control-Allow-Origin', '*')

        return fn(*args,**kw)

    return _add_cross
