#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : ZYD
# @version : V1.0.0
# @function: V1.0.0：
"""
解析.mot/.s19/.srec格式的SRecord记录文件,
获取S0中的描述信息保存在属性describe_info:str，
获取S3数据记录保存在属性s3records:List[S3Record]，
获取S3记录的擦写内存区域信息保存在属性erase_memory_infos:List[EraseMemoryInfo]

SRecord格式
SRecord文件是由Motorola公司定义的一种ASCII文本文件，
文件扩展名包括：.s19、.s28、.s37、.s、.s1、.s2、.s3、.sx、.srec、.exo、.mot、.mxt，都是同一种格式，
文件内容没有差异，主要用于记录微控制器、EPROM和其他类型的可编程设备的程序记录。SRecord以一行文本作为一条记录（Record），每行记录的格式如下：

Record_start	Type	Byte_count	Address_Data	CheckSum

Record_start：由字符‘S’表述记录的起始；
Type：由字符‘0’~‘9’表示本行记录的类型；
Byte_count：一个字节长度，两个十六进制字符，表示本字段后续其他字段字节总长度（address+data+checksum），最小值为0x3，最大值为0xFF；
Address：2/3/4字节长度，4/6/8个十六进制字符，表示本行记录的起始地址（大端字节序）；
Data：本行记录的数据
CheckSum：一个字节长度，2个十六进制字符，表示Byte count、Address、Data字段数据的校验和，计算公式为：0xFF & （sum & 0xFF）;

备注：每行S-Record记录的最长字符数为514个字符，S1/S2/S3记录的数据域长度最小为0，最大分别为504、502、500
"""


##############################
# Module imports
##############################

from typing import List

from utils import pad_hex
from utils import Crc32Bzip2 as Crc32


##############################
# Type definitions
##############################

class SrecordException(Exception):
    """
    自定义Srecord异常
    """

    def __init__(self, message: str):
        """
        :param message: 要显示的异常消息
        """
        self.message = message

    def __str__(self):
        return f"{self.message}"


class S3Record(object):
    """
    存储一条S3数据记录的信息
    """

    def __init__(self,
                 line_number: int,
                 raw_file_line_number: int,
                 record_type: str,
                 data_length: int,
                 start_address32: str,
                 data: str
                 ):
        self.line_number = line_number  # 本条数据记录在列表中的行号(0基)
        self.raw_file_line_number = raw_file_line_number  # 本条数据记录在源文件中的行号(1基)
        self.record_type = record_type  # 本条数据记录类型
        self.data_length = data_length  # 本条数据记录数据长度(Byte)
        self.start_address32 = start_address32  # 本条数据记录32位起始地址
        self.data = data  # 本条数据记录有效数据


class EraseMemoryRecord(object):
    """
    存储一段擦写内存的首尾行记录
    """

    def __init__(self,
                 begin_record: S3Record = None,
                 end_record: S3Record = None,
                 ):
        self.begin_record = begin_record  # 擦写内存块的首行记录
        self.end_record = end_record  # 擦写内存块的尾行记录


class EraseMemoryInfo(object):
    """
    一段擦写内存的信息
    """

    def __init__(self,
                 erase_number: int,
                 erase_start_address32: str,
                 erase_length: str,
                 erase_data: str,
                 erase_memory_record: EraseMemoryRecord
                 ):
        self.erase_number = erase_number  # 擦写内存段的标号(第几段连续内存区域)
        self.erase_start_address32 = erase_start_address32  # 本段擦写内存的起始地址
        self.erase_length = erase_length  # 本段擦写内存的长度Byte
        self.erase_data = erase_data  # 本段擦写数据
        self.erase_memory_record = erase_memory_record  # 本段擦写内存的首尾行记录


##############################
# Srecord API function declarations
##############################

