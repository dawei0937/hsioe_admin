    <div class='block'>
         <div class='header'>
             <h3>
             %if info.get('title',None):
               {{info['title']}}
             %end
           </h3>
         </div>
         <div class='content'>
              <form class='form-horizontal group-border-dashed' action="{{info['submitUrl']}}" method='POST' id='J_Form' onSubmit='return false'>
                     <div class="form-group">
                          <label class="col-sm-5 control-label">{{lang.CARD_SALER_TXT}}:</label>
                          <div class="col-sm-6">
                                <input type="text" style='width:100%;float:left' id="parentAccount" name="parentAg" value="{{info['parentAccount']}}" readonly='' class="form-control">
                          </div>
                     </div>  

                   <div class="form-group">
                        <label class="col-sm-5 control-label">{{lang.CARD_PACK_CHOOSE_TXT}}:</label>
                        <div class="col-sm-6">
                             <input type='text' name='cardNums' style='width:100%;float:left' data-rules="{required:true}" class='form-control' />
                        </div>
                   </div> 
                   
                     <div class="form-group">
                          <label class="col-sm-5 control-label">{{lang.CARD_REMARK_TXT}}:</label>
                          <div class="col-sm-6">
                                <textarea name='note' style='width:100%;height:100px;resize:none' class='form-control'></textarea>
                          </div>
                     </div>           

                     <div class="form-group">
                          <label class="col-sm-5 control-label">{{lang.INPUT_LABEL_PASSWD_TXT}}:</label>
                          <div class="col-sm-6">
                                <input type='password' name='passwd' style='width:100%;float:left' data-rules="{required:true}" class='form-control' />
                          </div>
                     </div>

                     <div class="modal-footer" style="text-align:center">
                         <button type="submit" class="btn btn-sm btn-primary">{{lang.CARD_APPLY_RECHARGE_TXT}}</button>
                         <button type="button" class="btn btn-sm btn-primary" name="backid" id="backid">{{lang.BTN_BACK_TXT}}</button>
                     </div>
              </form>
         </div>
    </div>
<script type="text/javascript">
    $('#J_Form').submit(function(){
          formAjax($(this).attr("action"), $(this).attr("method"), $(this).serialize(),'正在提交订单...');
    });

    $('#backid').click(function(){
        window.location.href="{{info['backUrl']}}";
   });
</script>
%rebase admin_frame_base