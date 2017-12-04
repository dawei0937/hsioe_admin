%if info['submitUrl'][-6:] == 'create':
<tr>
     <td class='table-title'>
                金币保底<br/>
                <small></small>
         </td>
         <td>
              <input type="text"  style='width:100%;float:left' class="form-control" name="need_coin" value='' checked="checked"/>
         </td>
</tr>
<tr>
         <td class='table-title'>
                金币价值<br/>
                <small></small>
         </td>
         <td>
            <input type="text"   style='width:100%;float:left' class="form-control" name="coin_value" value='' checked="checked"/>
         </td>
</tr>

%else:
<tr>
     <td class='table-title'>
                金币保底<br/>
                <small></small>
         </td>
         <td>
              <input type="text"  style='width:100%;float:left' class="form-control" name="need_coin" value='{{room_info["need_coin"]}}' checked="checked"/>
         </td>
</tr>
<tr>
         <td class='table-title'>
                金币价值<br/>
                <small></small>
         </td>
         <td>
            <input type="text" style='width:100%;float:left'  class="form-control" name="coin_value" value='{{room_info["coin_value"]}}' >
         </td>
</tr>
%end
