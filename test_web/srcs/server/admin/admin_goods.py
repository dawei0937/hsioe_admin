#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    商品管理模块
"""
from bottle import *
from admin import admin_app
from config.consts import  STATIC_LAYUI_PATH,STATIC_ADMIN_PATH,BACK_PRE,RES_VERSION
from common.utilt import *
from common.log import *
from datetime import datetime
from web_db_define import *
from model.goodsModel import *
from model.agentModel import *
from access_module import *
import hashlib
import json
import md5
import time

#奖品字段俞
reward_fields = (
            'token',
            'reward_id',
            'img_path1',
            'reward_name',
            'reward_stock',
            'img_path',
            'reward_need_ticket',
            'reward_pos',           #奖品位置
            'reward_nums',          #奖品总期数
            'reward_now_nums',      #奖品当前期数
            'reward_cost',          #奖品成本
            'reward_type',          #奖品类型
            'reward_status',        #奖品状态
            'reward_auto_charge',        #奖品自动续期开关
            'reward_card_no',           #奖品卡号
            'reward_card_pwd',          #奖品密码
)

@admin_app.get('/goods/list')
def getGoodList(redis,session):
    """
    商品列表视图
    """
    lang = getLang()

    isList = request.GET.get('list','').strip()

    info = {
            'title'         :     lang.GOODS_LIST_TXT,
            'addTitle'      :     lang.GOODS_CREATE_TXT,
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
            'tableUrl'      :     BACK_PRE+'/goods/list?list=1'
    }
    #accesses = eval(session['access'])

    if isList:
        res = getGoodsList(redis)
        return json.dumps(res)
    else:
        #info['createAccess'] = True if BACK_PRE+'/game/create' in accesses else False
        info['createUrl']   = BACK_PRE+'/goods/create'
        return template('admin_good_list',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/goods/fish/reward/list')
def getGoodList(redis,session):
    """
    捕鱼奖品兑换设置页面
    """
    lang = getLang()

    isList = request.GET.get('list','').strip()

    info = {
            'title'         :     '兑换奖品列表',
            'addTitle'      :     lang.GOODS_REWARD_CREATE_TXT,
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
            'exchang_record_list_url' :     BACK_PRE+'/goods/reward/exchange/list',
            'tableUrl'      :     BACK_PRE+'/goods/fish/reward/list?list=1'
    }

    if isList:
        res = get_fish_reward_list(redis)
        return json.dumps(res)
    else:
        #info['createAccess'] = True if BACK_PRE+'/game/create' in accesses else False
        info['createUrl']   = BACK_PRE+'/goods/reward/create'
        return template('admin_goods_reward',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/goods/reward/create')
def getGoodsCreate(redis,session):
    """
    创建捕鱼兑换奖品视图
    """
    lang = getLang()

    page_token = md5.new(str(time.time())).hexdigest()
    info = {
            'title'             :       lang.GOODS_CREATE_TXT,
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
            'back_pre'          :       BACK_PRE,
            'backUrl'           :       BACK_PRE+'/goods/list',
            'submitUrl'         :       BACK_PRE+'/goods/reward/create',
            'upload_url'        :       BACK_PRE+'/goods/reward/upload',
            'token'             :       page_token

    }
    #recordLastURL(session,BACK_PRE+'/game/list')
    return template('admin_goods_reward_create',message='',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/goods/reward/create')
def do_reward_create(redis,session):
    """
    创建捕鱼兑换奖品视图
    """
    lang = getLang()
    curTime = datetime.now()

    for reward_field in reward_fields:
        exec("%s = request.forms.get('%s','').strip()"%(reward_field,reward_field))

    check_null_fields = [
                {'fields':reward_name,'msg':'奖品名称不能为空'},
                {'fields':reward_stock,'msg':'奖品初始库存不能为空'},
                {'fields':reward_need_ticket,'msg':'奖品所需兑换卷不能为空'},
                {'fields':reward_nums,'msg':'奖品总期数不能为空'},
                {'fields':reward_now_nums,'msg':'奖品当前期数不能为空'}
    ]

    for check_field in check_null_fields:
        if not check_field['fields']:
            return {'code':1,'msg':check_field['msg']}

    log_debug('[try do_reward_create] reward_id[%s] reward_name[%s] reward_stock[%s] reward_img_path[%s]'\
                    %(reward_id,reward_name,reward_stock,img_path))

    reward_id = redis.incr(FISH_REWARD_ID_COUNT)
    reward_info = {
            'reward_id'            :      reward_id,
            'reward_name'          :      reward_name,
            'reward_stock'         :      reward_stock,
            'reward_img_path'      :      img_path[14:],
            'reward_need_ticket'   :      reward_need_ticket,
            'reward_pos'           :      reward_pos,           #奖品位置
            'reward_nums'          :      reward_nums,          #奖品总期数
            'reward_now_nums'      :      reward_now_nums,      #奖品当前期数
            'reward_cost'          :      reward_cost,          #奖品成本
            'reward_type'          :      reward_type,          #奖品类型
            'reward_status'        :      reward_status if reward_status else 0,        #奖品状态
            'reward_auto_charge'   :      0,
            'reward_card_no'       :      reward_card_no if reward_card_no else '',          #奖品卡号
            'reward_card_pwd'      :      reward_card_pwd if reward_card_pwd else ''         #奖品密码

    }

    try:
        do_create_reward(redis,reward_info)
    except Exception,e:
        return {'code':1,'msg':'创建奖品失败错误代码:[%s]'%(e)}

    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
            'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['reward_create']%('/goods/reward/create',reward_name)}
    #记录日志
    writeAgentOpLog(redis,session['id'],logInfo)
    return {'code':0,'msg':'创建奖品[%s]成功!'%(reward_name),'jumpUrl':BACK_PRE+'/goods/fish/reward/list'}

@admin_app.get('/goods/reward/modify')
def get_reward_modify(redis,session):
    """
    捕鱼奖品修改视图
    """

    curTime = datetime.now()
    lang    = getLang()
    reward_id  = request.GET.get('reward_id','').strip()

    reward_info  =  get_reward_info(redis,reward_id)
    page_token = md5.new(str(time.time())).hexdigest()
    info = {
                'title'     :       lang.GOODS_MODIFY_TXT%(reward_info['reward_name']),
                'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
                'back_pre'          :       BACK_PRE,
                'backUrl'           :       BACK_PRE+'/goods/fish/reward/list',
                'submitUrl'         :       BACK_PRE+'/goods/reward/modify',
                'upload_url'        :       BACK_PRE+'/goods/reward/upload',
                'token'             :       page_token
    }

    return template('admin_goods_reward_modify',info=info,reward=reward_info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/goods/reward/modify')
def do_reward_modify(redis,session):
    """
    修改捕鱼奖品接口
    """
    lang = getLang()
    curTime = datetime.now()

    for reward_field in reward_fields:
        exec("%s = request.forms.get('%s','').strip()"%(reward_field,reward_field))

    check_null_fields = [
                {'fields':reward_id,'msg':'奖品ID不能为空'},
                {'fields':reward_name,'msg':'奖品名称不能为空'},
                {'fields':reward_stock,'msg':'奖品初始库存不能为空'},
                {'fields':reward_need_ticket,'msg':'奖品所需兑换卷不能为空'},
                {'fields':reward_nums,'msg':'奖品总期数不能为空'},
                {'fields':reward_now_nums,'msg':'奖品当前期数不能为空'}
    ]

    for check_field in check_null_fields:
        if not check_field['fields']:
            return {'code':1,'msg':check_field['msg']}

    log_debug('[try do_reward_modify] reward_id[%s] reward_name[%s] reward_stock[%s] reward_img_path[%s]'\
                    %(reward_id,reward_name,reward_stock,img_path))

    if img_path.startswith("mahjong/static"):#去掉头部
        ori_file_name = "mahjong/static"+img_path1
        if os.path.exists(ori_file_name):
            #删除原来的图片。
            os.remove(ori_file_name)
        #生成新的路径
        img_path = img_path[14:]

    reward_info = {
            'reward_id'            :      reward_id,
            'reward_name'          :      reward_name,
            'reward_stock'         :      reward_stock,
            'reward_img_path'      :      img_path,
            'reward_need_ticket'   :      reward_need_ticket,
            'reward_pos'           :      reward_pos,           #奖品位置
            'reward_nums'          :      reward_nums,          #奖品总期数
            'reward_now_nums'      :      reward_now_nums,      #奖品当前期数
            'reward_cost'          :      reward_cost,          #奖品成本
            'reward_type'          :      reward_type,          #奖品类型
            'reward_status'        :      reward_status if reward_status else 0,        #奖品状态
            'reward_card_no'       :      reward_card_no if reward_card_no else '',           #奖品卡号
            'reward_card_pwd'      :      reward_card_pwd if reward_card_pwd else '',          #奖品密码
    }

    try:
        do_modify_reward(redis,reward_info)
    except Exception,e:
        return {'code':1,'msg':'修改奖品失败错误代码:[%s]'%(e)}

    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
            'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['reward_modify']%('/goods/reward/modify',reward_name)}
    #记录日志
    writeAgentOpLog(redis,session['id'],logInfo)
    return {'code':0,'msg':'修改奖品[%s]成功!'%(reward_name),'jumpUrl':BACK_PRE+'/goods/fish/reward/list'}

@admin_app.post('/goods/reward/upload')
def do_file_upload(redis,session):
    '''
    奖品图片上传接口
    @params:

    '''
    files = request.files.get('files')

    file_name,file_ext = files.filename.split('.')
    #文件新名称
    new_file_name = file_name+md5.new(str(file_name)+str(time.time())).hexdigest()+"."+file_ext
    #文件上传路劲
    file_save_path = FILES_REWARD_UPLOAD_PATH%(new_file_name)
    log_debug('[try do_file_upload] file_name[%s] file_path[%s]'%(new_file_name,file_save_path))
    #保存文件
    files.save(file_save_path)

    return json.dumps({'path':file_save_path})

@admin_app.post('/goods/reward/auto_charge')
def do_auto_charge(redis,session):
    """
    开启关闭自动续期接口
    """
    curTime = datetime.now()
    fields = ('reward_id',)
    for field in fields:
        exec("%s=request.forms.get('%s','').strip()"%(field,field))

    if not reward_id:
        return {'code':1,'msg':'参数错误'}

    checkDesc = {
             1      :     '关闭奖品ID为[%s]的自动续期成功',
             0      :     '开启奖品ID为[%s]的自动续期成功'
    }

    reward_table = FISH_REWARD_TABLE%(reward_id)
    reward_auto_charge = redis.hget(reward_table,'reward_auto_charge')
    if not reward_auto_charge:
        reward_auto_charge = 0
    reward_auto_charge = int(reward_auto_charge)

    pipe = redis.pipeline()
    auto_charge_set = redis.smembers(FISH_REWARD_AUTO_CHARGE)
    if reward_auto_charge == 1:
        if reward_id in auto_charge_set:
            pipe.srem(FISH_REWARD_AUTO_CHARGE,reward_id)
        pipe.hset(reward_table,'reward_auto_charge',0)
    else:
        pipe.hset(reward_table,'reward_auto_charge',1)
        pipe.sadd(FISH_REWARD_AUTO_CHARGE,reward_id)

    pipe.execute()
    return {'code':0,'msg':checkDesc[reward_auto_charge]%(reward_id),'jumpUrl':BACK_PRE+'/goods/fish/reward/list'}

@admin_app.post('/goods/reward/status')
def do_auto_charge(redis,session):
    """
    奖品上架接口
    """
    curTime = datetime.now()
    fields = ('reward_id',)
    for field in fields:
        exec("%s=request.forms.get('%s','').strip()"%(field,field))

    if not reward_id:
        return {'code':1,'msg':'参数错误'}

    checkDesc = {
             1      :     '奖品ID为[%s]的商品下架成功',
             0      :     '奖品ID为[%s]的商品上架成功'
    }

    reward_table = FISH_REWARD_TABLE%(reward_id)
    reward_status = redis.hget(reward_table,'reward_status')
    if not reward_status:
        reward_status = 0
    reward_status = int(reward_status)

    pipe = redis.pipeline()
    #auto_charge_set = redis.smembers(FISH_REWARD_AUTO_CHARGE)
    if reward_status == 1:
        pipe.hset(reward_table,'reward_status',0)
        pipe.lrem(FISH_REWARD_ON_SHOP_LIST,reward_id)
    else:
        pipe.hset(reward_table,'reward_status',1)
        pipe.lpush(FISH_REWARD_ON_SHOP_LIST,reward_id)

    pipe.execute()
    return {'code':0,'msg':checkDesc[reward_status]%(reward_id),'jumpUrl':BACK_PRE+'/goods/fish/reward/list'}


@admin_app.get('/goods/reward/exchange/list')
def get_reward_exchange_list(redis,session):
    """
    奖品兑换记录接口
    """
    lang = getLang()
    fields = ('isList','start_date','end_date','user_id')
    for field in fields:
        log_debug('%s = request.GET.get("%s",'').strip()'%(field,field))
        exec('%s = request.GET.get("%s","").strip()'%(field,field))

    log_debug('[try get_reward_exchange_list] isList[%s] start_date[%s] end_date[%s] user_id[%s]'\
                %(isList,start_date,end_date,user_id))

    if isList:
        exchange_infos = get_exchange_infos(redis,start_date,end_date,user_id)
        return json.dumps(exchange_infos)
    else:
        info = {
                'title'     :       '奖品兑换记录',
                'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
                'tableUrl'               :       BACK_PRE+'/goods/reward/exchange/list?isList=1',
                'searchTxt'              :       '请输入玩家ID',
                'submitUrl'              :       BACK_PRE+'/goods/reward/modify',
                'upload_url'             :       BACK_PRE+'/goods/reward/upload'
        }
        return template('admin_goods_reward_exchange',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/goods/create')
def getGoodsCreate(redis,session):
    """
    创建商品视图
    """
    lang = getLang()

    info = {
            'title'             :       lang.GOODS_CREATE_TXT,
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
            'back_pre'          :       BACK_PRE,
            'backUrl'           :       BACK_PRE+'/goods/list',
            'submitUrl'         :       BACK_PRE+'/goods/create'
    }

    #recordLastURL(session,BACK_PRE+'/game/list')

    return template('admin_good_create',message='',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/goods/create')
def do_goodsCreate(redis,session):
    """
    创建商品控制器
    """
    curTime = datetime.now()
    lang    = getLang()

    name     =  request.forms.get('name','').strip()
    cards    =  request.forms.get('cards','').strip()
    present_cards = request.forms.get('present_cards','').strip()
    price    =  request.forms.get('price','').strip()
    goods_type = request.forms.get('goods_type','').strip()

    checkNullFields = [
        {'field':name,'msg':lang.GOODS_NOT_EMPTY_TXT},
        {'field':cards,'msg':lang.GOODS_CARD_NOT_EMPTY_TXT},
        {'field':price,'msg':lang.GOODS_PRICE_NOT_EMPTY}
    ]

    for check in checkNullFields:
        if not check['field']:
            return {'code':1,'msg':check['msg']}

    #print
    print '[%s][goodsCreate][info] name[%s] cards[%s] present_cards[%s] price[%s]'\
                    %(curTime,name,cards,present_cards,price)

    goodsInfo = {

            'name'          :       name,
            'type'          :       goods_type, # 0-钻石 1-金币
            'cards'         :       cards,
            'present_cards' :       present_cards,
            'price'         :       price
    }

    if createGoods(redis,goodsInfo):
        return {'code':0,'msg':lang.GOODS_CREATE_SUCCESS_TXT%(name),'jumpUrl':BACK_PRE+'/goods/list'}

    return {'code':1,'msg':lang.GOODS_CREATE_ERROR_TXT%(name)}

@admin_app.get('/goods/modify')
def getGoodsModify(redis,session):
    """
    商品信息修改
    """

    curTime = datetime.now()
    lang    = getLang()
    goodsId  = request.GET.get('goodsId','').strip()

    #print
    print '[%s][game Modify] goodsId[%s]'%(curTime,goodsId)

    goodsInfo  =  getGoodsInfo(redis,goodsId)
    if not goodsInfo.has_key('type'):
        #默认为0
        goodsInfo['type'] = '0'

    info = {
                'title'     :       lang.GOODS_MODIFY_TXT%(goodsInfo['name']),
                'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
                'back_pre'          :       BACK_PRE,
                'backUrl'           :       BACK_PRE+'/goods/reward/list',
                'submitUrl'         :       BACK_PRE+'/goods/modify'
    }

    return template('admin_good_modify',info=info,goodsInfo=goodsInfo,lang=lang,goodsId=goodsId,RES_VERSION=RES_VERSION)

@admin_app.post('/goods/modify')
def do_goodsModify(redis,session):
    """
    商品信息修改控制器
    """
    curTime = datetime.now()
    lang    = getLang()

    goodsId  =  request.forms.get('goodsId','').strip()
    name     =  request.forms.get('name','').strip()
    cards    =  request.forms.get('cards','').strip()
    present_cards = request.forms.get('present_cards','').strip()
    price    =  request.forms.get('price','').strip()

    checkNullFields = [
        {'field':name,'msg':lang.GOODS_NOT_EMPTY_TXT},
        {'field':cards,'msg':lang.GOODS_CARD_NOT_EMPTY_TXT},
        {'field':price,'msg':lang.GOODS_PRICE_NOT_EMPTY}
    ]

    for check in checkNullFields:
        if not check['field']:
            return {'code':1,'msg':check['msg']}

    #print
    print '[%s][goodsModify][info] name[%s] cards[%s] present_cards[%s] price[%s]'\
                    %(curTime,name,cards,present_cards,price)

    goodsInfo = {

            'name'          :       name,
            'cards'         :       cards,
            'present_cards' :       present_cards,
            'price'         :       price
    }

    if goodsModify(redis,goodsId,goodsInfo):
        logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['goodsModify']%('/goods/modify',goodsId)}
        #记录日志
        writeAgentOpLog(redis,session['id'],logInfo)
        return {'code':0,'msg':lang.GOODS_MODIFY_SUCCESS_TXT%(name),'jumpUrl':BACK_PRE+'/goods/list'}

    return {'code':1,'msg':lang.GOODS_MODIFY_ERROR_TXT%(name)}

@admin_app.post('/goods/del')
def do_goodsModify(redis,session):
    """
    商品信息修改控制器
    """
    curTime = datetime.now()
    lang    = getLang()

    goodsId  =  request.forms.get('id','').strip()

    checkNullFields = [
        {'field':goodsId,'msg':'商品ID不存在'},
    ]

    for check in checkNullFields:
        if not check['field']:
            return {'code':1,'msg':check['msg']}

    pipe = redis.pipeline()
    try:
        pipe.lrem(GOODS_LIST,goodsId)
        pipe.delete(GOODS_TABLE%(goodsId))
    except Exception,e:
        log_debug('[GOODS][url:/goods/del] delete goods[%s] faield. reason[%s]'%(goodsId,e))
        return {'code':1,'msg':'删除商品失败'}

    pipe.execute()
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['goodsDel']%(goodsId)}
    #记录日志
    writeAgentOpLog(redis,session['id'],logInfo)
    return {'code':0,'msg':'删除商品成功','jumpUrl':BACK_PRE+'/goods/list'}

@admin_app.get('/goods/setting')
def getGoodsSetting(redis,session):
    """
    获取商品价格设置
    """
    curTime  =  datetime.now()
    lang     =  getLang()

    goodsPrice = getGoodsPrice(redis)

    info = {
                'title'                  :       lang.GOODS_SETTING_TXT,
                'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
                'back_pre'          :       BACK_PRE,
                'backUrl'           :       BACK_PRE+'/goods/setting',
                'createUrl'         :       BACK_PRE+'/goods/setting'
    }

    return template('admin_good_setting',info=info,lang=lang,goodsPrice=goodsPrice,RES_VERSION=RES_VERSION)

@admin_app.post('/goods/setting')
def do_GoodsSetting(redis,session):
    """
    设置商品价格
    """
    curTime = datetime.now()
    lang    = getLang()

    goodsPrice = request.forms.get('goodsPrice','').strip()

    if not goodsPrice:
        return {'code':1,'msg':lang.GOODS_PRICE_NOT_EMPTY}

    #print
    print '[%s][goods setting][info] goodsPrice[%s]'%(curTime,goodsPrice)

    info = {
                'title'                  :       lang.GOODS_SETTING_TXT,
                'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
                'back_pre'          :       BACK_PRE,
                'backUrl'           :       BACK_PRE+'/goods/setting',
                'createUrl'         :       BACK_PRE+'/goods/setting'
    }

    if setGoodsPrice(redis,goodsPrice):
        return {'code':0,'msg':lang.GOODS_PRICE_SETTING_TXT%(goodsPrice),'jumpUrl':BACK_PRE+"/goods/setting"}

    return {'code':1,'msg':lang.GOODS_SETTING_TXT_ERROR}
