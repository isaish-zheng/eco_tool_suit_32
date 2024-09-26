#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : ZYD
# @version : V1.0.0
# @function: V1.0.0：根据pcan驱动封装操作优控vcu的ccp服务，
#   下载流程封装于download线程，测量流程封装于measure线程


##############################
# Module imports
##############################

import ctypes  # 用于调用dll
import os
import platform  # 用于判断当前系统
import sys
import threading  # 用于多线程
import time
import traceback  # 用于获取异常详细信息
from typing import Any, Union

from crccheck.crc import Crc16Modbus, Crc16Ibm3740

from app.measure.model import MonitorItem
from srecord import Srecord
from utils import pad_hex, get_c_char

from .pcandrive import pcanccp
from .seed2key import get_key_of_seed

##############################
# Auxiliary functions
##############################

IS_WINDOWS = platform.system() == 'Windows'  # 判断当前系统是否为Windows
USE_GETCH = True  # 是否使用getch函数来等待用户输入
IS_PRINT_EXEC_DETAIL = True  # 是否打印执行细节,一级
IS_PRINT_MSG_DETAIL = False  # 是否打印消息细节,二级
IS_PRINT_MAP_DETAIL = False  # 是否打印地址映射细节,三级


def wait_getch_and_clear() -> None:
    """
    等待用户输入并清屏
    """

    def get_input() -> None:
        """
        等待输入
        """
        sys.stdin.read(1)

    def clear_console() -> None:
        """
        清屏
        """
        if IS_WINDOWS:
            os.system("cls")
        else:
            os.system("clear")

    if USE_GETCH:
        print("Press <Enter> to continue...")
        get_input()
        clear_console()


def print_exec_detail(txt: str, *args, **kwargs) -> None:
    """
    打印任务执行细节，可将此函数定向到指定的函数，以自定义打印功能

    :param txt: 待打印内容
    :type txt: str
    :param args: 位置参数
    :param kwargs: 关键字参数
    """
    if IS_PRINT_EXEC_DETAIL:
        print(txt)


def print_msg_detail(txt: str, *args, **kwargs) -> None:
    """
    打印消息数据信息，可将此函数定向到指定的函数，以自定义打印功能

    :param txt: 待打印内容
    :type txt: str
    :param args: 位置参数
    :param kwargs: 关键字参数
    """
    if IS_PRINT_MSG_DETAIL:
        print(txt)


def print_map_detail(txt: str, *args, **kwargs) -> None:
    """
    打印地址映射信息，可将此函数定向到指定的函数，以自定义打印功能

    :param txt: 待打印内容
    :type txt: str
    :param args: 位置参数
    :param kwargs: 关键字参数
    """
    if IS_PRINT_MAP_DETAIL:
        print(txt)


##############################
# Type definitions
##############################

class EcoPccpException(Exception):
    """
    EcoPccp异常类

    :param message: 要显示的异常消息
    :type message: str
    """

    def __init__(self, message: str) -> None:
        """
        构造函数
        """
        self.message = message

    def __str__(self):
        return f"{self.message}"


class ExecResult(object):
    """
    每一个操作的执行结果类型

    :param is_success: 操作是否成功
    :type is_success: bool
    :param data: 操作返回的数据
    :type data: Any
    """

    def __init__(self, is_success: bool = None, data: Any = None):
        """
        构造函数
        """
        self.is_success = is_success
        self.data = data


##############################
# PCAN-CCP-ECO API function declarations
##############################

