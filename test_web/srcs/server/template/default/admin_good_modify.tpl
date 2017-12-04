<style type="text/css">
    .config-table td.table-title{text-align:center;font-size:13px;vertical-align:middle}
</style>
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
             <form class="form-horizontal group-border-dashed" id='gameForm' onSubmit="return false;" action="{{info['submitUrl']}}" method="post" style="border-radius: 0px;" enctype="multipart/form-data">
               <input type="hidden" name="goodsId" value="{{goodsId}}" />
               <table class='table config-table'>
                        <tr>
                          <td width='20%' class='table-title'>编辑商品</td>
                        </tr>
                        <tr>
                              <td class='table-title'>`</td>
                              <td>
                                <table class='table config-table' border='1'>
                                    <tr>
                                         <td class='table-title'>商品名称</td>
                                         <td>
                                             <input type="text" style='width:100%;float:left' value="{{goodsInfo['name']}}" id="name" name="name" class="form-control">
                                             <label for='name' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>
                                    <tr>
                                         <td class='table-title'>{{lang.GOODS_TYPE_TXT}}</td>
                                         <td>
                                            %if goodsInfo['type'] == '0':
                                              <input type="radio" name="goods_type" value='0' checked='checked' />钻石
                                              <input type="radio" name="goods_type" value='1' />金币
                                            %else:
                                              <input type="radio" name="goods_type" value='0' />钻石
                                              <input type="radio" name="goods_type" value='1' checked='checked' />金币
                                            %end
                                         </td>
                                    </tr>                                      
                                    <tr>
                                         <td class='table-title'>商品钻石数</td>
                                         <td>
                                             <input type="text" style='width:100%;float:left' value="{{goodsInfo['cards']}}" id="cards" name="cards" class="form-control">
                                             <label for='cards' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>                                    
                                     <tr>
                                         <td class='table-title'>赠送钻石数</td>
                                         <td>
                                             <input type="text" style='width:100%;float:left' value="{{goodsInfo['present_cards']}}" id="present_cards" name="present_cards" class="form-control">
                                             <label for='present_cards' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>                                     
                                    <tr>
                                         <td class='table-title'>商品价格(单位:元)</td>
                                         <td>
                                             <input type="text" style='width:100%;float:left' value="{{goodsInfo['price']}}" id="price" name="price" class="form-control">
                                             <label for='price' class='hitLabel' style='float:left;line-height:30px'>*</label>
                                         </td>
                                    </tr>
                        </tr>                                
              </table>
              <div class="modal-footer" style="text-align:center">
                   <button type="submit" class="btn btn-primary">{{lang.BTN_SUBMIT_TXT}}</button>
                  <button type="button" class="btn btn-primary" id='backid'>{{lang.BTN_BACK_TXT}}</button>
              </div>
            </form>
          </div>
</div>
</div>
<script type="text/javascript">
    $('#gameForm').submit(function(){
          formAjax($(this).attr("action"), $(this).attr("method"), $(this).serialize(),'正在修改...');
    });

    $('#backid').click(function(){
        window.location.href="{{info['backUrl']}}";
   });
</script>
%rebase admin_frame_base