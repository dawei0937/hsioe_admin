  <div class="block">
            %include admin_frame_header
            <div class="content">
                %include search
                <table id="dataTable" class="table table-bordered table-hover"></table>
            </div>
  </div>
<script type="text/javascript">
    $('#btn_search').click(function(){
          
          $('#dataTable').bootstrapTable('refresh',{"url":'{{info["listUrl"]}}'});
    });

    var firstDate=new Date();
    firstDate.setDate(firstDate.getDate()-6);
    $('#pick-date-start').val(firstDate.Format("yyyy-MM-dd"));
    $('#pick-date-end').val(new Date().Format("yyyy-MM-dd"));

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
          pageList: '{{PAGE_LIST}}',
          responseHandler:responseFun,
          queryParams:getSearchP,

          columns:[
          [
                {
                           halign:"center",
                           align:"left",
                           size:'50',
                           class:'info',
                           colspan: 9
                }
          ],[{
              field: 'date',
              title: '日期',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'parentAg',
              title: '公会号',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'roomId',
              title: '房间号',
              align: 'center',
              valign: 'middle',
              sortable: true,
          },{
              field: 'totalCards',
              title: '总钻石数',
              align: 'center',
              valign: 'middle',
              sortable: true
          },{
              field: 'useCards',
              title: '钻石变更',
              align: 'center',
              valign: 'middle',
              sortable: true,
              formatter:getColorCredit
          },{
              field: 'useType',
              title: '钻石变更说明',
              align: 'center',
              valign: 'middle',
              sortable: true
          }]]
    });


        function getColorCredit(value,row,index) {
            if( parseInt(value) > 0)
                infoStr = String.format("<span style=\"color:red;\">+{0}</span>", value);
            else
                infoStr = String.format("<span style=\"color:green;\">{0}</span>", value);
            return [
                infoStr
            ].join('');
        }

        function getOp(value,row,index){
            var comfirmUrls = [
                '/admin/member/kick',
                '/admin/member/freeze'
            ];
            eval('rowobj='+JSON.stringify(row))
            var opList = []
            for (var i = 0; i < rowobj['op'].length; ++i) {
                var op = rowobj['op'][i];
                var str = JSON.stringify({id : rowobj['id']});
                var cStr = str.replace(/\"/g, "@");
                if(comfirmUrls.indexOf(op['url'])>=0)
                    opList.push(String.format("<a href=\"#\" class=\"btn btn-primary btn-xs\" onclick=\"comfirmDialog(\'{0}\', \'{1}\', \'{2}\')\"><i class=\"fa fa-edit\"> {3} </i></a> ", op['url'], op['method'], cStr, op['txt']));
                else
                    opList.push(String.format("<a href=\"{0}?id="+rowobj['id']+"\" class=\"btn btn-primary btn-xs\" ><i class=\"fa fa-edit\"> {1} </i></a> ", op['url'],op['txt']));
            }
            return opList.join('');
        }


        function getColor(value,row,index){
            eval('var rowobj='+JSON.stringify(row))
            statusstr = '<span style="color:#6600FF">'+value+'</span>';

            return [statusstr].join('');
        }
        
        //定义列操作
        function getSearchP(p){
          searchId = $("#searchId").val();
          startDate = $("#pick-date-start").val();
          endDate   = $("#pick-date-end").val();

          sendParameter = p;

          sendParameter['searchId'] = searchId;
          sendParameter['startDate'] = startDate;
          sendParameter['endDate'] = endDate;

          return sendParameter;
        }

        //获得返回的json 数据 
        function responseFun(res){
            startDate = $('#pick-date-start').val();
            endDate = $('#pick-date-end').val();
            count= res.count;
            img = res.headImgUrl;
            name = res.name || '<font color="red">请输入要查询的玩家ID</font>';
            $('.info').html("玩家名称: "+name+"&nbsp;  玩家头像:<img src='"+img+"' width='30' height='30' />");
            return res.data
        }
</script>
%rebase admin_frame_base

