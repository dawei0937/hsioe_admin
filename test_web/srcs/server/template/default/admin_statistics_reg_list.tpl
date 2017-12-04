<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/common.js"></script>
<div class="block">
          %include admin_frame_header
          <div class="content">
              <table id="dataTable" class="table table-bordered table-hover"></table>
          </div>
</div>
<script type="text/javascript">

    startDate = $("#pick-date-start").val();
    endDate   = $("#pick-date-end").val();
    $('#dataTable').bootstrapTable({
          method: 'get',
          url: '{{info["listUrl"]}}',
          contentType: "application/json",
          datatype: "json",
          cache: true,
          checkboxHeader: true,
          striped: true,
          pagination: true,
          pageSize: 15,
          pageList: [15, 50, 100,'All'],
          // queryParamsType:'',
          // sidePagination:"server",
          search: true,
          showColumns: true,
          minimumCountColumns: 2,
          clickToSelect: true,
          //smartDisplay: true,
          responseHandler:responseFun,
          //onLoadError:responseError,
          queryParams:getSearchP,
          //sortOrder: 'asc',
          //sortable: true,                     //是否启用排序
          showExport:true,
          exportTypes:['excel', 'csv', 'pdf', 'json'],
          // exportOptions:{fileName: "{{info['title']}}"+"_"+ new Date().Format("yyyy-MM-dd")},
          columns: [
          {
              field: 'account',
              title: '注册账号',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'nickname',
              title: '微信名称',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'headImgUrl',
              title: '微信头像',
              align: 'center',
              valign: 'middle',
              sortable: true,
              formatter:getAvatorImg,
          },{
              field: 'parentAg',
              title: '所属公会',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'last_login_date',
              title: '上次登录时间',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'login_out_date',
              title: '上次登出时间',
              align: 'center',
              valign: 'middle',
              sortable: true,
          }]
    });



      //前台查询参数
      function getSearchP(p){
          // account = $("#account").val();
          // member_level = $('#member_level').val();
          // member_status = $("#member_status").val();
          // userId = $("#userId").val();
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

      function responseError(status) {
          location.reload();
      }
</script>
%rebase admin_frame_base