class Srecord(object):
    """
    解析SRecord文件，处理S3数据记录，获取内存擦写信息
    """
    srecord_type_dic = {
        # 记录头16位地址，主要描述供应商相关信息，比如文件、产品、供应商等信息
        'record_head': 'S0',
        # 数据记录16位地址，记录从16位地址开始的数据，其中数据域可以为空，用于8位处理器，比如8051
        'data_record_addr16': 'S1',
        # 数据记录24位地址，记录从24位地址开始的数据，其中数据域可以为空
        'data_record_addr24': 'S2',
        # 数据记录32位地址，记录从32位地址开始的数据，其中数据域可以为空
        'data_record_addr32': 'S3',
        # 未定义
        'undefined': 'S4',
        # 计数16位计数，（可选项）用于记录文本文件中S1/S2/S3记录的个数，最大65535，超过需要使用S6
        'count_bit16': 'S5',
        # 计数24位计数，（可选项）用于记录文本文件中S1/S2/S3记录的个数，最大16777215
        'count_bit24': 'S6',
        # 起始地址（程序终止）32位地址，表示程序的执行起始地址（类似main函数地址），
        # 如果SREC文件仅用于对内存设备进行编程，则可以忽略该地址信息。也表示S3记录的结束
        'pgm_start_addr32': 'S7',
        # 起始地址（程序终止）24位地址，表示程序的执行起始地址（类似main函数地址），
        # 如果SREC文件仅用于对内存设备进行编程，则可以忽略该地址信息。也表示S2记录的结束
        'pgm_start_addr24': 'S8',
        # 起始地址（程序终止）16位地址，表示程序的执行起始地址（类似main函数地址），
        # 如果SREC文件仅用于对内存设备进行编程，则可以忽略该地址信息。也表示S1记录的结束
        'pgm_start_addr16': 'S9',
    }

    def __init__(self, filepath: str):
        """
        :param filepath: SRecord文件路径
        """
        self.__check_all_sum(filepath)
        (self.__s3_records,
         self.__describe_info,
         self.__pgm_start_addr) = self.__get_s3records(filepath)
        self.__erase_memory_records = self.__get_erase_memory_records(self.__s3_records)
        self.__erase_memory_infos = self.__get_erase_memory_infos(self.__s3_records,
                                                                  self.__erase_memory_records)
        self.__crc32_values = self.__get_crc32_values()

    def get_epk(self, epk_addr: str):
        """
        获取epk
        :return: 若存在返回epk，否则返回None
        """
        all_erase_datas = []
        for erase_memory_info in self.__erase_memory_infos:
            if int(erase_memory_info.erase_start_address32, 16) == int(epk_addr, 16):
                return erase_memory_info.erase_data

    @staticmethod
    def __check_all_sum(filepath: str):
        """
        校验Srecord文件的checksum
        :return: 若校验通过返回None，否则抛出在第几行校验错误的异常
        """

        def checksum(record: str):
            """
            长度、地址和数据参与checksum运算，类型、校验和不参与校验
            运算公式为：校验和=0xff – (长度 + 地址 + 数据)
            :param record: 一条记录
            :return: 本条记录的校验和
            """
            # 去除类型、校验和
            check_string = record[2:-2]
            # 将字符串每两个分割之后转换成16进制数字
            numbers = [int(check_string[i:i + 2], 16) for i in range(0, len(check_string), 2)]
            # 求 (长度 + 地址 + 数据)的和
            sum_number = sum(numbers)
            # 求 校验和=0xff – (长度 + 地址 + 数据) ；转化成字符串之后去掉前面的'0X'字符
            checksum = hex(0xff - (0xff & sum_number)).upper().replace('0X', '')
            # 格式化校验和字符串，如果长度大于2取后两位，如果长度小于2在前面补零
            if len(checksum) < 2:
                while len(checksum) < 2:
                    checksum = '0' + checksum
            else:
                checksum = checksum[-2:]
            return checksum

        with open(file=filepath, mode='r', encoding='utf-8') as f:
            raw_file_line_number = 0
            for line in f.readlines():
                line = line.strip()  # 去除该行的换行符
                raw_file_line_number += 1
                if line != '' and checksum(line) != line[-2:]:
                    f.close()
                    msg = f'Srecord文件在第{raw_file_line_number}行校验和错误，应为"{checksum(line)}"，实际为"{line[-2:]}"'
                    raise SrecordException(msg)
        return True

    def __get_s3records(self, filepath: str):
        """
        解析SRecord文件，将每条S3即32位地址的数据记录以列表形式保存到一个列表中
        :param filepath: SRecord文件路径
        :return: 解析后的S3数据记录列表,每条记录以列表形式保存为
            [line_number:int, raw_file_line_number:int,
            record_type:str, data_length:str, start_address32:str, data:str]
        """
        describe_info = ''  # 保存S0中的描述信息
        pgm_start_addr = []  # 保存S7中程序起始地址信息
        s3records = []  # 保存解析后的S3数据记录
        line_number = 0  # 列表中的存储的数据记录的行号(0基)
        raw_file_line_number = 0  # 源文件中的数据记录的行号(1基)
        with open(file=filepath, mode='r', encoding='utf-8') as f:
            for line in f.readlines():
                raw_file_line_number += 1
                line = line.strip()  # 去除该行的换行符
                if line == '':
                    msg = f'Srecord文件第{raw_file_line_number}行内容为空'
                    raise SrecordException(msg)
                record_type = line[0:2]  # 获取type
                if record_type == self.srecord_type_dic['data_record_addr32']:
                    # 获取数据长度(byte)
                    data_length = int(line[2:4], 16) - 4 - 1
                    # 获取32位起始地址
                    start_address32 = hex(int(line[4:12], 16))
                    # 32位16进制完整显示(eg:0x00000001)
                    start_address32 = pad_hex(start_address32, 4)
                    # 获取数据
                    data = line[12:12 + data_length * 2]
                    s3record = S3Record(line_number=line_number,
                                        raw_file_line_number=raw_file_line_number,
                                        record_type=record_type,
                                        data_length=data_length,
                                        start_address32=start_address32,
                                        data=data)
                    s3records.append(s3record)
                    line_number += 1
                elif record_type == self.srecord_type_dic['record_head']:
                    # 获取数据长度(byte)
                    data_length = int(line[2:4], 16) - 2 - 1
                    # 获取数据
                    data = line[8:8 + data_length * 2]
                    describe_info = bytes.fromhex(data).decode(encoding='utf-8')
                elif record_type == self.srecord_type_dic['pgm_start_addr32']:
                    # 获取地址长度(byte)
                    addr_length = int(line[2:4], 16) - 1
                    # 获取地址
                    addr = line[4:4 + addr_length * 2]
                    pgm_start_addr = [i for i in bytes.fromhex(addr)]
                else:
                    msg = f'Srecord文件第{raw_file_line_number}行的"{record_type}"类型无法处理'
                    raise SrecordException(msg)
        # 判断S3数据记录区域在源文件中是否连续，不连续抛出异常
        for i in range(len(s3records) - 1):
            if int(s3records[i + 1].start_address32, 16) <= int(s3records[i].start_address32, 16):
                msg = f'Srecord文件中的S3数据记录在第{s3records[i].raw_file_line_number}行地址非单调递增'
                raise SrecordException(msg)
            if s3records[i + 1].raw_file_line_number - s3records[i].raw_file_line_number != 1:
                msg = f'Srecord文件中的S3数据记录在第{s3records[i].raw_file_line_number}行不连续'
                raise SrecordException(msg)
        # 返回
        return s3records, describe_info, pgm_start_addr

    @staticmethod
    def __get_erase_memory_records(records: List[S3Record]):
        """
        从S3数据记录列表中提取出所有擦写内存区域的首尾行信息
        :param records: S3数据记录列表
        :return: 擦写内存区域首尾行数据记录的列表
        """
        erase_memory_records = []
        erase_memory_record = EraseMemoryRecord(begin_record=records[0],
                                                end_record=None)
        for i in range(1, len(records)):
            if (
                    int(records[i].start_address32, 16) -
                    int(records[i - 1].start_address32, 16)
                    != records[i - 1].data_length
            ):
                erase_memory_record.end_record = records[i - 1]
                erase_memory_records.append(erase_memory_record)
                erase_memory_record = EraseMemoryRecord(begin_record=records[i],
                                                        end_record=None)
        erase_memory_record.end_record = records[-1]
        erase_memory_records.append(erase_memory_record)
        return erase_memory_records

    def __get_erase_memory_infos(self,
                                 records: List[S3Record],
                                 erase_memory_records: List[EraseMemoryRecord]):
        """
        从S3数据记录列表中提取出所有擦写内存区域的首尾行信息
        :param records: S3数据记录列表
        :param erase_memory_records: 包含擦写内存区域的首尾行记录的列表
        :return: 包含每个擦写内存区域信息的列表
        """

        def get_erase_data(records: List[S3Record], begin_line_number: int, end_line_number: int):
            """
            获取一块擦写内存区域的数据
            :param records: S3数据记录列表
            :param begin_line_number: 擦写区域的首行
            :param end_line_number: 擦写区域的尾行
            :return: 擦写区域的数据
            """
            erase_data = []
            for i in range(begin_line_number, end_line_number + 1):
                erase_data.append(records[i].data)
            return ''.join(erase_data)

        erase_memory_infos = []
        erase_num = 0
        for erase_memory_record in erase_memory_records:
            erase_num += 1
            erase_begin_address32 = erase_memory_record.begin_record.start_address32
            erase_end_address32 = erase_memory_record.end_record.start_address32
            # 若是擦写区域只有一行
            if int(erase_end_address32, 16) - int(erase_begin_address32, 16) == 0:
                erase_length = erase_memory_record.begin_record.data_length
            # 若是擦写区域有多行
            else:
                erase_length = int(erase_end_address32, 16) - int(erase_begin_address32, 16) + \
                               erase_memory_record.end_record.data_length
            erase_length = pad_hex(hex(erase_length), 4)
            erase_data = get_erase_data(records,
                                        erase_memory_record.begin_record.line_number,
                                        erase_memory_record.end_record.line_number)
            erase_memory_info = EraseMemoryInfo(erase_number=erase_num,
                                                erase_start_address32=erase_begin_address32,
                                                erase_length=erase_length,
                                                erase_data=erase_data,
                                                erase_memory_record=erase_memory_record)
            erase_memory_infos.append(erase_memory_info)
        # 返回
        return erase_memory_infos

    def __get_crc32_values(self):
        """
        计算所有擦写数据段的数据CRC32校验值
        :return: 返回一个包含4个字节的列表，表示CRC32校验值，例如：[252, 137, 25, 24]，即b'\xfc\x89\x19\x18'，0xFC891918
        """
        all_erase_datas = []
        for erase_memory_info in self.__erase_memory_infos:
            all_erase_datas.append(erase_memory_info.erase_data)
        hex_string = ''.join(all_erase_datas)
        ascii_values = bytes.fromhex(hex_string)
        obj_crc32 = Crc32(check_data=ascii_values,
                          poly=0x04C11DB7,
                          init_crc=0xFFFFFFFF,
                          ref_in=False,
                          ref_out=False,
                          xor_out=0xFFFFFFFF)
        return obj_crc32.crc32_bytes_arr

    @property
    def describe_info(self) -> str:
        return self.__describe_info

    @property
    def pgm_start_addr(self) -> List[int]:
        return self.__pgm_start_addr

    @property
    def s3records(self):
        return self.__s3_records

    @property
    def erase_memory_infos(self):
        return self.__erase_memory_infos

    @property
    def crc32_values(self):
        return self.__crc32_values


