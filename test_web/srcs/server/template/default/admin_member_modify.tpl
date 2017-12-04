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
      <form class='form-horizontal group-border-dashed' action="{{info['submitUrl']}}" method='POST' id='agentCreate' onSubmit='return false'>
       <input type='hidden' name='memberId' value="{{info['memberId']}}" />

       <div class="form-group">
            <label class="col-sm-5 control-label">maxScore:<br/>
                <small>设置玩家可以设置的最大分</small>
            </label>
            <div class="col-sm-6">
                  <input type='text' readonly="" value="{{info['maxScore']}}" style='width:100%;float:left' name='maxScore' class="form-control" >
            </div>            
       </div>       

       <div class="form-group">
            <label class="col-sm-5 control-label">baseScore:<br/>
                <small>玩家可以选的分</small>
            </label>
            <div class="col-sm-6">
                 <input type="checkbox" name="score1" style='width:15px;height:15px;' checked="checked"  onclick="return false" value="1" />1 &nbsp;
                  %for score in baseScore:
                    %if str(score['score']) == '1':
                       %continue
                    %end
                    %if str(score['score']) in info['baseScore']:
                      <input type="checkbox" name="{{score['name']}}" style='width:15px;height:15px;' checked="checked" value="{{score['score']}}" />{{score['score']}} &nbsp;
                    %else:
                      <input type="checkbox" name="{{score['name']}}" style='width:15px;height:15px;' value="{{score['score']}}" />{{score['score']}} &nbsp;
                    %end
                  %end
                  <!-- <input type='text' value="{{info['maxScore']}}" style='width:250px;float:left' name='maxScore' class="form-control" > -->
            </div>           
       </div>



       <div class="modal-footer" style="text-align:center">
           <button type="submit" class="btn btn-sm btn-xs btn-primary btn-mobile">修改</button>
           <button type="button" class="btn btn-sm btn-xs btn-primary btn-mobile" name="backid" id="backid">返回</button>
       </div>
</form>
</div>
</div>
</div>
<script type="text/javascript">
    $('#backid').click(function(){
        window.location.href="{{info['backUrl']}}";
   });

</script>
%rebase admin_frame_base