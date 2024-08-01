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


##############################
# Function definitions
##############################

def pad_hex(num_hex: str, length: int = 4):
    """
    填充16进制字符串，不足指定字节大小则补0

    :param num_hex: 16进制数据，字符串形式
    :param length: 要填充到的长度，单位:字节
    ：returns: 填充后的16进制数据，字符串形式
    """
    if len(num_hex) < 2 + length * 5:
        num_list = ['0x', '0' * (10 - len(num_hex)), num_hex[2:]]
        return ''.join(num_list)


def get_c_char(c):
    """
    根据Python版本的不同，获取一个字符的C语言形式字符
    :param c: 字符
    :return: C语言形式字符
    """
    return c if sys.version_info.major >= 3 else chr(c)


def reverse32(v):
    """
    获取32位数据的反向字节序列
    :param v: 待反转的数据
    :return: 反转后的字节序列
    """
    res = ctypes.create_string_buffer(4)
    res[3] = get_c_char(v & 0x000000FF)
    res[2] = get_c_char((v >> 8) & 0x000000FF)
    res[1] = get_c_char((v >> 16) & 0x000000FF)
    res[0] = get_c_char((v >> 24) & 0x000000FF)
    return res
