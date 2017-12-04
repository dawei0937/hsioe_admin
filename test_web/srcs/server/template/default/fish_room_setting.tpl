%if info['submitUrl'][-6:] == 'create':
<tr>
     <td class='table-title'>
                是否允许试玩<br/>
                <small>设置为试玩则改房间为试玩房间</small>
         </td>
         <td>
              <input type="radio"  name="isTrail" value='0' checked="checked"/> 不允许
              <input type="radio"  name="isTrail" value='1'/> 允许
         </td>
</tr>
<tr>
         <td class='table-title'>
                限制金币<br/>
                <small>是否限制玩家携带的金币</small>
         </td>
         <td>
              最小携带金币:<br>
              <input type="text" style='width:100%;float:left' id="min_coin" name="min_coin" class="form-control" />
              最大携带金币:<br>
              <input type="text" style='width:100%;float:left' id="max_coin" name="max_coin" class="form-control" />
         </td>
</tr>
<tr>
         <td class='table-title'>
                房间最大人数<br/>
                <small>改房间允许的最大玩家人数</small>
         </td>
         <td>
              <input type="text" style='width:100%;float:left' id="max_player_count" name="max_player_count" class="form-control" />
         </td>
</tr>                                                                    
%else:
<tr>
     <td class='table-title'>
                是否允许试玩<br/>
                <small>设置为试玩则改房间为试玩房间</small>
         </td>
         <td>
            %if room_info['isTrail'] == '0':
              <input type="radio"  name="isTrail" value='0' checked="checked"/> 不允许
              <input type="radio"  name="isTrail" value='1'/> 允许
            %else:
              <input type="radio"  name="isTrail" value='0'/> 不允许
              <input type="radio"  name="isTrail" value='1' checked="checked"/> 允许
            %end
         </td>
</tr>
<tr>
         <td class='table-title'>
                限制金币<br/>
                <small>是否限制玩家携带的金币</small>
         </td>
         <td>
              最小携带金币:<br>
              <input type="text" style='width:100%;float:left' value="{{room_info['min_coin']}}" id="min_coin" name="min_coin" class="form-control" />
              最大携带金币:<br>
              <input type="text" style='width:100%;float:left' value="{{room_info['max_coin']}}" id="max_coin" name="max_coin" class="form-control" />
         </td>
    </tr>
</tr>
<tr>
         <td class='table-title'>
                房间最大人数<br/>
                <small>改房间允许的最大玩家人数</small>
         </td>
         <td>
              <input type="text" style='width:100%;float:left'  value="{{room_info['max_player_count']}}" id="max_player_count" name="max_player_count" class="form-control" />
         </td>
</tr>
%end
