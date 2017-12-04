#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    大厅Model
"""

from web_db_define import *
from datetime import datetime,timedelta
from wechat.wechatData import *
from admin  import access_module
from config.consts import *
from datetime import datetime
import mahjong_pb2
import poker_pb2
import replay4proto_pb2
from mahjong.model.agentModel import getTopAgentId

def onReg(redis, account, passwd, type, ip): #传入参数：账号，密码，类型；返回参数：成功返回账号和密码，失败返回None, None

    curTime = datetime.now()

    #print
    log_debug('[try onReg] account[%s] passwd[%s] type[%s]'%(account,passwd,type))

    if type == 1: #微信code登录
        tokenMessage = checkWeixinCode(account)
        if tokenMessage:
            password = account
            accessToken = tokenMessage["access_token"]
            refreshToken = tokenMessage["refresh_token"]
            openID = tokenMessage["openid"]
            userData = getWeixinData(openID, accessToken)
            unionid = userData['unionid']
            if redis.exists(WEIXIN2ACCOUNT%(unionid)):
                realAccount = redis.get(WEIXIN2ACCOUNT%(unionid))
                account2user_table = FORMAT_ACCOUNT2USER_TABLE%(realAccount)
                table = redis.get(account2user_table)
                redis.hmset(table, {'accessToken':accessToken, 'refreshToken':refreshToken, 'password':md5.new(password).hexdigest()})
            else:
                setOpenid2account(openID, accessToken, refreshToken, ip, redis, account)
            redis.srem(FORMAT_LOGIN_POOL_SET,account)
            return unionid, password
        redis.srem(FORMAT_LOGIN_POOL_SET,account)
    elif type == 2:
        if redis.exists(WEIXIN2ACCOUNT%(account)):
            realAccount = redis.get(WEIXIN2ACCOUNT%(account))
            account2user_table = FORMAT_ACCOUNT2USER_TABLE%(realAccount)
            table = redis.get(account2user_table)
            truePassword, openID, accessToken = redis.hmget(table, ('password', 'openid', 'accessToken'))
            print 'type 2:passwd[%s] md5[%s] truePassword[%s]'%(md5.new(passwd).hexdigest(), passwd, truePassword)
            if truePassword == md5.new(passwd).hexdigest():
                userData = getWeixinData(openID, accessToken)
                print 'onReg for type 2, userData:%s'%(userData)
                if userData:
                    redis.hmset(table,
                        {
                            'nickname'      :   userData['nickname'],
                            'sex'           :   userData['sex'],
                            'headImgUrl'    :   userData['headimgurl']
                        }
                    )
                redis.srem(FORMAT_LOGIN_POOL_SET,account)
                return account, passwd
        redis.srem(FORMAT_LOGIN_POOL_SET,account)
    elif type == 3: #微信WEBcode登录
        tokenMessage = checkWeixinCodeWEB(account)
        if tokenMessage:
            password = account
            accessToken = tokenMessage["access_token"]
            refreshToken = tokenMessage["refresh_token"]
            openID = tokenMessage["openid"]
            userData = getWeixinData(openID, accessToken)
            unionid = userData['unionid']
            if redis.exists(WEIXIN2ACCOUNT%(unionid)):
                realAccount = redis.get(WEIXIN2ACCOUNT%(unionid))
                account2user_table = FORMAT_ACCOUNT2USER_TABLE%(realAccount)
                table = redis.get(account2user_table)
                redis.hmset(table, {'accessToken':accessToken, 'refreshToken':refreshToken, 'password':md5.new(password).hexdigest()})
            else:
                setOpenid2account(openID, accessToken, refreshToken, ip, redis, account)
            redis.srem(FORMAT_LOGIN_POOL_SET,account)
            return unionid, password
        redis.srem(FORMAT_LOGIN_POOL_SET,account)
    elif type == 0:
        account2user_table = FORMAT_ACCOUNT2USER_TABLE%(account)
        if redis.exists(account2user_table):
            table = redis.get(account2user_table)
            truePassword = redis.hget(table, 'password')
            if truePassword == md5.new(passwd).hexdigest():
                return account, passwd
    redis.srem(FORMAT_LOGIN_POOL_SET,account)
    return None, None

def saveHotUpDateSetting(redis,settingInfo):
    """
    保存热更新配置
    """
    return redis.hmset(HOTUPDATE_TABLE,settingInfo)


def getHotSettingField(redis,field):
    """
    获取单个配置信息
    """
    return redis.hget(HOTUPDATE_TABLE,field)

def getHotSettingAll(redis):
    return redis.hgetall(HOTUPDATE_TABLE)

def get_fish_hall_setting(redis):
    return redis.hgetall(HOTUPDATE_TABLE)

def getUserByAccount(redis, account):
    """
    通过account获取玩家数据
    """
    account2user_table = FORMAT_ACCOUNT2USER_TABLE%(account)
    userTable = redis.get(account2user_table)
    return userTable

def do_sessionExpire(redis,session,SessionTable,SESSION_TTL):
    """
    刷新session
    """
    #refresh session
    redis.expire(session['session_key'],60*60)
    redis.expire(SessionTable,60*10)
    session.expire()

def check_session_verfiy(redis,api_name,SessionTable,account,sid,verfiySid):
    '''
    验证session是否合法
    return code,msg
    '''
    try:
        log_debug('[on refresh] account[%s] sid[%s]'%(account, sid))
    except Exception as e:
        log_debug('print error File[%s]'%(e))

    if verfiySid and sid != verfiySid:
        #session['member_account'],session['member_id'] = '',''
        return -4,'账号已在其他地方登录',False

    if not redis.exists(SessionTable):
        return -3,'sid 超时',False

    user_table = getUserByAccount(redis, account)
    if not redis.exists(user_table):
        return -5,'该用户不存在',False

    return 0,True,user_table

def packPrivaTeData4Game(chair, data, resp, proto):
    privateResp = proto()
    privateResp.ParseFromString(resp.privateData)
    for data in privateResp.data.gameInfo.roomInfo.playerList:
        if int(data.side) == int(chair):
            print 'replay side get,side:%s nickname:%s'%(data.side, data.nickname)
            privateResp.data.gameInfo.selfInfo.side = data.side
            privateResp.data.gameInfo.selfInfo.nickname = data.nickname
            privateResp.data.gameInfo.selfInfo.coin = data.coin
            privateResp.data.gameInfo.selfInfo.ip = data.ip
            privateResp.data.gameInfo.selfInfo.sex = data.sex
            privateResp.data.gameInfo.selfInfo.headImgUrl = data.headImgUrl
            privateResp.data.gameInfo.selfInfo.roomCards = 0
    resp.privateData = privateResp.SerializeToString()
    replayStr = resp.SerializeToString()
    return replayStr

def packPrivaTeData(chair, data):
    resp = replay4proto_pb2.ReplayData()
    resp.ParseFromString(data)
    refreshDataNameProtos = [mahjong_pb2.S_C_RefreshData, poker_pb2.S_C_RefreshData]
    for proto in refreshDataNameProtos:
        try:
            replayStr = packPrivaTeData4Game(chair, data, resp, proto)
            break
        except Exception as e:
            print 'packPrivaTeData error', e
    return replayStr

def getRuleText(rule, gameId, redis):
    ruleList = eval(rule)
    ruleText = '底分: %s\n'%(max(int(ruleList[-1]), 1))
    gameTable = GAME_TABLE%(gameId)

    for data in redis.lrange(USE_ROOM_CARDS_RULE%(gameId), 0, -1):
        datas = data.split(':')
        name, cards = datas[0], datas[1]
        try:
            playCount = int(datas[2])
        except:
            playCount = name
        if int(cards) == ruleList[-2]:
            ruleText += '局数: %s\n'%(playCount)

    num = 0
    for ruleNum in redis.lrange(GAME2RULE%(gameId), 0, -1):
        ruleTile, ruleType, rule = redis.hmget(GAME2RULE_DATA%(gameId, ruleNum), ('title', 'type', 'rule'))
        ruleDataList = rule.split(',')
        if int(ruleType) == 1:
            print '[on getRuleText]get ruleList[%s] num[%s]'%(ruleList, num)
            try:
                ruleText += '%s: %s\n'%(ruleTile, ruleDataList[int(ruleList[num])])
            except:
                ruleText += '%s: %s\n'%(ruleTile, ruleDataList[int(ruleList[num][0])])
        else:
            text = '%s: '%(ruleTile)
            textList = []
            for ruleData in ruleList[num]:
                textList.append(ruleDataList[ruleData])
            textData = ','.join(textList)
            text += textData
            ruleText =ruleText + text + '\n'
        num += 1
    ruleText = ruleText.decode('utf-8')
    return ruleText

def tryExitGroup(redis, userTable, account, id, groupId):
    pipe = redis.pipeline()
    key = redis.get(ACCOUNT2WAIT_JOIN_PARTY_TABLE%account)
    # for key in redis.keys(WAIT_JOIN_PARTY_ROOM_PLAYERS%('*', '*', '*')): #在等待匹配娱乐模式的话则离开列表
    if key:
        waitJoinList = redis.lrange(key, 0, -1)
        if account in waitJoinList:
            pipe.lrem(key, account)
    pipe.srem(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(groupId), id) #上线代理需要获得
    pipe.hmset(userTable, {'parentAg':'', 'isVolntExitGroup':1,'lastGroup':groupId})
    #记录到省级公会的房卡
    topAgId = getTopAgentId(redis,groupId)
    roomcard = redis.get(USER4AGENT_CARD%(groupId,id))
    if not roomcard:
        roomcard = 0
    print '[try exitGroup] topAgId[%s] roomCards[%s]'%(topAgId,roomcard)
    pipe.set(USER4AGENT_CARD%(topAgId,id),int(roomcard))
    pipe.execute()
