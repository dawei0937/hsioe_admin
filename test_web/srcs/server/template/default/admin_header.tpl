<header class="layout-header">
            <!-- <span class="header-logo">{{session['account']}}</span> -->
            %if agentInfo['type'] in ['2','3']:
                <!-- 只有2,3级代理顶部才显示 -->
                <span class="header-logo" style='margin-left:20px;font-size:1em'>代开模式:&nbsp;<span class='badge'>{{info['open_auth_text']}}</span></span>
            %end
            %if info.has_key('show_card_bar'):
                <span class="header-logo" style='margin-left:20px;font-size:1em'>{{lang.LABEL_ROOMCARD_TITLE}}:&nbsp;<span class='badge badge-card'>{{roomcard}}</span></span>
            %end
            <span class="header-logo"><a href="javascript:;" class='label label-small label-primary' onclick="logout();">{{lang.LABEL_LOGOUT_TXT}}</a></span>
            %if agentInfo['type'] in ['0']:
                <!-- 只有超级管理员显示切换 -->
                <span class="header-logo"><a href="{{info['link_fish_url']}}" class='label label-small label-primary'>{{info['link_fish_txt']}}</a></span>
            %end
            <a class="header-menu-btn" href="javascript:;"><i class="icon-font">&#xe600;</i></a>
            <ul class="header-bar">
                <li class="header-bar-role"><a href="javascript:;">{{lang.LABEL_AGENTROLE_TXT}}:{{TYPE2TXT[agentInfo['type']]}}</a></li>
                <li class="header-bar-role"><a href="javascript:;">{{lang.LABEL_AGENTID_TXT}}:{{agentInfo['id']}}</a></li>
                <li class="header-bar-role"><a href="javascript:;">{{lang.LABEL_LASTLOIN_TIME_TXT}}:{{session['lastLoginDate']}}</a></li>
                <li class="header-bar-role"><a href="javascript:;">{{lang.LABEL_LASTLOIN_IP_TXT}}:{{session['lastLoginIp']}}</a></li>
<!--                 <li class="header-bar-nav"></li> -->
<!--                 <li class="header-bar-nav">
                    <a href="javascript:;" title="换肤"><i class="icon-font">&#xe608;</i></a>
                    <ul class="header-dropdown-menu right dropdown-skin">
                        <li><a href="javascript:;" data-val="qingxin" title="清新">清新</a></li>
                        <li><a href="javascript:;" data-val="blue" title="蓝色">蓝色</a></li>
                        <li><a href="javascript:;" data-val="molv" title="墨绿">墨绿</a></li>

                    </ul>
                </li> -->
            </ul>
</header>
