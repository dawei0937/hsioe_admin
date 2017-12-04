<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/common.js"></script>
      <div class="block">
                %include admin_frame_header
                <div class="content">
                    %include search
                    <table id="dataTable" class="table table-bordered table-hover"></table>
                </div>
</div>
<script type="text/javascript">
    $('#btn_search').click(function(){
          $('#dataTable').bootstrapTable('refresh');
    });

    $('#dataTable').bootstrapTable({
          method: 'get',
          url: '{{info["listUrl"]}}',
          contentType: "application/json",
          datatype: "json",
          cache: false,
          striped: true,
          toolbar:'#toolbar',
          pagination: true,
          pageSize: 15,
          pageList: [15, 50, 100],
          queryParamsType:'',
          sidePagination:"server",
          minimumCountColumns: 2,
          clickToSelect: true,
          //smartDisplay: true,
          responseHandler:responseFun,
          queryParams:getSearchP,
          onSort:getCellSortByClick,
          //sortOrder: 'asc',
          //sortable: true,                     //是否启用排序
          // exportOptions:{fileName: "{{info['title']}}"+"_"+ new Date().Format("yyyy-MM-dd")},
          columns: [
          [
                {
                    "halign":"center",
                    "align":"center",
                    "class":'count',
                    "colspan": 11
                }
          ],

          [{
              field: 'id',
              title: '用户ID',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'name',
              title: '用户名称',
              align: 'center',
              valign: 'middle'
          },{
              field: 'nickname',
              title: '微信名称',
              align: 'center',
              valign: 'middle'
          },{
              field: 'headImgUrl',
              title: '微信头像',
              align: 'center',
              valign: 'middle',
              formatter:getAvatorImg,
          },{
              field: 'parentAg',
              title: '公会号',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'roomcard',
              title: '钻石剩余数',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'last_login_date',
              title: '最近登录时间',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'last_logout_date',
              title: '最近登出时间',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'rechargeTotal',
              title: '充值总额(当前公会)',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'open_auth',
              title: '代开权限<br/>(仅权限代开模式生效)',
              align: 'center',
              valign: 'middle',
              sortable: true,
              formatter:status
          },{
              field: 'op',
              title: '操作',
              align: 'center',
              valign: 'middle',
              formatter:getOp
          }]]
    });

      function status(value,row,index){
          eval('var rowobj='+JSON.stringify(row))
          var statusstr = '';
          if(rowobj['open_auth'] == '1'){
              statusstr = '<span class="label label-success">是</span>';
          }else if(rowobj['open_auth'] == '0'){
              statusstr = '<span class="label label-danger">否</span>';
          }

          return [
              statusstr
          ].join('');
      }

      function getCellSortByClick(name,sort){ //用于服务端排序重写

          console.log(String.format('------getCellSortByClick name[{0}] sort[{1}]',name,sort));
          $('#dataTable').bootstrapTable('refresh',{'url':String.format('{0}&sort_name={1}&sort_method={2}','{{info["listUrl"]}}',name,sort)});
      }

      function getOp(value,row,index){
          var comfirmUrls = [
              '/admin/member/kick',
              '/admin/member/freeze',
              '/admin/member/open_auth'
          ];
          eval('rowobj='+JSON.stringify(row))
          var opList = []
          for (var i = 0; i < rowobj['op'].length; ++i) {
              var op = rowobj['op'][i];
              var str = JSON.stringify({id : rowobj['id']});
              var cStr = str.replace(/\"/g, "@");
              if(comfirmUrls.indexOf(op['url'])>=0)
                  opList.push(String.format("<a href=\"#\" class=\"btn btn-primary btn-sm\" onclick=\"comfirmDialog(\'{0}\', \'{1}\', \'{2}\')\">{3}</a> ", op['url'], op['method'], cStr, op['txt']));
              else
                  opList.push(String.format("<a href=\"{0}?id="+rowobj['id']+"\" class=\"btn btn-primary btn-sm\" > {1} </a> ", op['url'],op['txt']));
          }
          return opList.join('');
      }

      //定义列操作
      function getSearchP(p){
        var searchId = $("#searchId").val();

        sendParameter = p;
        sendParameter['searchId'] = searchId;

        return sendParameter;
      }

      function responseFun(res){
          count= res.total;
          //实时刷
          $('.count').text(String.format("会员总人数:{0}",count));

          return {"rows": res.result,
                  "total": res.total};
      }

      function responseError(status) {
          location.reload();
      }
</script>
%rebase admin_frame_base
