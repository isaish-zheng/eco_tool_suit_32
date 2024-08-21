#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : ZYD
# @Time    : 2024/7/11 上午9:09
# @version : V1.0.0
# @function:


##############################
# Module imports
##############################

import ctypes
import sys
from typing import Any


##############################
# Function definitions
##############################

def pad_hex(num_hex: str, length: int = 4) -> str:
    """
    填充16进制字符串，不足指定字节大小则补0

    :param num_hex: 0x开头的16进制数据
    :type num_hex: str
    :param length: 要填充到的长度，单位:字节
    :type length: int
    :returns: 填充后0x开头的16进制数据
    :rtype: str
    """
    length_sum = length * 2 + 2  # 填充以后得总长度
    if len(num_hex) < length_sum:
        num_list = ['0x', '0' * (length_sum - len(num_hex)), num_hex[2:]]
        return ''.join(num_list)
    else:
        return num_hex


def get_c_char(c: int) -> int:
    """
    根据Python版本的不同，获取一个字符的C语言形式字符

    :param c: 单个字符
    :type c: int
    :return: C语言形式字符
    :rtype: int
    """
    return c if sys.version_info.major >= 3 else chr(c)


def reverse32(v: int) -> Any:
    """
    获取32位数据的反向字符序列

    :param v: 待反转的数据
    :type v: int
    :return: 反转后的字节序列
    :rtype: Any
    """
    res = ctypes.create_string_buffer(4)
    res[3] = get_c_char(v & 0x000000FF)
    res[2] = get_c_char((v >> 8) & 0x000000FF)
    res[1] = get_c_char((v >> 16) & 0x000000FF)
    res[0] = get_c_char((v >> 24) & 0x000000FF)
    return res
