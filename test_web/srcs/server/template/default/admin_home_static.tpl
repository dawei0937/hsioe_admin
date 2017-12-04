<div class='col-md-3'>
    <button style='width:100%;height:45px;padding:5px;'>
        <strong>{{lang.LABEL_MEMBER_TOTAL}}</strong><br>
        <span>{{info['memberTotal']}}</span>
    </button>
</div>
%if session['id'] == '1':
<div class='col-md-3'>
    <button style='width:100%;height:45px;padding:5px;'>
        <strong>{{lang.LABEL_REGIST_DAY}}</strong><br>
        <span>{{info['registByday']}}</span>
    </button>
</div>
%end
<div class='col-md-3'>
    <button style='width:100%;height:45px;padding:5px;'>
        <strong>{{lang.LABEL_LOGIN_DAY}}</strong><br>
        <span>{{info['loginByday']}}</span>
    </button>
</div>
<div class='col-md-3'>
    <button style='width:100%;height:45px;padding:5px;'>
        <strong>{{lang.LABEL_PLAYROOM_DAY}}</strong><br>
        <span>{{info['playRoomByday']}}</span>
    </button>
</div>

%rebase component_panel title='欢迎使用东胜后台管理系统',panel_color='info'
