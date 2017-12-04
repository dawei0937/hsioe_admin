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
             <form class='form-horizontal group-border-dashed' action="{{info['submitUrl']}}" method='POST' id='noticeForm' onSubmit='return false'>
              <input type="hidden" name="noticeId" value="{{info['noticeId']}}" />
              <div class="form-group">
                 <label class="col-sm-3 control-label">
                    消息标题<br/>
                    <small>(消息/邮件标题)</small>
                 </label>
                 <div class='col-sm-7'>
                    <input type="text" name="title" class='form-control' value="{{noticInfo['title']}}" style="width:{{MAIL_SETTING_INFO['mailTextWidth']}};height:40px;" />
                 </div>
              </div>              
              <div class="form-group">
                 <label class="col-sm-3 control-label">
                    有效天数<br/>
                    <small>(该天数后自动删除)</small>
                 </label>
                 <div class='col-sm-7'>
                    %if noticInfo['validDate'] == '0':
                      <input type="radio" name="validDate" value='0'  checked='checked' style='line-height:50px;'/> 永久 &nbsp;&nbsp;&nbsp;
                      <input type="radio" name="validDate" value='7' style='line-height:50px;' /> 一周 &nbsp;&nbsp;&nbsp;
                      <input type="radio" name="validDate" value='30' style='line-height:50px;'/> 一月
                    %elif noticInfo['validDate'] == '30':
                      <input type="radio" name="validDate" value='0'  style='line-height:50px;'/> 永久 &nbsp;&nbsp;&nbsp;
                      <input type="radio" name="validDate" value='7' checked='checked' style='line-height:50px;' /> 一周 &nbsp;&nbsp;&nbsp;
                      <input type="radio" name="validDate" value='30' style='line-height:50px;'/> 一月
                    %else:
                      <input type="radio" name="validDate" value='0'  style='line-height:50px;'/> 永久 &nbsp;&nbsp;&nbsp;
                      <input type="radio" name="validDate" value='7'  style='line-height:50px;' /> 一周 &nbsp;&nbsp;&nbsp;
                      <input type="radio" name="validDate" value='30' checked='checked' style='line-height:50px;'/> 一月
                    %end
                 </div>
              </div>              
              <div class="form-group">
                 <label class="col-sm-3 control-label">
                    消息类型<br/>
                    <small>(公告类型)</small>
                 </label>
                 <div class='col-sm-7'>
                    <input type="text" name="messageType" value="{{MSGTYPE2DESC[noticInfo['messageType']]}}" readonly="" style="height:35px;width:100%;" clsss='form-control'/>
                 </div>
              </div>
              <div class="form-group">
                <label class="col-sm-3 control-label">
                    消息内容<br/>
                    <small>(推送给用户)</small>
                </label>
                <div class="col-sm-7">
                    <textarea style="width:{{MAIL_SETTING_INFO['mailTextWidth']}};height:{{MAIL_SETTING_INFO['mailTextHeight']}};float:left"  name='content' class="form-control xheditor">{{!noticInfo['content']}}</textarea>
                </div>
              </div>

              <div class="modal-footer" style="text-align:center">
                   <button type="submit" class="btn btn-sm btn-primary">{{lang.BTN_SUBMIT_TXT}}</button>
                   <button type="button" class="btn btn-sm btn-primary" name="backid" id="backid">{{lang.BTN_BACK_TXT}}</button>
              </div>
            </form>
          </div>
</div>
</div>


<script type="text/javascript">
       $('#backid').click(function(){
           window.location.href="{{info['backUrl']}}";
      });

       $('#noticeForm').submit(function(){
             formAjax($(this).attr("action"), $(this).attr("method"), $(this).serialize(),'正在创建...');
       });
</script>
%rebase admin_frame_base