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
          responseHandler:responseFunc,
          //onLoadError:responseError,
          queryParams:getSearchP,
          //sortOrder: 'asc',
          //sortable: true,                     //是否启用排序
          showExport:true,
          exportTypes:['excel', 'csv', 'pdf', 'json'],
          // exportOptions:{fileName: "{{info['title']}}"+"_"+ new Date().Format("yyyy-MM-dd")},
          columns: [
          [
                {
                    "align":"center",
                    "hlign":"center",
                    "class":"total_room",
                    "colspan": 9
                }
          ],
          [{
              field: 'id',
              title: '房间ID',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'game_id',
              title: '游戏ID',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'game_name',
              title: '游戏名称',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'dealer',
              title: '房主',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'player_count',
              title: '玩家数',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'op',
              title: '操作',
              align: 'center',
              valign: 'middle',
              formatter:getOp
          }]]
    });

        function getOp(value,row,index){
            eval('rowobj='+JSON.stringify(row))
            var opList = []
            for (var i = 0; i < rowobj['op'].length; ++i) {
                var op = rowobj['op'][i];
                var str = JSON.stringify({id : rowobj['id']});
                var cStr = str.replace(/\"/g, "@");
                if(op['url'] == '/admin/agent/room/kick')
                    opList.push(String.format("<a href=\"#\" class=\"btn btn-primary btn-sm\" onclick=\"comfirmDialog(\'{0}\', \'{1}\', \'{2}\')\"> {3}</a> ", op['url'], op['method'], cStr, op['txt']));
                else
                    opList.push(String.format("<a href=\"{0}?id="+rowobj['id']+"\" class=\"btn btn-primary btn-sm\" >{1}</a> ", op['url'],op['txt']));
            }
            return opList.join('');
        }


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
        function responseFunc(res){
            data = res.data;
            count= res.count;
            //实时刷
            $('.total_room').html("当前房间总数:"+count);

            return data;
        }
        function responseError(status) {
            location.reload();
        }
</script>
%rebase admin_frame_base
