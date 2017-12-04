#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    捕鱼模块模型
"""
from web_db_define import *
from admin  import access_module
from datetime import datetime,timedelta
from config.consts import *
from common.log import *
from common.utilt import formatCredit,ServerPagination
import random
from datetime import datetime,timedelta
from operator import itemgetter

#房间数据字段
FISH_FIELDS = ('room_id','room_name','min_coin','max_coin','base_coin',\
               'max_base_coin','step_base_coin','isTrail','max_player_count','status','ip_mask','need_coin','coin_value')
#投注记录字段
BET_FIELDS = ('')

#充值记录字段
RECHARGE_FIELDS = ('')

#在线列表要显示的数据
FISH_ONLINE_FIELDS = ('nickname','headImgUrl','parentAg','lastLoginClientType','coin')

#捕鱼房间列表可操作列表
FISH_OP_LIST = [
                    {'url':BACK_PRE+'/fish/room/modify','txt':'修改','method':'GET'},\
                    {'url':BACK_PRE+'/fish/room/delete','txt':'删除','method':'POST'},\
                    # {'url':BACK_PRE+'/game/editDesc','txt':'规则介绍修改','method':'GET'}\
]

#投注明细可操作列表
BET_OP_LIST = {
        'url':BACK_PRE+'/fish/bet/replay','txt':'查看回放','method':'POST'
}

#投注记录查询映射
SEARCH_KEY_2_TABLE = {
    'room_id'           :       FISH_BET_DATA_DETAIL4ROOM,
    'user_id'           :       ''
}

def get_room_list(redis,searchId=False,op=False):
    """
    获取捕鱼房间列表1
    params: redis,searchId(是否查询指定列表)
    """
    room_ids = redis.lrange(FISH_ROOM_LIST,0,-1)
    room_list = []
    log_debug('[try get_room_list] room_ids[%s]'%(room_ids))
    trans2IntList = ('min_coin','max_coin','base_coin','max_base_coin','step_base_coin','max_player_count')
    for room_id in room_ids:
        room_info = redis.hgetall(FISH_ROOM_TABLE%(room_id))
        room_info['need_coin']  = room_info['need_coin']  if 'need_coin'  in room_info.keys() else 0
        room_info['coin_value'] = room_info['coin_value'] if 'coin_value' in room_info.keys() else 0
        for transkey in trans2IntList:
            if room_info[transkey]:
                room_info[transkey] = int(room_info[transkey])
        if op:
            room_info['op'] = FISH_OP_LIST
        room_list.append(room_info)

    room_list = sorted(room_list, key=itemgetter('base_coin'))
    if not op:
        return room_list
    count = len(room_list)
    log_debug('[try get_room_list] dataLen[%s] room_list[%s]'%(count,room_list))
    return {'data':room_list,'count':count}

def create_fish_room(redis,roomInfo):
    """
    创建捕鱼房间
    params: redis,roomInfo(创建的房间信息)
    """
    channel_id = roomInfo['room_id']
    room_table = FISH_ROOM_TABLE%(channel_id)
    log_debug('[try create_fish_room] room_id[%s] room_table[%s]'%(channel_id,room_table))
    pipe  =  redis.pipeline()
    pipe.hmset(room_table,roomInfo)
    pipe.sadd(FISH_ROOM_ID_SETS,channel_id)
    pipe.sadd(GAMEID_SET,channel_id)
    pipe.lpush(FISH_ROOM_LIST,channel_id)
    pipe.execute()

def modify_fish_room(redis,roomInfo):
    """
    创建捕鱼房间
    params: redis,roomInfo(创建的房间信息)
    """
    channel_id = roomInfo['room_id']
    room_table = FISH_ROOM_TABLE%(channel_id)
    log_debug('[try modify_fish_room] room_id[%s] room_table[%s]'%(channel_id,room_table))
    pipe  =  redis.pipeline()
    pipe.hmset(room_table,roomInfo)
    pipe.execute()

def get_bet_list(redis,startDate,endDate,room_id,page_info,sort_info,userId=None,groupId=None):
    """
    获取捕鱼投注明细数据
    params: reids,condition(查询条件列表)
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

    bet_table = ALL_FISH_BET_DATA_DETAIL
    sum_table = ALL_FISH_BET_DATA4DAY
    if room_id:
        #根据房间号查询
        bet_table = FISH_BET_DATA_DETAIL4ROOM%(room_id,'%s')
        sum_table = FISH_BET_DATA4DAY4ROOM%(room_id,'%s')

    res,totalBetMoney,totalWinLostMoney,winLostRate = [],0,0,0
    total_datas = []
    now_time = datetime.now()
    log_debug('[try get_bet_list] startDate->[%s]'%(datetime.now()))
    while endDate >= startDate:
        if endDate > now_time:#不查没有数据的时间
            endDate-=deltaTime
            continue
        dateStr = endDate.strftime('%Y-%m-%d')
        bet_records = redis.lrange(bet_table%(dateStr),0,-1)
        #记录总投注额
        betMoney,winLostMoney = redis.hmget(sum_table%(dateStr),('bet','profit'))
        if not betMoney:
            betMoney = 0
        if not winLostMoney:
            winLostMoney = 0
        betMoney,winLostMoney = float(betMoney),float(winLostMoney)
        totalBetMoney+=betMoney
        totalWinLostMoney+=winLostMoney
        #索引出所有数据
        total_datas.extend(bet_records)

        endDate -= deltaTime

    totla_len = len(total_datas)
    #分页处理
    total_datas = ServerPagination(total_datas,page_info['page_size'],page_info['page_number'])
    for bet_record in total_datas:
        bet_record = eval(bet_record)
        betInfo = {}
        betInfo['profit'] = bet_record['profit']
        betInfo['bet_id'] = bet_record['bet_id']
        betInfo['room_id'] = bet_record['room_id']
        betInfo['bet'] = bet_record['bet']
        betInfo['uid'] = bet_record['uid']
        betInfo['datetime'] = bet_record['datetime']
        betInfo['init_coin'] = bet_record['init_coin'] if 'init_coin' in bet_record.keys() else 0
        betInfo['add_coin'] = bet_record['add_coin'] if 'add_coin' in bet_record.keys() else 0
        betInfo['login_time'] = bet_record['login_time'] if 'login_time' in bet_record.keys() else '未知'
        betInfo['op'] = []
        betInfo['op'].append(BET_OP_LIST)
        res.append(betInfo)

    if totalWinLostMoney:
        winLostRate = round(((totalWinLostMoney-totalBetMoney)/totalBetMoney)*100,2)

    if sort_info['sort_name']:
        #如果排序
        res = sorted(res, key=itemgetter(sort_info['sort_name']),reverse=FONT_CONFIG['STR_2_SORT'][sort_info['sort_method']])
    log_debug('[try get_bet_list] endDtime->[%s]'%(datetime.now()))
    return {'result':res,'count':totla_len,'betTotal':formatCredit(totalBetMoney),'winLostTotal':formatCredit(totalWinLostMoney),'winLostRate':winLostRate}


