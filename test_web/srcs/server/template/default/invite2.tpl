<!DOCTYPE html>
<html>
<head>
        <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
        <title>{{info['entry_title']}}</title>
        <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate" />
        <meta http-equiv="Pragma" content="no-cache" />
        <meta http-equiv="Expires" content="0" />
        <meta id="MobileViewport" name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1 user-scalable=0" servergenerated="true">
        <script type="text/javascript" src='/assest/default/lib/jquery-2.1.4.min.js'></script>
        <style>
            *{
                padding: 0px;
                margin:0px;
            }
            html{
                height: 100%;
                width: 100%;
                /*background: #AAA url(/assest/default/image/invite/bg.png) no-repeat;*/
                background-size: 100% 100%;
            }
            #downdiv a{
                    position:relative;
                    display:block;
                    width:100%;
                    height:100%;
                    z-index:1;
            }

            #downdiv{
                width: 100%;
                top:47%;
                position: absolute;
                text-align: center;
                display:none;
            }
            #downdiv img{
                width: 60%;
            }
            #translayer{
                position:fixed;
                height: 100%;
                width: 100%;
                z-index:999;
                display:none;
            }

            #layertip{
                width: 100%;
                height:100%;
                position:relative;
            }

        </style>
</head>

<body>
    <div id="downdiv">
        <a  id='open' href="javascript:;">
            <img src="/assest/default/image/invite/dakai.png" />
        </a>
        <a  href="{{info['android_download']}}" id="download_a">
            <img src="/assest/default/image/invite/dlbtn.png" />
        </a>          
        <a  href="{{info['web_href']}}">
            <img src="/assest/default/image/invite/open_web.png" />
        </a>        
    </div>
    
    <div id="translayer">
        <div id="layertip"></div>
    </div>

    <iframe src="{{info['ifr_src']}}" id="ifr"  style="display:none;"></iframe>
</body>

<script type="text/javascript">
    $(function(){
        if( /micromessenger/.test(agent) || /qq\//.test(agent) || (/iphone|ipad|ipod/.test(agent) && /micromessenger/.test(agent))){       
               $('#translayer').css({'display':'block'});
               $('#layertip').css({
                       'background':'url(/assest/default/image/invite/bg1.jpg) no-repeat',
                       'background-size':'100% 100%'
               });
        }else{
              
          $('html').css({
                      "background":"url(/assest/default/image/invite/bg.png) no-repeat",
                      "background-size":'100% 100%'
              });

              $('#downdiv').css('display','block');
        }


        openApp();

        //打开按钮
        $('#open').click(function(){
            openAppHandle();
        });
    });


    var cfg = {
        scheme_ios:'{{info["scheme_ios"]}}',
        scheme_android: '{{info["scheme_android"]}}',
        ios_download:'{{info["ios_download"]}}',
        android_download:'{{info["android_download"]}}',
        timeout:{{info['timeout']}}
    };
    var agent = navigator.userAgent.toLowerCase();
    var ios = false;
    var tx = true;
    var hasApp = true;
    var downloadUrl =cfg.android_download;
    var scheme = cfg.scheme_android;

    if( /micromessenger/.test(agent) || /qq\//.test(agent) )
    {
        tx = true;

    }

    if( /iphone|ipad|ipod/.test(agent) )
    {
        ios = true;
        downloadUrl = cfg.ios_download;
        scheme =  cfg.scheme_ios;
        document.getElementById("download_a").href= downloadUrl;
    }

    //手动打开
    function openAppHandle(){
        window.location=scheme;
    }

    function openApp()
    {   

        if(hasApp)
        {   
            var loadTime = +(new Date());
            window.setTimeout( function(){
                var timeOut = +(new Date());
                if( timeOut - loadTime < 50000 )//打开失败
                {   
                    if( ios ){
                        window.location=scheme;
                    } else{
                        //window.location = '11';
                        //window.parent.location = scheme;
                        //document.getElementById("ifr").src = scheme;
                        //window.parent.location=scheme
                        document.getElementById("downdiv").style.display = "block";
                    }
                    hasApp = false;
                    // break
                } else{
                    window.close();
                }
            }, 100);

            if( ios )
                window.location = scheme;
            window.location = scheme;
            document.getElementById("ifr").src = scheme;
        }

    }
</script>
</html>
