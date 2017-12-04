<div class="block">
          <div class="header">                          
            <h3>
                %if info.get('title',None):
                    {{info['title']}}
                %end
            </h3>
          </div>
             <div class="content">
                  <div class='user-avator' style='text-align:center;margin-top:30px;'>
                      <img style="border-radius:30px;" src="{{info['headImgUrl']}}" widht='80' height='80' />
                  </div>
                  <form class='form-horizontal group-border-dashed definewidth m10' action="{{info['submitUrl']}}" method='POST' id='J_Form' onSubmit='return false'>
                         <div class="form-group">
                              <label class="col-sm-5 control-label">会员ID</label>
                              <div class="col-sm-6">
                                      <input type='text' style='width:100%;float:left;' class="form-control"  id='memberId' name='memberId' value="{{info['memberId']}}" readonly="" />
                              </div>
                         </div>        
                         <div class="form-group">
                              <label class="col-sm-5 control-label">微信名称:</label>
                              <div class="col-sm-6">
                                      <input type='text' style='width:100%;float:left;' class="form-control"  name='account' value="{{info['name']}}" readonly="" />
                              </div>
                         </div>        
                         <div class="form-group">
                              <label class="col-sm-5 control-label">剩余钻石:</label>
                              <div class="col-sm-6">
                                      <input type='text' style='width:100%;float:left;' class="form-control"  name='roomCard' value="{{info['roomCard']}}" readonly="" />
                              </div>
                         </div>         
                         <div class="form-group">
                              <label class="col-sm-5 control-label">选择充值套餐:</label>
                              <div class="col-sm-6">
                                    <select name='cardNums' id='cardNums' class="form-control" style='width:100%;height:30px;'>
                                        %for type in info['rechargeTypes']:
                                          <option value="{{type['roomCard']}}">{{type['txt']}}</option>
                                        %end
                                    </select>
                              </div>
                         </div>       

                         <div class="form-group">
                              <label class="col-sm-5 control-label">密码:</label>
                              <div class="col-sm-6">
                                    <input type='password' style='width:100%;float:left;' class="form-control" name='passwd' data-rules="{required:true}">
                              </div>
                         </div>

                         <div class="modal-footer" style="text-align:center">
                             <button type="submit" class="btn btn-sm btn-primary">确认充值</button>
                             <button type="button" class="btn btn-sm btn-primary" name="backid" id="backid">返回</button>
                         </div>
                  </form>
              </div>
        </div>
<script type="text/javascript">
    $('#J_Form').submit(function(){
          var _this = $(this);
          var logTxt   = '正在充值...';
          formAjax(_this.attr("action"),_this.attr("method"),_this.serialize(),logTxt);
    });

    $('#backid').click(function(){
        window.location.href="{{info['backUrl']}}";
   });
</script>
%rebase admin_frame_base