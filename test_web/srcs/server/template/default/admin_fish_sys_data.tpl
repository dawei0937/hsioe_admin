<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/common.js"></script>
<div class="block">
          %include admin_frame_header
          <div class="content">
              <!-- %include original_search_bar -->
              <table id="memberOLtable" class="table table-bordered table-hover"></table>
          </div>
</div>
<script type="text/javascript">
  /**
    * 服务端刷新表格
    --------------------------------------------
  */
  $(function () {
      $('#memberOLtable').bootstrapTable({
          method:'get',
          url   :'{{info["listUrl"]}}',
          smartDisplay: true,
          pagination: true,
          pageSize: 15,
          pageList: [15, 50, 100, 'All'],
          responseHandler:responseFunc,
          columns: [
                    [{
                        "halign":"center",
                        "align":"center",
                        "class": 'count',
                        "colspan": 11
                    }],
                    [{
                        field: 'id',
                        title: '当日注册',
                        align: 'center',
                        valign: 'middle',
                        sortable: true
                    },{
                        field: 'name',
                        title: '当日活跃',
                        align: 'center',
                        valign: 'middle',
                        sortable: true
                    },{
                        field: 'parentAg',
                        title: '日均活跃',
                        align: 'center',
                        valign: 'middle',
                        sortable: true
                    },{
                        field: 'clientKind',
                        title: '日均充值',
                        align: 'center',
                        valign: 'middle',
                        sortable: true
                    },{
                        field: 'coin',
                        title: '总共充值',
                        align: 'center',
                        valign: 'middle',
                        sortable: true,
                        formatter:getColor
                    }]]
      });

      function getOp(value,row,index){
          eval('rowobj='+JSON.stringify(row))
          var opList = []
          opList.push("<a href='javascript:;' onClick=\"comfirmDialog('/admin/member/kicks?account="+rowobj['account']+"&groupId="+rowobj['parentAg']+"','GET','{}')\" class=\"btn btn-sm btn-primary\" <i class=\"fa fa-edit\"> </i>踢出</a> ");
          return opList.join('');
      }


      function responseFunc(res){
          data = res.data;
          count= res.count;
          //实时刷
          $('.count').text(String.format("当前在线人数: {0}",count));

          return data;
      }
  });
</script>
<script type="text/javascript">
  /**
    * 捕鱼实时在线
    ---------------------------------------------
  */
  setInterval('refreshTable()',1000);
  var refreshTime = 15;
  $(".countTime").text(refreshTime);
  var timerTick;

  //实时在线刷新
  function refreshTable(){
      clearTimeout(timerTick);
      refreshTime -= 1;
      if(refreshTime == 0){
          $('#memberOLtable').bootstrapTable('refresh',{
                   url   : '{{info["listUrl"]}}',
                   query : {ajaxOptions:{async:true,timeout:3000}}}
          );
          refreshTime = 15;
      }else{
          $(".countTime").text(refreshTime);
          timerTick = setTimeout('refreshTable();', 1000);
      }
  }
</script>
%rebase admin_frame_base
