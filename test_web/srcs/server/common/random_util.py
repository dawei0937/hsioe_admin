# -*- coding:utf-8 -*-
#!/bin/python

"""
Author: $Author$
Date: $Date$
Revision: $Revision$

Description:
    随机数工具函数
"""

import random
import uuid
from common import except_util

#随机数生成基数###############
#小写字母
lowercase_letters = "abcdefghijklmnopqrstuvwxyz"
#大写字母
majuscule = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
#数字
numbers = "0123456789"
###########################

def __get_randoms(length,value):
    """
    内部函数，获取指定长度的随机字符
    :params length 将要生成的字符长度
    :params text 生成随机字符串的字符池
    :return 生成好的随机字符串
    """
    return random.sample(value,length)

def get_number(length):
    """
    获取指定长度的数字,类型是字符串
    :params length 将要生成的字符长度
    :return 生成好的指定长度的随机数字
    """
    return  ''.join(__get_randoms(length,number))

def get_number_of_range(minnums,maxnums):
    """
    获取指定大小的整形数字
    :params minnums 最小数字
    :params maxnums 最大数字
    :return 生成好的随机数值
    """
    return random.randint(minnums,maxnums)

def get_string(lenght):
    """
    获取指定长度的字符串
    :params length 指定的长度
    :return 生成好的随机字符串
    """
    return ''.join(__get_randoms(length,lowercase_letters+majuscule+number))

def get_letter(length):
    """
    生成随机英文字母字符串(大小写英文字母)
    :params length 长度
    :return 生成好的字符串
    """
    return ''.join(__get_randoms(length,lowercase_letters+majuscule))

def get_uuid():
    """
    随机生成uuid
    :params
    :return 生成好的uuid
    """
    return str(uuid.uuid4()).replace('-','')
