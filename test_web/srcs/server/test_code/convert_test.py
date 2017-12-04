# -*- coding:utf-8 -*-
#!/bin/python

"""
Author: $Author$
Date: $Date$
Revision: $Revision$

Description: Describe module function
"""

import datetime
import unittest
from common import convert_util

class ConvertUtilTest(unittest.TestCase):
    """转换操作包测试类"""

    def setUp(self):
        """初始化测试环境"""
        print('------ini------')

    def tearDown(self):
        """清理测试环境"""
        print('------clear------')

def test_to_int(self):
        self.assertEqual(convert_util.to_int('1'), 1)
        self.assertEqual(convert_util.to_int('1.0'), 0)
        self.assertEqual(convert_util.to_int('1a'), 0)
        self.assertEqual(convert_util.to_int('aaa'), 0)
        self.assertEqual(convert_util.to_int(''), 0)
        self.assertEqual(convert_util.to_int(None), 0)
        self.assertEqual(convert_util.to_int('-1'), -1)
        self.assertEqual(convert_util.to_int(10), 10)
        self.assertEqual(convert_util.to_int(-10), -10)

        self.assertEqual(convert_util.to_int0('1'), 1)
        self.assertEqual(convert_util.to_int0('1.0'), 0)
        self.assertEqual(convert_util.to_int0('1a'), 0)
        self.assertEqual(convert_util.to_int0('aaa'), 0)
        self.assertEqual(convert_util.to_int0(''), 0)
        self.assertEqual(convert_util.to_int0(None), 0)
        self.assertEqual(convert_util.to_int0('-1'), 0)
        self.assertEqual(convert_util.to_int0(10), 10)
        self.assertEqual(convert_util.to_int0(-10), 0)

        self.assertEqual(convert_util.to_int1('1'), 1)
        self.assertEqual(convert_util.to_int1('1.0'), 1)
        self.assertEqual(convert_util.to_int1('1a'), 1)
        self.assertEqual(convert_util.to_int1('aaa'), 1)
        self.assertEqual(convert_util.to_int1(''), 1)
        self.assertEqual(convert_util.to_int1(None), 1)
        self.assertEqual(convert_util.to_int1('-1'), 1)
        self.assertEqual(convert_util.to_int1(10), 10)
        self.assertEqual(convert_util.to_int1(-10), 1)


if __name__ == '__main__':
    unittest.main()
