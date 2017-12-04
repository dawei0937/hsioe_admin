<div class="block">
         %include admin_frame_header
          <div class="content">
              %include search
              <div id="toolbar" class="btn-group">
                  %if info['atype'] == '0':
                   <button id="btn_add" type="button" class="btn btn-sm btn-primary">
                      <span class="glyphicon glyphicon-plus">
                          <a href="{{info['createUrl']}}" style='color:#FFF;text-decoration:none;'>添加省级代理</a>
                      </span>
                  </button>
                  %elif info['atype'] in ['1']:
                   <button id="btn_add" type="button" class="btn btn-sm btn-primary">
                      <span class="glyphicon glyphicon-plus">
                           <a href="{{info['createUrl']}}" style='color:#FFF;text-decoration:none;'>添加直属代理</a>
                      </span>
                  </button>
                  %elif info['atype'] in ['2'] and info['create_auth'] == 1:
                   <button id="btn_add" type="button" class="btn btn-sm btn-primary">
                      <span class="glyphicon glyphicon-plus">
                           <a href="{{info['createUrl']}}" style='color:#FFF;text-decoration:none;'>添加市级代理(2)</a>
                      </span>
                  </button>
                  %end
                  <!-- 解 绑 规 则 -->
                  <button id="btn_refresh" type="button" class="btn btn-sm btn-primary">
                     <span class="glyphicon glyphicon-refresh">
                         <a href="javascript:;" style='color:#FFF;text-decoration:none;'>显示全部代理</a>
                     </span>
                 </button>
              </div>
              <table id="agentTable" class="table table-bordered table-hover"></table>
          </div>
</div>
<script type="text/javascript">
  $('#btn_search').click(function(){ //刷新代理
        start_date = $('#pick-date-start').val();
        end_date   = $('#pick-date-end').val();
        searchId   = $('#searchId').val();
        $('#agentTable').bootstrapTable('refresh',{'url':'{{info["listUrl"]}}'+"&searchId="+searchId+"&start_date="+start_date+"&end_date="+end_date});
  });

  $('#btn_refresh').click(function(){ //刷新代理
        $('#agentTable').bootstrapTable('refresh',{'url':'{{info["listUrl"]}}'});
  });

  $("#agentTable").bootstrapTable({
            url: '{{info["listUrl"]}}',
            method: 'get',
            detailView: {{info['showPlus']}},//父子表
            //sidePagination: "server",
            pagination: true,
            pageSize: 15,
            toolbar:'#toolbar',
            sortOrder: 'desc',
            sortName: 'regDate',
            sorttable:true,
            responseHandler:responseFunc,
            queryParams:getSearchP,
            pageList: '{{PAGE_LIST}}',
            columns:[
            [{
                    halign    : "center",
                    font      :  15,
                    align     :  "left",
                    class     :  "totalTitle",
                    colspan   :  13
            }],
            [
            {
                field: 'parentAg',
                title: '代理账号',
                align: 'center',
                valign: 'middle',
                sortable: true,
            },{
                field: 'regDate',
                sortable: true,
                title: '创建时间',
                align: 'center',
                valign: 'middle',
            },{
                field: 'parentId',
                title: '公会ID',
                align: 'center',
                valign: 'middle',
                sortable: true,
            },{
                field: 'allMembers',
                title: '会员总数',
                align: 'center',
                valign: 'middle',
                sortable: true,
            },{
                field: 'members',
                sortable: true,
                title: '会员活跃数',
                align: 'center',
                valign: 'middle',
            },{
                field: 'roomCard',
                sortable: true,
                title: '当日耗钻数',
                align: 'center',
                valign: 'middle',
            },{
                field: 'isTrail',
                title: '是否试玩',
                valign: 'middle',
                align: 'center',
                formatter:statusTrail,
            },{
                field: 'valid',
                title: '状态',
                align: 'center',
                valign: 'middle',
                sortable: true,
                formatter:status
            },{
                field: 'recharge',
                title: '商城充钻',
                valign: 'middle',
                align: 'center',
                formatter:statusRecharge,
            },{
                field: 'auto_check',
                title: '是否自动审核',
                valign: 'middle',
                align: 'center',
                formatter:statusCheck,
            },
            %if info['atype'] in ['0']:
                    {
                        field: 'create_auth',
                        title: '市级公会(2)',
                        valign: 'middle',
                        align: 'center',
                        formatter:statusCheck,
                    },
            %end
            %if info['atype'] in ['0','1','2']:
                  {
                        field: 'open_auth',
                        title: '仅权限者代开房',
                        valign: 'middle',
                        align: 'center',
                        formatter:statusCheck,
                    },
            %end
            {
                field: 'op',
                title: '操作',
                valign: 'middle',
                formatter:getOp
            }]],
            //注册加载子表的事件。注意下这里的三个参数！
            onExpandRow: function (index, row, $detail) {
                console.log(index,row,$detail);
                InitSubTable(index, row, $detail);
            }
  });


