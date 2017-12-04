<div class="cl-mcont">
<div class="block">
          <div class="header">                          
              %if info.get('title', None):
                <i class="widget-icon fa fa-tags themesecondary"></i>
                <span class="widget-caption themesecondary">{{info['title']}}</span>
              %end
          </div>
          
          <div class="content">
             <form class='form-horizontal group-border-dashed' action="{{info['subUrl']}}" method='POST' id='broadcastForm' onSubmit='return false'>
             <input type='hidden' name='gameId' value="{{info['defaultGameId']}}" />
              <div class="form-group">
                <label class="col-sm-3 control-label">{{lang.INPUT_LABEL_BROADCAST_TYPE_TXT}}</label>
                <div class="col-sm-6">
                  <input type="radio" checked='checked' name="bType" value='0' id="bType" />&nbsp;游戏广播&nbsp;&nbsp
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
                <label class="col-sm-3 control-label">{{lang.INPUT_LABEL_BROADCAST_REPEAT_COUNT_TXT}}</label>
                <div class="col-sm-6">
                  <input style="width:100%;float:left;" class="form-control" type="text" name="repeatTimes" id="repeatTimes" >
                  <label class="hitLabel" for="repeatTimes">*</label>
                </div>
              </div>

              <div class="form-group">
                <label class="col-sm-3 control-label">{{lang.INPUT_LABEL_BROADCAST_REPEAT_INTERVAL_TXT}}</label>
                <div class="col-sm-6">
                   <input style="width:100%;float:left;" class="form-control" type="text" name="repeatInterval" id="repeatInterval"  value="0">
                   <label class="hitLabel" for="repeatInterval">*</label>
                </div>
              </div>

              <div class="modal-footer" style="text-align:center">
                   <button type="submit" class="btn btn-primary">{{lang.BTN_SUBMIT_TXT}}</button>
              </div>
            </form>
      </div>
</div>
</div>
<script type="text/javascript">
    $('#broadcastForm').submit(function(){
          formAjax($(this).attr("action"), $(this).attr("method"), $(this).serialize(),'正在提交...');
    });

</script>
%rebase admin_frame_base
