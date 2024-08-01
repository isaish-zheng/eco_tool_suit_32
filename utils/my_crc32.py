#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : ZYD
# @version : V1.0.0
# @function: V1.0.0：crc32校验类（使用查表法）


##############################
# Module imports
##############################

import srecord
from typing import List, Union


##############################
# CRC32 API function declarations
##############################

class Crc32Bzip2(object):
    """CRC-32/BZIP2

    Aliases: CRC-32/AAL5, CRC-32/DECT-B, B-CRC-32
    _names = ('CRC-32/BZIP2', 'CRC-32/AAL5', 'CRC-32/DECT-B', 'B-CRC-32')
    _width = 32
    _poly = 0x04c11db7
    _initvalue = 0xffffffff
    _reflect_input = False
    _reflect_output = False
    _xor_output = 0xffffffff
    _check_result = 0xfc891918
    """
    def __init__(self,
                 check_data: Union[List[int], bytes],
                 poly: int = 0x04C11DB7,
                 init_crc: int = 0xFFFFFFFF,
                 ref_in: bool = False,
                 ref_out: bool = False,
                 xor_out: int = 0xFFFFFFFF):
        """
        CRC32校验类
        :param check_data: 待测数据，整数列表，例如：字符串'123456789'，
            转换为整数列表[0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39],
            或b'123456789'
        :param poly: 生成项的简写，例如：0x04C11DB7，忽略最高位的"1"，即完整的生成项是0x104C11DB7
        :param init_crc: 算法开始时crc的初始化预置值，例如：0xFFFFFFFF
        :param ref_in: 待测数据的每个字节是否按位反转，True或False
        :param ref_out: 在计算后之后，异或输出之前，整个数据是否按位反转，True或False
        :param xor_out: 计算结果与此参数异或后得到最终的crc值
        """
        self.__check_value = check_data
        self.__poly = poly
        self.__init_crc = init_crc
        self.__ref_in = ref_in
        self.__ref_out = ref_out
        self.__xor_out = xor_out
        self.__crc32_table = self.__generate_crc32_table(self.__poly)
        self.__crc32_int = self.__get_crc32(check_data=self.__check_value,
                                            table=self.__crc32_table,
                                            init_crc=self.__init_crc,
                                            ref_in=self.__ref_in,
                                            ref_out=self.__ref_out,
                                            xor_out=self.__xor_out)

    @staticmethod
    def __generate_crc32_table(poly: int):
        """
        生成crc32校验表
        :param poly: 生成项
        :return: crc32校验表
        """
        poly = poly & 0xFFFFFFFF
        table = [0 for _ in range(0, 256)]
        for i in range(256):
            c = i << 24
            for j in range(8):
                if c & 0x80000000:
                    c = (c << 1) ^ poly
                else:
                    c = c << 1
            table[i] = c & 0xFFFFFFFF
        return table

    @staticmethod
    def __get_crc32(check_data: Union[List[int], bytes],
                    table: List[int],
                    init_crc: int,
                    ref_in: bool,
                    ref_out: bool,
                    xor_out: int):
        """
        计算crc32校验值，以局部变量访问可以大幅提升计算速度
        :param check_data: 待测数据，整数列表，例如：字符串'123456789'，
            转换为整数列表[0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39],
            或b'123456789'
        :param table: crc32校验表
        :param init_crc: 算法开始时crc的初始化预置值，例如：0xFFFFFFFF
        :param ref_in: 待测数据的每个字节是否按位反转，True或False
        :param ref_out: 在计算后之后，异或输出之前，整个数据是否按位反转，True或False
        :param xor_out: 计算结果与此参数异或后得到最终的crc值
        :return: crc32校验值，整型
        """

        def get_reverse(temp_data: int, byte_length: int):
            """
            获取数据的位逆序
            :param temp_data: 待位逆序的数据
            :param byte_length: 待位逆序的数据的字节长度
            :return: 位逆序后的数据
            """
            reverse_data = 0
            bits_length = byte_length << 3
            for i in range(0, bits_length):
                reverse_data += ((temp_data >> i) & 1) << (bits_length - 1 - i)
            return reverse_data

        if check_data is not None:
            crc = init_crc
            if ref_in:
                for byte in check_data:
                    crc = table[get_reverse(byte, 1) ^ ((crc >> 24) & 0xFF)] \
                          ^ ((crc << 8) & 0xFFFFFF00)
            else:
                for byte in check_data:
                    crc = table[byte ^ ((crc >> 24) & 0xFF)] ^ ((crc << 8) & 0xFFFFFF00)
        else:
            crc = init_crc

        # 返回计算的CRC值
        crc = ref_out and (get_reverse(crc, 4) ^ xor_out) or (crc ^ xor_out)
        return crc & 0xFFFFFFFF

    @property
    def crc32_int(self):
        """
        :return: crc32校验值的整数形式，例如：4236843288，即0xfc891918
        """
        return self.__crc32_int

    @property
    def crc32_bytes(self):
        """
        :return: crc32校验值的bytes形式，例如：b'\xfc\x89\x19\x18'，即0xFC891918
        """
        return self.__crc32_int.to_bytes(length=4, byteorder='big', signed=False)

    @property
    def crc32_bytes_arr(self):
        """
        :return: crc32校验值的列表形式，例如：[252, 137, 25, 24]，即b'\xfc\x89\x19\x18'，0xFC891918
        """
        return [b for b in self.crc32_bytes]


if __name__ == '__main__':
    pass
    # file = r'.\other\xjmain.mot'
    # obj_s = srecord.Srecord(file)
    # all_erase_datas = []
    # for erase_memory_info in obj_s.erase_memory_infos:
    #     all_erase_datas.append(erase_memory_info.erase_data)
    # hex_string = ''.join(all_erase_datas)
    # ascii_values = bytes.fromhex(hex_string)
    # # 自定义crc32
    # buf_s = [0x31, 0x32, 0x33, 0x34, 0x35, 0x36, 0x37, 0x38, 0x39]
    # obj_crc32 = Crc32(check_data=buf_s,
    #                   poly=0x04C11DB7,
    #                   init_crc=0xFFFFFFFF,
    #                   ref_in=False,
    #                   ref_out=False,
    #                   xor_out=0xFFFFFFFF)
    # crc_value = obj_crc32.crc32_int
    # # print('自定义算出来的CRC值:', '0x' + "{:0>8s}".format(str('%x' % crc_stm)))
    # print(f"自定义—CRC-32: {crc_value & 0xffffffff:08x}")
    # print(f"自定义—CRC-32: {crc_value}")
    # print(obj_crc32.crc32_bytes)
    # print(obj_crc32.crc32_bytes_arr)
