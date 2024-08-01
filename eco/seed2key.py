#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : ZYD
# @time    : 2024/6/13 下午3:03
# @function: 加载.dll，根据种子计算密钥，函数原型ASAP1A_CCP_ComputeKeyFromSeed或seedgetkey
# @version : V1.0.0


##############################
# Module imports
##############################

import ctypes
from typing import List, Union


##############################
# Function declarations
##############################

def get_key_of_seed(seed2key_filepath: str, seed_data: Union[List[int], bytes, bytearray]):
    """
    根据种子和算法计算密钥
    :param seed2key_filepath: 算法所在dll的文件路径
    :param seed_data: 存有种子的字节列表
    :return: 存有密钥的字节列表
    """
    dll = ctypes.windll.LoadLibrary(seed2key_filepath)
    if hasattr(dll, 'ASAP1A_CCP_ComputeKeyFromSeed'):
        # print('存在ASAP1A_CCP_ComputeKeyFromSeed')
        seed_len = len(seed_data)
        seed_data = (ctypes.c_char * seed_len)(*seed_data)
        seed_size = ctypes.c_uint16(seed_len)
        key_len = seed_len
        key_data = (ctypes.c_char * key_len)()
        max_size = ctypes.c_uint16(key_len)
        key_size = ctypes.c_uint16()
        res = dll.ASAP1A_CCP_ComputeKeyFromSeed(ctypes.byref(seed_data),
                                                seed_size,
                                                ctypes.byref(key_data),
                                                max_size,
                                                ctypes.byref(key_size))
        return [byte for byte in key_data.value]
    elif hasattr(dll, 'seedgetkey'):
        # int __stdcall seedgetkey(unsigned int *a1, unsigned int *a2, unsigned int *a3, unsigned int *a4)
        # print('存在seedgetkey')
        a1 = ctypes.c_int(seed_data[0])
        a2 = ctypes.c_int(seed_data[1])
        a3 = ctypes.c_int(seed_data[2])
        a4 = ctypes.c_int(seed_data[3])
        res = dll.seedgetkey(ctypes.byref(a1),
                             ctypes.byref(a2),
                             ctypes.byref(a3),
                             ctypes.byref(a4))
        return [a1.value, a2.value, a3.value, a4.value]
    else:
        msg = f'{seed2key_filepath}中不存在ASAP1A_CCP_ComputeKeyFromSeed或seedgetkey函数'
        raise LookupError(msg)


if __name__ == '__main__':
    pass
    # 32位ccp
    # filepath = r'C:\Users\XCMGSC\Desktop\pythonProject\Eco_Downloader_32\other\PG_Default.dll'
    # filepath = r'C:\Users\XCMGSC\Desktop\pythonProject\Eco_Downloader_32\other\SeedKeyDll.dll'

    # 32位uds
    # filepath = r'C:\Users\XCMGSC\Desktop\pythonProject\Eco_Downloader_32\other\UdsSeedKeyDll.dll'
    # filepath = r'C:\Users\XCMGSC\Desktop\pythonProject\Eco_Downloader_32\other\sdkey.dll'
    #
    # seed_ccp = [0x17, 0x7E, 0x64, 0x19]
    # # seed_ccp = [0x19, 0x64, 0x7E, 0x17]
    # key_ccp = [0x84, 0xf7, 0xe7, 0x30]
    #
    # seed_uds = [0x2a, 0x46, 0xb8, 0xde]
    # # seed_uds = [0xde, 0xb8, 0x46, 0x2a]
    # key_uds = [0xb8, 0x56, 0xbd, 0xd0]
    #
    # seed = seed_uds
    # key = get_key_of_seed(filepath, seed)
    # print([hex(i) for i in key])
