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
          pageList: '{{PAGE_LIST}}',
          // queryParamsType:'',
          // sidePagination:"server",
          minimumCountColumns: 2,
          //smartDisplay: true,
          responseHandler:responseFun,
          //onLoadError:responseError,
          queryParams:getSearchP,
          //sortOrder: 'asc',
          //sortable: true,                     //是否启用排序
          showExport:true,
          showFooter:true,
          exportTypes:['excel', 'csv', 'pdf', 'json'],
          // exportOptions:{fileName: "{{info['title']}}"+"_"+ new Date().Format("yyyy-MM-dd")},
          columns: [
          [{
                    "title": "日期:"+"{{date}}" + "详情列表",
                    "halign":"center",
                    "align":"center",
                    "colspan": 9
          }],
          [{
              field: 'id',
              title: '会员账号',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'name',
              title: '会员名称',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'parentAg',
              title: '公会ID',
              align: 'center',
              valign: 'middle',
              sortable: true,
              footerFormatter:function(values){
                  return '总计:'
              }
          },{
              field: 'use_count',
              title: '钻石消耗',
              align: 'center',
              valign: 'middle',
              sortable: true,
              footerFormatter:function(values){
                  var count = 0 ;
                  for (var val in values)
                      count+=parseInt(values[val].use_count)

                  return colorFormat(count)
              }

          }]]
    });

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
            console.log('----------------------data:'+res);
            return res;
        }

        function responseError(status) {
            location.reload();
        }
</script>
%rebase admin_frame_base
