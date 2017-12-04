<style type="text/css">
    .config-table td{text-align:center;font-size:13px;vertical-align:middle}
    .config-table td .input{border:none;text-align:center;}
</style>
<div class="cl-mcont">
<div class="block">
          <div class="header">                          
             %if info.get('title', None):
             <i class="widget-icon fa fa-tags themesecondary"></i>
             <span class="widget-caption themesecondary" id="subTitle">{{info['title']}}</span>
             %end
             <div class='clearfix'></div>
          </div>
          <div class="content">
            <form class="form-horizontal" id='createConfig' onSubmit="return false;" action="" method="POST" style="border-radius: 0px;">
                <table class='table config-table'>
                    <tr>
                      <td align='center'>配置名称</td>                    
                      <td align='center'>配置值</td>                    
                      <td align='center'>配置说明</td>
                    </tr>
                    %for setting in settings:
                      <tr>
                        <td align='center'>{{setting['title']}}</td>
                        <td align='center'>
                            <input type='text' name='{{setting["name"]}}' id='config_name' value="{{setting['value']}}" style='width:100%;height:30px;' class='input'/>
                        </td> 
                        <td>{{setting['desc']}}</td>                    
                      </tr>
                     %end
                     <tr>
                      <td colspan="3" align='center'><button type="submit" class="btn btn-primary">保存更改</button></td>
                     </tr>
                </table>
              </form>
          </div>
</div>
</div>
<script type="text/javascript">
    $('#createConfig').submit(function(){
          formAjax($(this).attr("action"), $(this).attr("method"), $(this).serialize(),'正在保存...');
    });
</script>
%rebase admin_frame_base