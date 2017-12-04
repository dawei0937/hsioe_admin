#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    this is Description
"""
from bottle import *
from admin import admin_app
from config.consts import  STATIC_LAYUI_PATH,STATIC_ADMIN_PATH,BACK_PRE,PARTY_PLAYER_COUNT
from common.utilt import *
from common.log import *
from datetime import datetime
from model.gameModel import *
from model.agentModel import *
from model.protoclModel import *
from model.fishModel import *
import json

FORMART_POST_STR = "%s = request.forms.get('%s','').strip()"
FORMART_GET_STR  = "%s = request.GET.get('%s','').strip()"

@admin_app.get('/fish')
def get_fish_admin(redis,session):
    '''
    捕鱼后台入口
    '''
    lang = getLang()
    curTime = datetime.now()
    myAccesses = eval(session['access'])
    agentInfo = redis.hgetall(AGENT_TABLE%(session['id']))
    mainModules = []
    # 一级菜单定位
    i= -1
    # 二级菜单定位
    j= -1
    for accessObj in access_module.FISH_MENU_MODULES:
        if accessObj.check and (accessObj.url in myAccesses):
            i+=1
            # 重置二级菜单定位
            j=-1
            mainModule = {}
            mainModule['url'] = accessObj.url
            mainModule['txt'] = accessObj.getTxt(lang)
            mainModule['subModules'] = []
            mainModules.append(mainModule)

        elif len(accessObj.tree) != 2 and (accessObj.url in myAccesses):
            j+=1
            subModule = {}
            subModule['url'] = accessObj.url
            subModule['txt'] = accessObj.getTxt(lang)
            subModule['subsubModules'] = []
            mainModules[i]['subModules'].append(subModule)
        elif len(accessObj.tree) == 2 and (accessObj.url in myAccesses):
            if j==-1:
                subModule = {}
                subModule['url'] = accessObj.url
                subModule['txt'] = accessObj.getTxt(lang)
                subModule['subsubModules'] = []
                mainModules[i]['subModules'].append(subModule)
            else:
                subsubModule = {}
                subsubModule['url'] = accessObj.url
                subsubModule['txt'] = accessObj.getTxt(lang)
                mainModules[i]['subModules'][j]['subsubModules'].append(subsubModule)

    if int(agentInfo['type']) in [SYSTEM_ADMIN]:
        roomcard = '无限制'
    else:
        roomcard = agentInfo['roomcard']

    try:
        open_auth = int(agentInfo['open_auth'])
    except:
        open_auth = 0

    open_auth_text = OPENAUTH_2_TXT[open_auth]
    if int(agentInfo['type']) != 0:
        parentId = agentInfo['parent_id']
        parentAccount = redis.hget(AGENT_TABLE%(parentId),'account')
    else:
        parentId=''
        parentAccount=''

    info = {
        'STATIC_ADMIN_PATH'     :   STATIC_ADMIN_PATH,
        'ADMIN_DEFAULT_PAGE'    :   '/admin/home',
        'agentType'             :   int(agentInfo['type']),
        'parentId'              :   parentId,
        'parentAccount'         :   parentAccount,
        'open_auth_text'        :   open_auth_text,
        'link_fish_url'         :   '/admin',
        'link_fish_txt'         :   '棋牌后台管理'
    }

    index_tpl = template('admin_base',info=info,roomcard=roomcard,RES_VERSION=RES_VERSION,lang=lang,\
                          session=session,agentInfo=agentInfo,TYPE2TXT=lang.TYPE_2_ADMINTYPE,mainModules=mainModules)

    return index_tpl

@admin_app.get('/fish/room/list')
@checkAccess
def getFishRoomList(redis,session):
    """
    捕鱼房间列表
    """
    lang = getLang()
    isList = request.GET.get('list','').strip()
    info = {
            'title'         :     lang.FISH_ROOM_LIST_TXT,
            'addTitle'      :     lang.FISH_ROOM_CREATE_TXT,
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
            'serversUrl'    :     BACK_PRE+'/game/server/list?list=1',
            'tableUrl'      :     BACK_PRE+'/fish/room/list?list=1'
    }
    #accesses = eval(session['access'])
    if isList:
        res = get_room_list(redis,False,True)
        return json.dumps(res)
    else:
        #info['createAccess'] = True if BACK_PRE+'/game/create' in accesses else False
        info['createUrl']   = BACK_PRE+'/fish/room/create'
        return template('admin_fish_room_list',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/fish/room/create')
@checkAccess
def getFishRoomCreate(redis,session):
    """
    创建捕鱼房间
    """
    lang = getLang()

    info = {
            'title'             :       lang.FISH_ROOM_CREATE_TXT,
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
            'back_pre'          :       BACK_PRE,
            'backUrl'           :       BACK_PRE+'/fish/room/list',
            'submitUrl'         :       BACK_PRE+'/fish/room/create',
    }

    return template('admin_fish_room_create',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.post('/fish/room/create')
def do_createFishRoom(redis,session):
    """
    创建捕鱼房间
    """
    lang = getLang()
    curTime = datetime.now()
    #获取数据
    for FIELDS in FISH_FIELDS:
        exec(FORMART_POST_STR%(FIELDS,FIELDS))

    log_debug('[try do_createFishRoom]')

    checkNullFields = [
        {'field':room_name,'msg':lang.FISH_ROOM_NAME_EMPTY_TXT},
        {'field':room_id,'msg':lang.FISH_ROOM_ID_EMPTY_TXT},
        {'field':base_coin,'msg':lang.FISH_ROOM_BASE_EMPTY_TXT},
        {'field':max_base_coin,'msg':lang.FISH_ROOM_MAX_BASE_EMPTY_TXT},
        {'field':step_base_coin,'msg':lang.FISH_ROOM_STEP_BASE_EMPTY_TXT}
    ]

    for check in checkNullFields:
        if not check['field']:
            return {'code':1,'msg':check['msg']}

    fish_ids = redis.smembers(GAMEID_SET)
    if room_id in fish_ids:
        #房间ID不能重复
        return {'code':1,'msg':'房间ID[%s]已经存在!'%(room_id)}

    roomInfo = {
            'room_id'            :       room_id,
            'room_name'          :       room_name,
            'min_coin'           :       min_coin,
            'max_coin'           :       max_coin,
            'ip_mask'            :       ip_mask,
            'max_player_count'   :       max_player_count,
            'base_coin'          :       base_coin,
            'max_base_coin'      :       max_base_coin,
            'step_base_coin'     :       step_base_coin,
            'status'             :       0,
            'need_coin'          :       need_coin  if need_coin else 0,
            'coin_value'         :       coin_value if coin_value else 0,
            'isTrail'            :       isTrail,
    }

    try:
        create_fish_room(redis,roomInfo)
        log_debug('[try do_createFishRoom] room_id[%s] roomInfo[%s] create success.'%(room_id,roomInfo))
    except Exception,e:
        return {'code':2,'msg':'reason[%s]'%(e)}

    #记录操作日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                    'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['createFishRoom']%(room_name)}
    #记录日志
    writeAgentOpLog(redis,session['id'],logInfo)
    return {'code':0,'msg':'房间[%s]创建成功.'%(room_name),'jumpUrl':BACK_PRE+'/fish/room/list'}

@admin_app.get('/fish/room/modify')
def getFishRoomModify(redis,session):
    """
    修改捕鱼房间
    """
    lang = getLang()
    room_id = request.GET.get('room_id','').strip()
    fish_ids = redis.smembers(FISH_ROOM_ID_SETS)
    if room_id not in fish_ids:
        raise "room_id[%s] is not exists."%(room_id)
        return

    log_debug('[try getFishRoomModify] room_id[%s]'%(room_id))
    room_info  =  get_fish_room_info(redis,room_id)

    #避免新增字段
    if 'need_coin' not in room_info.keys():
        room_info['need_coin'] = 0
    if 'coin_value' not in room_info.keys():
        room_info['coin_value'] = 0

    info = {
            'title'             :       lang.FISH_ROOM_MODIFY_TXT,
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
            'backUrl'           :       BACK_PRE+'/fish/room/list',
            'submitUrl'         :       BACK_PRE+'/fish/room/modify',
            'back_pre'          :       BACK_PRE
    }

    return template('admin_fish_room_modify',info=info,lang=lang,room_info=room_info,RES_VERSION=RES_VERSION)


@admin_app.post('/fish/room/modify')
def do_modifyFishRoom(redis,session):
    """
    修改捕鱼房间
    """
    lang = getLang()
    curTime = datetime.now()
    #获取数据
    for FIELDS in FISH_FIELDS:
        exec(FORMART_POST_STR%(FIELDS,FIELDS))

    log_debug('[try do_modifyFishRoom]')

    checkNullFields = [
        {'field':room_name,'msg':lang.FISH_ROOM_NAME_EMPTY_TXT},
        {'field':room_id,'msg':lang.FISH_ROOM_ID_EMPTY_TXT},
        {'field':base_coin,'msg':lang.FISH_ROOM_BASE_EMPTY_TXT},
        {'field':max_base_coin,'msg':lang.FISH_ROOM_MAX_BASE_EMPTY_TXT},
        {'field':step_base_coin,'msg':lang.FISH_ROOM_STEP_BASE_EMPTY_TXT}
    ]

    for check in checkNullFields:
        if not check['field']:
            return {'code':1,'msg':check['msg']}

    roomInfo = {
            'room_id'            :       room_id,
            'room_name'          :       room_name,
            'min_coin'           :       min_coin,
            'max_coin'           :       max_coin,
            'ip_mask'            :       ip_mask,
            'max_player_count'   :       max_player_count,
            'base_coin'          :       base_coin,
            'max_base_coin'      :       max_base_coin,
            'step_base_coin'     :       step_base_coin,
            'status'             :       0,
            'isTrail'            :       isTrail,
            'need_coin'          :       need_coin  if need_coin else 0,
            'coin_value'         :       coin_value if coin_value else 0,
    }

    try:
        modify_fish_room(redis,roomInfo)
        log_debug('[try do_modifyFishRoom] room_id[%s] roomInfo[%s] modify success.'%(room_id,roomInfo))
    except Exception,e:
        return {'code':2,'msg':'reason[%s]'%(e)}

    #记录操作日志
    logInfo = {'datetime':curTime.strftime('%Y-%m-%d %H:%M:%S'),\
                    'ip':request.remote_addr,'desc':lang.AGENT_OP_LOG_TYPE['modifyFishRoom']%(room_name)}
    #记录日志
    writeAgentOpLog(redis,session['id'],logInfo)
    return {'code':0,'msg':'房间[%s]修改成功.'%(room_name),'jumpUrl':BACK_PRE+'/fish/room/list'}

@admin_app.get('/fish/bet/list')
@checkAccess
def get_betlist(redis,session):
    """
    获取投注明细列表
    """
    lang = getLang()
    isList = request.GET.get('list','').strip()
    start_date = request.GET.get('startDate','').strip()
    end_date   = request.GET.get('endDate','').strip()
    user_id    = request.GET.get('memberId','').strip()
    group_id   = request.GET.get('groupId','').strip()
    room_id = request.GET.get('room_id','').strip()
    page_size = request.GET.get('pageSize','').strip()
    page_number = request.GET.get('pageNumber','').strip()
    sort_name   = request.GET.get('sort_name','').strip()
    sort_method = request.GET.get('sort_method','').strip()

    page_info = {   #分页数据
            'page_size'     :       page_size,
            'page_number'   :       page_number
    }

    sort_info = {   #排序数据
            'sort_name'     :       sort_name,
            'sort_method'   :       sort_method
    }

    if isList:
        bet_records = get_bet_list(redis,start_date,end_date,room_id,page_info,sort_info)
        return json.dumps(bet_records)
    else:
        info = {
                    'title'                  :       '胜负统计',
                    'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
                    'back_pre'               :       BACK_PRE,
                    'room_search'            :       True,#房间搜索
                    'rooms'                  :       get_room_list(redis),
                    'tableUrl'               :       BACK_PRE+'/fish/bet/list?list=1'
        }

        return template('admin_fish_room_bet',PAGE_LIST=PAGE_LIST,info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/fish/bet/report')
def get_betReport(redis,session):
    """
    捕鱼投注输赢报表
    """
    lang = getLang()
    isList = request.GET.get('list','').strip()
    start_date = request.GET.get('startDate','').strip()
    end_date   = request.GET.get('endDate','').strip()
    user_id    = request.GET.get('memberId','').strip()
    group_id   = request.GET.get('group_id','').strip()

    log_debug('[try get_betReport] user_id[%s] group_id[%s] startDate[%s] endDate[%s]'\
                    %(user_id,group_id,start_date,end_date))
    if isList:
        bet_records = get_bet_reports(redis,start_date,end_date,group_id)
        return json.dumps(bet_records)
    else:
        info = {
                    'title'                  :       lang.MENU_FISH_AGENT_REPORT_TXT,
                    'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
                    'back_pre'               :       BACK_PRE,
                    'group_search'           :       True,#开启代理ID查询
                    'tableUrl'               :       BACK_PRE+'/fish/bet/report?list=1'
        }

        return template('admin_fish_room_report',PAGE_LIST=PAGE_LIST,info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/fish/recharge/list')
def get_rechargeList(redis,session):
    """
    获取金币充值列表
    """
    lang = getLang()
    isList = request.GET.get('list','').strip()
    start_date = request.GET.get('startDate','').strip()
    end_date   = request.GET.get('endDate','').strip()
    recharge_source     = request.GET.get('recharge_source','').strip()
    group_id   = request.GET.get('groupId','').strip()

    if isList:
        pass
    else:
        info = {
                    'title'                  :       '金币充值记录',
                    'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
                    'back_pre'               :       BACK_PRE,
                    'tableUrl'               :       BACK_PRE+'/fish/recharge/list?list=1'
        }

        return template('admin_fish_coin_charge',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/fish/bet/replay')
def get_fish_replay(redis,session):
    """
    打开捕鱼回放数据
    """
    lang = getLang()
    replay_id = request.GET.get('replay_id','').strip()
    if not replay_id:
        return {'code':0,'msg':'回放参数错误.'}

    log_debug('[try get_fish_replay] replay_id[%s]'%(replay_id))
    info = {
            'title'                  :       '投注ID[%s]游戏记录'%(replay_id),
            'STATIC_LAYUI_PATH'      :       STATIC_LAYUI_PATH,
            'STATIC_ADMIN_PATH'      :       STATIC_ADMIN_PATH,
            'dataUrl'                :       BACK_PRE+'/fish/bet/replayData?replay_id=%s'%(replay_id)
    }

    return template('admin_fish_replay',info=info,lang=lang,RES_VERSION=RES_VERSION)

@admin_app.get('/fish/bet/replayData')
def get_replay_data(redis,session):
    """
    return data
    """
    replay_id = request.GET.get('replay_id','').strip()

    replay_info = get_replay_info(redis,replay_id)
    log_debug('[try get_replay_data] replayId[%s] replay_info[%s]'%(replay_id,replay_info))

    return json.dumps(replay_info)

@admin_app.get('/fish/online/list')
def get_fish_online_page(redis,session):
    """
    获取捕鱼在线
    """
    curTime =  datetime.now()
    isList  =  request.GET.get('list','').strip()
    lang = getLang()
    if isList:
        fish_online_datas = get_fish_online(redis,lang)
        return json.dumps(fish_online_datas)
    else:
        info = {
                'title'                  :           lang.MENU_FISH_ONLINE_REAL_TXT,
                'listUrl'                :           BACK_PRE+'/fish/online/list?list=1',
                'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }

        return template('admin_fish_online',info=info,lang=lang,RES_VERSION=RES_VERSION)


@admin_app.get('/fish/data/query')
@checkAccess
def get_fish_data_query(redis,session):
    """
    后台捕鱼数据查询接口
    """
    lang = getLang()
    fields = ('isList','start_date','end_date')
    for field in fields:
        exec('%s=request.forms.get("%s","").strip()'%(field,field))

    if isList:
        fish_system_datas = get_fish_sys_datas(redis,start_date,end_date)
        return json.dumps(fish_system_datas)
    else:
        info = {
                    'title'                  :           lang.MENU_FISH_DATA_REAL_TXT,
                    'listUrl'                :           BACK_PRE+'/fish/data/query?isList=1',
                    'STATIC_LAYUI_PATH'      :           STATIC_LAYUI_PATH,
                    'STATIC_ADMIN_PATH'      :           STATIC_ADMIN_PATH
        }
        return template('admin_fish_sys_data',info=info,lang=lang,RES_VERSION=RES_VERSION)