class EcoPccpFunc(object):
    """
    EcoPccpFunc类，用于实现Pcan设备通过CCP协议操作优控VCU的各项服务

    :param channel: Pcan设备通道
    :type channel: pcanccp.TPCANHandle
    :param baudrate: Pcan设备波特率
    :type baudrate: pcanccp.TPCANBaudrate
    :param ecu_addr: ecu站地址，Intel格式
    :type ecu_addr: int
    :param cro_can_id: 请求设备的CAN_ID
    :type cro_can_id: int
    :param dto_can_id: 响应设备的CAN_ID
    :type dto_can_id: int
    :param is_intel_format: 传输数据格式，True：Intel，False：Motorola
    :type is_intel_format: bool
    :param timeout: 等ECU响应请求的超时时间，单位：毫秒
    :type timeout: int
    """

    def __init__(
            self,
            channel: pcanccp.TPCANHandle,
            baudrate: pcanccp.TPCANBaudrate,
            ecu_addr: int,
            cro_can_id: int,
            dto_can_id: int,
            is_intel_format: bool,
            timeout: int) -> None:
        """
        构造函数
        """

        # self.transmission_error_number = 0
        # self.response_error_number = 0
        self.channel = channel
        self.baudrate = baudrate
        self.ecu_addr = pcanccp.c_uint16(ecu_addr)
        self.cro_can_id = pcanccp.c_uint32(cro_can_id)
        self.dto_can_id = pcanccp.c_uint32(dto_can_id)
        self.is_intel_format = pcanccp.c_bool(is_intel_format)
        self.timeout: pcanccp.c_uint16 = pcanccp.c_uint16(timeout)

        self.obj_pcan = pcanccp.PCANBasic()
        self.obj_pccp = pcanccp.PcanCCP()
        self.ccp_handle = pcanccp.TCCPHandle()

    def custom_cro(self,
                   data: Union[list[int], bytes, bytearray],
                   timeout: int,
                   is_must_response: bool) -> ExecResult:
        """
        自定义服务命令

        :param data: 待发送的命令帧
        :type data: Union[list[int], bytes, bytearray]
        :param timeout: 等待响应超时时间，单位：毫秒
        :type timeout: int
        :param is_must_response: 是否必须响应。True：若无响应则会抛出异常，False：若无响应不会抛出异常，返回全零报文数据
        :type is_must_response: bool
        :returns: 操作结果
        :rtype: ExecResult
        :raises EcoPccpException: 发送失败；接收超时
        """

        def __write(data: Union[list[int], bytes, bytearray]) -> int:
            """
            发送自定义服务消息

            :param data: 待发送消息数据，8个字节
            :type data: Union[list[int], bytes, bytearray]
            :returns: 发送状态码
            :rtype: int
            """
            if len(data) != 8:
                msg = f'发送数据不是8字节'
                raise EcoPccpException(msg)

            msgCanMessage = pcanccp.TPCANMsg()
            msgCanMessage.ID = self.cro_can_id
            msgCanMessage.LEN = len(data)
            msgCanMessage.MSGTYPE = pcanccp.PCAN_MESSAGE_STANDARD
            for i in range(len(data)):
                msgCanMessage.DATA[i] = data[i]
            status = self.obj_pcan.Write(self.channel, msgCanMessage)
            return status

        def __read(timeout: int,
                   is_must_response: bool) -> tuple[int, bytes]:
            """
            接收自定义服务消息

            :param timeout: 超出时间则抛出异常，毫秒
            :type timeout: int
            :param is_must_response: 是否必须响应
            :type is_must_response: bool
            :returns: 若在指定时间内接收到消息，则返回接收状态和消息数据
            :rtype: tuple[int, bytes]
            :raises EcoPccpException: 接收消息超时
            """
            status = pcanccp.PCAN_ERROR_QRCVEMPTY
            time_start = time.time()
            while status != pcanccp.PCAN_ERROR_OK:
                # time.sleep(0.002)
                status, msg, timestamp = self.obj_pcan.Read(self.channel)
                time_stop = time.time()
                # print(f'status={status}')
                if status == pcanccp.PCAN_ERROR_OK:
                    return status, bytes(msg.DATA)
                elif time_stop - time_start > timeout / 1000:
                    if is_must_response:
                        msg = f'接收自定义服务消息超时'
                        raise EcoPccpException(msg)
                    else:
                        return status, bytes([0, 0, 0, 0, 0, 0, 0, 0])

        status = __write(data)
        if status == pcanccp.PCAN_ERROR_OK:
            status, recv_msg = __read(timeout=timeout, is_must_response=is_must_response)
            # print(status, recv_msg)
            if recv_msg[0] == 0xFF and recv_msg[1] == pcanccp.PCAN_ERROR_OK:
                exec_result = ExecResult(is_success=True, data=recv_msg)
            else:
                exec_result = ExecResult(is_success=False, data=recv_msg)
            return exec_result
        else:
            status, text = self.obj_pcan.GetErrorText(status, 9)
            msg = f'发送自定义服务消息失败: {bytes.decode(text)}'
            raise EcoPccpException(msg)

    def initialize_device(self) -> ExecResult:
        """
        初始化设备

        :returns: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPccpException: 初始化设备失败
        """
        # 初始化
        status = self.obj_pccp.Initialize(self.channel, self.baudrate, 0, 0, 0)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'初始化设备:{text.decode()}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
        else:
            msg = f'初始化设备:{text.decode()}'
            print_exec_detail(msg)
            raise EcoPccpException(msg)

        return exec_result

    def uninitialize_device(self) -> ExecResult:
        """
        关闭设备

        :returns: 执行结果ExecResult
        :rtype: ExecResult
        """
        status = self.obj_pccp.Uninitialize(self.channel)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'关闭设备:{text.decode()}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
        else:
            msg = f'关闭设备:{text.decode()}'
            print_exec_detail(msg)
            raise EcoPccpException(msg)

        return exec_result

    def read_msg(self) -> ExecResult:
        """
        读取消息

        :returns: 执行结果ExecResult,ExecResult.data含消息中的数据
        :rtype: ExecResult
        """
        exec_result = None
        recv_msg = pcanccp.TCCPMsg()
        status = self.obj_pccp.ReadMsg(ccp_handle=self.ccp_handle,
                                       msg=recv_msg)
        # _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            data = [x for x in recv_msg.Data]
            exec_result = ExecResult(is_success=True, data=data)
        return exec_result

    def reset(self) -> None:
        """
        清空消息缓存
        """
        self.obj_pccp.Reset(ccp_handle=self.ccp_handle)

    def connect(self) -> ExecResult:
        """
        建立连接

        :returns: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPccpException: 建立连接失败
        """
        ccp_handle = pcanccp.TCCPHandle()

        slave_data = pcanccp.TCCPSlaveData()
        slave_data.EcuAddress = self.ecu_addr
        slave_data.IdCRO = self.cro_can_id
        slave_data.IdDTO = self.dto_can_id
        slave_data.IntelFormat = self.is_intel_format

        status = self.obj_pccp.Connect(channel=self.channel,
                                       slave_data=slave_data,
                                       ccp_handle=ccp_handle,
                                       timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'建立连接:{text.decode()},连接代号为:{pad_hex(hex(ccp_handle.value), 4)}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            self.ccp_handle = ccp_handle
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'建立连接:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def disconnect(self,
                   is_temporary: bool) -> ExecResult:
        """
        断开连接；
        断开分为两种模式，一种离线模式，一种扯断断开与ECU的通信，彻底断开通信时，ECU将会被自动初始化；
        暂时断开即离线模式不会终止与当前ECU的DAQ通信，也不会影响先前的各项设置。在该命令中的ECU地址采用Intel格式，低位在前。

        :param is_temporary: 是否为暂时离线模式
        :type is_temporary: bool
        :returns: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPccpException: 断开连接失败
        """
        status = self.obj_pccp.Disconnect(ccp_handle=self.ccp_handle,
                                          temporary=pcanccp.c_bool(is_temporary),
                                          timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'{is_temporary and "暂时断开" or "终止"}连接:{text.decode()}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'{is_temporary and "暂时断开" or "终止"}连接:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def get_ccp_version(self,
                        expected_main_version: int,
                        expected_release_version: int) -> ExecResult:
        """
        获取CCP协议版本号；
        该命令用于统一主、从设备所使用的CCP协议版本，该命令应在EXCHANGE_ID命令之前执行。

        :param expected_main_version: 期望的主版本号
        :type expected_main_version: int
        :param expected_release_version: 期望的次版本号
        :type expected_release_version: int
        :returns: 执行结果ExecResult，ExecResult.data含有版本号信息
        :rtype: ExecResult
        :raises EcoPccpException: 获取协议版本失败
        """
        main_version = pcanccp.c_ubyte(expected_main_version)
        release_version = pcanccp.c_ubyte(expected_release_version)

        status = self.obj_pccp.GetCcpVersion(ccp_handle=self.ccp_handle,
                                             main_buffer=main_version,
                                             release_buffer=release_version,
                                             timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            version = str(main_version.value) + "." + str(release_version.value)
            msg = f'获取版本号:{text.decode()},版本号: {version}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=version)
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'获取版本号:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def exchange_id(self) -> ExecResult:
        """
        交换站标识符,MCD（主设备）与ECU的通信需要ASAP2文件的支持，
        通过这个命令，自动化系统可以由DTO返回的ID标识符自动为ECU分配一ASAP文件

        :returns: 执行结果ExecResult，ExecResult.data含有ecu_data数据
        :rtype: ExecResult
        :raises EcoPccpException: 交换站标识符失败
        """
        ecu_data = pcanccp.TCCPExchangeData()
        master_data_length = 0
        master_data = pcanccp.create_string_buffer(master_data_length)

        status = self.obj_pccp.ExchangeId(ccp_handle=self.ccp_handle,
                                          ecu_data=ecu_data,
                                          master_data_buffer=master_data,
                                          master_data_length=pcanccp.c_uint32(master_data_length),
                                          timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'交换站标识符:{text.decode()}'
            print_exec_detail(msg)
            msg = (f'从设备ID标识符的长度: {hex(ecu_data.IdLength)}\n' +
                   f'\t\t  从设备ID数据类型: {hex(ecu_data.DataType)}\n' +
                   f'\t\t  资源可用状态: {hex(ecu_data.AvailabilityMask)}\n' +
                   f'\t\t  资源保护状态: {hex(ecu_data.ProtectionMask)}')
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=ecu_data)
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'交换站标识符:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def get_seed(self,
                 ask_resource: pcanccp.TCCPResourceMask) -> ExecResult:
        """
        申请密钥

        :param ask_resource: 要申请的资源
        :type ask_resource: pcanccp.TCCPResourceMask
        :returns: 执行结果ExecResult，ExecResult.data含有seed数据
        :rtype: ExecResult
        :raises EcoPccpException: 申请密钥失败
        """

        seed_buffer = pcanccp.c_void_p()
        current_status = pcanccp.c_bool()

        status = self.obj_pccp.GetSeed(ccp_handle=self.ccp_handle,
                                       resource=ask_resource,
                                       current_status=current_status,
                                       seed_buffer=seed_buffer,
                                       timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'申请密钥:{text.decode()},seed={pad_hex(hex(seed_buffer.value), 4)},'
            msg = msg + f'请求资源类型为{hex(ask_resource.value)},'
            msg = msg + f'保护状态为{current_status.value and "真" or "假"}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=seed_buffer.value)
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'申请密钥:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def unlock(self,
               key: Union[list[int], bytes, bytearray]) -> ExecResult:
        """
        解除保护

        :param key: 密钥数据
        :type key: list[int] or bytes or bytearray
        :returns: 执行结果ExecResult，ExecResult.data含有privileges数据(请求资源的授权状态)
        :rtype: ExecResult
        :raises EcoPccpException: 解除保护失败
        """
        if key:
            key_length = len(key)
            key_buffer = ctypes.create_string_buffer(key_length)
            for i in range(key_length):
                key_buffer[i] = get_c_char(ord(chr(key[i])))
        else:
            key_length = 0
            key_buffer = None

        privileges = pcanccp.c_ubyte()

        status = self.obj_pccp.Unlock(ccp_handle=self.ccp_handle,
                                      key_buffer=key_buffer,
                                      key_length=pcanccp.c_ubyte(key_length),
                                      privileges=privileges,
                                      timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'解除保护:{text.decode()},授权状态为{hex(privileges.value)}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=privileges.value)
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'解除保护:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def set_session_status(self,
                           expected_status: pcanccp.TCCPSessionStatus) -> ExecResult:
        """
        设置主从设备间的通信状态

        :param expected_status: 要设置的通信状态
            0x01: Calibration Status.
            0x02: Data acquisition Status.
            0x04: Request resuming.
            0x40: Request storing.
            0x80: Running status.
        :type expected_status: pcanccp.TCCPSessionStatus
        :returns: 执行成功，返回执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPccpException: 设置通信状态失败
        """

        status = self.obj_pccp.SetSessionStatus(ccp_handle=self.ccp_handle,
                                                status=expected_status,
                                                timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'设置通信状态为{hex(expected_status.value)}:{text.decode()}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'设置通信状态为{hex(expected_status.value)}:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def get_session_status(self) -> ExecResult:
        """
        获取主从设备间的通信状态

        :returns: 执行结果ExecResult，ExecResult.data中含有通信状态信息，
            0x01: Calibration Status.
            0x02: Data acquisition Status.
            0x04: Request resuming.
            0x40: Request storing.
            0x80: Running status.
        :rtype: ExecResult
        :raises EcoPccpException: 获取通信状态失败
        """

        session_status = pcanccp.TCCPSessionStatus()
        status = self.obj_pccp.GetSessionStatus(ccp_handle=self.ccp_handle,
                                                status=session_status,
                                                timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'获取通信状态:{text.decode()}，当前状态:{hex(session_status.value)}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=hex(session_status.value))
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'获取通信状态:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def set_mta(self,
                mta: int,
                addr_offset: int,
                addr_base: int) -> ExecResult:
        """
        设置内存操作的初始地址（32位基地址+地址偏移），后续对内存的读取操作都由该起始地址开始

        :param mta: mta序号(0或1)，DNLOAD、UPLOAD、DNLOAD_6、SELECT_CAL_PAGE、
            CLEAR_MEMORY、PROGRAM及PROGRAM_6命令使用MTA0，MOVE命令使用MTA1
        :type mta: int
        :param addr_offset: 地址偏移
        :type addr_offset: int
        :param addr_base: 基地址
        :type addr_base: int
        :returns: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPccpException: 设置内存操作地址失败
        """

        status = self.obj_pccp.SetMemoryTransferAddress(ccp_handle=self.ccp_handle,
                                                        used_mta=pcanccp.c_ubyte(mta),
                                                        addr_extension=pcanccp.c_ubyte(addr_offset),
                                                        addr=pcanccp.c_uint32(addr_base),
                                                        timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'设置内存操作地址为{pad_hex(hex(addr_base)), 4},偏移{pad_hex(hex(addr_offset)), 1}:{text.decode()}'
            print_msg_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'设置内存操作地址为{pad_hex(hex(addr_base)), 4},偏移{pad_hex(hex(addr_offset)), 1}:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def upload(self,
               size: int) -> ExecResult:
        """
        根据当前mta0地址，查询数据

        :param size: 要查询的数据的长度，单位：字节
        :type size: int
        :returns: 执行结果ExecResult，ExecResult.data含有data数据(bytes)
        :rtype: ExecResult
        :raises EcoPccpException: 查询数据失败
        """

        data_buffer = pcanccp.c_buffer(size)

        status = self.obj_pccp.Upload(ccp_handle=self.ccp_handle,
                                      size=pcanccp.c_ubyte(size),
                                      data_buffer=data_buffer,
                                      timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'查询数据:{text.decode()},data={data_buffer.value}'
            print_msg_detail(msg)
            exec_result = ExecResult(is_success=True, data=bytes(data_buffer))
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'查询数据:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def select_cal_page(self) -> ExecResult:
        """
        选择标定数据页；
        此命令取决于ecu内部实现。执行此命令后，先前设置的mta0地址将会自动指向该命令激活的标定页。

        :returns: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPccpException: 选择标定数据页失败
        """

        data_buffer = pcanccp.c_void_p()

        status = self.obj_pccp.SelectCalibrationDataPage(ccp_handle=self.ccp_handle,
                                                         timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'选择标定数据页:{text.decode()}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=data_buffer.value)
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'选择标定数据页:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def get_active_cal_page(self):
        """
        获取处于激活状态下的标定数据页的首地址

        :returns: 执行结果ExecResult，ExecResult.data含首地址信息
        :rtype: ExecResult
        :raises EcoPccpException: 获取激活标定数据页失败
        """

        mta0_ext = pcanccp.c_ubyte()
        mta0_addr = pcanccp.c_uint32()

        status = self.obj_pccp.GetActiveCalibrationPage(ccp_handle=self.ccp_handle,
                                                        mta0_ext=mta0_ext,
                                                        mta0_addr=mta0_addr,
                                                        timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            addr = int.to_bytes(mta0_addr.value, 4, 'big', signed=False)
            addr = int.from_bytes(addr, 'little', signed=False)
            first_addr = pad_hex(hex(addr + mta0_ext.value), 4)
            msg = f'获取激活标定数据页:{text.decode()},首地址为{first_addr}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=first_addr)
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'获取激活标定数据页:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def get_daq_list_size(self,
                          list_number: int,
                          dto_id: str):
        """
        获取某特定DAQ列表的大小，即其中ODT列表的个数，并清空当前DAQ列表内的数据，为下次通讯做准备
        如果GET_DAQ_SIZE命令中选定的DAQ列表不存在或者不可用，，从设备返回的ODT列表个数为0。

        :param list_number: daq列表号
        :type list_number: int
        :param dto_id: dto的can_id
        :type dto_id: str
        :returns: 执行结果ExecResult，
            ExecResult.data含(daq列表序号: int, daq列表的第一个pid号: str, daq列表大小: str,)
        :rtype: ExecResult
        :raises EcoPccpException: 获取daq列表大小失败
        """

        dto_id = int.to_bytes(int(dto_id, 16), 4, 'big', signed=False)
        dto_id = int.from_bytes(dto_id, 'little', signed=False)
        size = pcanccp.c_ubyte()
        first_pid = pcanccp.c_ubyte()
        status = self.obj_pccp.GetDAQListSize(ccp_handle=self.ccp_handle,
                                              list_number=pcanccp.c_ubyte(list_number),
                                              dto_id=pcanccp.c_uint32(dto_id),
                                              size=size,
                                              first_pid=first_pid,
                                              timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'获取daq列表大小:{text.decode()},daq列表数为{hex(size.value)}，首个pid为{hex(first_pid.value)}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True,
                                     data=(list_number, hex(first_pid.value), hex(size.value)))
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'获取daq列表大小:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def set_daq_list_ptr(self,
                         list_number: int,
                         odt_number: int,
                         element_number: int) -> ExecResult:
        """
        设置daq列表指针，在进行DAQ通讯前，必须将DAQ列表进行配置，将数据写入到相应的DAQ列表里的ODT元素中。
        SET_DAQ_PTR用来为写入DAQ列表数据设置入口地址指针。

        :param list_number: daq列表号
        :type list_number: int
        :param odt_number: odt列表号
        :type odt_number: int
        :param element_number: 当前odt列表中的元素号
        :type element_number: int
        :returns: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPccpException: 设置daq列表指针失败
        """

        size = pcanccp.c_ubyte()
        first_pid = pcanccp.c_ubyte()

        status = self.obj_pccp.SetDAQListPointer(ccp_handle=self.ccp_handle,
                                                 list_number=pcanccp.c_ubyte(list_number),
                                                 odt_number=pcanccp.c_ubyte(odt_number),
                                                 element_number=pcanccp.c_ubyte(element_number),
                                                 timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'设置daq列表指针:{text.decode()},列表序号{list_number},odt序号{odt_number},元素序号{element_number}'
            print_msg_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'设置daq列表指针:{text.decode()},列表序号{list_number},odt序号{odt_number},元素序号{element_number}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def write_daq_list_entry(self,
                             size_element: int,
                             addr_ext: int,
                             addr: str) -> ExecResult:
        """
        写入daq列表，在DAQ通信前，需要对DAQ列表进行配置，将需要上传的数据先写到DAQ列表所在的ODT列表中，
        先前由SET_DAQ_PTR命令所定义的地址即为该命令的数据写入地址，在此命令中，一次写入的数据被成为一个DAQ元素，
        其字节可分为1字节、2字节、4字节。

        :param size_element: 元素长度，单位：字节
        :type size_element: int
        :param addr_ext: 地址偏移量
        :type addr_ext: int
        :param addr: 地址
        :type addr: str
        :returns: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPccpException: 写入daq列表失败
        """

        addr_rev = int.to_bytes(int(addr, 16), 4, 'big', signed=False)
        addr_rev = int.from_bytes(addr_rev, 'little', signed=False)
        status = self.obj_pccp.WriteDAQListEntry(ccp_handle=self.ccp_handle,
                                                 size_element=pcanccp.c_ubyte(size_element),
                                                 addr_ext=pcanccp.c_ubyte(addr_ext),
                                                 addr=pcanccp.c_uint32(addr_rev),
                                                 timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'写入daq列表:{text.decode()},元素长度{size_element},元素地址{addr}'
            print_msg_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'写入daq列表:{text.decode()},元素长度{size_element},元素地址{addr}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def start_stop_data_transmission(self,
                                     mode: int,
                                     list_number: int,
                                     last_odt_number: int,
                                     event_channel: int,
                                     prescaler: str) -> ExecResult:
        """
        启动/停止DAQ数据传输，用于DAQ通信模式，其作用是开始或终止某个DAQ列表的数据上传。

        :param mode: 0: Stop, 1: Start, 2: prepare for synchronized data transmission
        :type mode: int
        :param list_number: DAQ list number to process.
        :type list_number: int
        :param last_odt_number: ODTs to be transmitted (from 0 to LastODTNumber).
        :type last_odt_number: int
        :param event_channel: Generic signal source for timing determination.
        :type event_channel: int
        :param prescaler: Transmission rate prescaler.
        :type prescaler: str
        :returns: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPccpException: mode参数错误；启动/停止DAQ数据传输错误
        """
        if mode == 0:
            type_transmission = '停止'
        elif mode == 1:
            type_transmission = '停止'
        elif mode == 2:
            type_transmission = '准备同步'
        else:
            raise EcoPccpException('mode参数错误')

        prescaler = int.to_bytes(int(prescaler, 16), 2, 'big', signed=False)
        prescaler = int.from_bytes(prescaler, 'little', signed=False)

        data = pcanccp.TCCPStartStopData()
        data.Mode = pcanccp.c_ubyte(mode)  # 0: Stop, 1: Start, 2: prepare for synchronized data transmission
        data.ListNumber = pcanccp.c_ubyte(list_number)  # DAQ list number to process.
        data.LastODTNumber = pcanccp.c_ubyte(last_odt_number)  # ODTs to be transmitted (from 0 to LastODTNumber).
        data.EventChannel = pcanccp.c_ubyte(event_channel)  # Generic signal source for timing determination.
        data.TransmissionRatePrescaler = pcanccp.c_uint16(prescaler)  # Transmission rate prescaler.

        status = self.obj_pccp.StartStopDataTransmission(ccp_handle=self.ccp_handle,
                                                         data=data,
                                                         timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):

            msg = f'{type_transmission}DAQ数据传输:{text.decode()}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'{type_transmission}DAQ数据传输:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def start_stop_sync_data_transmission(self,
                                          is_start: bool) -> ExecResult:
        """
        启动/停止同步数据传输。
        在start_stop_data_transmission命令中，如果模式值为0x02，则对DAQ列表进行标识，为同步数据传输做准备。

        :param is_start: true: Starts the configured DAQ lists. false: Stops all DAQ lists.
        :type is_start: bool
        :returns: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPccpException: 启动/停止同步数据传输错误
        """

        status = self.obj_pccp.StartStopSynchronizedDataTransmission(ccp_handle=self.ccp_handle,
                                                                     start_or_stop=pcanccp.c_bool(is_start),
                                                                     timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'{is_start and "启动" or "停止"}同步数据传输:{text.decode()}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'{is_start and "启动" or "停止"}同步数据传输:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def clear_memory(self,
                     memory_size: int) -> ExecResult:
        """
        擦除非易失性内存

        :param memory_size: 要擦除的内存长度，单位:字节
        :type memory_size: int
        :returns: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPccpException: 擦除内存错误
        """

        status = self.obj_pccp.ClearMemory(ccp_handle=self.ccp_handle,
                                           memory_size=pcanccp.c_uint32(memory_size),
                                           timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'擦除内存:{text.decode()}'
            print_msg_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'擦除内存:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def program(self,
                data: Union[list[int], bytes, bytearray]) -> ExecResult:
        """
        编程

        :param data: 要编程的数据
        :type data: list[int] or bytes or bytearray
        :returns: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPccpException: 编程错误
        """
        data_length = len(data)
        data_buffer = ctypes.create_string_buffer(data_length)
        if data:
            for i in range(data_length):
                data_buffer[i] = get_c_char(ord(chr(data[i])))

        mta0_ext = pcanccp.c_ubyte()
        mta0_addr = pcanccp.c_uint32()

        status = self.obj_pccp.Program(ccp_handle=self.ccp_handle,
                                       data_buffer=data_buffer,
                                       size=pcanccp.c_ubyte(data_length),
                                       mta0_ext=mta0_ext,
                                       mta0_addr=mta0_addr,
                                       timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            addr = int.to_bytes(mta0_addr.value, 4, 'big', signed=False)
            addr = int.from_bytes(addr, 'little', signed=False)
            msg = f'编程:{text.decode()},当前地址为{pad_hex(hex(addr + mta0_ext.value), 4)}'
            print_msg_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'编程:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def build_checksum(self,
                       block_size: int) -> ExecResult:
        """
        内存校验

        :param block_size: 要校验的内存区域长度，单位:字节
        :type block_size: int
        :returns: 执行结果ExecResult，ExecResult.data含有checksum_buffer数据
        :rtype: ExecResult
        :raises EcoPccpException: 内存校验错误
        """
        checksum_buffer = ctypes.c_void_p()
        checksum_size = pcanccp.c_ubyte()

        status = self.obj_pccp.BuildChecksum(ccp_handle=self.ccp_handle,
                                             block_size=pcanccp.c_uint32(block_size),
                                             checksum_buffer=checksum_buffer,
                                             checksum_size=checksum_size,
                                             timeout=self.timeout)
        _, text = self.obj_pccp.GetErrorText(status)
        if self.obj_pccp.StatusIsOk(status, pcanccp.TCCP_ERROR_ACKNOWLEDGE_OK):
            msg = f'内存校验:{text.decode()}'
            print_msg_detail(msg)
            exec_result = ExecResult(is_success=True, data=checksum_buffer.value)
            # self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'内存校验:{text.decode()}'
            print_exec_detail(msg)
            # self.__display_uds_msg(request, None, False)
            raise EcoPccpException(msg)

        return exec_result

    def erase_write_data(self,
                         obj_srecord: Srecord) -> float:
        """
        将Srecord文件的S3数据，擦除并写入Flash。
        擦写流程：
        对于每个连续擦写段执行擦除内存后，再执行编程每个连续数据段，
        编程结束后checksum各数据段，最后通过自定义服务消息(0x1D)定位程序起始地址启动程序

        :param obj_srecord: Srecord对象，对象中包含erase_memory_infos属性，此属性含有各连续擦写数据段的详细信息
        :type obj_srecord: Srecord
        :return: 返回执行时间，单位s
        :rtype: float
        :raises EcoPccpException: 擦写错误
        """

        # 开始时间戳
        time_start = time.time()

        if not obj_srecord:
            msg = f'->擦写:Srecord对象为空'
            raise EcoPccpException(msg)

        # 擦除各数据段
        msg = f'擦除:共需擦除{len(obj_srecord.erase_memory_infos)}个数据段'
        print_exec_detail(msg)
        for erase_memory_info in obj_srecord.erase_memory_infos:
            # if erase_memory_info.erase_number != obj_srecord.erase_memory_infos[-1].erase_number:
            #     continue
            msg = f'-> 擦除:擦除第{erase_memory_info.erase_number}个数据段,'
            msg = msg + f'地址为{erase_memory_info.erase_start_address32},'
            msg = msg + f'长度为{erase_memory_info.erase_length}'
            print_exec_detail(msg)
            # 设置内存操作地址
            addr = int.to_bytes(int(erase_memory_info.erase_start_address32, 16), 4, 'big', signed=False)
            addr = int.from_bytes(addr, 'little', signed=False)
            ecec_result = self.set_mta(mta=0,
                                       addr_offset=0,
                                       addr_base=addr)
            # 擦除内存
            erase_length = int.to_bytes(int(erase_memory_info.erase_length, 16), 4, 'big', signed=False)
            erase_length = int.from_bytes(erase_length, 'little', signed=False)
            ecec_result = self.clear_memory(memory_size=erase_length)

        # 编程各数据段
        msg = f'编程:共需编程{len(obj_srecord.erase_memory_infos)}个数据段'
        print_exec_detail(msg)
        for erase_memory_info in obj_srecord.erase_memory_infos:
            # if erase_memory_info.erase_number != obj_srecord.erase_memory_infos[-1].erase_number:
            #     continue
            msg = f'-> 编程:编程第{erase_memory_info.erase_number}个数据段,'
            msg = msg + f'地址为{erase_memory_info.erase_start_address32},'
            msg = msg + f'长度为{erase_memory_info.erase_length}'
            print_exec_detail(msg)
            # 设置内存操作地址
            addr = int.to_bytes(int(erase_memory_info.erase_start_address32, 16), 4, 'big', signed=False)
            addr = int.from_bytes(addr, 'little', signed=False)
            ecec_result = self.set_mta(mta=0,
                                       addr_offset=0,
                                       addr_base=addr)
            # 编程
            erase_data = bytes.fromhex(erase_memory_info.erase_data)
            for i in range(0, len(erase_data), 5):
                data = erase_data[i:i + 5]
                ecec_result = self.program(data=data)
        # 编程完所有数据段最后再发送数据全0的编程帧，否则最后一个数据段校验结果不正确
        ecec_result = self.program(data=[])
        # return

        # 校验各数据段
        msg = f'校验:共需校验{len(obj_srecord.erase_memory_infos)}个数据段'
        print_exec_detail(msg)
        for erase_memory_info in obj_srecord.erase_memory_infos:
            # if erase_memory_info.erase_number != obj_srecord.erase_memory_infos[-1].erase_number:
            #     continue
            msg = f'-> 校验:校验第{erase_memory_info.erase_number}个数据段,'
            msg = msg + f'地址为{erase_memory_info.erase_start_address32},'
            msg = msg + f'长度为{erase_memory_info.erase_length}'
            print_exec_detail(msg)
            # 设置内存操作地址
            addr = int.to_bytes(int(erase_memory_info.erase_start_address32, 16), 4, 'big', signed=False)
            addr = int.from_bytes(addr, 'little', signed=False)
            ecec_result = self.set_mta(mta=0,
                                       addr_offset=0,
                                       addr_base=addr)
            # 校验
            erase_length = int.to_bytes(int(erase_memory_info.erase_length, 16), 4, 'big', signed=False)
            erase_length = int.from_bytes(erase_length, 'little', signed=False)
            ecec_result = self.build_checksum(block_size=erase_length)
            # 比对校验结果
            erase_data = bytes.fromhex(erase_memory_info.erase_data)
            crc_local = Crc16Modbus.calchex(erase_data, byteorder='little')
            crc_local = ''.join(['0x', crc_local])  # 本地校验结果
            match_result = (int(crc_local, 16) == ecec_result.data) and '成功' or '失败'
            msg = f'--> 校验:校验第{erase_memory_info.erase_number}个数据段{match_result},'
            msg = msg + f'远程校验结果为{hex(ecec_result.data)},'
            msg = msg + f'本地校验结果为{crc_local}'
            print_exec_detail(msg)
            if int(crc_local, 16) != ecec_result.data:
                raise EcoPccpException(msg)

        # 程序执行起始地址
        msg = f'-> 启动程序:程序起始地址为{bytes(obj_srecord.pgm_start_addr)}'
        print_exec_detail(msg)
        data = [0x1d, 0xff, 0x01]
        data.extend(obj_srecord.pgm_start_addr)
        if len(data) < 8:
            data.extend([0 for _ in range(8 - len(data))])
        ecec_result = self.custom_cro(data, self.timeout.value, True)

        # 结束时间戳
        time_stop = time.time()
        return time_stop - time_start


##############################
# PCAN-CCP-ECO Download
##############################

class DownloadThread(threading.Thread):
    """
    刷写线程类

    :param request_can_id: 请求设备的CAN_ID(0x开头的16进制)
    :type request_can_id: str
    :param response_can_id: 响应设备的CAN_ID(0x开头的16进制)
    :type response_can_id: str
    :param ecu_addr: ecu站地址，Intel格式(0x开头的16进制)
    :type ecu_addr: str
    :param is_intel_format: 传输数据格式，True：Intel，False：Motorola
    :type is_intel_format: bool
    :param timeout: 等ECU响应请求的超时时间，单位：毫秒
    :type timeout: int
    :param device_channel: Pcan设备通道(0x开头的16进制)
    :type device_channel: str
    :param device_baudrate: Pcan设备波特率
    :type device_baudrate: str
    :param download_filepath: 程序记录文件路径
    :type download_filepath: str
    :param seed2key_filepath: 密钥文件路径
    :type seed2key_filepath: str
    :param obj_srecord: 程序记录文件对象
    :type obj_srecord: Srecord
    """

    def __init__(self,
                 request_can_id: str,
                 response_can_id: str,
                 ecu_addr: str,
                 is_intel_format: bool,
                 timeout: int,
                 device_channel: str,
                 device_baudrate: str,
                 download_filepath: str,
                 seed2key_filepath: str,
                 obj_srecord: Srecord) -> None:
        """
        构造函数
        """
        super().__init__()
        self.__request_can_id = request_can_id
        self.__response_can_id = response_can_id
        self.__ecu_addr = ecu_addr
        self.__is_intel_format = is_intel_format
        self.__timeout = timeout
        self.__device_channel = device_channel
        self.__device_baudrate = device_baudrate
        self.__download_filepath = download_filepath
        self.__seed2key_filepath = seed2key_filepath
        self.__obj_srecord = obj_srecord

        self.obj_pccp = self.__create_pccp_obj()
        self.__has_open_device = False
        self.__has_ecu_reset = False
        self.__ew_time = 0.0

    def __del__(self) -> None:
        """
        析构函数
        """
        try:
            if self.__has_ecu_reset:
                self.print_detail(f"\n\t<-下载完成->，用时{self.__ew_time:.2f}s", 'done')
            obj_pccp = self.obj_pccp
            if self.__has_open_device and obj_pccp.uninitialize_device().is_success:
                self.__has_open_device = False
        except Exception as e:
            pass

    @staticmethod
    def print_detail(txt: str, *args, **kwargs) -> None:
        """
        打印消息，可以定向到指定向函数，以自定义打印功能，例如向text_info控件写入信息

        :param txt: 待写入的信息
        :type txt: str
        :param args: 位置参数，第一个参数为文字颜色
                    None-灰色,'done'-绿色,'warning'-黄色,'error'-红色
        :param kwargs: 关键字参数
        """
        print(txt)

    def __deal_comm_para(self) -> tuple[pcanccp.c_ushort, pcanccp.c_ushort, int, int, int]:
        """
        处理通信参数

        :return: channel, baudrate, cro_can_id, dto_can_id, ecu_addr
        :rtype:  tuple[pcanccp.c_ushort, pcanccp.c_ushort, int, int, int]
        """

        cro_can_id = int(self.__request_can_id, 16)
        dto_can_id = int(self.__response_can_id, 16)
        ecu_addr = int(self.__ecu_addr, 16)
        channel = pcanccp.PCAN_USBBUS1
        baudrate = pcanccp.PCAN_BAUD_500K

        if self.__device_channel == '0x1':
            channel = pcanccp.PCAN_USBBUS1
        elif self.__device_channel == '0x2':
            channel = pcanccp.PCAN_USBBUS2
        if self.__device_baudrate == '50kbps':
            baudrate = pcanccp.PCAN_BAUD_50K
        elif self.__device_baudrate == '100kbps':
            baudrate = pcanccp.PCAN_BAUD_100K
        elif self.__device_baudrate == '125kbps':
            baudrate = pcanccp.PCAN_BAUD_125K
        elif self.__device_baudrate == '250kbps':
            baudrate = pcanccp.PCAN_BAUD_250K
        elif self.__device_baudrate == '500kbps':
            baudrate = pcanccp.PCAN_BAUD_500K
        elif self.__device_baudrate == '800kbps':
            baudrate = pcanccp.PCAN_BAUD_800K
        elif self.__device_baudrate == '1000kbps':
            baudrate = pcanccp.PCAN_BAUD_1M

        return channel, baudrate, cro_can_id, dto_can_id, ecu_addr

    def __create_pccp_obj(self) -> EcoPccpFunc:
        """
        创建flash对象

        :return: flash对象
        :rtype: EcoPccpFunc
        """
        try:
            # 参数配置
            channel, baudrate, cro_can_id, dto_can_id, ecu_addr = \
                self.__deal_comm_para()

            # 创建对象
            return EcoPccpFunc(channel=channel,
                               baudrate=baudrate,
                               ecu_addr=ecu_addr,
                               cro_can_id=cro_can_id,
                               dto_can_id=dto_can_id,
                               is_intel_format=self.__is_intel_format,
                               timeout=self.__timeout)
        except Exception as e:
            self.print_detail(f'发生异常 {e}', 'error')
            self.print_detail(f"{traceback.format_exc()}", 'error')

    def run(self) -> None:
        """
        程序刷写流程

        """
        try:
            msg = f"当前设备 -> 请求地址:{self.__request_can_id}, 响应地址:{self.__response_can_id}, ecu地址:{self.__ecu_addr}, " + \
                  f"设备通道:{self.__device_channel}, 波特率:{self.__device_baudrate}"
            self.print_detail(msg)
            if self.__download_filepath:
                msg = f"下载文件 -> {self.__download_filepath}"
                self.print_detail(msg)
            else:
                self.print_detail('未选择下载文件', 'warning')
                return
            if self.__seed2key_filepath:
                msg = f"秘钥文件 -> {self.__seed2key_filepath}"
                self.print_detail(msg)
            else:
                self.print_detail('未选择秘钥文件', 'warning')
                return

            # flash对象
            obj_pccp = self.obj_pccp
            self.print_detail('======启动下载流程======')
            self.print_detail('------设备初始化------')
            if obj_pccp.initialize_device().is_success:
                self.__has_open_device = True
                self.print_detail(f"设备初始化成功", 'done')
            else:
                self.print_detail(f"设备初始化失败", 'error')

            # 刷写流程
            # 建立连接
            # 此处连接用于开机-关机-开机持续发出连接命令
            self.print_detail('------建立连接------')
            conn_start_time = time.time()
            while True:
                addr = int.to_bytes(int(self.__ecu_addr, 16), 2, 'big', signed=False)
                # addr = int.from_bytes(addr, 'little', signed=False)
                status = obj_pccp.custom_cro([0x01, 0x01, addr[1], addr[0], 0x00, 0x00, 0x00, 0x00],
                                             100,
                                             False)
                conn_stop_time = time.time()
                if conn_stop_time - conn_start_time > self.__timeout / 1000:
                    msg = f'建立连接超时'
                    self.print_detail(msg, 'error')
                    return
                if status.is_success:
                    break
            # 此处连接用于获取连接对象代号，否则其它服务将不能使用
            obj_pccp.connect()
            # 交换站标识符
            self.print_detail('------交换站标识符------')
            obj_pccp.exchange_id()
            # 申请seed
            self.print_detail('------申请seed------')
            exec_result = obj_pccp.get_seed(pcanccp.TCCP_RSM_MEMORY_PROGRAMMING)
            if exec_result.is_success and exec_result.data:
                seed_data = int.to_bytes(exec_result.data, 4, 'little', signed=False)
                self.print_detail(f'已获取Seed：{[hex(v) for v in seed_data]}', 'done')
            else:
                self.print_detail(f'获取Seed失败', 'error')
                return
            self.print_detail(f'根据Seed2Key文件{self.__seed2key_filepath}计算Key中')
            key_data = get_key_of_seed(seed2key_filepath=self.__seed2key_filepath, seed_data=seed_data)
            self.print_detail(f'已生成Key：{[hex(v) for v in key_data]}', 'done')
            # 发送key
            self.print_detail('------发送key------')
            obj_pccp.unlock(key_data)
            # 擦写数据
            self.print_detail('------擦写数据------')
            self.__ew_time = obj_pccp.erase_write_data(self.__obj_srecord)
            # 程序已启动
            if self.__ew_time:
                self.__has_ecu_reset = True
        except Exception as e:
            self.print_detail(f'发生异常 {e}', 'error')
            self.print_detail(f"{traceback.format_exc()}", 'error')
            # msg = f"下载失败"
            # raise EcoPudsFlashException(msg) from e
        finally:
            # self.__del__()
            pass


##############################
# PCAN-CCP-ECO Measure
##############################

class Measure(object):
    """
    测量连接类

    :param request_can_id: 请求设备的CAN_ID(0x开头的16进制)
    :type request_can_id: str
    :param response_can_id: 响应设备的CAN_ID(0x开头的16进制)
    :type response_can_id: str
    :param ecu_addr: ecu站地址，Intel格式(0x开头的16进制)
    :type ecu_addr: str
    :param is_intel_format: 传输数据格式，True：Intel，False：Motorola
    :type is_intel_format: bool
    :param timeout: 等ECU响应请求的超时时间，单位：毫秒
    :type timeout: int
    :param device_channel: Pcan设备通道
    :type device_channel: str
    :param device_baudrate: Pcan设备波特率
    :type device_baudrate: str
    :param pgm_filepath: 密钥文件路径
    :type pgm_filepath: str
    :param a2l_filepath: a2l文件路径
    :type a2l_filepath: str
    :param obj_srecord: 程序记录文件对象
    :type obj_srecord: Srecord
    """

    def __init__(self,
                 request_can_id: str,
                 response_can_id: str,
                 ecu_addr: str,
                 is_intel_format: bool,
                 timeout: int,
                 device_channel: str,
                 device_baudrate: str,
                 pgm_filepath: str,
                 a2l_filepath: str,
                 obj_srecord: Srecord):
        """
        构造函数
        """
        self.__request_can_id = request_can_id
        self.__response_can_id = response_can_id
        self.__ecu_addr = ecu_addr
        self.__is_intel_format = is_intel_format
        self.__timeout = timeout
        self.__device_channel = device_channel
        self.__device_baudrate = device_baudrate
        self.__a2l_filepath = a2l_filepath
        self.__pgm_filepath = pgm_filepath
        self.__obj_srecord = obj_srecord

        self.obj_pccp = self.__create_eco_pccp_obj()
        self.has_open_device = False
        self.has_connected = False
        self.has_measured = False
        self.__has_ecu_reset = False
        self.__ew_time = 0.0

    def __del__(self):
        """析构函数"""
        try:
            self.disconnect()
        except Exception as e:
            # 输出异常信息
            self.print_detail(f'发生异常 {e}', 'error')
            self.print_detail(f"{traceback.format_exc()}", 'error')

    @staticmethod
    def print_detail(txt: str, *args, **kwargs) -> None:
        """
        打印消息，可以定向到指定向函数，以自定义打印功能，例如向text_info控件写入信息

        :param txt: 待写入的信息
        :type txt: str
        :param args: 位置参数，第一个参数为文字颜色
                    None-灰色,'done'-绿色,'warning'-黄色,'error'-红色
        :param kwargs: 关键字参数
        """
        print(txt)

    def connect(self, epk_addr: str, epk_len: int) -> str | None:
        """
        连接流程

        :param epk_addr: 参数epk信息的首地址(0x开头的16进制)
        :type epk_addr: str
        :param epk_len: 参数epk信息的长度(字节数)
        :type epk_len: int
        :returns: 若执行成功，返回epk字符串；否则返回None
        :rtype: str or None
        """

        def _get_epk_from_ecu() -> str:
            """
            从ecu获取epk

            :returns: epk字符串
            :rtype: str
            """
            epk = []
            self.print_detail('------从ecu获取epk------')
            # 设置内存操作地址
            addr = int.to_bytes(int(epk_addr, 16), 4, 'big', signed=False)
            addr = int.from_bytes(addr, 'little', signed=False)
            obj_pccp.set_mta(mta=0,
                             addr_offset=0,
                             addr_base=addr)
            upd_sum = epk_len
            while True:
                if upd_sum >= 0x5:
                    exec_result = obj_pccp.upload(size=0x5)
                    epk.append(exec_result.data)
                    upd_sum -= 0x5
                else:
                    exec_result = obj_pccp.upload(size=upd_sum)
                    epk.append(exec_result.data)
                    break
            return b''.join(epk).decode('utf-8').rstrip('\x00')

        def _check_ecu_ram_cal(check_addr: int, check_length: int) -> tuple[str, str]:
            """
            校验ecu ram中的标定区，分成两块校验

            :param check_addr: 校验区域首地址
            :type check_addr: int
            :param check_length: 每块区域校验长度
            :type check_length: int
            :returns: 校验结果，(区域1校验值，区域2校验值)
            :rtype: tuple[str, str]
            """
            # 校验区域1
            addr = int.to_bytes(check_addr, 4, 'big', signed=False)
            addr = int.from_bytes(addr, 'little', signed=False)
            obj_pccp.set_mta(mta=0,
                             addr_offset=0,
                             addr_base=addr)
            size = int.to_bytes(check_length, 4, 'big', signed=False)
            size = int.from_bytes(size, 'little', signed=False)
            exec_result_1 = obj_pccp.build_checksum(block_size=size)
            self.print_detail(f"ecu_cal_1校验值为{hex(exec_result_1.data)}")
            # 校验区域2
            addr = int.to_bytes(check_addr + check_length, 4, 'big', signed=False)
            addr = int.from_bytes(addr, 'little', signed=False)
            obj_pccp.set_mta(mta=0,
                             addr_offset=0,
                             addr_base=addr)
            size = int.to_bytes(check_length, 4, 'big', signed=False)
            size = int.from_bytes(size, 'little', signed=False)
            exec_result_2 = obj_pccp.build_checksum(block_size=size)
            self.print_detail(f"ecu_cal_2校验值为{hex(exec_result_2.data)}")
            return hex(exec_result_1.data), hex(exec_result_2.data)

        def _check_pgm_cal(pgm: Srecord, check_addr: int, check_length: int) -> tuple[str, str]:
            """
            校验pgm中的标定区，分成两块校验

            :param pgm: Srecord程序对象
            :type pgm: Srecord
            :param check_addr: 校验区域首地址
            :type check_addr: int
            :param check_length: 每块区域校验长度
            :type check_length: int
            :returns: 校验结果，(区域1校验值，区域2校验值)
            :rtype: tuple[str, str]
            """
            erase_memory_info = None
            for erase_memory_info in pgm.erase_memory_infos:
                if int(erase_memory_info.erase_start_address32, 16) == check_addr:
                    break
            if erase_memory_info:
                msg = (f"在pgm中已找到地址为{erase_memory_info.erase_start_address32}的标定数据区,"
                       f"已用长度为{erase_memory_info.erase_length}")
                self.print_detail(msg)
                cal_data = bytes.fromhex(erase_memory_info.erase_data)
                # pgm标定区域小于等于校验长度
                if len(cal_data) <= check_length:
                    # 校验区域1
                    cal_data_1 = cal_data + b'\xff' * (check_length - len(cal_data))
                    cal_value_1 = Crc16Ibm3740.calchex(cal_data_1, byteorder='little')
                    # 校验区域2
                    cal_data_2 = b'\xff' * check_length
                    cal_value_2 = Crc16Ibm3740.calchex(cal_data_2, byteorder='little')
                # pgm标定区域不大于校验长度
                else:
                    # 校验区域1
                    cal_data_1 = cal_data[0:check_length]
                    cal_value_1 = Crc16Ibm3740.calchex(cal_data_1, byteorder='little')

                    # 校验区域2
                    cal_data_2 = cal_data[check_length:]
                    cal_data_2 += b'\xff' * (check_length - len(cal_data_2))
                    cal_value_2 = Crc16Ibm3740.calchex(cal_data_2, byteorder='little')
                value1 = '0x' + cal_value_1
                value2 = '0x' + cal_value_2
                self.print_detail(f"pgm_cal_1校验值为{value1}")
                self.print_detail(f"pgm_cal_1校验值为{value2}")
                return value1, value2
            else:
                msg = f"在pgm文件中未找到地址为{check_addr}的标定区域"
                self.print_detail(msg)
                raise EcoPccpException(msg)

        try:
            # 若已连接，则返回
            if self.has_connected:
                return

            msg = f"当前设备 -> 请求地址:{self.__request_can_id}, 响应地址:{self.__response_can_id}, ecu地址:{self.__ecu_addr}, " + \
                  f"设备通道:{self.__device_channel}, 波特率:{self.__device_baudrate}"
            self.print_detail(msg)
            if self.__pgm_filepath:
                msg = f"程序文件 -> {self.__pgm_filepath}"
                self.print_detail(msg)
            else:
                self.print_detail('未选择程序文件', 'warning')
                return
            if self.__a2l_filepath:
                msg = f"a2l文件 -> {self.__a2l_filepath}"
                self.print_detail(msg)
            else:
                self.print_detail('未选择a2l文件', 'warning')
                return

            # 获取measure对象
            obj_pccp = self.obj_pccp
            self.print_detail('------设备初始化------')
            if obj_pccp.initialize_device().is_success:
                self.has_open_device = True
                self.print_detail(f"设备初始化成功", 'done')
            else:
                self.print_detail(f"设备初始化失败", 'error')

            # 连接流程
            # 建立连接
            # 此处连接用于持续发出连接命令
            self.print_detail('------连接ecu------')
            conn_start_time = time.time()
            while True:
                addr = int.to_bytes(int(self.__ecu_addr, 16), 2, 'big', signed=False)
                # addr = int.from_bytes(addr, 'little', signed=False)
                status = obj_pccp.custom_cro([0x01, 0x01, addr[1], addr[0], 0x00, 0x00, 0x00, 0x00],
                                             100,
                                             False)
                conn_stop_time = time.time()
                if conn_stop_time - conn_start_time > self.__timeout / 1000:
                    msg = f'连接超时'
                    self.print_detail(msg, 'error')
                    # 复位设备
                    if self.has_open_device and obj_pccp.uninitialize_device().is_success:
                        self.has_open_device = False
                    return
                if status.is_success:
                    break
            # 此处连接用于获取连接对象代号，否则其它服务将不能使用
            obj_pccp.connect()
            # 获取ccp协议版本
            self.print_detail('------获取ccp协议版本------')
            obj_pccp.get_ccp_version(expected_main_version=2,
                                     expected_release_version=1)
            # 交换站标识符
            self.print_detail('------交换站标识符------')
            obj_pccp.exchange_id()
            # # 获取当前通信状态
            self.print_detail('------获取当前通信状态------')
            obj_pccp.get_session_status()
            # 获取激活的标定页
            self.print_detail('------获取激活的标定页------')
            obj_pccp.get_active_cal_page()

            # 获取ecu的epk
            ecu_epk = _get_epk_from_ecu()
            self.print_detail(f'ecu_epk为{ecu_epk}')
            # 获取激活的标定页
            self.print_detail('------获取激活的标定页------')
            ecec_result = obj_pccp.get_active_cal_page()
            cal_page_addr = int(ecec_result.data, 16)  # 激活的标定数据页首地址
            # 选择标定页
            self.print_detail('------选择标定页------')
            addr = int.to_bytes(cal_page_addr, 4, 'big', signed=False)
            addr = int.from_bytes(addr, 'little', signed=False)
            obj_pccp.set_mta(mta=0,
                             addr_offset=0,
                             addr_base=addr)
            obj_pccp.select_cal_page()

            # 校验ecu ram中的标定数据区
            self.print_detail('------校验标定数据区------')
            cal_page_checksum_length = 0x4000  # 标定区校验长度
            ecu_cal_1, ecu_cal_2 = _check_ecu_ram_cal(cal_page_addr, cal_page_checksum_length)

            # 校验pgm中的标定数据区
            pgm_cal_1, pgm_cal_2 = _check_pgm_cal(self.__obj_srecord, 0x00fd0000, cal_page_checksum_length)

            # 比对校验结果
            if ecu_cal_1 == pgm_cal_1 and ecu_cal_2 == pgm_cal_2:
                self.print_detail('ecu标定数据区与pgm标定数据区一致', 'done')
            else:
                self.print_detail('ecu标定数据区与pgm标定数据区不一致', 'error')
            self.has_connected = True  # 置位连接标识
            # 返回epk
            return ecu_epk
        except Exception as e:
            # 输出异常信息
            self.print_detail(f'发生异常 {e}', 'error')
            self.print_detail(f"{traceback.format_exc()}", 'error')
            # 复位设备
            if self.has_open_device and self.obj_pccp.uninitialize_device().is_success:
                self.has_open_device = False
        finally:
            pass
            # if self.has_open_device and self.obj_pccp.uninitialize_device().is_success:
            #     self.has_open_device = False

    def disconnect(self) -> None:
        """
        断开连接流程

        """
        try:
            # 若未打开设备或未连接，则返回
            if not self.has_open_device or not self.has_connected:
                return

            if self.has_measured:
                # 终止同步数据传输
                self.print_detail('------停止同步数据传输------')
                self.obj_pccp.start_stop_sync_data_transmission(is_start=False)

            # 断开连接
            self.print_detail('------断开连接------')
            self.obj_pccp.disconnect(is_temporary=True)
            self.has_connected = False  # 复位连接标识
            self.has_measured = False  # 复位测量标识
            # 关闭设备
            if self.has_open_device and self.obj_pccp.uninitialize_device().is_success:
                self.has_open_device = False
        except Exception as e:
            # 输出异常信息
            self.print_detail(f'发生异常 {e}', 'error')
            self.print_detail(f"{traceback.format_exc()}", 'error')
            # 关闭设备
            if self.has_open_device and self.obj_pccp.uninitialize_device().is_success:
                self.has_open_device = False

    def get_daq_cfg(self, daq_number: int) -> list[int, str, str] | None:
        """
        获取daq列表配置

        :param daq_number: daq列表序号
        :type daq_number: int
        :return: daq_cfg，daq列表配置 (daq列表序号: int, daq列表的第一个pid号: str, daq列表大小: str)
        :rtype: list[int, str, str] or None
        """
        try:
            # 若未连接，则返回
            if not self.has_connected:
                return

            # 获取measure对象
            obj_pccp = self.obj_pccp
            self.print_detail(f'------获取daq列表{daq_number}配置------')
            # 设置当前通信状态
            obj_pccp.set_session_status(expected_status=pcanccp.TCCPSessionStatus(0x0))

            # 获取daq列表大小
            ecec_result = obj_pccp.get_daq_list_size(list_number=daq_number,
                                                     dto_id=self.__response_can_id)
            return ecec_result.data
        except Exception as e:
            # 输出异常信息
            self.print_detail(f'发生异常 {e}', 'error')
            self.print_detail(f"{traceback.format_exc()}", 'error')

    def start_measure(self, daqs: dict[int, dict[int, list[MonitorItem]]]) -> None:
        """
        启动测量流程

        :param daqs: daq列表
        :type daqs: dict[int, dict[int, list[MonitorItem]]]
        """
        try:
            # 若未连接，则返回
            if not self.has_connected:
                return

            # 获取measure对象
            obj_pccp = self.obj_pccp
            self.print_detail('------设置daq列表启动测量监视流程------')
            # 设置daq列表指针
            for daq_number, odts in daqs.items():
                for odt_number, odt in odts.items():
                    for element_number in range(len(odt)):
                        item = odt[element_number]  # 获取监视数据项

                        # msg = (f"设置daq列表->daq:{item.daq_number},odt:{item.odt_number},element:{item.element_number}"
                        #        f"name:{item.name},size:{item.element_size},addr{item.element_addr}")
                        # self.print_detail(msg)

                        # self.print_detail('------设置daq列表指针------')
                        obj_pccp.set_daq_list_ptr(list_number=item.daq_number,
                                                  odt_number=item.odt_number,
                                                  element_number=item.element_number)
                        # self.print_detail('------写入daq列表------')
                        obj_pccp.write_daq_list_entry(size_element=item.element_size,
                                                      addr_ext=0,
                                                      addr=item.element_addr)

            # 设置当前通信状态
            self.print_detail('设置当前通信状态')
            obj_pccp.set_session_status(expected_status=pcanccp.TCCPSessionStatus(0x02))

            for daq_number, odts in daqs.items():
                if daq_number == 1:
                    # 开始数据传输
                    self.print_detail(f'开始daq{daq_number}数据传输')
                    last_odt_number = len(odts) - 1
                    obj_pccp.start_stop_data_transmission(mode=2,
                                                          list_number=daq_number,
                                                          last_odt_number=last_odt_number,
                                                          event_channel=daq_number,
                                                          prescaler='0x01')
                elif daq_number == 2:
                    # 开始数据传输
                    self.print_detail(f'开始daq{daq_number}数据传输')
                    last_odt_number = len(odts) - 1
                    obj_pccp.start_stop_data_transmission(mode=2,
                                                          list_number=daq_number,
                                                          last_odt_number=last_odt_number,
                                                          event_channel=daq_number,
                                                          prescaler='0x01')
            # 开始同步数据传输
            self.print_detail('------启动同步数据传输------')
            obj_pccp.start_stop_sync_data_transmission(is_start=True)

            self.has_measured = True  # 置位测量标识
        except Exception as e:
            # 输出异常信息
            self.print_detail(f'发生异常 {e}', 'error')
            self.print_detail(f"{traceback.format_exc()}", 'error')

    def stop_measure(self) -> None:
        """
        停止测量流程

        """
        try:
            # 若未连接或已停止测量，则返回
            if not self.has_connected or not self.has_measured:
                return
            # 终止同步数据传输
            self.print_detail('------停止同步数据传输------')
            self.obj_pccp.start_stop_sync_data_transmission(is_start=False)

            self.has_measured = False  # 复位测量标识
        except Exception as e:
            # 输出异常信息
            self.print_detail(f'发生异常 {e}', 'error')
            self.print_detail(f"{traceback.format_exc()}", 'error')

    def read_dto_msg(self) -> list[int] | None:
        """
        读取pid数据

        :return: 若执行成功，返回pid数据；否则返回None
        :rtype: list[int] or None
        """
        # 若已启动测量，则读取消息
        if self.has_measured:
            exec_result = self.obj_pccp.read_msg()
            if exec_result and exec_result.is_success:
                return exec_result.data

    def clear_recv_queue(self) -> None:
        """
        清空消息接收缓冲区

        """
        # 若已连接，则清空
        if self.has_connected:
            self.obj_pccp.reset()

    def __deal_comm_para(self) -> tuple[pcanccp.c_ushort, pcanccp.c_ushort, int, int, int]:
        """
        处理通信参数

        :return: channel, baudrate, cro_can_id, dto_can_id, ecu_addr
        :rtype: tuple[pcanccp.c_ushort, pcanccp.c_ushort, int, int, int]
        """

        cro_can_id = int(self.__request_can_id, 16)
        dto_can_id = int(self.__response_can_id, 16)
        ecu_addr = int(self.__ecu_addr, 16)
        channel = pcanccp.PCAN_USBBUS1
        baudrate = pcanccp.PCAN_BAUD_500K

        if self.__device_channel == '0x1':
            channel = pcanccp.PCAN_USBBUS1
        elif self.__device_channel == '0x2':
            channel = pcanccp.PCAN_USBBUS2
        if self.__device_baudrate == '50kbps':
            baudrate = pcanccp.PCAN_BAUD_50K
        elif self.__device_baudrate == '100kbps':
            baudrate = pcanccp.PCAN_BAUD_100K
        elif self.__device_baudrate == '125kbps':
            baudrate = pcanccp.PCAN_BAUD_125K
        elif self.__device_baudrate == '250kbps':
            baudrate = pcanccp.PCAN_BAUD_250K
        elif self.__device_baudrate == '500kbps':
            baudrate = pcanccp.PCAN_BAUD_500K
        elif self.__device_baudrate == '800kbps':
            baudrate = pcanccp.PCAN_BAUD_800K
        elif self.__device_baudrate == '1000kbps':
            baudrate = pcanccp.PCAN_BAUD_1M

        return channel, baudrate, cro_can_id, dto_can_id, ecu_addr

    def __create_eco_pccp_obj(self) -> EcoPccpFunc:
        """
        创建measure对象

        :return: measure对象
        :rtype: EcoPccpFunc
        """
        try:
            # 参数配置
            channel, baudrate, cro_can_id, dto_can_id, ecu_addr = \
                self.__deal_comm_para()

            # 创建对象
            return EcoPccpFunc(channel=channel,
                               baudrate=baudrate,
                               ecu_addr=ecu_addr,
                               cro_can_id=cro_can_id,
                               dto_can_id=dto_can_id,
                               is_intel_format=self.__is_intel_format,
                               timeout=self.__timeout)
        except Exception as e:
            self.print_detail(f'发生异常 {e}', 'error')
            self.print_detail(f"{traceback.format_exc()}", 'error')


if __name__ == '__main__':
    pass
