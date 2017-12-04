<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/common.js"></script>
<div class='block'>
     %include admin_frame_header
     <div class='content'>
      %include search
      <table id='loadDataTable' class="table table-bordered table-hover table-striped" ></table>
     </div>
</div>
<script type="text/javascript">
/**
  *表格数据
*/
var editId;        //定义全局操作数据变量
var isEdit;
var startDate;
var endDate;
$('#loadDataTable').bootstrapTable({
      method: 'get',
      url: "{{info['tableUrl']}}",
      contentType: "application/json",
      datatype: "json",
      cache: false,
      checkboxHeader: true,
      striped: true,
      pagination: true,
      pageSize: 15,
      pageList: [15, 50, 100,'All'],
      search: true,
      showRefresh: true,
      minimumCountColumns: 2,
      clickToSelect: true,
      smartDisplay: true,
      //sidePagination : "server",
      sortOrder: 'desc',
      sortName: 'datetime',
      responseHandler:responseFunc,
      //onLoadError:responseError,
      showExport:true,
      exportTypes:['excel', 'csv', 'pdf', 'json'],
      //exportOptions:{fileName: "{{info['title']}}"+"_"+ new Date().Format("yyyy-MM-dd")},
      columns: [
      {
          field: 'exchange_reward_id',
          title: '奖品ID',
          align: 'center',
          valign: 'middle'
      },{

          field: 'exchange_reward_name',
          title: '奖品名称',
          align: 'center',
          valign: 'middle'
      },{

          field: 'exchange_reward_img_path',
          title: '奖品图片',
          align: 'center',
          valign: 'middle',
          formatter:getReardImages
      },{

          field: 'exchange_need_ticket',
          title: '奖品单价(/券)',
          align: 'center',
          valign: 'middle'
      },{

          field: 'exchange_use_ticket',
          title: '兑换使用券',
          align: 'center',
          valign: 'middle'
      },{

          field: 'exchange_user_phone',
          title: '联系人',
          align: 'center',
          valign: 'middle'
      },{

          field: 'exchange_user_addr',
          title: '收获地址',
          align: 'center',
          valign: 'middle'
      },{

          field: 'exchange_user_name',
          title: '姓名',
          align: 'center',
          valign: 'middle'
      },{

          field: 'exchange_date',
          title: '兑换时间',
          align: 'center',
          valign: 'middle'
      },{

          field: 'user_id',
          title: '玩家ID',
          align: 'center',
          valign: 'middle',
      },{

          field: 'exchange_reward_status',
          title: '发货状态',
          align: 'center',
          valign: 'middle',
      },{

          field: 'exchange_card_info',
          title: '卡密',
          align: 'center',
          valign: 'middle',
      },{
          field: 'op',
          title: '操作',
          align: 'center',
          valign: 'middle',
          formatter:getOp
      }]
  });


    function getOp(value,row,index){
        eval('rowobj='+JSON.stringify(row))
        comfirmUrls = [
                '/admin/goods/reward/auto_charge',
                '/admin/goods/reward/status',
                '/admin/goods/reward/del'
        ]
        var opList = []
        for (var i = 0; i < rowobj['op'].length; ++i) {
            var op = rowobj['op'][i];
            var str = JSON.stringify({reward_id : rowobj['reward_id']});
            var cStr = str.replace(/\"/g, "@");
            if(comfirmUrls.indexOf(op['url']) !=-1){
                opList.push(String.format("<a href=\"#\" class=\"btn btn-primary\" onclick=\"comfirmDialog(\'{0}\', \'{1}\', \'{2}\')\"> {3}</a> ", op['url'], op['method'], cStr, op['txt']));
            }else{
                opList.push(String.format("<a href=\"{0}?reward_id="+rowobj['reward_id']+"\" class=\"btn btn-primary\" >{1}</a> ", op['url'],op['txt']));
            }
        }
        return opList.join('');
    }

    function getReardImages(value,row,index){
          eval('var rowobj='+JSON.stringify(row))
          statusstr = '<img src="'+row['exchange_reward_img_path']+'" width="50" height="50" />';

          return [statusstr].join('');
    }


    function responseFunc(res){

        return res.data;
    }

    function responseError(status) {
        location.reload();
    }
</script>
%rebase admin_frame_base
