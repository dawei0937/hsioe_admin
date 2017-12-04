<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/refreshDateInit.js"></script>
<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/common.js"></script>
<div class="block">
        %include admin_frame_header
        <div class="content">
           %include original_search_bar
           <table id="dataTable" class="table table-bordered table-hover"></table>
        </div>
</div>
<script type="text/javascript">

  function initTable() {
    $('#dataTable').bootstrapTable({
          method: 'get',
          url: '{{info["listUrl"]}}',
          contentType: "application/json",
          datatype: "json",
          cache: false,
          detailView: true,
          checkboxHeader: true,
          striped: true,
          pagination: true,
          pageSize: 15,
          showExport: true,
          exportTypes:['excel', 'csv', 'pdf', 'json'],
          pageList: [15,50,100, 'All'],
          search: true,
          clickToSelect: true,
          //sidePagination : "server",
          sortOrder: 'desc',
          sortName: 'date',
          queryParams:getSearchP,
          responseHandler:responseFun,
          //onLoadError:responseError,
          showExport:true,
          showFooter:true,
          exportTypes:['excel', 'csv', 'pdf', 'json'],
          // exportOptions:{fileName: "{{info['title']}}"+"_"+ new Date().Format("yyyy-MM-dd")},
          columns: [
            {
              field: 'date',
              title: '日期',
              align: 'center',
              valign: 'middle'
          },{
              field: 'id',
              title: 'ID',
              align: 'center',
              valign: 'middle',
              footerFormatter:function(values){
                  return '销售总计'
              }
          },{
              field: 'number',
              title: '销售个数',
              align: 'center',
              valign: 'middle',
              footerFormatter:function(values){
                  var count = 0;
                  for (var val in values)
                      count+=parseInt(values[val].number)

                  return colorFormat(count);
              }
          },
          %if info['aType'] != '0':
                    {
                        field: 'unitPrice',
                        title: '销售单价(元)',
                        align: 'center',
                        valign: 'middle',
                        formatter:getColor,
                    },{
                        field: 'rate',
                        title: '占额/个(元)',
                        align: 'center',
                        valign: 'middle',
                        formatter:getColor,
                    },
          %end

          {
              field: 'rateTotal',
              title: '我的总占额(元)',
              align: 'center',
              valign: 'middle',
              formatter:getColor,
              footerFormatter:function(values){
                  var count = 0;
                  for (var val in values)
                      count+=parseInt(values[val].rateTotal);

                  return colorFormat(count);
              }
          }

           %if info['aType'] != '0':
              ,{
                  field: 'superRateTotal',
                  title: '上线总占额(元)',
                  align: 'center',
                  valign: 'middle',
                  formatter:getColor,
                  footerFormatter:function(values){
                      var count = 0;
                      for (var val in values)
                          count+=parseInt(values[val].superRateTotal);

                      return colorFormat(count);
                  }
              }
            %end
           ],
          onExpandRow: function (index, row, $detail) {
              console.log(index,row,$detail);
              InitSubTable(index, row, $detail);
          }
      });

//初始化子表格(无线循环)
function InitSubTable(index, row, $detail) {
        var parentDate = row.date;
        var parentId = row.id;
        var unitPrice = row.unitPrice;
        var cur_table = $detail.html('<table table-bordered table-hover definewidth></table>').find('table');
        $(cur_table).bootstrapTable({
                url: '{{info["listUrl"]}}',
                method: 'get',
                detailView: false,
                contentType: "application/json",
                datatype: "json",
                cache: false,
                queryParams:getSearchP,
                sortOrder: 'desc',
                sortName: 'regDate',
                pageSize: 15,
                pageList: [15, 25],
                columns: [{
              field: 'id',
              title: 'ID',
              align: 'center',
              valign: 'middle'
          },{
              field: 'number',
              title: '销售个数',
              align: 'center',
              valign: 'middle'
          },{
              field: 'unitPrice',
              title: '销售单价(元)',
              align: 'center',
              valign: 'middle',
              formatter:getColor
          },{
              field: 'rate',
              title: '占额/个(元)',
              align: 'center',
              valign: 'middle'
          },{
              field: 'meAndNextTotal',
              title: '给该代理的总占额(元)',
              align: 'center',
              valign: 'middle'
          },{
              field: 'superRateTotal',
              title: '上线总占额(元)',
              align: 'center',
              valign: 'middle',
              formatter:getColor
          }],
                //注册加载子表的事件。注意下这里的三个参数！
        });

        //定义列操作
        function getSearchP(p){
              sendParameter = p;
              sendParameter['id'] = parentId;
              sendParameter['date'] = parentDate;
              sendParameter['unitPrice'] = unitPrice;
              return sendParameter;
        }
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
            data = res.date
            return data;
        }

}
</script>
%rebase admin_frame_base