//初始化子表格(无线循环)
function InitSubTable(index, row, $detail) {
        var parentAg = row.parentId;
        var cur_table = $detail.html('<table table-bordered table-hover definewidth style="margin-left:55px;background:#EEEEE0"></table>').find('table');
        $(cur_table).bootstrapTable({
                url: '{{info["listUrl"]}}',
                method: 'get',
                detailView: {{info['showPlus']}},//父子表
                contentType: "application/json",
                datatype: "json",
                cache: false,
                search: true,
                sorttable:true,
                queryParams:getSearchP,
                sortOrder: 'desc',
                sortName: 'regDate',
                pageSize: 15,
                pageList: [15, 25],
                columns: [{
                    field: 'parentAg',
                    title: '代理名称',
                    align: 'center',
                    valign: 'middle'
                },{
                    field: 'agentType',
                    title: '代理类型',
                    align: 'center',
                    valign: 'middle',
                    sortable: true,
                },{
                    field: 'parentId',
                    title: '公会ID',
                    valign: 'middle',
                    align: 'center',
                    sortable: true
                },{
                    field: 'allMembers',
                    title: '会员总数',
                    align: 'center',
                    valign: 'middle',
                    sortable: true
                },{
                    field: 'members',
                    title: '活跃会员数',
                    align: 'center',
                    valign: 'middle',
                    sortable: true
                },{
                    field: 'roomCard',
                    title: '当日耗钻数',
                    align: 'center',
                    valign: 'middle',
                    sortable: true
                },{
                    field: 'regDate',
                    title: '创建时间'
                },{
                    field: 'valid',
                    title: '状态',
                    align: 'center',
                    valign: 'middle',
                    formatter:status
                },{
                    field: 'isTrail',
                    title: '是否试玩',
                    valign: 'middle',
                    align: 'center',
                    formatter:statusTrail,
                },{
                    field: 'auto_check',
                    title: '是否自动审核',
                    valign: 'middle',
                    align: 'center',
                    formatter:statusCheck,
                },{
                    field: 'recharge',
                    title: '商城充钻',
                    valign: 'middle',
                    align: 'center',
                    formatter:statusRecharge,
                },
                %if info['atype'] in ['0','1','2']:
                      {
                            field: 'open_auth',
                            title: '仅权限者代开房',
                            valign: 'middle',
                            align: 'center',
                            formatter:statusCheck,
                        },
                %end
                {
                    field: 'op',
                    title: '操作',
                    align: 'center',
                    valign: 'middle',
                    formatter:getOp
                }],
                //注册加载子表的事件。注意下这里的三个参数！
                onExpandRow: function (index, row, $detail) {
                    console.log(index,row,$detail);
                    InitSubTable(index, row, $detail);
                }
        });

        //定义列操作
        function getSearchP(p){
              sendParameter = p;
              sendParameter['id'] = parentAg;
              return sendParameter;
        }

        function responseFunc(res){
            data = res.data;
            count= res.count;
            //实时刷

            return data;
        }

}

