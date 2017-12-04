#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
@Author: $Author$
@Date: $Date$
@version: $Revision$

Description:
    Web启动
"""
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.insert(0, 'server_common')
sys.path.insert(0, './server')
sys.path.insert(0, '.')
import bottle
import server.main


if __name__ == '__main__':
    bottle.run(server='paste', host='0.0.0.0', port=9798, reloader=True, debug=False)
else:
    application = bottle.default_app()
