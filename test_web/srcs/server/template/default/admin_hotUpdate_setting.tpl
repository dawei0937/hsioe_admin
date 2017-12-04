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
            <form class="form-horizontal" id='createConfig' onSubmit="return false;" action="{{info['submitUrl']}}" method="POST" style="border-radius: 0px;">
                <table class='table config-table'>
                    <tr>
                      <td align='center'>更新配置名称</td>                    
                      <td align='center'>更新配置值</td>                    
                    </tr>
                    <tr>
                      <td align='center'>packName</td>
                      <td align='center'>
                          <input type='text' name='packName' id='packName' value="{{settingInfo['packName']}}" style='width:100%;height:30px;' class='input'/>
                      </td> 
                    </tr>                    

                    <tr>
                      <td align='center'>resVersion</td>
                      <td align='center'>
                          <input type='text' name='resVersion' id='resVersion' value="{{settingInfo['resVersion']}}" style='width:100%;height:30px;' class='input'/>
                      </td> 
                    </tr>                    

                    <tr>
                      <td align='center'>minVersion</td>
                      <td align='center'>
                          <input type='text' name='minVersion' id='minVersion' value="{{settingInfo['minVersion']}}" style='width:100%;height:30px;' class='input'/>
                      </td> 
                    </tr>                    

                    <tr>
                      <td align='center'>iosMinVersion</td>
                      <td align='center'>
                          <input type='text' name='iosMinVersion' id='iosMinVersion' value="{{settingInfo['iosMinVersion']}}" style='width:100%;height:30px;' class='input'/>
                      </td> 
                    </tr>                    

                    <tr>
                      <td align='center'>downloadURL</td>
                      <td align='center'>
                          <input type='text' name='downloadURL' id='downloadURL' value="{{settingInfo['downloadURL']}}" style='width:100%;height:30px;' class='input'/>
                      </td> 
                    </tr>                    

                    <tr>
                      <td align='center'>IPAURL</td>
                      <td align='center'>
                          <input type='text' name='IPAURL' id='IPAURL' value="{{settingInfo['IPAURL']}}" style='width:100%;height:30px;' class='input'/>
                      </td> 
                    </tr>                    

                    <tr>
                      <td align='center'>apkSize</td>
                      <td align='center'>
                          <input type='text' name='apkSize' id='apkSize' value="{{settingInfo['apkSize']}}" style='width:100%;height:30px;' class='input'/>
                      </td> 
                    </tr>                    

                    <tr>
                      <td align='center'>apkMD5</td>
                      <td align='center'>
                          <input type='text' name='apkMD5' id='apkMD5' value="{{settingInfo['apkMD5']}}" style='width:100%;height:30px;' class='input'/>
                      </td> 
                    </tr>                    

                    <tr>
                      <td align='center'>hotUpdateURL</td>
                      <td align='center'>
                          <input type='text' name='hotUpdateURL' id='hotUpdateURL' value="{{settingInfo['hotUpdateURL']}}" style='width:100%;height:30px;' class='input'/>
                      </td> 
                    </tr>                    

                    <tr>
                      <td align='center'>hotUpdateScriptsURL</td>
                      <td align='center'>
                          <input type='text' name='hotUpdateScriptsURL' id='hotUpdateScriptsURL' value="{{settingInfo['hotUpdateScriptsURL']}}" style='width:100%;height:30px;' class='input'/>
                      </td> 
                    </tr>                    

                    <tr>
                      <td align='center'>updateAndroid</td>
                      <td align='center'>
                          <input type='text' name='updateAndroid' id='updateAndroid' value="{{settingInfo['updateAndroid']}}" style='width:100%;height:30px;' class='input'/>
                      </td> 
                    </tr>                    

                    <tr>
                      <td align='center'>updateYYB</td>
                      <td align='center'>
                          <input type='text' name='updateYYB' id='updateYYB' value="{{settingInfo['updateYYB']}}" style='width:100%;height:30px;' class='input'/>
                      </td> 
                    </tr>                    

                    <tr>
                      <td align='center'>updateAppStore1</td>
                      <td align='center'>
                          <input type='text' name='updateAppStore1' id='updateAppStore1' value="{{settingInfo['updateAppStore1']}}" style='width:100%;height:30px;' class='input'/>
                      </td> 
                    </tr>                    

                    <tr>
                      <td align='center'>updateAppStore2</td>
                      <td align='center'>
                          <input type='text' name='updateAppStore2' id='updateAppStore2' value="{{settingInfo['updateAppStore2']}}" style='width:100%;height:30px;' class='input'/>
                      </td> 
                    </tr>

                     <tr>
                      <td colspan="2" align='center'><button type="submit" class="btn btn-primary">保存更改</button></td>
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