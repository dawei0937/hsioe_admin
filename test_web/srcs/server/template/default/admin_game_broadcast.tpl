<div class="block">
          %include admin_frame_header
          <div class="content">
             <form class='form-horizontal group-border-dashed' action="{{info['subUrl']}}" method='POST' id='broadcastForm' onSubmit='return false'>
             <input type='hidden' name='gameId' value="{{info['defaultGameId']}}" />
              <div class="form-group">
                <label class="col-sm-3 control-label">{{lang.INPUT_LABEL_BROADCAST_TYPE_TXT}}</label>
                <div class="col-sm-6">
                    %if info['agent_type'] in ['0']:
                          <input type="radio" checked='checked' name="broad_type" value='0' class="broad_type" />&nbsp;全服维护广播&nbsp;&nbsp;
                          <input type="radio" name="broad_type" value='1' class="broad_type" />&nbsp;全服循环广播&nbsp;&nbsp;
                    %elif info['agent_type'] in ['1']:
                          <input type="radio" checked='checked' name="broad_type" value='2' class="broad_type" />&nbsp;地区维护广播&nbsp;&nbsp;
                          <input type="radio" name="broad_type" value='3' class="broad_type" />&nbsp;地区循环广播&nbsp;&nbsp;
                    %end
                </div>
              </div>
              <div class="form-group">
                  <label class="col-sm-3 control-label">开始时间</label>
                  <div  class="input-group date timeStamp col-sm-1"  data-min-view="0" data-date-format="yyyy-mm-dd hh:ii">
                            <input class="form-control" style='width:140px;' id='pick-date-end' name="start_date" size="18" type="text" value="{{lang.INPUT_LABEL_END_DATE_TXT}}" readonly>
                            <span class="input-group-addon btn btn-primary pickdate-btn1"><span class="pickdate1 glyphicon pickdate-btn1 glyphicon-th"></span></span>
                  </div>
              </div>
              <div class="form-group endDateDiv" style='display:none;'>
                  <label class="col-sm-3 control-label">结束时间</label>
                  <div class="input-group date timeStamp col-sm-1" data-min-view="0" data-date-format="yyyy-mm-dd hh:ii">
                    <input class="form-control" size="18" type="text" style='width:140px;' id='pick-date-start' name="end_date" value="{{lang.INPUT_LABEL_START_DATE_TXT}}" readonly>
                    <span class="input-group-addon btn btn-primary pickdate-btn1"><span class="pickdate1 glyphicon pickdate-btn1 glyphicon-th"></span></span>
                  </div>
              </div>
              <div class="form-group">
                <label class="col-sm-3 control-label">{{lang.INPUT_LABEL_BROADCAST_CONTENT_TXT}}</label>
                <div class="col-sm-6">
                  <input style="width:100%;float:left;" class="form-control" type="text" name="content" id="content">
                  <label for='content' class='hitLabel'>*</label>
                </div>
              </div>

              <div class="form-group">
                <label class="col-sm-3 control-label">{{lang.INPUT_LABEL_BROADCAST_REPEAT_INTERVAL_TXT}}</label>
                <div class="col-sm-6">
                  <input style="width:100%;float:left;" class="form-control" type="text" name="per_sec" id="per_sec" >
                  <label class="hitLabel" for="per_sec">*</label>
                </div>
              </div>

              <div class="modal-footer" style="text-align:center">
                   <button type="submit" class="btn btn-primary">{{lang.BTN_SUBMIT_TXT}}</button>
              </div>
            </form>
      </div>
</div>
<script type="text/javascript">

    $('.broad_type').click(function(){
        var choosVal = $(this).val()
        console.log('--------------chose value'+choosVal);
        if (['0','2'].indexOf(choosVal)>=0){
            $('.endDateDiv').css({'display':'none'});
        }else{
            $('.endDateDiv').css({'display':'block'});
        }
    });
    var firstDate=new Date();
    $('#pick-date-start').val(firstDate.Format("yyyy-MM-dd hh:mm"));
    $('#pick-date-end').val(firstDate.Format("yyyy-MM-dd hh:mm"));

    $('#broadcastForm').submit(function(){
          formAjax($(this).attr("action"), $(this).attr("method"), $(this).serialize(),'正在提交...');
    });

</script>
%rebase admin_frame_base
