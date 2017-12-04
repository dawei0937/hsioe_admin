<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/refreshDateInit.js"></script>
<div class="cl-mcont">
  <div class="block">
            <div class="header">              
              <h3>
                %if info.get('title',None):
                  {{info['title']}}
                %end
              </h3>
            </div>
            <div class="content">
               %include original_search_bar
               <table id="dataTable" class="table table-bordered table-hover"></table>
            </div>
  </div>
</div>
<script type="text/javascript">
  var firstDate=new Date();
  firstDate.setDate(firstDate.getDate()-6);
  $('#pick-date-start').val(firstDate.Format("yyyy-MM-dd"));
  $('#pick-date-end').val(new Date().Format("yyyy-MM-dd"));
  
  /**------------------------------------------------
    *  代理操作日志
    *
    -------------------------------------------------
  */
  function initTable() {
    startDate = $("#pick-date-start").val();
    endDate   = $("#pick-date-end").val();
    $('#dataTable').bootstrapTable({
          method: 'get',
          url: '{{info["listUrl"]}}',
          contentType: "application/json",
          datatype: "json",
          cache: false,
          checkboxHeader: true,
          striped: true,
          pagination: true,
          pageSize: 24,
          pageList: [24, 48, 100, 'All'],
          search: true,
          clickToSelect: true,
          //sidePagination : "server",
          sortOrder: 'desc',
          sortName: 'datetime',
          queryParams:getSearchP,
          responseHandler:responseFun,
          //onLoadError:responseError,
          showExport:true,
          exportTypes:['excel', 'csv', 'pdf', 'json'],
          // exportOptions:{fileName: "{{info['title']}}"+"_"+ new Date().Format("yyyy-MM-dd")},
          columns: [
            {
              field: 'account',
              title: '登录账号',
              align: 'center',
              valign: 'middle'
          },{
              field: 'type',
              title: '登录状态',
              align: 'center',
              valign: 'middle',
              formatter:status,
          },{
              field: 'datetime',
              title: '登录时间',
              align: 'center',
              valign: 'middle'
          },{
              field: 'ip',
              title: '登录IP',
              align: 'center',
              valign: 'middle',
          }]
      });
        function status(value,row,index){
           if( parseInt(value) == 1)
               infoStr = String.format("<span class=\"label label-success\">{0}</span>", '成功');
           else if (parseInt(value) == 2)
               infoStr = String.format("<span class=\"label label-danger\">{0}</span>", '密码错误');
           else 
               infoStr = String.format("<span class=\"label label-danger\">{0}</span>", '未知错误');
           return [
                infoStr
            ].join('');
          }
        //定义列操作
        function getSearchP(p){
          startDate = $("#pick-date-start").val();
          endDate   = $("#pick-date-end").val();

          sendParameter = p;

          sendParameter['startDate'] = startDate;
          sendParameter['endDate']  = endDate;

          return sendParameter;
        }

        //获得返回的json 数据
        function responseFun(res){
            return res;
        }
}
</script>
%rebase admin_frame_base