if __name__ == '__main__':
    pass
    # filepath = r'C:\Users\XCMGSC\Desktop\CCP程序刷写\0609\xjmain.mot'
    # srecord = Srecord(filepath)

    # for res in srecord.s3records:
    #     print(f'{res.line_number} {res.raw_file_line_number} {res.record_type}', end=" ")
    #     print(f'{res.data_length} {res.start_address32} {res.data}')

    # for res in srecord.erase_memory_infos:
    #     print(f'区域{res.erase_number}')
    #     print(f'  首行', end=' ')
    #     print(f'{res.erase_memory_record.begin_record.line_number}', end=' ')
    #     print(f'{res.erase_memory_record.begin_record.raw_file_line_number}', end=' ')
    #     print(f'{res.erase_memory_record.begin_record.record_type}', end=' ')
    #     print(f'{res.erase_memory_record.begin_record.data_length}', end=' ')
    #     print(f'{res.erase_memory_record.begin_record.start_address32}', end=' ')
    #     print(f'{res.erase_memory_record.begin_record.data}')
    #     print(f'  尾行', end=' ')
    #     print(f'{res.erase_memory_record.end_record.line_number}', end=' ')
    #     print(f'{res.erase_memory_record.end_record.raw_file_line_number}', end=' ')
    #     print(f'{res.erase_memory_record.end_record.record_type}', end=' ')
    #     print(f'{res.erase_memory_record.end_record.data_length}', end=' ')
    #     print(f'{res.erase_memory_record.end_record.start_address32}', end=' ')
    #     print(f'{res.erase_memory_record.end_record.data}')
    #     print(f'  擦除信息', end=' ')
    #     print(f'{res.erase_start_address32}', end=' ')
    #     print(f'{res.erase_length}', end=' ')
    #     print(f'{res.erase_data}')
