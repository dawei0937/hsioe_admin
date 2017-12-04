# -*- coding:utf-8 -*-
#!/bin/python

"""
Author: $Author$
Date: $Date$
Revision: $Revision$

Description:
    加密工具函数
"""

import hashlib

def to_md5(value):
    """ md5加密函数 """
    md5 = hashlib.md5()
    if not isinstance(value,bytes):
        value = str(value).encode('utf-8')
    md5.update(value)

    return md5.hexdigest()

def to_sha256(value):
    """ sha256加密函数 """
    sha256  = hashlib.sha256()
    if not isinstance(value,bytes):
        value = str(value).encode('utf-8')
    sha256.update(value)
    return sha256.hexdigest()


import time
if __name__ == '__main__':
    value1 = 'dawei0937'
    print to_md5(value1)
