<script type="text/javascript" src="{{info['STATIC_ADMIN_PATH']}}/js/agent_create.js"></script>
<div class="cl-mcont">
    <div class='block'>
         <div class='header'>
             <h3>
             %if info.get('title',None):
               {{info['title']}}
             %end
           </h3>
         </div>
<div class='content'>
      <form class='form-horizontal group-border-dashed' action="{{info['submitUrl']}}" method='POST' id='selfModify' onSubmit='return false'>
       <div class="form-group">
            <label class="col-sm-5 control-label">{{lang.INPUT_LABEL_OLD_PASSWD_TXT}}:</label>
            <div class="col-sm-6">
                  <input type='password' style='width:100%;float:left' name='passwd' class="form-control" >
            </div>
       </div>

       <div class="form-group">
            <label class="col-sm-5 col-xs-10 control-label">{{lang.INPUT_LABEL_PASSWD1_TXT}}</label>
            <div class="col-sm-6 col-xs-12">
                  <input type='password' style='width:100%;float:left' name='comfirmPasswd'  data-rules="{required:true}" class="form-control">
            </div>
       </div>


       <div class="form-group">
            <label class="col-sm-5 col-xs-10 control-label">{{lang.INPUT_LABEL_PASSWD2_TXT}}</label>
            <div class="col-sm-6 col-xs-12">
                  <input type='password' style='width:100%;float:left' name='comfirmPasswd1'  data-rules="{required:true}" class="form-control">
            </div>
       </div>

       <div class="modal-footer" style="text-align:center">
           <button type="submit" class="btn btn-sm btn-xs btn-primary btn-mobile">修改</button>
       </div>


</form>
</div>
</div>
</div>

%rebase admin_frame_base