def get_bet_reports(redis,startDate,endDate,agent_id,userId=None,groupId=None):
    """
    获取捕鱼投注明细数据
    params: reids,condition(查询条件列表)
    """
    if agent_id:
        #按代理查询
        agent_lines = [agent_id]
    else:
        agent_lines = redis.smembers(AGENT_CHILD_TABLE%(1))

    try:
        startDate = datetime.strptime(startDate,'%Y-%m-%d')
        endDate   = datetime.strptime(endDate,'%Y-%m-%d')
    except:
        weekDelTime = timedelta(7)
        weekBefore = datetime.now()-weekDelTime
        startDate = weekBefore
        endDate   = datetime.now()

    tempStartDate,tempEndDate = startDate,endDate
    deltaTime = timedelta(1)
    now_time = datetime.now()
    res= []

    for agent in agent_lines:
        betInfo = {}
        totalBetMoney,totalWinLostMoney = 0,0
        startDate,endDate = tempStartDate,tempEndDate
        agent_account = redis.hget(AGENT_TABLE%(agent),'account')
        while endDate >= startDate:
            if endDate > now_time:
                endDate-=deltaTime
                continue
            dateStr = endDate.strftime('%Y-%m-%d')
            betMoney,winLostMoney = redis.hmget((AGENT_FISH_BET_DATA4DAY%(agent,dateStr)),('bet','profit'))
            if not betMoney:
                betMoney = 0
            if not winLostMoney:
                winLostMoney = 0
            betMoney,winLostMoney = float(betMoney),float(winLostMoney)
            totalBetMoney+=betMoney
            totalWinLostMoney+=winLostMoney

            endDate -= deltaTime
        betInfo['agent_id'] = agent
        betInfo['agent_account'] = agent_account
        betInfo['bet'] = totalBetMoney
        betInfo['profit'] = totalWinLostMoney
        res.append(betInfo)

    return {'data':res,'count':len(res)}

def get_recharge_list(redis,condition=[]):
    """
    获取金币充值列表
    params: redis,condition(查询条件)
    """
    pass

def get_fish_room_info(redis,room_id):
    """
    获取捕鱼房间信息
    params: redis, room_id
    """
    return redis.hgetall(FISH_ROOM_TABLE%(room_id))

def get_replay_info(redis,replay_id):
    """
    获取当局游戏的回放记录
    params: redis,replay_id(投注记录ID)
    """
    replayData = []
    datas = redis.zrangebyscore(PLAYER_REPLAY_SET, int(replay_id), int(replay_id))

    return {"data":eval(",".join(datas))}

def get_fish_online(redis,lang):
    """
    获取捕鱼在线玩家数据
    params:redis,lang
    """
    online_list = []

    online_members = redis.smembers(ONLINE_ACCOUNTS_TABLE4FISH)
    if not online_members:
        return {
            'count' :   0,   \
            'data'  :   online_list
        }
    for online_member in online_members:
        onLineTable = FORMAT_CUR_USER_GAME_ONLINE%(online_member)
        date,roomTag,serviceTag,ip = redis.hmget(onLineTable,\
                                                        ('date','game','serviceTag','ip'))
        account2user_table = FORMAT_ACCOUNT2USER_TABLE%(online_member) #从账号获得账号信息，和旧系统一样
        table = redis.get(account2user_table)
        info = redis.hgetall(table)
        userId = table.split(':')[1]
        name,imgUrl,parentAg,clientKind,coin = redis.hmget(table,FISH_ONLINE_FIELDS)
        if not coin:
            coin = 0
        online_list.append({
                'id'            :       userId,
                'account'       :       online_member,
                'name'          :       name,
                'coin'          :       coin,
                'roomTag'       :       roomTag if roomTag else '正在闲逛',
                'date'          :       date,
                'serverTag'     :       serviceTag,
                'clientKind'    :       lang.CLINET_KIND_TXTS[clientKind] if clientKind else '未知设备',
                'login_ip'      :       ip,
                'parentAg'      :       parentAg
        })

    return {
        'count' :   len(online_list),   \
        'data'  :   online_list
    }


def get_fish_sys_datas(redis,start_date,end_date):
    """
    获取捕鱼系统统计数据
    params: redis, start_date,end_date
    """
    pass
