%if info['submitUrl'][-6:] == 'create':
<tr>
     <td class='table-title'>
                最小底分<br/>
                <small>游戏最小底分</small>
         </td>
         <td>
              <input type="text" style='width:100%;float:left' id="base_coin" name="base_coin" class="form-control">
         </td>
    </tr>                                   
    <tr>
         <td class='table-title'>
                最大底分<br/>
                <small>游戏最大底分</small>
         </td>
         <td>
              <input type="text" style='width:100%;float:left' id="max_base_coin" name="max_base_coin" class="form-control">
         </td>
    </tr>                                   
    <tr>
         <td class='table-title'>
                步长底分<br/>
                <small>游戏中玩家切换的炮分间隔值</small>
         </td>
         <td>
                <input type="text" style='width:100%;float:left' id="step_base_coin" name="step_base_coin" class="form-control">
         </td>
    </tr>
</tr>
%else:
<tr>
     <td class='table-title'>
                最小底分<br/>
                <small>游戏最小底分</small>
         </td>
         <td>
              <input type="text" style='width:100%;float:left' value="{{room_info['base_coin']}}" id="base_coin" name="base_coin" class="form-control">
         </td>
    </tr>                                   
    <tr>
         <td class='table-title'>
                最大底分<br/>
                <small>游戏最大底分</small>
         </td>
         <td>
              <input type="text" style='width:100%;float:left' value="{{room_info['max_base_coin']}}" id="max_base_coin" name="max_base_coin" class="form-control">
         </td>
    </tr>                                   
    <tr>
         <td class='table-title'>
                步长底分<br/>
                <small>游戏中玩家切换的炮分间隔值</small>
         </td>
         <td>
                <input type="text" style='width:100%;float:left' value="{{room_info['step_base_coin']}}" id="step_base_coin" name="step_base_coin" class="form-control">
         </td>
    </tr>
</tr>
%end