function getOp(value,row,index){
      var comfirmList = [       //需要dialog确认打开的url
        '/admin/agent/freeze',
        '/admin/agent/trail',
        '/admin/agent/del',
        '/admin/agent/recharge',
        '/admin/agent/auto_check',
        '/admin/agent/create_auth',
        '/admin/agent/open_auth',
      ];
      eval('rowobj='+JSON.stringify(row))
      var opList = []
      for (var i = 0; i < rowobj['op'].length; ++i) {
          var op = rowobj['op'][i];
          var str = JSON.stringify({id : rowobj['parentId']});
          var cStr = str.replace(/\"/g, "@");
          var param = rowobj['parentId'] ;
          if(comfirmList.indexOf(op['url'])>=0){
              btn_type = 'primary'
              if (op['url'].substring(op['url'].length-3) == 'del')
                      btn_type = 'danger'
              opList.push(String.format("<a href=\"#\" class=\"btn btn-{4} btn-sm btn-xs\" onclick=\"comfirmDialog(\'{0}\', \'{1}\', \'{2}\')\"><i class=\"glyphicon glyphicon-edit\"> {3} </i></a> ", op['url'], op['method'], cStr, op['txt'],btn_type));
          }else{
              opList.push(String.format("<a href=\"{0}?id={1}\" class=\"btn btn-primary btn-sm btn-xs\"><i class=\"glyphicon glyphicon-edit\"> {2}</i></a> ", op['url'], param, op['txt']));
          }
      }
      return opList.join('');
}


function responseFunc(res){
    data = res.data;
    count= res.count;
    //实时刷

    $('.totalTitle').html("下线代理总数: "+count)

    return data;
}

//定义列操作
function getSearchP(p){
  sendParameter = p;

  return sendParameter;
}

function status(value,row,index){
    eval('var rowobj='+JSON.stringify(row))
    var statusstr = '';
    if(rowobj['valid'] == '0'){
        statusstr = '<span class="label label-danger">冻结</span>';
    }else if(rowobj['valid'] == '1'){
        statusstr = '<span class="label label-success">有效</span>';
    }

    return [
        statusstr
    ].join('');
}

function statusTrail(value,row,index){
    eval('var rowobj='+JSON.stringify(row))
    var statusstr = '';
    if(rowobj['isTrail'] == '0'){
        statusstr = '<span class="label label-success">正式公会</span>';
    }else if(rowobj['isTrail'] == '1'){
        statusstr = '<span class="label label-warning">试玩公会</span>';
    }

    return [
        statusstr
    ].join('');
}

function statusRecharge(value,row,index){
    eval('var rowobj='+JSON.stringify(row))
    var statusstr = '';
    if(rowobj['recharge'] == '1'){
        statusstr = '<span class="label label-success">开放</span>';
    }else if(rowobj['recharge'] == '0'){
        statusstr = '<span class="label label-warning">未开放</span>';
    }

    return [
        statusstr
    ].join('');
}

function statusCheck(value,row,index){
    eval('var rowobj='+JSON.stringify(row))
    var statusstr = '';
    if(value == '1'){
        statusstr = '<span class="label label-success">是</span>';
    }else if(value == '0'){
        statusstr = '<span class="label label-warning">否</span>';
    }

    return [
        statusstr
    ].join('');
}

function statusOpen(value,row,index){
    eval('var rowobj='+JSON.stringify(row))
    var statusstr = '';
    if(value == '0'){
        statusstr = '<span class="label label-success">是</span>';
    }else if(value == '1'){
        statusstr = '<span class="label label-warning">否</span>';
    }

    return [
        statusstr
    ].join('');
}

String.format = function() {
    if( arguments.length == 0 ) {
    return null;
    }
    var str = arguments[0];
    for(var i=1;i<arguments.length;i++) {
    var re = new RegExp('\\{' + (i-1) + '\\}','gm');
    str = str.replace(re, arguments[i]);
    }
    return str;
}

</script>
%rebase admin_frame_base
