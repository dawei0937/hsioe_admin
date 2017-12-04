#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    捕鱼大厅接口
"""

from bottle import request, Bottle, redirect, response,default_app
from web_db_define import *
import mahjong_pb2
import poker_pb2
import replay4proto_pb2
from talk_data import sendTalkData
from wechat.wechatData import *
from common.install_plugin import install_redis_plugin,install_session_plugin
from common.log import *
from common.utilt import allow_cross,getInfoBySid
from config.consts import *
from datetime import datetime
from model.goodsModel import *
from model.userModel import do_user_modify_addr,do_user_del_addr,get_user_exchange_list
from model.hallModel import *
from model.protoclModel import sendProtocol2GameService
from model.mailModel import *
from model.fishModel import get_room_list
import time
import urllib2
import json
import random
import md5
import re
from urlparse import urlparse
#from pyinapp import *
ACCEPT_NUM_BASE = 198326
ACCEPT_TT = [md5.new(str(ACCEPT_NUM_BASE+i)).hexdigest() for i in xrange(10)]
SESSION_TTL = 60*60

#生成捕鱼APP
fish_app = Bottle()
#获取配置
conf = default_app().config
#安装插件
install_redis_plugin(fish_app)
install_session_plugin(fish_app)

FORMAT_PARAMS_POST_STR = "%s = request.forms.get('%s','').strip()"
FORMAT_PARAMS_GET_STR  = "%s = request.GET.get('%s','').strip()"

#用户信息
USER_INFO = ('headImgUrl', 'sex', 'parentAg', 'isVolntExitGroup','coin','exchange_ticket')

SHOP_OPEN = 0
SHOP_CLOSE = 1

@fish_app.post('/login')
@allow_cross
def do_login(redis,session):
    """
    大厅登录接口

    """
    tt = request.forms.get('tt', '').strip()
    curTime = datetime.now()
    ip = request.remote_addr
    getIp = request['REMOTE_ADDR']
    _account = request.forms.get('account', '').strip()
    clientType = request.forms.get('clientType', '').strip()
    if not clientType:
        clientType = 0
    passwd = request.forms.get('passwd', '').strip()
    login_type = request.forms.get('type', '').strip() #登录类型
    login_type = int(login_type)
    sid=0
    try:
        log_debug('[on login]account[%s] clientType[%s] passwd[%s] type[%s]'%(_account, clientType, passwd, login_type))
    except Exception as e:
        print 'print error File', e

    login_pools = redis.smembers(FORMAT_LOGIN_POOL_SET)
    log_debug('[try do_login] account[%s] login_pools[%s]'%(_account,login_pools))

    if _account in login_pools:
        log_debug('[try do_login] account[%s] is already login.'%(_account))
        return

    redis.sadd(FORMAT_LOGIN_POOL_SET,_account)
    log_debug('[try do_login] account[%s] login_pools[%s]'%(_account,login_pools))
    reAccount, rePasswd = onReg(redis, _account, passwd, login_type, ip)

    if reAccount:
        if login_type:
            realAccount = redis.get(WEIXIN2ACCOUNT%(reAccount))
        else:
            realAccount = reAccount
        if not redis.sismember(ACCOUNT4WEIXIN_SET4FISH, realAccount):
            redis.sadd(ACCOUNT4WEIXIN_SET4FISH, realAccount)
            redis.sadd(FORMAT_REG_DATE_TABLE4FISH%(curTime.strftime("%Y-%m-%d")), realAccount)
        #读取昵称和group_id
        account2user_table = FORMAT_ACCOUNT2USER_TABLE%(realAccount)
        userTable = redis.get(account2user_table)
        id = userTable.split(':')[1]
        if redis.exists(UNIONID2GROUP%reAccount):
            unionId = reAccount
            needJoinGroup = redis.get(UNIONID2GROUP%unionId)
            adminTable = AGENT_TABLE%(needJoinGroup)
            if redis.exists(adminTable):
                agValid, auto_check, groupType = redis.hmget(adminTable, ('valid', 'auto_check', 'type'))
                if agValid == '1' and groupType != '1':
                    if not auto_check:
                        auto_check = CHECK_SUCCESS
                    pipe = redis.pipeline()
                    if auto_check == CHECK_SUCCESS:
                        pipe.hset(FORMAT_USER_TABLE%(id), 'parentAg', needJoinGroup)
                        pipe.sadd(FORMAT_ADMIN_ACCOUNT_MEMBER_TABLE%(needJoinGroup), id)
                    pipe.lpush(JOIN_GROUP_LIST%(needJoinGroup), id)
                    pipe.set(JOIN_GROUP_RESULT%(id), '%s:%s:%s'%(needJoinGroup, auto_check, curTime.strftime('%Y-%m-%d %H:%M:%S')))
                    pipe.execute()
        account, name, groupId,loginIp, loginDate, picUrl, gender,valid = \
                redis.hmget(userTable, ('account', 'nickname', 'parentAg', 'lastLoginIp', 'lastLoginDate', 'picUrl', 'gender','valid'))
        agentTable = AGENT_TABLE%(groupId)
        isTrail,shop = redis.hmget(agentTable,('isTrail','recharge'))
        if not isTrail:
            isTrail = 0

        #默认开放上次
        shop = 1

        shop = int(shop)
        if int(valid) == 0:
            #冻结后不能登录
            redis.srem(FORMAT_LOGIN_POOL_SET,_account)
            return {'code':105,'msg':'该帐号被冻结,请与客服联系'}

        #会话信息
        type2Sid = {
            True     :  sid,
            False    :  md5.new(str(id)+str(time.time())).hexdigest()
        }
        sid = type2Sid[login_type == 3]
        SessionTable = FORMAT_USER_HALL_SESSION%(sid)
        if redis.exists(SessionTable):
            print "[try do_login] account[%s] sid[%s] is existed."%(curTime,realAccount,sid)
            redis.srem(FORMAT_LOGIN_POOL_SET,account)
            return {'code':-1, 'msg':'链接超时'}

        #同一账号不能同时登录
        if type==3:##网页登录不更新session
            pass
        else:
            redis.set(FORMAT_USER_PLATFORM_SESSION%(id),sid)

        #更新登录IP和登陆日期
            redis.hmset(userTable, {'lastLoginIp':request.remote_addr, 'lastLoginDate':datetime.now().strftime("%Y-%m-%d %H:%M:%S"), \
                    'lastLoginClientType':clientType})

            #记录session信息
            session['member_id'] = id
            session['member_account'] = account
            session['member_lastIp'] = loginIp
            session['member_lastDate'] = loginDate
            session['session_key']  = sid
            pipe = redis.pipeline()
            pipe.hmset(SessionTable, {'account':account,'uid':id,'sid':sid,'loginIp':ip})
            pipe.expire(SessionTable, 60*40)
            pipe.execute()
        urlRes = urlparse(request.url)
        serverIp = ''
        serverPort = 0
        gameid = 0
        # exitPlayerData = EXIT_PLAYER%(realAccount)
        # print '[hall][login]exitPlayerData[%s]'%(exitPlayerData)
        # if redis.exists(exitPlayerData):
            # serverIp, serverPort, game = redis.hmget(exitPlayerData, ('ip', 'port', 'game'))
            # print '[hall][login]exitPlayerData get succed, ip[%s], serverPort[%s], game[%s]'%(serverIp, serverPort, game)
            # serverIp = urlRes.netloc.split(':')[0]
            # gameid = redis.hget(ROOM2SERVER%(game), 'gameid')
            # try:
                # int(gameid)
            # except:
                # serverIp = ''
                # serverPort = 0
                # gameid = 0
                # redis.delete(exitPlayerData)
                # print '[hall][login][delete] exitPlayerData[%s]'%(exitPlayerData)
        if redis.sismember(ONLINE_ACCOUNTS_TABLE4FISH, realAccount):
            key = FORMAT_CUR_USER_GAME_ONLINE%(realAccount)
            if key:
                gameNum = redis.hget(key, 'game')
                if gameNum:
                    # gameId = redis.hget(ROOM2SERVER%(gameNum), 'gameid')
                    playerSid = redis.get(FORMAT_USER_PLATFORM_SESSION%(id))
                    sendProtocol2GameService(redis, gameNum, HEAD_SERVICE_PROTOCOL_KICK_MEMBER4REPEAT%(realAccount, playerSid))

        userInfo = {'name':name,'isTrail':int(isTrail),'shop':int(shop),'group_id':groupId,'account':reAccount, 'passwd':rePasswd}
        joinNum = ''
        id = userTable.split(':')[1]
        joinMessage = redis.get(JOIN_GROUP_RESULT%(id))
        if joinMessage:
            joinMessage = joinMessage.split(':')
            joinNum = int(joinMessage[0])
            joinResult = int(joinMessage[1])
            userInfo['applyId'] = joinNum
            if joinResult == 1:
                redis.delete(JOIN_GROUP_RESULT%(id))

        key = redis.get(ACCOUNT2WAIT_JOIN_PARTY_TABLE%account)
        # for key in redis.keys(WAIT_JOIN_PARTY_ROOM_PLAYERS%('*', '*', '*')):
        if key:
            if account in redis.lrange(key, 0, -1):
                try:
                    gameId, serviceTag = redis.get('account:%s:wantServer'%account).split(',')
                    message = HEAD_SERVICE_PROTOCOL_NOT_JOIN_PARTY_ROOM%(account, ag)
                    redis.lpush(FORMAT_SERVICE_PROTOCOL_TABLE%(gameId, serviceTag), message)
                except:
                    print '[account wantServer][%s]'%(redis.get('account:%s:wantServer'%account))
                redis.lrem(key, account)
        if serverIp:
            urlRes = urlparse(request.url)
            domain = urlRes.netloc.split(':')[0]
            gameInfo = {'ip':domain, 'port':int(serverPort), 'gameid':gameid}

            gameState = {}
            gameTable = GAME_TABLE%(gameid)
            if redis.exists(gameTable):
                name, webTag, version,packName = redis.hmget(gameTable, ('name', 'web_tag', 'version','pack_name'))
                gameState[gameid] = {
                    'id'                :           gameid,
                    'name'              :           name,
                    'web_tag'           :           webTag,
                    'version'           :           version,
                    'downloadUrl'       :           packName
                }

            if joinNum:
                redis.srem(FORMAT_LOGIN_POOL_SET,_account)
                return {'code':0, 'sid':sid, 'userInfo':userInfo,\
                    'gameInfo':gameInfo, 'joinResult':joinResult, 'gameState':gameState}
            redis.srem(FORMAT_LOGIN_POOL_SET,_account)
            return {'code':0, 'sid':sid, 'userInfo':userInfo, 'gameInfo':gameInfo, 'gameState':gameState}
        else:
            if joinNum:
                redis.srem(FORMAT_LOGIN_POOL_SET,_account)
                return {'code':0, 'sid':sid, 'userInfo':userInfo, 'joinResult':joinResult}
            redis.srem(FORMAT_LOGIN_POOL_SET,account)
            return {'code':0, 'sid':sid, 'userInfo':userInfo}
    else: #失败
        redis.srem(FORMAT_LOGIN_POOL_SET,_account)
        return {'code':101, 'msg':'账号或密码错误或者微信授权失败'}

@fish_app.post('/refresh')
@allow_cross
def do_refresh(redis,session):
    """
    Refresh接口
    """
    ip = request.remote_addr
    curTime = datetime.now()
    fields = ('sid',)
    for field in fields:
        exec(FORMAT_PARAMS_POST_STR%(field,field))

    try:
        log_debug('[try do_refresh] get params sid[%s]'%(sid))
    except:
        return {'code':-300,'msg':'接口参数请求失败'}

    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    check_code,check_msg,user_table = check_session_verfiy(redis,'/fish/refresh/',SessionTable,account,sid,verfiySid)
    log_debug('[try do_refresh] check_code[%s] check_msg[%s]'%(check_code,check_msg))
    if int(check_code)<0:
        if check_code == -4:
            return {'code':check_code,'msg':check_msg,'osid':sid}
        return {'code':check_code,'msg':check_msg}

    #refresh session
    do_sessionExpire(redis,session,SessionTable,SESSION_TTL)
    #获取用户信息
    head_url, gender, groupId, isVolntExitGroup,coin,exchange_ticket = redis.hmget(user_table,USER_INFO)
    log_debug('[try do_refresh] userId[%s] gender[%s] groupId[%s] coin[%s]'%(uid,gender,groupId,coin))
    group_table = AGENT_TABLE%(groupId)
    isTrail,shop = redis.hmget(group_table,('isTrail','recharge'))

    if not isTrail:
        isTrail = 0

    shop = 1
    shop,isTrail = int(shop),int(isTrail)
    try:
        exchange_ticket = int(exchange_ticket)
    except:
        exchange_ticket = 0

    hasBroad = False
    if redis.exists(FORMAT_BROADCAST_LIST_TABLE):
        #有广播内容
        hasBroad = True

    #判断是否能领取奖励
    if uid not in redis.smembers(FISH_FIRST_SHARE_PER_DAY_SET):
        is_take_reward = 0
    else:
        if uid in redis.smembers(FISH_SHARE_NOT_TAKE_SETS):
            is_take_reward = 1
        elif uid in redis.smembers(FISH_SHARE_TAKE_SETS):
            is_take_reward = 2

    userInfo = {  #用户数据
            'id'                :       uid,
            'ip'                :       ip,
            'picUrl'            :       head_url,
            'exchangeTicket'    :       exchange_ticket,                         #兑换券
            'isTakeReward'      :       is_take_reward,                         # 0-为分享 1-未领取 2-已领取
            'shareCoin'         :       conf.get('fish.share_coin'),             #分享赠送金币金额
            'gender'            :       gender,
            'isTrail'           :       int(isTrail),
            'shop'              :       int(shop),
            'exchangeShop'      :       conf.get('fish.exchange_shop'),     #兑换商城是否开放
            'coin'              :       coin
    }

    lobbyInfo = getHotSettingAll(redis)
    #获取roomInfo
    roomInfo  = get_room_list(redis,False,False)
    lobbyInfo['hotUpdateURL'] = lobbyInfo['hotUpdateURL']+"/"+lobbyInfo['packName']
    log_debug('[try do_refresh] roomInfo[%s] userInfo[%s] lobbyInfo[%s]'%(roomInfo,userInfo,lobbyInfo))
    return {'code':0,'lobbyInfo':lobbyInfo,'hasBroad':hasBroad,'shopVerison':int(conf.get('fish.shop_version')),'roomInfo':roomInfo,'userInfo':userInfo}

@fish_app.post('/getShopInfo')
@allow_cross
def get_fish_goods_info(redis,session):
    '''
    捕鱼获取商城商品接口
    '''
    fields = ('sid',)
    for field in fields:
        exec(FORMAT_PARAMS_POST_STR%(field,field))

    try:
        log_debug('[try get_fish_goods_info] get params sid[%s]'%(sid))
    except:
        return {'code':-300,'msg':'接口参数请求错误'}

    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    check_code,check_msg,user_table = check_session_verfiy(redis,'/fish/getShopInfo/',SessionTable,account,sid,verfiySid)

    log_debug('[try do_refresh] check_code[%s] check_msg[%s]'%(check_code,check_msg))
    if int(check_code)<0:
        if check_code == -4:
            return {'code':check_code,'msg':check_msg,'osid':sid}
        return {'code':check_code,'msg':check_msg}

    goods_info = getCoinGoodsList(redis)
    log_debug('[try get_fish_goods_info]  sid[%s] goodsInfo[%s]'%(sid,goods_info))
    return {'code':0,'goodsInfo':goods_info}

@fish_app.post('/getRewardInfo')
@allow_cross
def get_fish_goods_info(redis,session):
    '''
    捕鱼获取商城商品接口
    '''
    fields = ('sid','ver')
    onshop_fields = ('reward_name','reward_stock','reward_img_path','reward_need_ticket')
    for field in fields:
        exec(FORMAT_PARAMS_POST_STR%(field,field))

    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    check_code,check_msg,user_table = check_session_verfiy(redis,'/fish/getRewardInfo/',SessionTable,account,sid,verfiySid)
    log_debug('[try do_refresh] check_code[%s] check_msg[%s]'%(check_code,check_msg))
    if int(check_code)<0:
        if check_code == -4:
            return {'code':check_code,'msg':check_msg,'osid':sid}
        return {'code':check_code,'msg':check_msg}

    #获取奖品列表
    reward_info = get_reward_shop_data(redis,onshop_fields)
    log_debug('[try get_fish_goods_info]  sid[%s] goodsInfo[%s]'%(sid,reward_info))
    return {'code':0,'rewardInfo':reward_info}

@fish_app.post('/getExchangeRecord')
@allow_cross
def get_user_reward_record(redis,session):
    """
    玩家兑换记录接口
    """
    fields = ('sid',)
    exchange_fields = ( # 兑换记录需要的字段
        'exchange_reward_name',
        'exchange_card_no',
        'exchange_card_pwd',
        'exchange_date',
        'exchange_reward_status'
    )
    for field in fields:
        exec(FORMAT_PARAMS_POST_STR%(field,field))

    try:
        log_debug('[try get_user_reward_record] get params sid[%s]'%(sid))
    except:
        return {'code':-300,'msg':'接口参数错误'}
    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    check_code,check_msg,user_table = check_session_verfiy(redis,'/fish/getRewardInfo/',SessionTable,account,sid,verfiySid)
    log_debug('[try do_refresh] check_code[%s] check_msg[%s]'%(check_code,check_msg))
    if int(check_code)<0:
        if check_code == -4:
            return {'code':check_code,'msg':check_msg,'osid':sid}
        return {'code':check_code,'msg':check_msg}

    user_exchange_list = get_user_exchange_list(redis,uid,exchange_fields)
    log_debug('[try get_user_reward_record]  sid[%s] user_exchange_list[%s]'%(sid,user_exchange_list))
    return {'code':0,'userExchangeInfo':user_exchange_list}

@fish_app.post('/doExchange')
@allow_cross
def do_reward_exchange(redis,session):
    '''
    玩家兑换奖品协议
    @params:
            sid : 玩家sesion
            rewardId : 奖品ID
    '''
    curTime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    dateStr = datetime.now().strftime('%Y-%m-%d')
    fields = ('sid','rewardId','needTicket')
    for field in fields:
        log_debug(FORMAT_PARAMS_POST_STR%(field,field))
        exec(FORMAT_PARAMS_POST_STR%(field,field))

    try:
        log_debug('[try do_reward_exchange] get params ticket[%s] sid[%s] rewardId[%s]'%(needTicket,sid,rewardId))
        needTicket = int(needTicket)
    except:
        return {'code':-300,'msg':'接口参数错误.'}

    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    check_code,check_msg,user_table = check_session_verfiy(redis,'/fish/doExchange/',SessionTable,account,sid,verfiySid)
    log_debug('[try do_refresh] check_code[%s] check_msg[%s]'%(check_code,check_msg))
    if int(check_code)<0:
        if check_code == -4:
            return {'code':check_code,'msg':check_msg,'osid':sid}
        return {'code':check_code,'msg':check_msg}

    if not redis.exists(FISH_REWARD_TABLE%(rewardId)):
        return {'code':-4001,'msg':'兑换商品不存在或已过期'}

    reward_table    = FISH_REWARD_TABLE%(rewardId)
    user_addr_table = FORMAT_USER_ADDRESS_TABLE%(uid)
    if not redis.exists(user_addr_table):
        return {'code':-4004,'msg':'请先设置奖品收货地址信息'}

    user_exchange_ticket = redis.hget(user_table,'exchange_ticket')
    if not user_exchange_ticket:
        user_exchange_ticket = 0
    user_exchange_ticket = int(user_exchange_ticket)

    reward_need_ticket,reward_need_ticket,reward_name,reward_stock,reward_img_path,reward_card_no,reward_card_pwd= \
                redis.hmget(reward_table,('reward_need_ticket','reward_need_ticket','reward_name','reward_stock','reward_img_path','reward_card_no','reward_card_pwd'))

    if int(needTicket) != int(reward_need_ticket):
        return {'code':-4002,'msg':'兑换使用卷和奖品所需兑换使用卷不一致.','needTicket':int(reward_need_ticket)}

    if int(user_exchange_ticket) < int(needTicket):
        log_debug('[try do_reward_exchange] needTicke[%s] user_exchange_ticket[%s]'%(needTicket,user_exchange_ticket))
        return {'code':-4003,'msg':'兑换奖券不足.','needTicket':int(reward_need_ticket)}
    #写入相应的兑换记录表
    #减去玩家相应的兑换卷
    #减去兑换奖品库存
    user_addr_info = redis.hgetall(user_addr_table)
    exchange_info = {
            'user_id'                   :   uid,
            'exchange_date'             :   curTime,
            'exchange_reward_id'        :   rewardId,
            'exchange_reward_name'      :   reward_name,
            'exchange_use_ticket'       :   needTicket,
            'exchange_leave_ticket'     :   user_exchange_ticket-needTicket,
            'exchange_reward_img_path'  :   reward_img_path,
            'exchange_need_ticket'      :   reward_need_ticket,
            'exchange_card_no'          :   reward_card_no if reward_card_no else '',
            'exchange_card_pwd'         :   reward_card_pwd if reward_card_pwd else '',
            'exchange_reward_status'    :   0,
            'exchange_user_name'        :   user_addr_info['name'],
            'exchange_user_phone'       :   user_addr_info['phone'],
            'exchange_user_addr'        :   user_addr_info['city']+user_addr_info['address']
    }
    pipe = redis.pipeline()
    try:
        ori_exchange_id = redis.get(FISH_EXCHANGE_ID_COUNT)
        exchange_id = redis.incr(FISH_EXCHANGE_ID_COUNT)
        pipe.hincrby(user_table,'exchange_ticket',-int(needTicket))
        pipe.hincrby(reward_table,'reward_stock',-1)
        #设置兑换表
        pipe.set(FISH_EXCHANGE_TABLE%(exchange_id),exchange_info)
        #写入兑换记录列表
        pipe.lpush(FISH_EXCHANGE_LIST,exchange_id)
        #写入用户兑换记录表
        pipe.lpush(FISH_USER_EXCHANGE_LIST%(uid),exchange_id)
        #写入兑换记日期索引表
        pipe.lpush(FISH_USER_EXCHANGE_DATE%(dateStr),exchange_id)
        #写入状态索
        pipe.lpush(FISH_USER_EXCHANGE_STATUS_LIST%(0),exchange_id)
    except Exception,e:
        redis.set(FISH_EXCHANGE_ID_COUNT,ori_exchange_id)
        log_debug('[try do_reward_exchange] exchange error reason[%s]'%(e))
        return {'code':-4004,'msg':'数据错误'}

    pipe.execute()
    log_debug('[try do_reward_exchange] return userTicket[%s]'%(exchange_info['exchange_leave_ticket']))
    return {'code':0,'msg':'兑换成功','userTicket':exchange_info['exchange_leave_ticket']}

@fish_app.post('/doAddress')
@allow_cross
def do_address(redis,session):
    '''
    玩家操作收获地址接口
    @params:
        sid
        phone
        province
        city
        address
        name
    '''
    fields = ('sid','name','phone','city','address','action')
    for field in fields:
        exec(FORMAT_PARAMS_POST_STR%(field,field))

    try:
        log_debug('[try do_address] get parasm sid[%s] name[%s] province[%s] phone[%s] city[%s] addr[%s]'%(sid,name,province,phone,city,address))
    except:
        return {'code':-300,'msg':'接口参数错误'}

    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    check_code,check_msg,user_table = check_session_verfiy(redis,'/fish/getRewardInfo/',SessionTable,account,sid,verfiySid)
    log_debug('[try do_refresh] check_code[%s] check_msg[%s]'%(check_code,check_msg))
    if int(check_code)<0:
        if check_code == -4:
            return {'code':check_code,'msg':check_msg,'osid':sid}
        return {'code':check_code,'msg':check_msg}

    if action not in ['add','modify','delete']:
        return {'code':-2001,'msg':'不被允许的操作,请重试.'}

    address_info = {
            'name'      :       name,
            'phone'     :       phone,
            'city'      :       city,
            'province'  :       province,
            'address'   :       address
    }
    action_2_fun = {
        'add'       :   do_user_modify_addr,
        'modify'    :   do_user_modify_addr,
        'delete'    :   do_user_del_addr
    }
    op_result = action_2_fun[action](redis,uid,address_info)
    log_debug('[try do_address] sid[%s] action[%s] op_result[%s]'%(sid,action,op_result))
    return {'code':0,'msg':'操作成功'}

@fish_app.post('/getAddress')
@allow_cross
def do_address(redis,session):
    '''
    玩家操作收获地址接口
    @params:
        sid
        phone
        city
        address
        name
    '''
    fields = ('sid',)
    for field in fields:
        exec(FORMAT_PARAMS_POST_STR%(field,field))

    try:
        log_debug('[try do_address] get parasm sid[%s] '%(sid))
    except:
        return {'code':-300,'msg':'接口参数错误'}

    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    check_code,check_msg,user_table = check_session_verfiy(redis,'/fish/getRewardInfo/',SessionTable,account,sid,verfiySid)
    log_debug('[try do_refresh] check_code[%s] check_msg[%s]'%(check_code,check_msg))
    if int(check_code)<0:
        if check_code == -4:
            return {'code':check_code,'msg':check_msg,'osid':sid}
        return {'code':check_code,'msg':check_msg}

    user_addr_table = FORMAT_USER_ADDRESS_TABLE%(uid)
    if not redis.exists(user_addr_table):
        return {'code':-5000,'msg':'你还没设置收货地址'}

    addr_info = redis.hgetall(user_addr_table)
    log_debug('[try do_address] sid[%s] addr_info[%s]'%(sid,addr_info))
    return {'code':0,'addressInfo':addr_info}

@fish_app.post('/doGainExchangeTicket')
@allow_cross
def do_gain_exchange_ticket(redis,session):
    """
    获取捕鱼奖品兑换卷接口
    """
    fields = ('sid','tickets')
    for field in fields:
        exec(FORMAT_PARAMS_POST_STR%(field,field))

    try:
        log_debug('[try do_gain_exchange_ticket] sid[%s] tickets[%s]'%(sid,tickets))
    except:
        return {'code':-300,'msg':'接口请求参数错误'}

    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    check_code,check_msg,user_table = check_session_verfiy(redis,'/fish/getRewardInfo/',SessionTable,account,sid,verfiySid)
    log_debug('[try do_refresh] check_code[%s] check_msg[%s]'%(check_code,check_msg))
    if int(check_code)<0:
        if check_code == -4:
            return {'code':check_code,'msg':check_msg,'osid':sid}
        return {'code':check_code,'msg':check_msg}

    if int(tickets) < 0:
        return {'code':-5001,'msg':'奖券数据错误'}
    #测试
    exchange_ticket = redis.hincrby(user_table,'exchange_ticket',int(tickets))
    return {'code':0,'userTickets':exchange_ticket}

@fish_app.post('/onGetShareReward')
@allow_cross
def get_fish_share_reward(redis,session):
    """
    金币分享获取金币接口
      分享游戏成功后回调获取分享金币
    """
    fields = ('sid',)
    for field in fields:
        exec(FORMAT_PARAMS_POST_STR%(field,field))

    try:
        log_debug('[try get_fish_share_reward] get params sid[%s]'%(sid))
    except:
        return {'code':-300,'msg':'接口请求参数错误'}

    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    check_code,check_msg,user_table = check_session_verfiy(redis,'/fish/getRewardInfo/',SessionTable,account,sid,verfiySid)
    log_debug('[try do_refresh] check_code[%s] check_msg[%s]'%(check_code,check_msg))
    if int(check_code)<0:
        if check_code == -4:
            return {'code':check_code,'msg':check_msg,'osid':sid}
        return {'code':check_code,'msg':check_msg}

    has_share_users = uid in redis.smembers(FISH_FIRST_SHARE_PER_DAY_SET)
    is_can_share    = uid in redis.smembers(FISH_SHARE_NOT_TAKE_SETS)

    if not has_share_users:
        return {'code':-3000,'msg':'你今天还未分享过游戏,赶快去分享吧!'}

    if not is_can_share:
        return {'code':-3002,'msg':'你今天已经领取过奖励!'}

    share_coin = conf.get('fish.share_coin')
    if not share_coin:
        return {'code':-3001,'msg':'error in get share_coin,try again.'}
    pipe = redis.pipeline()
    try:
        pipe.srem(FISH_SHARE_NOT_TAKE_SETS,uid)
        pipe.sadd(FISH_SHARE_TAKE_SETS,uid)
        pipe.hincrby(user_table,'coin',share_coin)
    except:
        return {'code':-3003,'msg':'数据错误'}

    pipe.execute()
    coin = redis.hget(user_table,'coin')
    log_debug('[try get_fish_share_reward] sid[%s] get shareCoin[%s] after user coin[%s]'%(sid,share_coin,coin))
    return {'code':0,'coin':int(coin)}

@fish_app.post('/getFishVersion')
@allow_cross
def getHallVersion(redis,session):
    """
    """
    HALL2VERS = getHotSettingAll(redis)
    HALL2VERS['hotUpdateURL'] = HALL2VERS['hotUpdateURL']+"/"+HALL2VERS['packName']
    return HALL2VERS

@fish_app.post('/buyCoin')
@allow_cross
def do_buyCoin(redis,session):
    """
    购买金币1
    """
    fields = ('sid','card')
    for field in fields:
        exec('%s = request.forms.get("%s","").strip()'%(field,field))

    try:
        log_debug('[try do_buyCoin] sid[%s] cardNums[%s]'%(sid,cardNums))
    except:
        return {'code':-300,'msg':'接口参数请求错误'}

    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    check_code,check_msg,user_table = check_session_verfiy(redis,'/fish/getRewardInfo/',SessionTable,account,sid,verfiySid)
    log_debug('[try do_refresh] check_code[%s] check_msg[%s]'%(check_code,check_msg))
    if int(check_code)<0:
        if check_code == -4:
            return {'code':check_code,'msg':check_msg,'osid':sid}
        return {'code':check_code,'msg':check_msg}

    groupId = redis.hget(user_table, 'parentAg')
    adminTable = AGENT_TABLE%(groupId)
    #获取增加后返回的金币
    coin = redis.hincrby(user_table,'coin',int(cardNums))
    # pipe = redis.pipeline()
    # ymd = datetime.now().strftime("%Y-%m-%d")
    # useDatas = [int(cardNums), 6, roomCards]
    # useStr = ';'.join(map(str, useDatas))
    # pipe.lpush(PLAYER_DAY_USE_CARD%(id, ymd), useStr)
    # pipe.expire(PLAYER_DAY_USE_CARD%(id, ymd), SAVE_PLAYER_DAY_USE_CARD_TIME)
    # pipe.execute()
    return {'code':0,'msg':'购买金币成功', 'coin':coin}

@fish_app.post('/joinRoom')
@allow_cross
def do_joinRoom(redis,session):
    """
    加入房间接口
    """
    fields = ('sid','gameid')
    for field in fields:
        exec('%s = request.forms.get("%s",'').strip()'%(field,field))

    try:
        log_debug('[try do_joinRoom] get params sid[%s] gameid[%s]'%(sid,gameid))
        gameId = int(gameid)
    except:
        return {'code':-300,'msg':'接口参数错误'}

    SessionTable,account,uid,verfiySid = getInfoBySid(redis,sid)
    check_code,check_msg,user_table = check_session_verfiy(redis,'/fish/getRewardInfo/',SessionTable,account,sid,verfiySid)
    log_debug('[try do_refresh] check_code[%s] check_msg[%s]'%(check_code,check_msg))
    if int(check_code)<0:
        if check_code == -4:
            return {'code':check_code,'msg':check_msg,'osid':sid}
        return {'code':check_code,'msg':check_msg}

    ag = redis.hget(user_table, 'parentAg')
    adminTable = AGENT_TABLE%(ag)
    agValid = redis.hget(adminTable,'valid')
    # if agValid != '1':
        # print  '[CraeteRoom][info] agentId[%s] has freezed. valid[%s] '%(ag,agValid)
        # return {'code':-7,'msg':'该公会已被冻结,不能创建或加入该公会的房间'}

    countPlayerLimit = 0
    gameTable = GAME_TABLE%(gameId)
    maxRoomCount = redis.hget(gameTable,'maxRoomCount')
    if not maxRoomCount:
        maxRoomCount = 0
    maxPlayerCount = redis.hget(FISH_ROOM_TABLE%(gameId), 'max_player_count')
    if maxRoomCount and maxPlayerCount:
        countPlayerLimit = int(maxRoomCount) * maxPlayerCount

    reservedServers = []
    serverList = redis.lrange(FORMAT_GAME_SERVICE_SET%(gameId), 0, -1)
    for serverTable in serverList:
        playerCount = redis.hincrby(serverTable, 'playerCount', 0)
        roomCount = redis.hincrby(serverTable, 'roomCount', 0)
        if not playerCount:
            playerCount = 0
        if not roomCount:
            roomCount = 0
        playerCount = int(playerCount)
        roomCount = int(roomCount)
        countPlayerLimit = int(countPlayerLimit)
        if countPlayerLimit and (playerCount >= countPlayerLimit or roomCount >= maxRoomCount):
            continue
        _, _, _, currency, ipData, portData = serverTable.split(':')
        reservedServers.append((currency, ipData, portData))

    if reservedServers:
        currency, serverIp, serverPort = reservedServers[0]
        # ruleText = getRuleText(rule, gameId, redis)
        # if isOther:
            # params = eval(rule)
            # params.append(int(hidden))
            # rule = str(params)
            # protocolStr = HEAD_SERVICE_PROTOCOL_CREATE_OTHER_ROOM%(account, ag, rule, ruleText)
            # redis.rpush(FORMAT_SERVICE_PROTOCOL_TABLE%(gameId, '%s:%s:%s'%(currency, serverIp, serverPort)), protocolStr)
            # return {'code':0, 'msg':'房间开启成功', 'ip':'', 'port':''}

        # redis.hmset(SessionTable,
            # {
                # 'action'   :   1,
                # 'rule'     :   rule,
                # 'ruleText' :   ruleText,
                # 'hidden'   :   hidden,
            # }
        # )
        urlRes = urlparse(request.url)
        domain = urlRes.netloc.split(':')[0]
        return {'code' : 0, 'ip' : domain, 'port' : serverPort}
    else:
        return {'code':-1, 'msg':'服务器忙碌或维护中'}

@fish_app.get('/invite')
def get_invite_page(redis,session):
    """
    捕鱼邀请页面链接
    """
    ip = request.remote_addr
    rid = request.GET.get('rid','').strip()

    HALL2VERS = get_fish_hall_setting(redis)
    log_debug('[try get_invite_path] requestIp[%s] rid[%s] versionInfo[%s]'%(ip,rid,HALL2VERS))

    links = {
            'scheme_android'        :       'dsmj://com.dsmj/invite?rid=%s'%(rid),
            'scheme_ios'            :       'com.DSYL://invite?rid=%s'%(rid),
            'download_ios'          :        HALL2VERS['IPAURL'],
            'download_android'      :       'http://a.app.qq.com/o/simple.jsp?pkgname=com.dsmj'
    }

    info = {
        'entry_title'           :           '东胜麻将',
        'scheme_ios'            :           links['scheme_ios'],
        'scheme_android'        :           links['scheme_android'],
        'ios_download'          :           links['download_android'],
        'android_download'      :           links['download_android'],
        'ifr_src'               :           '',
        'timeout'               :           1000,
    }

    response.add_header("Expires", 0);
    response.add_header( "Cache-Control", "no-cache" );
    response.add_header( "Cache-Control", "no-store" );
    response.add_header( "Cache-Control", "must-revalidate" );
    #是否限制IP
    return template('invite',info=info)
