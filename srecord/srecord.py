#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : ZYD
# @version : V1.0.0
# @function:
"""
解析.mot/.s19/.srec格式的SRecord记录文件,
获取S0中的描述信息保存在属性describe_info:str，
获取S3数据记录保存在属性s3records:List[S3Record]，
获取S3记录的擦写内存区域信息保存在属性erase_memory_infos:List[EraseMemoryInfo]

SRecord格式
SRecord文件是由Motorola公司定义的一种ASCII文本文件，
文件扩展名包括：.s19、.s28、.s37、.s、.s1、.s2、.s3、.sx、.srec、.exo、.mot、.mxt，都是同一种格式，
文件内容没有差异，主要用于记录微控制器、EPROM和其他类型的可编程设备的程序记录。SRecord以一行文本作为一条记录（Record），每行记录的格式如下：

Record_start	Type	Byte_count	Address    Data    CheckSum

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
import os
import shutil
import time

from utils import pad_hex
from utils import Crc32Bzip2 as Crc32


##############################
# Type definitions
##############################

class SrecordException(Exception):
    """
    Srecord异常类

    :param message: 要显示的异常消息
    :type message: str
    """

    def __init__(self, message: str):
        """
        构造函数
        """
        self.message = message

    def __str__(self):
        return f"{self.message}"


class S3Record(object):
    """
    存储一条S3数据记录的信息

    :param line_number: 本条数据记录在当前S3Record列表中的序号(0基)
    :type line_number: int
    :param raw_file_line_number: 本条数据记录在源文件中的行号(1基)
    :type raw_file_line_number: int
    :param record_type: 本条数据记录类型(例如'S3')
    :type record_type: str
    :param data_length: 本条数据记录数据长度(单位Byte)
    :type data_length: int
    :param start_address32: 本条数据记录32位起始地址(0x开头16进制)
    :type start_address32: str
    :param data: 本条数据记录有效数据(16进制序列)
    :type data: str
    """

    def __init__(self,
                 line_number: int,
                 raw_file_line_number: int,
                 record_type: str,
                 data_length: int,
                 start_address32: str,
                 data: str
                 ) -> None:
        self.line_number = line_number  # 本条数据记录在列表中的行号(0基)
        self.raw_file_line_number = raw_file_line_number  # 本条数据记录在源文件中的行号(1基)
        self.record_type = record_type  # 本条数据记录类型(例如S3)
        self.data_length = data_length  # 本条数据记录数据长度(单位Byte)
        self.start_address32 = start_address32  # 本条数据记录32位起始地址(0x开头16进制)
        self.data = data  # 本条数据记录有效数据(16进制形式序列)


class EraseMemoryRecord(object):
    """
    存储一段擦写内存的首尾行记录

    :param begin_record: 擦写内存块的首行记录
    :type begin_record: S3Record
    :param end_record: 擦写内存块的尾行记录
    :type end_record: S3Record
    """

    def __init__(self,
                 begin_record: S3Record = None,
                 end_record: S3Record = None,
                 ) -> None:
        self.begin_record = begin_record  # 擦写内存块的首行记录
        self.end_record = end_record  # 擦写内存块的尾行记录


class EraseMemoryInfo(object):
    """
    一段擦写内存的信息

    :param erase_number: 擦写内存段的标号(第几段连续内存区域)
    :type erase_number: int
    :param erase_start_address32: 本段擦写内存的起始地址(0x开头16进制)
    :type erase_start_address32: str
    :param erase_length: 本段擦写内存的长度，单位Byte(0x开头16进制)
    :type erase_length: str
    :param erase_data: 本段擦写数据(16进制序列)
    :type erase_data: str
    :param erase_memory_record: 本段擦写内存的首尾行记录
    :type erase_memory_record: EraseMemoryRecord
    """

    def __init__(self,
                 erase_number: int,
                 erase_start_address32: str,
                 erase_length: str,
                 erase_data: str,
                 erase_memory_record: EraseMemoryRecord
                 ):
        """
        构造函数
        """
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
    解析SRecord文件，处理S3数据记录，获取内存擦写信息、校验信息等

    :param filepath: SRecord文件路径
    :type filepath: str
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

    def __init__(self, filepath: str) -> None:
        """
        构造函数
        """
        self.__filepath = filepath # 文件路径
        self.__check_all_sum(filepath)
        (self.__s3_records,
         self.__describe_info,
         self.__pgm_start_addr) = self.__get_s3records(filepath)
        self.__erase_memory_records = self.__get_erase_memory_records(self.__s3_records)
        self.__erase_memory_infos = self.__get_erase_memory_infos(self.__s3_records,
                                                                  self.__erase_memory_records)
        self.__crc32_values = self.__get_crc32_values()

        self.__cal_data: bytes = b'' # 标定区数据序列
        self.__cal_memory_info: EraseMemoryInfo = None # 标定区数据段信息

    @staticmethod
    def __checksum(record: str) -> str:
        """
        计算一条记录的校验和，
        长度、地址和数据参与checksum运算，类型、校验和不参与校验，
        运算公式为：校验和=0xff – (长度 + 地址 + 数据)

        :param record: 一条记录
        :type record: str
        :return: 本条记录的校验和(一个字节的16进制序列)
        :rtype: str
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

    def get_epk(self, addr: str) -> str | None:
        """
        获取epk

        :param addr: epk信息首地址(0x开头的16进制)
        :type addr: str
        :return: 若存在返回epk(16进制序列)，否则返回None
        :rtype: str or None
        """
        for erase_memory_info in self.__erase_memory_infos:
            if int(erase_memory_info.erase_start_address32, 16) == int(addr, 16):
                return erase_memory_info.erase_data

    def assign_cal_data(self, addr: int) -> bytes:
        """
        根据首地址指定pgm标定区，并返回其数据序列；
        指定标定区后方可使用get_raw_data_from_cal_data、flush_cal_data等

        :param addr: 标定区域首地址
        :type addr: int
        :returns: 标定区的数据序列
        :rtype: bytes
        :raises SrecordException: 不存在指定地址的标定数据区
        """
        for erase_memory_info in self.__erase_memory_infos:
            if int(erase_memory_info.erase_start_address32, 16) == addr:
                self.__cal_data = bytes.fromhex(erase_memory_info.erase_data)
                self.__cal_memory_info = erase_memory_info
                return self.__cal_data
        else:
            msg = f"在Srecord文件中不存在首地址为{hex(addr)}的标定数据区"
            raise SrecordException(msg)

    def get_raw_data_from_cal_data(self, offset: int, length: int) -> bytes:
        """
        从pgm标定区中获取指定地址和长度的原始值

        :param offset: 相对标定区首地址的偏移地址(0基)
        :type offset: int
        :param length: 长度
        :type length: int
        :returns: 原始值数据序列
        :rtype: bytes
        :raises SrecordException: 尚未指定标定数据区；参数超出指定标定数据区的范围
        """
        if self.__cal_data:
            if offset < len(self.__cal_data) and offset + length <= len(self.__cal_data):
                return self.__cal_data[offset:offset+length]
            else:
                msg = f"参数超出指定标定数据区的范围"
                raise SrecordException(msg)
        else:
            msg = f"在Srecord文件中尚未指定标定数据区"
            raise SrecordException(msg)

    def flush_cal_data(self, offset: int, data: bytes) -> None:
        """
        刷新标定数据

        :param offset: 相对标定区首地址的偏移地址(0基)
        :type offset: int
        :param data: 标定数据序列
        :type data: bytes
        """
        l = [i for i in self.__cal_data]  # bytes转列表
        l[offset:offset + len(data)] = [i for i in data]  # 修改数据
        self.__cal_data = bytes(l)  # 列表转bytes

    def creat_cal_file(self, filetype: str) -> str:
        """
        根据当前标定数据创建新的标定文件

        :param filetype: 创建的文件类型，'program':完整的程序文件；'calibrate':仅标定区文件
        :type filetype: str
        :returns: 新文件的路径
        :rtype: str
        :raises SrecordException: 类型尚未支持；标定数据区首地址不一致；标定区行数不一致
        """
        def _get_str_time() -> str:
            """
            获取当前时间，格式化字符串"%Y-%m-%d %H-%M-%S"

            :return: 当前时间
            :rtype: str
            """
            time_now = time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())  # 时间戳
            return str(time_now)

        def _get_new_filepath(old_filepath:str, filetype: str) -> str | None:
            """
            根据已有文件路径生成新的文件路径。
            其格式为在原文件名后加上时间戳("%Y-%m-%d %H-%M-%S")

            :param old_filepath: 原文件路径
            :type old_filepath: str
            :param filetype: 创建的文件类型，'program':完整的程序文件；'calibrate':仅标定区文件,带'_cal'后缀
            :type filetype: str
            :return: 新文件路径
            :rtype: str or None
            """
            if os.path.isfile(old_filepath):
                file_basename = os.path.basename(old_filepath)
                file_name, file_extension = os.path.splitext(file_basename)
                file_path = os.path.dirname(old_filepath)
                # 对于已经存在指定后缀格式的名称，则重新添加后缀，否则直接添加后缀
                pos = file_name.find('_pgm')
                if pos >= 0:
                    file_name = file_name[:pos]
                if filetype == 'calibrate':
                    return ''.join([file_path,'/',file_name,'_cal(',_get_str_time(),')',file_extension])
                else:
                    return ''.join([file_path, '/', file_name, '_pgm(', _get_str_time(), ')', file_extension])

        raw_lines = []
        new_lines = ''
        raw_file_line_number_start = self.__cal_memory_info.erase_memory_record.begin_record.raw_file_line_number
        raw_file_line_number_end = self.__cal_memory_info.erase_memory_record.end_record.raw_file_line_number
        with open(file=self.__filepath, mode='r', encoding='utf-8') as f:
            raw_lines = f.readlines()  # 读取所有行(0基)
            raw_line = raw_lines[raw_file_line_number_start - 1]
            raw_record_type = raw_line[0:2]  # 获取type
            if raw_record_type != self.srecord_type_dic['data_record_addr32']:
                msg = f"类型{raw_record_type}尚未支持"
                raise SrecordException(msg)
            if int(raw_line[4:12], 16) !=  int(self.__cal_memory_info.erase_start_address32, 16):
                msg = f"标定区首地址{self.__cal_memory_info.erase_start_address32}与Srecord文件标定区首地址'0x'{raw_line[4:12]}不一致"
                raise SrecordException(msg)
            raw_byte_count = raw_line[2:4] # Srecord行中的byte_count
            raw_checksum = 'FF' # Srecord行中的checksum
            addr_base = int(self.__cal_memory_info.erase_start_address32, 16) # Srecord文件标定区的基地址
            data_length = int(raw_byte_count, 16) - 4 - 1 # Srecord行中的数据的长度=byte_count-地址长度4-checksum1
            new_line_number = 1 # 行号(1基础)
            for i in range(0, len(self.__cal_data), data_length):
                raw_addr = int.to_bytes(i + addr_base,
                                        length=4,
                                        byteorder='big',
                                        signed=False).hex().upper()
                raw_data = self.__cal_data[i:i + data_length].hex().upper()
                if len(self.__cal_data[i:i + data_length]) == data_length:
                    bc = raw_byte_count
                elif len(self.__cal_data[i:i + data_length]) < data_length:
                    bc = int.to_bytes(len(self.__cal_data[i:i + data_length])+4+1,
                                      length=1,
                                      byteorder='big',
                                      signed=False).hex().upper()
                new_line = raw_record_type + bc + raw_addr + raw_data + raw_checksum
                new_line = new_line[:-2] + self.__checksum(new_line) + '\n'
                new_lines += new_line
                raw_lines[raw_file_line_number_start - 1 + new_line_number - 1] = new_line
                new_line_number += 1
            if new_line_number - 1 != raw_file_line_number_end - raw_file_line_number_start + 1:
                msg = f"标定区行数{new_line_number - 2}与Srecord文件标定区行数{raw_file_line_number_end -raw_file_line_number_start + 1}不一致"
                raise SrecordException(msg)
        # 保存到新文件
        new_filepath = _get_new_filepath(old_filepath=self.__filepath, filetype=filetype)  # 新文件路径
        with open(new_filepath, 'w', encoding='utf-8') as f:
            if filetype == 'calibrate':
                f.write(new_lines)
            else:
                f.write(''.join(raw_lines))
        # 返回文件路径
        return new_filepath

    def __check_all_sum(self, filepath: str) -> bool:
        """
        校验Srecord文件各行的checksum

        :return: 若校验通过返回True
        :rtype: bool
        :raises SrecordException: 某行校验错误
        """
        with open(file=filepath, mode='r', encoding='utf-8') as f:
            raw_file_line_number = 0
            for line in f.readlines():
                line = line.strip()  # 去除该行的换行符
                raw_file_line_number += 1
                if line != '' and self.__checksum(line) != line[-2:]:
                    f.close()
                    msg = f'Srecord文件在第{raw_file_line_number}行校验和错误，应为"{self.__checksum(line)}"，实际为"{line[-2:]}"'
                    raise SrecordException(msg)
        return True

    def __get_s3records(self, filepath: str) ->  tuple[list[S3Record], str, list[int]]:
        """
        解析SRecord文件，将每条S3即32位地址的数据记录以列表形式保存，获取S0信息以及S7程序起始地址

        :param filepath: SRecord文件路径
        :type filepath: str
        :return: 解析后的S3数据记录列表, S0中的描述信息, S7中的程序起始地址信息
        :rtype: tuple[list[S3Record], str, list[int]]
        :raises SrecordException: 某行内容为空；某行类型无法处理；某行地址不递增；某行不连续
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
    def __get_erase_memory_records(records: list[S3Record]) -> list[EraseMemoryRecord]:
        """
        从S3数据记录列表中提取出所有擦写内存区域的首尾行记录

        :param records: S3数据记录列表
        :type records: list[S3Record]
        :return: 擦写内存区域首尾行数据记录的列表
        :rtype: list[EraseMemoryRecord]
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

    @staticmethod
    def __get_erase_memory_infos(records: list[S3Record],
                                 erase_memory_records: list[EraseMemoryRecord]) -> list[EraseMemoryInfo]:
        """
        从S3数据记录列表中提取出所有擦写内存区域的首尾行信息

        :param records: S3数据记录列表
        :type records: list[S3Record]
        :param erase_memory_records: 包含擦写内存区域的首尾行记录的列表
        :type erase_memory_records: list[EraseMemoryRecord]
        :return: 包含每个擦写内存区域信息的列表
        :rtype: list[EraseMemoryInfo]
        """

        def get_erase_data(records: list[S3Record], begin_line_number: int, end_line_number: int) -> str:
            """
            获取一块擦写内存区域的数据

            :param records: S3数据记录列表
            :type records: list[S3Record]
            :param begin_line_number: 擦写区域的首行序号
            :type begin_line_number: int
            :param end_line_number: 擦写区域的尾行序号
            :type end_line_number: int
            :return: 擦写区域的数据(16进制序列)
            :rtype: str
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

    def __get_crc32_values(self) -> list[int]:
        """
        计算所有擦写数据段的数据CRC32校验值

        :return: 返回一个包含4个字节的列表，表示CRC32校验值，例如：[252, 137, 25, 24]，即b'\xfc\x89\x19\x18'，0xFC891918
        :rtype: list[int]
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
        """
        S0描述信息

        :return: S0描述信息
        :rtype: str
        """
        return self.__describe_info

    @property
    def pgm_start_addr(self) -> list[int]:
        """
        S7程序起始地址

        :return: S7程序起始地址
        :rtype: list[int]
        """
        return self.__pgm_start_addr

    @property
    def s3records(self) -> list[S3Record]:
        """
        S3记录

        :return: S3记录
        :rtype: list[S3Record]
        """
        return self.__s3_records

    @property
    def erase_memory_infos(self) -> list[EraseMemoryInfo]:
        """
        擦写内存信息

        :return: 擦写内存信息
        :rtype: list[EraseMemoryInfo]
        """
        return self.__erase_memory_infos

    @property
    def crc32_values(self) -> list[int]:
        """
        所有擦写内容的CRC32校验值

        :return: CRC32校验值
        :rtype: list[int]
        """
        return self.__crc32_values



if __name__ == '__main__':
    pass
    # filepath = r'C:\Users\XCMGSC\Desktop\pythonProject\eco_tool_suit_32\other\A2L_CCP_测量与标定\main.mot'
    # srecord = Srecord(filepath)
    #
    # for res in srecord.s3records:
    #     print(f'{res.line_number} {res.raw_file_line_number} {res.record_type}', end=" ")
    #     print(f'{res.data_length} {res.start_address32} {res.data}')
    #
    # for res in srecord.erase_memory_infos:
    #     print(f'\n区域{res.erase_number}')
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
        # print(f'{res.erase_data}')
