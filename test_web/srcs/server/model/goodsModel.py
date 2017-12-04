#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    商品模型
"""
from web_db_define import *
from common.log import *
import agentModel

FISH_REWARD_LIST_OP = [
        {'url':'/admin/goods/reward/status','txt':'上架','method':'POST'},
        {'url':'/admin/goods/reward/modify','txt':'编辑','method':'POST'},
        {'url':'/admin/goods/reward/auto_charge','txt':'自动续期','method':'POST'},
        {'url':'/admin/goods/reward/del','txt':'删除','method':'POST'},
]

FISH_EXCHANGE_LIST_OP = [
        {'url':'/admin/goods/reward/exchange/status','txt':'发货','method':'POST'},

]

def createGoods(redis,goodsInfo):
    """
        创建商品
    """
    goodsId  =  redis.incr(GOODS_COUNT)
    goodsInfo['id'] = goodsId

    goodsTable = GOODS_TABLE%(goodsId)
    pipe = redis.pipeline()

    pipe.hmset(goodsTable,goodsInfo)
    pipe.lpush(GOODS_LIST,goodsId)
    return pipe.execute()

def getGoodsMoney(redis,groupId,cardNums):
    """
    获取每个玩家所在公会的价格
    """
    companyId = agentModel.getTopAgentId(redis,groupId)
    log_debug('[getGoodsMoney] groupId[%s] cardNums[%s] companyId[%s]'%(groupId,cardNums,companyId))
    unitPrice = redis.hget(AGENT_TABLE%(companyId),'unitPrice')

    return int(cardNums)*float(unitPrice)

def getGoodsList(redis):
    """
    获取商品列表
    """
    goodIds = redis.lrange(GOODS_LIST,0,-1)
    goodsList = []
    type2name = {
            '0'     :       '游戏钻石',
            '1'     :       '游戏金币'
    }
    for goodId in goodIds:
        goodInfo = redis.hgetall(GOODS_TABLE%(goodId))
        if not goodInfo.has_key('type'):
            #默认为钻石
            goodInfo['type'] = '0'

        goodInfo['goods_type'] = type2name[goodInfo['type']]
        goodInfo['op'] = [
                        {'url':'/admin/goods/modify','txt':'修改','method':'POST'},
                        {'url':'/admin/goods/del','txt':'删除','method':'POST'},
        ]
        goodsList.append(goodInfo)

    return goodsList

def getDimonGoodsList(redis,groupId):
    """
    获取钻石商品列表
    """
    goodIds = redis.lrange(GOODS_LIST,0,-1)
    goodsList = []
    for goodId in goodIds:
        goodInfo = redis.hgetall(GOODS_TABLE%(goodId))
        if goodInfo.has_key('type') and goodInfo['type'] != '0':
            continue

        goodsMoney = getGoodsMoney(redis,groupId,goodInfo['cards'])
        goodInfo['price'] = goodsMoney
        goodsList.append(goodInfo)

    return goodsList


def getCoinGoodsList(redis):
    """
    获取金币商品列表
    """
    goodIds = redis.lrange(GOODS_LIST,0,-1)
    goodsList = []
    for goodId in goodIds:
        goodInfo = redis.hgetall(GOODS_TABLE%(goodId))
        log_debug('[goodsInfo][%s]'%(goodInfo))
        if not goodInfo.has_key('type'):
            continue
        if goodInfo['type'] != '1':
            continue
        # goodsMoney = getGoodsMoney(redis,groupId,goodInfo['cards'])
        # goodInfo['price'] = goodsMoney
        goodsList.append(goodInfo)

    log_debug('[return goods[%s]]'%(goodsList))
    return goodsList

def goodsModify(redis,goodsId,goodsInfo):
    """
    商品模块修改
    """
    return redis.hmset(GOODS_TABLE%(goodsId),goodsInfo)

def getGoodsInfo(redis,goodsId):
    """
    获取商品信息
    """
    return redis.hgetall(GOODS_TABLE%(goodsId))

def get_reward_info(redis,reward_id):
    '''
    获取奖品信息
    '''
    return redis.hgetall(FISH_REWARD_TABLE%(reward_id))


def setGoodsPrice(redis,price):
    """
    设置房卡单价
    """

    return redis.lpush(GOODS_ROOMCARD_PRICE,price)


def getGoodsPrice(redis):
    """
    获取最新房卡单价
    """
    return redis.lrange(GOODS_ROOMCARD_PRICE,0,1)[0]

def do_create_reward(redis,reward_info):
    '''
    创建奖品列表
    '''
    pipe = redis.pipeline()
    try:
        pipe.lpush(FISH_REWARD_LIST,reward_info['reward_id'])
        pipe.hmset(FISH_REWARD_TABLE%(reward_info['reward_id']),reward_info)
        pipe.sadd(FISH_REWARD_ID_SET,reward_info['reward_id'])
    except Exception,e:
        log_debug('[try do_create_reward] create error[%s]'%(e))
        return

    pipe.execute()

def do_modify_reward(redis,reward_info):
    '''
    修改奖品信息
    '''
    pipe = redis.pipeline()
    pipe.hmset(FISH_REWARD_TABLE%(reward_info['reward_id']),reward_info)

    pipe.execute()

def get_fish_reward_list(redis,get_op=True):
    '''
    获取奖品列表
    '''
    reward_ids = redis.lrange(FISH_REWARD_LIST,0,-1)
    reward_lists = []
    for reward_id in reward_ids:
        reward_info = redis.hgetall(FISH_REWARD_TABLE%(reward_id))
        if get_op:
            reward_info['op'] = FISH_REWARD_LIST_OP
        reward_lists.append(reward_info)

    return reward_lists

def get_reward_shop_data(redis,on_shop_fields):
    """
    获取商城数据
    """
    reward_onshop_ids = redis.lrange(FISH_REWARD_ON_SHOP_LIST,0,-1)
    shop_lists = []
    #onshop_fields = ('reward_name','reward_id','reward_stock','reward_img_path','reward_need_ticket')
    for onshop_id in reward_onshop_ids:
        log_debug('onshopId[%s]'%(onshop_id))
        shop_info = {}
        reward_name,reward_stock,reward_img_path,reward_need_ticket = redis.hmget(FISH_REWARD_TABLE%(onshop_id),on_shop_fields)
        shop_info['reward_name'] = reward_name
        shop_info['reward_id'] = int(onshop_id)
        shop_info['reward_stock'] = reward_stock
        shop_info['reward_img_path'] = reward_img_path
        shop_info['reward_need_ticket'] = int(reward_need_ticket)
        shop_lists.append(shop_info)
    return shop_lists

def get_exchange_infos(redis,start_date,end_date,user_id):
    '''
    获取玩家兑换信息列表
    '''
    exchange_ids = redis.lrange(FISH_EXCHANGE_LIST,0,-1)

    exchange_id_keys = [FISH_EXCHANGE_TABLE%(exchange_id) for exchange_id in exchange_ids]
    log_debug(exchange_id_keys)
    exchange_details = [exchange_detail for exchange_detail in redis.mget(exchange_id_keys)]
    exchange_info = []
    log_debug(exchange_details)
    for exchange_detail in exchange_details:
        exchange_detail = eval(exchange_detail)
        exchange_detail['op'] = FISH_EXCHANGE_LIST_OP
        exchange_info.append(exchange_detail)

    return {'data':exchange_info,'count':len(exchange_info)}
