#-*- coding:utf-8 -*-
#!/usr/bin/python
"""
Author:$Author$
Date:$Date$
Revision:$Revision$

Description:
    后台配置文件
"""
##################################################################################
### 邮件服务参数 ###
# 邮件服务器
SMTP = 'smtp.qq.com'
# 邮件服务器端口
SMTP_PORT = 465
# email发送账号
EMAIL_USER = '514303208@qq.com'
# email发送密码
EMAIL_PWD = 'xxxxxxxxxxx'
# 系统异常邮件通知地址，多个地址用逗号分隔
EMAIL_LIST = '514303208@qq.com'
# 异常邮件通知标题
# ——由于我们有开发环境、测试环境、预生产环境、生产环境等多个不同的环境，
# ——所以在发送异常通知时如果区分的话，可能就弄不清是那个环境出了问题，
# ——我们可以通过设置邮件标题为：开发、测试、预生产、生产等标签来方便区分是那个环境发送的异常通知
EMAIL_ERR_TITLE = '系统异常通知-hsioe_admin-开发'
