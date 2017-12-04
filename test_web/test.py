#-*- coding:utf-8 -*-
#!/usr/bin/env python

"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    平台入口
"""
import urllib2
import cookielib
import urllib
import re
import sys
'''模拟登录'''
reload(sys)
sys.setdefaultencoding("utf-8")
# 防止中文报错
#CaptchaUrl = "http://202.115.80.153/CheckCode.aspx"
PostUrl = "https://www.sg909.com/api/zh-cn/login"
# 验证码地址和post地址
cookie = cookielib.CookieJar()
handler = urllib2.HTTPCookieProcessor(cookie)
opener = urllib2.build_opener(handler)
# 将cookies绑定到一个opener cookie由cookielib自动管理
username = 'username'
password = 'password123'
# 用户名和密码
picture = opener.open(PostUrl).read()

# 打开保存的验证码图片 输入
postData = {
'username': username,
'password': password,
}
# 根据抓包信息 构造表单
headers = {
'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
'Accept-Language': 'zh-CN,zh;q=0.8',
'Connection': 'keep-alive',
'Content-Type': 'application/json',
#'Referer' : "https://www.365-777.com/?&cb=105802121595",
'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.86 Safari/537.36',
}

# 根据抓包信息 构造headers
data = urllib.urlencode(postData)
# 生成post数据 ?key1=value1&key2=value2的形式
request = urllib2.Request(PostUrl, data, headers)
# 构造request请求
try:
    response = opener.open(request)
    result = response.read().decode('')
    # 由于该网页是gb2312的编码，所以需要解码
    print '111111'
    print result
    # 打印登录后的页面
except urllib2.HTTPError, e:
    print e.code
# 利用之前存有cookie的opener登录页面
