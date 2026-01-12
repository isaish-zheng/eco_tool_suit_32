#!/usr/bin/env python
# -*- coding: utf-8 -*-
# author:ZYD
# @version : V1.0.0
# @function: V1.0.0：根据pcan驱动封装操作优控vcu的uds服务，
#   下载流程封装于download线程


##############################
# Module imports
##############################

import copy  # 用于深拷贝
import ctypes  # 用于调用dll
import os
import platform  # 用于判断当前系统
import sys
import traceback  # 用于获取异常详细信息
import threading  # 用于多线程
import time
from typing import List, Any, NamedTuple, Union

from eco.pcandrive.PCAN_UDS_2013 import PUDS_MSGTYPE_UUDT
from .pcandrive import pcanuds
from srecord import Srecord
from .seed2key import get_key_of_seed
from utils import get_c_char

##############################
# Auxiliary functions
##############################

IS_WINDOWS = platform.system() == 'Windows'  # 判断当前系统是否为Windows
USE_GETCH = True  # 是否使用getch函数来等待用户输入
IS_PRINT_EXEC_DETAIL = False  # 是否打印执行细节,一级
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

class EcoPudsException(Exception):
    """
    EcoPudsFlash异常

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

    def __init__(self, is_success: bool = None, data: Any = None) -> None:
        """
        构造函数
        """
        self.is_success = is_success
        self.data = data


class Nrc(NamedTuple):
    """
    # Represents UDS negative response codes (see ISO 14229-1:2013 A.1 Negative response codes p.325)
    """
    code_0x00: str = 'Positive Response'
    code_0x10: str = 'General Reject'
    code_0x11: str = 'Service Not Supported'
    code_0x12: str = 'Sub Function Not Supported'
    code_0x13: str = 'Incorrect Message Length Or Invalid Format'
    code_0x14: str = 'Response Too Long'
    code_0x21: str = 'Busy Repeat Request'
    code_0x22: str = 'Conditions Not Correct'
    code_0x24: str = 'Request Sequence Error'
    code_0x25: str = 'No Response From Subnet Component'
    code_0x26: str = 'Failure Prevents Execution Of Requested Action'
    code_0x31: str = 'Request Out Of Range'
    code_0x33: str = 'Security Access Denied'
    code_0x34: str = 'Authentication Required'
    code_0x35: str = 'Invalid Key'
    code_0x36: str = 'Exceeded Number Of Attempts'
    code_0x37: str = 'Required Time Delay Not Expired'
    code_0x38: str = 'Secure Data Transmission Required'
    code_0x39: str = 'Secure Data Transmission Not Allowed'
    code_0x3A: str = 'Secure Data Verification Failed'
    code_0x50: str = 'Certificate Verification Failed Invalid Time Period'
    code_0x51: str = 'Certificate Verification Failed Invalid SIGnature'
    code_0x52: str = 'Certificate Verification Failed Invalid Chain of Trust'
    code_0x53: str = 'Certificate Verification Failed Invalid Type'
    code_0x54: str = 'Certificate Verification Failed Invalid Format'
    code_0x55: str = 'Certificate Verification Failed Invalid Content'
    code_0x56: str = 'Certificate Verification Failed Invalid SCoPe'
    code_0x57: str = 'Certificate Verification Failed Invalid CERTificate(revoked)'
    code_0x58: str = 'Ownership Verification Failed'
    code_0x59: str = 'Challenge Calculation Failed'
    code_0x5A: str = 'Setting Access Rights Failed'
    code_0x5B: str = 'Session Key Creation / Derivation Failed'
    code_0x5C: str = 'Configuration Data Usage Failed'
    code_0x5D: str = 'DeAuthentication Failed'
    code_0x70: str = 'Upload Download Not Accepted'
    code_0x71: str = 'Transfer Data Suspended'
    code_0x72: str = 'General Programming Failure'
    code_0x73: str = 'Wrong Block Sequence Counter'
    code_0x78: str = 'Request Correctly Received - Response Pending'
    code_0x7E: str = 'Sub Function Not Supported In Active Session'
    code_0x7F: str = 'Service Not Supported In Active Session'
    code_0x81: str = 'RPM Too High'
    code_0x82: str = 'RPM Too Low'
    code_0x83: str = 'Engine Is Running'
    code_0x84: str = 'Engine Is Not Running'
    code_0x85: str = 'Engine Run Time Too Low'
    code_0x86: str = 'TEMPerature Too High'
    code_0x87: str = 'TEMPerature Too Low'
    code_0x88: str = 'Vehicle Speed Too High'
    code_0x89: str = 'Vehicle Speed Too Low'
    code_0x8A: str = 'Throttle / Pedal Too High'
    code_0x8B: str = 'Throttle / Pedal Too Low'
    code_0x8C: str = 'Transmission Range Not In Neutral'
    code_0x8D: str = 'Transmission Range Not In Gear'
    code_0x8F: str = 'Brake Switch(es) Not Closed(brake pedal not pressed or not applied)'
    code_0x90: str = 'Shifter Lever Not In Park'
    code_0x91: str = 'Torque Converter Clutch Locked'
    code_0x92: str = 'Voltage Too High'
    code_0x93: str = 'Voltage Too Low'
    code_0x94: str = 'Resource Temporarily Not Available'


##############################
# PCAN-UDS-ECO API function declarations
##############################

class EcoPudsFunc(object):
    """
    EcoPudsFlash类，用于实现Pcan设备通过UDS协议刷写优控VCU程序

    :param channel: Pcan设备通道
    :type channel: ctypes.c_uint32
    :param baudrate: Pcan设备波特率
    :type baudrate: ctypes.c_uint32
    :param tester_can_id: 诊断仪的CAN_ID
    :type tester_can_id: int
    :param ecu_can_id: ECU的CAN_ID
    :type ecu_can_id: int
    :param broadcast_can_id: 广播CAN_ID
    :type broadcast_can_id: int
    :param is_stop_if_msg_error: 若为True，当消息错误时停止执行并抛出异常
    :type is_stop_if_msg_error: bool
    """

    def __init__(self,
                 channel: ctypes.c_uint32,
                 baudrate: ctypes.c_uint32,
                 tester_can_id: int,
                 ecu_can_id: int,
                 broadcast_can_id: int,
                 is_stop_if_msg_error: bool = True) -> None:
        """
        构造函数
        """
        self.obj_puds = pcanuds.PCAN_UDS_2013()
        self.transmission_error_number = 0
        self.response_error_number = 0
        self.channel = channel
        self.baudrate = baudrate
        self.is_stop_if_msg_error = is_stop_if_msg_error

        # PUDS消息配置
        self.puds_msg_config = pcanuds.uds_msgconfig()
        self.puds_msg_config.can_id = -1
        self.puds_msg_config.can_msgtype = pcanuds.PCANTP_CAN_MSGTYPE_STANDARD
        self.puds_msg_config.nai.protocol = pcanuds.PUDS_MSGPROTOCOL_ISO_15765_2_11B_NORMAL
        self.puds_msg_config.nai.source_addr = pcanuds.PUDS_ISO_15765_4_ADDR_TEST_EQUIPMENT
        self.puds_msg_config.nai.target_addr = pcanuds.PUDS_ISO_15765_4_ADDR_ECU_1
        self.puds_msg_config.nai.target_type = pcanuds.PCANTP_ISOTP_ADDRESSING_PHYSICAL
        self.puds_msg_config.type = pcanuds.PUDS_MSGTYPE_USDT
        # 节点CAN_ID
        self.tester_can_id = tester_can_id
        self.ecu_can_id = ecu_can_id
        self.broadcast_can_id = broadcast_can_id

    def reset(self):
        self.obj_puds.Reset_2013(self.channel)

    def create_connect(self, timeout_ms: int):
        """
        建立连接

        :param timeout_ms: 等待响应超时时间，单位：毫秒
        :type timeout_ms: int
        :returns: 操作结果
        :rtype: bool
        """

        timeout_response = ctypes.c_uint32(0)
        status = self.obj_puds.GetValue_2013(self.channel,
                                             pcanuds.PUDS_PARAMETER_TIMEOUT_RESPONSE,
                                             timeout_response,
                                             ctypes.sizeof(timeout_response))
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            timeout_ms = timeout_response.value

        # text = pcanuds.create_string_buffer(256)
        connected_count = 0
        conn_start_time = time.time()
        self.reset()
        while True:
            request = pcanuds.uds_msg()
            response = pcanuds.uds_msg()
            confirmation = pcanuds.uds_msg()
            status = self.obj_puds.SvcDiagnosticSessionControl_2013(self.channel,
                                                                    self.puds_msg_config,
                                                                    request,
                                                                    self.obj_puds.PUDS_SVC_PARAM_DSC_DS)
            # self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
            # msg = f'发送自定义请求消息:{text.value.decode()}'
            # print(msg)

            time.sleep(0.05)
            status = self.obj_puds.Read_2013(self.channel, response, request, None)
            # self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
            # msg = f'接收自定义请求消息:{text.value.decode()}'
            # print(msg)

            if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False)\
                    and response.msg.msgdata.any.contents.data[0] == 0x50\
                    and response.msg.msgdata.any.contents.data[1] == 0x01:
                connected_count += 1
            self.__free_msg([request, response, confirmation])
            self.reset()
            if connected_count >= 3:
                return True
            if time.time() - conn_start_time > timeout_ms / 1000:
                return False

    def __free_msg(self, msgs: list[pcanuds.uds_msg]) -> None:
        """
        释放uds_msg对象资源

        :param msgs: 包含uds_msg对象的列表
        :type msgs: list[pcanuds.uds_msg]
        """
        for msg in msgs:
            status = self.obj_puds.MsgFree_2013(msg)
            # msg = (f'释放msg资源' +
            #        f'{"成功" if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False) else "失败"}')
            # print_exec_detail(msg)

    def __display_uds_msg(self,
                          request: pcanuds.uds_msg,
                          response: pcanuds.uds_msg,
                          no_response_expected: bool) -> bool:
        """
        显示UDS请求和响应消息(若没有响应或响应不符合预期则进行错误计数)

        :param request: 请求消息
        :type request: pcanuds.uds_msg
        :param response: 响应消息
        :type response: pcanuds.uds_msg
        :param no_response_expected: 若不需要响应，则不会进行错误计数
        :type no_response_expected: bool
        :return: 若响应符合预期则返回True
        :rtype: bool
        :raises EcoPudsException: 请求消息发送失败；响应消息接收失败；响应消息为空；响应消息非预期
        """
        if request and request.msg.msgdata.isotp:
            msg = ("UDS请求消息 -> 结果: %i - %s\n"
                   % (request.msg.msgdata.any.contents.netstatus,
                      "ERROR!!!" if request.msg.msgdata.any.contents.netstatus != pcanuds.PCANTP_NETSTATUS_OK.value
                      else "OK!"))
            # display data
            s = "\t-> 长度:{x1}, 数据: ".format(x1=format(request.msg.msgdata.any.contents.length, "d"))
            s = msg + s
            for i in range(request.msg.msgdata.any.contents.length):
                s += "{x1} ".format(x1=format(request.msg.msgdata.any.contents.data[i], "02X"))
            print_msg_detail(s)
            if self.is_stop_if_msg_error and request.msg.msgdata.any.contents.netstatus != pcanuds.PCANTP_NETSTATUS_OK.value:
                msg = f'请求消息发送失败'
                raise EcoPudsException(msg)
        if response and response.msg.msgdata.isotp:
            msg = ("UDS响应消息 -> 结果: %i - %s\n"
                   % (response.msg.msgdata.any.contents.netstatus,
                      "ERROR!!!" if response.msg.msgdata.any.contents.netstatus != pcanuds.PCANTP_NETSTATUS_OK.value
                      else "OK!"))
            # display data
            s = "\t-> 长度:{x1}, 数据: ".format(x1=format(response.msg.msgdata.any.contents.length, "d"))
            s = msg + s
            for i in range(response.msg.msgdata.any.contents.length):
                s += "{x1} ".format(x1=format(response.msg.msgdata.any.contents.data[i], "02X"))
            print_msg_detail(s)
            if self.is_stop_if_msg_error and response.msg.msgdata.any.contents.netstatus != pcanuds.PCANTP_NETSTATUS_OK.value:
                msg = f'响应消息接收失败'
                raise EcoPudsException(msg)
        elif not no_response_expected:
            print_msg_detail("\n\n\t /!\\ ERROR: 无响应!!!\n", 'error')
            self.transmission_error_number += 1
        # 若是正响应，则返回True
        if response and (response.links.service_id.contents.value == request.links.service_id.contents.value + 0x40):
            return True
        # 若非正响应，则接收错误计数加1
        elif self.is_stop_if_msg_error:
            self.response_error_number += 1
            if not response:
                msg = f'响应消息为空'
                raise EcoPudsException(msg)
            else:
                obj_nrc = Nrc()
                nrc_code = 'code_0x' + hex(response.links.nrc.contents.value)[2:].upper()
                if hasattr(obj_nrc, nrc_code):
                    nrc_text = getattr(obj_nrc, nrc_code, 'Nrc Code Non-existent')
                msg = (f'响应消息非预期:{nrc_text}\n'
                       f'\tsid={hex(response.msg.msgdata.any.contents.data[0])},应为"{hex(request.links.service_id.contents.value + 0x40)}"\n'
                       f'\tnrc={hex(response.links.nrc.contents.value)}')
                raise EcoPudsException(msg)

    def initialize_device(self) -> ExecResult:
        """
        初始化设备并设置时间参数

        :return: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPudsException: 初始化设备失败；设置时间参数失败
        """
        # 初始化
        status = self.obj_puds.Initialize_2013(self.channel, self.baudrate, 0, 0, 0)
        text = pcanuds.create_string_buffer(256)
        self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            msg = f'初始化设备:{text.value.decode()}'
            print_exec_detail(msg)
        else:
            msg = f'初始化设备:{text.value.decode()}'
            print_exec_detail(msg)
            raise EcoPudsException(msg)
        # 设置通信参数
        tmp_buffer = ctypes.c_ubyte(pcanuds.PCANTP_ISO_TIMEOUTS_15765_2)
        status = self.obj_puds.SetValue_2013(self.channel,
                                             pcanuds.PUDS_PARAMETER_ISO_TIMEOUTS, tmp_buffer, ctypes.sizeof(tmp_buffer))
        text = pcanuds.create_string_buffer(256)
        self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            msg = f'设置ISO 15765-2时间参数:{text.value.decode()}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
        else:
            msg = f'设置ISO 15765-2时间参数:{text.value.decode()}'
            print_exec_detail(msg)
            raise EcoPudsException(msg)
        return exec_result

    def uninitialize_device(self) -> ExecResult:
        """
        关闭设备

        :return: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPudsException: 关闭设备失败
        """
        status = self.obj_puds.Uninitialize_2013(self.channel)
        text = pcanuds.create_string_buffer(256)
        self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            msg = f'关闭设备:{text.value.decode()}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
        else:
            msg = f'关闭设备:{text.value.decode()}'
            print_exec_detail(msg)
            raise EcoPudsException(msg)
        return exec_result

    def set_mapping(self,
                    mapping_type: str) -> ExecResult:
        """
        设置节点CAN_ID与UDS_NAI的映射关系

        :param mapping_type: 'tester'：tester与ecu映射；'ecu'：ecu与tester映射；'broadcast'：broadcast与ecu的映射
        :type mapping_type: str
        :return: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPudsException: 参数错误；设置映射关系失败
        """
        mapping = pcanuds.uds_mapping()
        mapping.can_msgtype = pcanuds.PCANTP_CAN_MSGTYPE_STANDARD
        mapping.can_tx_dlc = 0x0
        mapping.nai = copy.deepcopy(self.puds_msg_config.nai)
        if mapping_type == 'tester':
            if not (self.tester_can_id and self.ecu_can_id):
                msg = f'设置CAN_ID与其UDS_NAI映射错误:缺少tester/ecu的ID参数'
                print_map_detail(msg)
                raise EcoPudsException(msg)
            local_can_id = self.tester_can_id
            remote_can_id = self.ecu_can_id
        elif mapping_type == 'ecu':
            if not (self.tester_can_id and self.ecu_can_id):
                msg = f'设置CAN_ID与其UDS_NAI映射错误:缺少tester/ecu的ID参数'
                print_map_detail(msg)
                raise EcoPudsException(msg)
            local_can_id = self.ecu_can_id
            remote_can_id = self.tester_can_id
            mapping.nai.source_addr = self.puds_msg_config.nai.target_addr
            mapping.nai.target_addr = self.puds_msg_config.nai.source_addr
        elif mapping_type == 'broadcast':
            if not (self.ecu_can_id and self.broadcast_can_id):
                msg = f'设置CAN_ID与其DS_NAI映射错误:缺少broadcast/ecu的ID参数'
                print_map_detail(msg)
                raise EcoPudsException(msg)
            local_can_id = self.broadcast_can_id
            remote_can_id = self.ecu_can_id
        else:
            msg = f'设置CAN_ID与其UDS_NAI映射错误:未定义mapping_type类型"{mapping_type}"'
            print_map_detail(msg)
            raise EcoPudsException(msg)

        mapping.can_id = local_can_id
        mapping.can_id_flow_ctrl = remote_can_id
        status = self.obj_puds.AddMapping_2013(self.channel, mapping)
        text = pcanuds.create_string_buffer(256)
        self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            msg = f'设置ID映射:{text.value.decode()},{mapping_type}的CAN_ID与其UDS_NAI映射关系,{mapping_type}_can_id={hex(local_can_id)}'
            print_map_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
        else:
            msg = f'设置ID映射:{text.value.decode()},{mapping_type}的CAN_ID与其UDS_NAI映射关系，{mapping_type}_can_id={hex(local_can_id)}'
            print_map_detail(msg)
            raise EcoPudsException(msg)
        return exec_result

    def get_mapping(self,
                    can_id: int) -> ExecResult:
        """
        获取节点CAN_ID与其UDS_NAI的映射关系

        :param can_id: 节点CAN_ID
        :type can_id: int
        :return: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPudsException: 获取映射关系失败
        """
        mapping = pcanuds.uds_mapping()
        status = self.obj_puds.GetMapping_2013(self.channel, mapping, can_id, pcanuds.PCANTP_CAN_MSGTYPE_STANDARD)
        text = pcanuds.create_string_buffer(256)
        self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            msg = f'获取ID映射:{text.value.decode()},CAN_ID为{hex(can_id)}的与其UDS_NAI映射关系'
            exec_result = ExecResult(is_success=True, data=msg)
            print_map_detail(msg)
            msg = (f'\tuid: {hex(mapping.uid)}\n' +
                   f'\tcan_id: {hex(mapping.can_id)}\n' +
                   f'\tcan_id_flow_ctrl: {hex(mapping.can_id_flow_ctrl)}\n' +
                   f'\tcan_msgtype: {mapping.can_msgtype}\n' +
                   f'\tcan_tx_dlc: {mapping.can_tx_dlc}\n' +
                   f'\tnai protocol: {mapping.nai.protocol}\n' +
                   f'\tnai source_addr: {hex(mapping.nai.source_addr)}\n' +
                   f'\tnai target_addr: {hex(mapping.nai.target_addr)}\n' +
                   f'\tnai target_type: {mapping.nai.target_type}')
            print_map_detail(msg)
        else:
            msg = f'获取ID映射:{text.value.decode()},CAN_ID为{hex(can_id)}的与其UDS_NAI映射关系'
            print_map_detail(msg)
            raise EcoPudsException(msg)
        return exec_result

    def remove_mapping_by_can_id(self,
                                 can_id: int) -> ExecResult:
        """
        清除节点CAN_ID与其UDS_NAI的映射关系

        :param can_id: 节点CAN_ID
        :type can_id: int
        :return: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPudsException: 清除映射关系失败
        """
        status = self.obj_puds.RemoveMappingByCanId_2013(self.channel, can_id)
        text = pcanuds.create_string_buffer(256)
        self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            msg = f'删除ID映射:{text.value.decode()},CAN_ID为{hex(can_id)}的与其UDS_NAI映射关系'
            print_map_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
        else:
            msg = f'删除ID映射:{text.value.decode()},CAN_ID为{hex(can_id)}的与其UDS_NAI映射关系'
            print_map_detail(msg)
            raise EcoPudsException(msg)
        return exec_result

    def diagnostic_session_control(self,
                                   session_type: int) -> ExecResult:
        """
        诊断会话控制

        :param session_type: 会话类型
        :type session_type: int
        :return: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPudsException: 参数错误；切换诊断会话模式失败
        """
        request = pcanuds.uds_msg()
        response = pcanuds.uds_msg()
        confirmation = pcanuds.uds_msg()

        if session_type == self.obj_puds.PUDS_SVC_PARAM_DSC_DS:
            session_type_describe = '默认'
        elif session_type == self.obj_puds.PUDS_SVC_PARAM_DSC_ECUPS:
            session_type_describe = '编程'
        elif session_type == self.obj_puds.PUDS_SVC_PARAM_DSC_ECUEDS:
            session_type_describe = '扩展'
        else:
            msg = f'诊断会话控制参数错误：未定义会话模式"{session_type}"'
            print_exec_detail(msg)
            raise EcoPudsException(msg)

        msg = f'切换诊断会话模式中:{session_type_describe}会话'
        print_exec_detail(msg)
        status = self.obj_puds.SvcDiagnosticSessionControl_2013(self.channel, self.puds_msg_config, request,
                                                                session_type)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            status = self.obj_puds.WaitForService_2013(self.channel, request, response, confirmation)
        text = pcanuds.create_string_buffer(256)
        self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            msg = f'切换诊断会话模式:{text.value.decode()},{session_type_describe}会话'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'切换诊断会话模式:{text.value.decode()},{session_type_describe}会话'
            print_exec_detail(msg)
            self.__display_uds_msg(request, None, False)
            raise EcoPudsException(msg)
        # 释放msg资源
        self.__free_msg([request, response, confirmation])
        return exec_result

    def routine_control(self,
                        control_type: int,
                        routine_id: int,
                        data: list[int] = None) -> ExecResult:
        """
        例行程序控制

        :param control_type: 控制类型
        :type control_type: int
        :param routine_id: 任务ID
        :type routine_id: int
        :param data: 包含数据的列表
        :type data: list[int]
        :return: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPudsException: 参数错误；例行程序控制失败
        """
        request = pcanuds.uds_msg()
        response = pcanuds.uds_msg()
        confirmation = pcanuds.uds_msg()

        if data:
            routine_control_option_record_size = len(data)
            routine_control_option_record = ctypes.create_string_buffer(routine_control_option_record_size)
            for i in range(routine_control_option_record_size):
                routine_control_option_record[i] = get_c_char(ord(chr(data[i])))
        else:
            routine_control_option_record_size = 0
            routine_control_option_record = None

        if control_type == self.obj_puds.PUDS_SVC_PARAM_RC_STR:
            control_type_describe = '启动'
            if routine_id == 0x0203:
                routine_type_describe = '检查编程条件'
            elif routine_id == 0x0202:
                routine_type_describe = '检查数据完整性'
            elif routine_id == self.obj_puds.PUDS_SVC_PARAM_RC_RID_EM_:
                routine_type_describe = '擦除内存'
            elif routine_id == self.obj_puds.PUDS_SVC_PARAM_RC_RID_CPD_:
                routine_type_describe = '检查编程依赖关系'
            else:
                msg = f'例行程序控制参数错误:未定义routine_id类型"{hex(routine_id)}"'
                print_exec_detail(msg)
                raise EcoPudsException(msg)
        else:
            msg = f'例行程序控制参数错误:未定义控制类型"{hex(control_type)}"'
            print_exec_detail(msg)
            raise EcoPudsException(msg)

        msg = f'例行程序控制:{control_type_describe}程序"{routine_type_describe}中",routine_id={hex(routine_id)}'
        print_exec_detail(msg)
        status = self.obj_puds.SvcRoutineControl_2013(self.channel, self.puds_msg_config, request, control_type,
                                                      routine_id,
                                                      routine_control_option_record, routine_control_option_record_size)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            status = self.obj_puds.WaitForService_2013(self.channel, request, response, confirmation)
        text = pcanuds.create_string_buffer(256)
        self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            msg = f'例行程序控制:{text.value.decode()},{control_type_describe}程序"{routine_type_describe}中"成功,routine_id={hex(routine_id)}'
            print_exec_detail(msg)
            length = response.msg.msgdata.any.contents.length
            res_data = response.msg.msgdata.any.contents.data[2:length]
            if res_data[-1] == 0x00:
                msg = f'{routine_type_describe}成功'
                print_exec_detail(msg)
            else:
                msg = f'{routine_type_describe}失败'
                print_exec_detail(msg)
                self.__display_uds_msg(confirmation, response, False)
                raise EcoPudsException(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'例行程序控制:{text.value.decode()},{control_type_describe}程序失败,routine_id={hex(routine_id)}'
            print_exec_detail(msg)
            self.__display_uds_msg(request, None, False)
            raise EcoPudsException(msg)
        # 释放msg资源
        self.__free_msg([request, response, confirmation])
        return exec_result

    def control_dtc_setting(self,
                            setting_type: int) -> ExecResult:
        """
        控制DTC设置

        :param setting_type: 设置类型
        :type setting_type: int
        :return: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPudsException: 参数错误；控制DTC设置失败
        """
        request = pcanuds.uds_msg()
        response = pcanuds.uds_msg()
        confirmation = pcanuds.uds_msg()

        if setting_type == self.obj_puds.PUDS_SVC_PARAM_CDTCS_OFF:
            setting_type_describe = '禁用'
            dtc_setting_control_option_record = None
            dtc_setting_control_option_record_size = 0
        else:
            msg = f'控制DTC设置参数错误:未定义的设置类型"{setting_type}"'
            print_exec_detail(msg)
            raise EcoPudsException(msg)

        msg = f'控制DTC设置:{setting_type_describe}DTC状态更新中'
        print_exec_detail(msg)
        status = self.obj_puds.SvcControlDTCSetting_2013(self.channel,
                                                         self.puds_msg_config,
                                                         request,
                                                         setting_type,
                                                         dtc_setting_control_option_record,
                                                         dtc_setting_control_option_record_size)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            status = self.obj_puds.WaitForService_2013(self.channel, request, response, confirmation)
        text = pcanuds.create_string_buffer(256)
        self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            msg = f'控制DTC设置:{text.value.decode()},{setting_type_describe}DTC状态更新成功'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'控制DTC设置:{text.value.decode()},{setting_type_describe}DTC状态更新失败'
            print_exec_detail(msg)
            self.__display_uds_msg(request, None, False)
            raise EcoPudsException(msg)
        # 释放msg资源
        self.__free_msg([request, response, confirmation])
        return exec_result

    def communication_control(self,
                              control_type: int,
                              communication_type: int) -> ExecResult:
        """
        通讯控制

        :param control_type: 控制类型
        :type control_type: int
        :param communication_type: 通讯类型
        :type communication_type: int
        :return: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPudsException: 参数错误；通讯控制失败
        """
        request = pcanuds.uds_msg()
        response = pcanuds.uds_msg()
        confirmation = pcanuds.uds_msg()

        if control_type == self.obj_puds.PUDS_SVC_PARAM_CC_DRXTX:
            control_type_describe = f'抑制{communication_type}所指定报文类型的发送与接收'
        else:
            msg = f'通讯控制参数错误:未定义的控制类型"{control_type}"'
            print_exec_detail(msg)
            raise EcoPudsException(msg)

        msg = f'通讯控制:{control_type_describe}中'
        print_exec_detail(msg)
        status = self.obj_puds.SvcCommunicationControl_2013(self.channel,
                                                            self.puds_msg_config,
                                                            request,
                                                            control_type,
                                                            communication_type,
                                                            0)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            status = self.obj_puds.WaitForService_2013(self.channel, request, response, confirmation)
        text = pcanuds.create_string_buffer(256)
        self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            msg = f'通讯控制:{text.value.decode()},{control_type_describe}成功'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'通讯控制:{text.value.decode()},{control_type_describe}失败'
            print_exec_detail(msg)
            self.__display_uds_msg(request, None, False)
            raise EcoPudsException(msg)
        # 释放msg资源
        self.__free_msg([request, response, confirmation])
        return exec_result

    def read_data_by_id(self,
                        did: int) -> ExecResult:
        """
        通过ID读数据

        :param did: 数据ID
        :type did: int
        :return: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPudsException: 读取数据失败
        """
        data_identifier = ctypes.c_uint16(did)
        request = pcanuds.uds_msg()
        response = pcanuds.uds_msg()
        confirmation = pcanuds.uds_msg()

        msg = f'通过ID读数据:读取中,DID={hex(did)}'
        print_exec_detail(msg)
        status = self.obj_puds.SvcReadDataByIdentifier_2013(self.channel, self.puds_msg_config, request,
                                                            data_identifier, 1)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            status = self.obj_puds.WaitForService_2013(self.channel, request, response, confirmation)
        text = pcanuds.create_string_buffer(256)
        self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            msg = f'通过ID读数据:{text.value.decode()},DID={hex(did)}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'通过ID读数据:{text.value.decode()},DID={hex(did)}'
            print_exec_detail(msg)
            self.__display_uds_msg(request, None, False)
            raise EcoPudsException(msg)
        # 释放msg资源
        self.__free_msg([request, response, confirmation])
        return exec_result

    def security_access(self,
                        access_type: int,
                        data: list[int] = None) -> ExecResult:
        """
        安全访问

        :param access_type: 访问类型
        :type access_type: int
        :param data: 包含数据的列表
        :type data: list[int]
        :return: 执行结果ExecResult，ExecResult.data中含有seed数据
        :rtype: ExecResult
        :raises EcoPudsException: 参数错误；安全访问失败
        """
        request = pcanuds.uds_msg()
        response = pcanuds.uds_msg()
        confirmation = pcanuds.uds_msg()

        if data:
            # security_access_data = reverse32(data)
            # security_access_data_size = 4
            security_access_data_size = len(data)
            security_access_data = ctypes.create_string_buffer(security_access_data_size)
            for i in range(security_access_data_size):
                security_access_data[i] = get_c_char(ord(chr(data[i])))
        else:
            security_access_data_size = 0
            security_access_data = None
        if access_type == self.obj_puds.PUDS_SVC_PARAM_SA_RSD_3:
            access_type_describe = '申请Seed'
        elif access_type == self.obj_puds.PUDS_SVC_PARAM_SA_SK_4:
            access_type_describe = '发送Key'
        else:
            msg = f'安全访问参数错误:未定义的访问类型"{access_type}"'
            print_exec_detail(msg)
            raise EcoPudsException(msg)

        msg = f'安全访问:{access_type_describe}中'
        print_exec_detail(msg)
        status = self.obj_puds.SvcSecurityAccess_2013(self.channel, self.puds_msg_config, request, access_type,
                                                      security_access_data, security_access_data_size)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            status = self.obj_puds.WaitForService_2013(self.channel, request, response, confirmation)
        text = pcanuds.create_string_buffer(256)
        self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            msg = f'安全访问:{text.value.decode()},{access_type_describe}成功'
            print_exec_detail(msg)
            length = response.msg.msgdata.any.contents.length
            seed = response.msg.msgdata.any.contents.data[2:length]
            exec_result = ExecResult(is_success=True, data=seed)
            self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'安全访问:{text.value.decode},{access_type_describe}失败'
            print_exec_detail(msg)
            self.__display_uds_msg(request, None, False)
            raise EcoPudsException(msg)
        # 释放msg资源
        self.__free_msg([request, response, confirmation])
        return exec_result

    def request_download(self,
                         memory_address: List[int],
                         memory_size: List[int]) -> ExecResult:
        """
        请求下载

        :param memory_address: 内存起始地址，包含4字节数据的列表
        :type memory_address: list[int]
        :param memory_size: 内存长度Byte，包含4字节数据的列表
        :type memory_size: list[int]
        :return: 执行结果ExecResult，ExecResult.data中含有block_size
        :rtype: ExecResult
        :raises EcoPudsException: 参数错误；请求下载失败
        """
        request = pcanuds.uds_msg()
        response = pcanuds.uds_msg()
        confirmation = pcanuds.uds_msg()

        if memory_address and memory_size:
            memory_address_size = len(memory_address)
            memory_address_buffer = ctypes.create_string_buffer(memory_address_size)
            for i in range(memory_address_size):
                memory_address_buffer[i] = get_c_char(ord(chr(memory_address[i])))

            memory_size_size = len(memory_size)
            memory_size_buffer = ctypes.create_string_buffer(memory_size_size)
            for i in range(memory_address_size):
                memory_size_buffer[i] = get_c_char(ord(chr(memory_size[i])))
        else:
            msg = f'请求下载参数错误:无效的负载数据'
            print_exec_detail(msg)
            raise EcoPudsException(msg)

        msg = f'请求下载:请求中,从地址{"0x" + bytes(memory_address).hex()}开始共{"0x" + bytes(memory_size).hex()}字节'
        print_exec_detail(msg)
        status = self.obj_puds.SvcRequestDownload_2013(self.channel, self.puds_msg_config, request, 0x0, 0x0,
                                                       memory_address_buffer, memory_address_size,
                                                       memory_size_buffer, memory_size_size)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            status = self.obj_puds.WaitForService_2013(self.channel, request, response, confirmation)
        text = pcanuds.create_string_buffer(256)
        self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            msg = f'请求下载:{text.value.decode()}'
            print_exec_detail(msg)
            block_size = int.from_bytes(bytes(response.msg.msgdata.any.contents.data[2:4]), 'big')
            exec_result = ExecResult(is_success=True, data=block_size)
            self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'请求下载:{text.value.decode()}'
            print_exec_detail(msg)
            self.__display_uds_msg(request, None, False)
            raise EcoPudsException(msg)
        # 释放msg资源
        self.__free_msg([request, response, confirmation])
        return exec_result

    def transfer_data(self,
                      block_sequence_counter: int,
                      data: list[int]) -> ExecResult:
        """
        数据传输

        :param block_sequence_counter: 块序列计数器
        :type block_sequence_counter: int
        :param data: 数据列表
        :type data: list[int]
        :return: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPudsException: 参数错误；数据传输失败
        """
        request = pcanuds.uds_msg()
        response = pcanuds.uds_msg()
        confirmation = pcanuds.uds_msg()

        if data:
            transfer_request_parameter_record_size = len(data)
            transfer_request_parameter_record = ctypes.create_string_buffer(transfer_request_parameter_record_size)
            for i in range(transfer_request_parameter_record_size):
                transfer_request_parameter_record[i] = get_c_char(ord(chr(data[i])))
        else:
            msg = f'数据传输参数错误:无效的负载数据'
            print_exec_detail(msg)
            raise EcoPudsException(msg)

        msg = f'数据传输:传输中'
        print_exec_detail(msg)
        status = self.obj_puds.SvcTransferData_2013(self.channel, self.puds_msg_config, request,
                                                    block_sequence_counter,
                                                    transfer_request_parameter_record,
                                                    transfer_request_parameter_record_size)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            status = self.obj_puds.WaitForService_2013(self.channel, request, response, confirmation)
        text = pcanuds.create_string_buffer(256)
        self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            msg = f'数据传输:{text.value.decode()},block_sequence_counter={block_sequence_counter}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'数据传输:{text.value.decode()},block_sequence_counter={block_sequence_counter}'
            print_exec_detail(msg)
            self.__display_uds_msg(request, None, False)
            raise EcoPudsException(msg)
        # 释放msg资源
        self.__free_msg([request, response, confirmation])
        return exec_result

    def request_transfer_exit(self,
                              data: list[int] = None) -> ExecResult:
        """
        请求退出传输

        :param data: 包含数据的列表
        :type data: list[int]
        :return: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPudsException: 请求退出传输失败
        """
        request = pcanuds.uds_msg()
        response = pcanuds.uds_msg()
        confirmation = pcanuds.uds_msg()

        if data:
            transfer_request_parameter_record_size = len(data)
            transfer_request_parameter_record = ctypes.create_string_buffer(transfer_request_parameter_record_size)
            for i in range(transfer_request_parameter_record_size):
                transfer_request_parameter_record[i] = get_c_char(ord(chr(data[i])))
        else:
            transfer_request_parameter_record_size = 0
            transfer_request_parameter_record = None

        msg = f'请求退出传输:退出中'
        print_exec_detail(msg)
        status = self.obj_puds.SvcRequestTransferExit_2013(self.channel, self.puds_msg_config, request,
                                                           transfer_request_parameter_record,
                                                           transfer_request_parameter_record_size)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            status = self.obj_puds.WaitForService_2013(self.channel, request, response, confirmation)
        text = pcanuds.create_string_buffer(256)
        self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            msg = f'请求退出传输:{text.value.decode()}'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'请求退出传输:{text.value.decode()}'
            print_exec_detail(msg)
            self.__display_uds_msg(request, None, False)
            raise EcoPudsException(msg)
        # 释放msg资源
        self.__free_msg([request, response, confirmation])
        return exec_result

    def ecu_reset(self,
                  reset_type: int) -> ExecResult:
        """
        ecu复位

        :param reset_type: 复位类型
        :type reset_type: int
        :return: 执行结果ExecResult
        :rtype: ExecResult
        :raises EcoPudsException: 参数错误；ecu复位失败
        """
        request = pcanuds.uds_msg()
        response = pcanuds.uds_msg()
        confirmation = pcanuds.uds_msg()

        if reset_type == self.obj_puds.PUDS_SVC_PARAM_ER_HR:
            reset_type_describe = '硬复位'
        else:
            msg = f'ecu复位参数错误:未定义的复位类型"{reset_type}"'
            print_exec_detail(msg)
            raise EcoPudsException(msg)

        msg = f'ecu复位:{reset_type_describe}中'
        print_exec_detail(msg)
        status = self.obj_puds.SvcECUReset_2013(self.channel, self.puds_msg_config, request, reset_type)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            status = self.obj_puds.WaitForService_2013(self.channel, request, response, confirmation)
        text = pcanuds.create_string_buffer(256)
        self.obj_puds.GetErrorText_2013(status, 0x09, text, 256)
        if self.obj_puds.StatusIsOk_2013(status, pcanuds.PUDS_STATUS_OK, False):
            msg = f'ecu复位:{text.value.decode()},{reset_type_describe}成功'
            print_exec_detail(msg)
            exec_result = ExecResult(is_success=True, data=msg)
            self.__display_uds_msg(confirmation, response, False)
        else:
            msg = f'ecu复位:{text.value.decode()},{reset_type_describe}失败'
            print_exec_detail(msg)
            self.__display_uds_msg(request, None, False)
            raise EcoPudsException(msg)
        # 释放msg资源
        self.__free_msg([request, response, confirmation])
        return exec_result

    def erase_write_data(self,
                         obj_srecord: Srecord) -> float:
        """
        将Srecord文件的S3数据，擦除并写入Flash
        擦写流程：
        对于每个连续擦写段执行routine_control(擦除内存)后，再执行request_download(请求下载),
        将擦写段分成单个或多个block执行transfer_data(数据传输),当前擦写段的所有block传输完毕执行request_transfer_exit(退出传输),
        然后开始下一段擦写,直到将所有的擦写段擦写完毕

        :param obj_srecord: Srecord对象，对象中包含erase_memory_infos属性，此属性含有各连续擦写数据段的详细信息
        :type obj_srecord: Srecord
        :return: 返回执行时间，单位s
        :rtype: float
        :raises EcoPudsException: Srecord对象为空；执行擦除内存未得到有效反馈；执行请求下载未得到有效反馈；执行数据传输未得到有效反馈；
            执行退出传输未得到有效反馈
        """

        def hex2byte(hex_value: str):
            """
            将32位16进制字符串转换为单个字节的整型
            :param hex_value: 32位16进制字符串(eg:0x12345678)
            :return: 包含4个字节的列表(eg:[0x12,0x34,0x56,0x78])
            """
            b0 = int(hex_value, 16) >> 0 & 0xFF
            b1 = int(hex_value, 16) >> 8 & 0xFF
            b2 = int(hex_value, 16) >> 16 & 0xFF
            b3 = int(hex_value, 16) >> 24 & 0xFF
            return [b3, b2, b1, b0]

        # 开始时间戳
        time_start = time.time()

        if not obj_srecord:
            msg = f'擦写:Srecord对象为空'
            print_exec_detail(msg)
            raise EcoPudsException(msg)

        msg = f'擦写:共需擦写{len(obj_srecord.erase_memory_infos)}个数据段'
        print_exec_detail(msg)
        for erase_memory_info in obj_srecord.erase_memory_infos:
            msg = f'-> 擦写:擦写第{erase_memory_info.erase_number}个数据段中'
            print_exec_detail(msg)

            # 擦除内存
            msg = f'--> 擦写:擦除第{erase_memory_info.erase_number}个数据段中'
            print_exec_detail(msg)
            data = [0x44]
            data.extend(hex2byte(erase_memory_info.erase_start_address32))
            data.extend(hex2byte(erase_memory_info.erase_length))
            exec_result = self.routine_control(self.obj_puds.PUDS_SVC_PARAM_RC_STR,
                                               self.obj_puds.PUDS_SVC_PARAM_RC_RID_EM_,
                                               data=data)
            if exec_result.is_success and exec_result.data:
                msg = f'--> 擦写:擦除第{erase_memory_info.erase_number}个数据段成功'
                print_exec_detail(msg)
            else:
                msg = f'--> 擦写:执行擦除内存未得到有效反馈'
                print_exec_detail(msg)
                raise EcoPudsException(msg)

            # 请求下载
            msg = f'--> 擦写:请求下载第{erase_memory_info.erase_number}个数据段中'
            print_exec_detail(msg)
            memory_address = hex2byte(erase_memory_info.erase_start_address32)
            memory_size = hex2byte(erase_memory_info.erase_length)
            exec_result = self.request_download(memory_address,
                                                memory_size)
            if exec_result.is_success and exec_result.data:
                block_size = exec_result.data
                msg = f'--> 擦写:请求下载第{erase_memory_info.erase_number}个数据段成功,每个block最大传输{block_size}字节负载数据'
                print_exec_detail(msg)
            else:
                msg = f'--> 擦写:执行请求下载未得到有效反馈'
                print_exec_detail(msg)
                raise EcoPudsException(msg)

            # 数据传输
            block_size -= 2  # 减去命令标识与块序列计数器2个字节
            erase_data = [byte for byte in bytes.fromhex(erase_memory_info.erase_data)]
            if block_size >= len(erase_data):
                block_sum = 1
            else:
                block_sum = int(len(erase_data) / block_size) + 1
            msg = f'--> 擦写:传输第{erase_memory_info.erase_number}个数据段中,共{block_sum}个block'
            print_exec_detail(msg)
            # 单Block传输
            if block_size >= len(erase_data):
                block_sequence_counter = 1
                msg = f'---> 擦写:传输第1个block中,block_sequence_counter={block_sequence_counter}'
                print_exec_detail(msg)
                exec_result = self.transfer_data(block_sequence_counter, erase_data)
                if exec_result.is_success and exec_result.data:
                    msg = f'---> 擦写:传输第1个block成功,block_sequence_counter={block_sequence_counter}'
                    print_exec_detail(msg)
                else:
                    msg = f'---> 擦写:执行数据传输未得到有效反馈'
                    print_exec_detail(msg)
                    raise EcoPudsException(msg)
            # 多Block传输
            else:
                block_sequence_counter = 0
                # 非最后一个Block
                for i in range(int(len(erase_data) / block_size)):
                    # 若块序列计数器达到0xFF则重置为0
                    if block_sequence_counter == 0xFF:
                        block_sequence_counter = 0
                    block_sequence_counter += 1
                    msg = f'---> 擦写:传输第{i + 1}个block中,block_sequence_counter={block_sequence_counter}'
                    print_exec_detail(msg)
                    data = erase_data[i * block_size:(i + 1) * block_size]
                    exec_result = self.transfer_data(block_sequence_counter, data)
                    if exec_result.is_success and exec_result.data:
                        msg = f'---> 擦写:传输第{i + 1}个block成功,block_sequence_counter={block_sequence_counter}'
                        print_exec_detail(msg)
                    else:
                        msg = f'---> 擦写:执行数据传输未得到有效反馈'
                        print_exec_detail(msg)
                        raise EcoPudsException(msg)
                # 最后一个Block
                i = int(len(erase_data) / block_size)
                if block_sequence_counter == 0xFF:
                    block_sequence_counter = 0
                block_sequence_counter += 1
                msg = f'---> 擦写:传输第{i + 1}个block中,block_sequence_counter={block_sequence_counter}'
                print_exec_detail(msg)
                data = erase_data[i * block_size:]
                exec_result = self.transfer_data(block_sequence_counter, data)
                if exec_result.is_success and exec_result.data:
                    msg = f'---> 擦写:传输第{i + 1}个block成功,block_sequence_counter={block_sequence_counter}'
                    print_exec_detail(msg)
                else:
                    msg = f'---> 擦写:执行数据传输未得到有效反馈'
                    print_exec_detail(msg)
                    raise EcoPudsException(msg)
            # 请求退出数据传输
            msg = f'--> 擦写:请求退出传输第{erase_memory_info.erase_number}个数据段中'
            print_exec_detail(msg)
            exec_result = self.request_transfer_exit()
            if exec_result.is_success and exec_result.data:
                msg = f'--> 擦写:请求退出传输第{erase_memory_info.erase_number}个数据段成功'
                print_exec_detail(msg)
            else:
                msg = f'--> 擦写:执行请求退出传输未得到有效反馈'
                print_exec_detail(msg)
                raise EcoPudsException(msg)

        # 结束时间戳
        time_stop = time.time()
        return time_stop - time_start


##############################
# PCAN-UDS-ECO Threading
##############################

class DownloadThread(threading.Thread):
    """
    刷写线程类

    :param request_can_id: 请求设备的CAN_ID(0x开头的16进制)
    :type request_can_id: str
    :param response_can_id: 响应设备的CAN_ID(0x开头的16进制)
    :type response_can_id: str
    :param function_can_id: 功能地址(0x开头的16进制)
    :type function_can_id: str
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
                 function_can_id: str,
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
        self.__function_can_id = function_can_id
        self.__device_channel = device_channel
        self.__device_baudrate = device_baudrate
        self.__download_filepath = download_filepath
        self.__seed2key_filepath = seed2key_filepath
        self.__obj_srecord = obj_srecord

        self.obj_flash = self.__create_flash_obj()
        self.__has_open_device = False
        self.__has_ecu_reset = False
        self.__ew_time = 0.0

    def __del__(self) -> None:
        """
        析构函数
        """
        try:
            obj_flash = self.obj_flash
            if self.__has_open_device:
                if obj_flash.uninitialize_device().is_success:
                    self.__has_open_device = False
                # 显示报告并退出
                if obj_flash.transmission_error_number > 0:
                    msg = ("\n\tERROR: %d个UDS消息传输错误!!!" % obj_flash.transmission_error_number)
                    self.print_detail(msg, 'error')
                    return
                else:
                    self.print_detail("\n\t所有UDS消息传输成功", 'done')
                if obj_flash.response_error_number > 0:
                    msg = ("\n\tERROR: %d个UDS消息响应错误!!!" % obj_flash.response_error_number)
                    self.print_detail(msg, 'error')
                    return
                else:
                    self.print_detail("\n\t所有UDS消息响应正确", 'done')
                if obj_flash.transmission_error_number <= 0 and \
                        obj_flash.response_error_number <= 0 and \
                        self.__has_ecu_reset:
                    self.print_detail(f"\n\t<-下载完成->，用时{self.__ew_time:.2f}s", 'done')
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

    def __deal_comm_para(self) -> tuple[pcanuds.c_uint32, pcanuds.c_uint32, int, int, int]:
        """
        处理通信参数

        :return: channel, baudrate, tester_can_id, ecu_can_id, broadcast_can_id
        :rtype:  tuple[pcanuds.c_uint32, pcanuds.c_uint32, int, int, int]
        """

        tester_can_id = int(self.__request_can_id, 16)
        ecu_can_id = int(self.__response_can_id, 16)
        broadcast_can_id = int(self.__function_can_id, 16)
        channel = pcanuds.PCANTP_HANDLE_USBBUS1
        baudrate = pcanuds.PCANTP_BAUDRATE_500K

        if self.__device_channel == '0x1':
            channel = pcanuds.PCANTP_HANDLE_USBBUS1
        elif self.__device_channel == '0x2':
            channel = pcanuds.PCANTP_HANDLE_USBBUS2
        if self.__device_baudrate == '50kbps':
            baudrate = pcanuds.PCANTP_BAUDRATE_50K
        elif self.__device_baudrate == '100kbps':
            baudrate = pcanuds.PCANTP_BAUDRATE_100K
        elif self.__device_baudrate == '125kbps':
            baudrate = pcanuds.PCANTP_BAUDRATE_125K
        elif self.__device_baudrate == '250kbps':
            baudrate = pcanuds.PCANTP_BAUDRATE_250K
        elif self.__device_baudrate == '500kbps':
            baudrate = pcanuds.PCANTP_BAUDRATE_500K
        elif self.__device_baudrate == '800kbps':
            baudrate = pcanuds.PCANTP_BAUDRATE_800K
        elif self.__device_baudrate == '1000kbps':
            baudrate = pcanuds.PCANTP_BAUDRATE_1M

        return channel, baudrate, tester_can_id, ecu_can_id, broadcast_can_id

    def __create_flash_obj(self) -> EcoPudsFunc:
        """
        创建flash对象

        :return: flash对象
        :rtype: EcoPudsFunc
        """
        try:
            # 参数配置
            channel, baudrate, tester_can_id, ecu_can_id, broadcast_can_id = \
                self.__deal_comm_para()

            # 创建刷写对象
            return EcoPudsFunc(channel=channel,
                               baudrate=baudrate,
                               tester_can_id=tester_can_id,
                               ecu_can_id=ecu_can_id,
                               broadcast_can_id=broadcast_can_id)
        except Exception as e:
            self.print_detail(f'发生异常 {e}', 'error')
            self.print_detail(f"{traceback.format_exc()}", 'error')

    def run(self) -> None:
        """
        程序刷写流程

        """
        try:
            msg = f"当前设备 -> 请求地址:{self.__request_can_id}, 响应地址:{self.__response_can_id}, 功能地址:{self.__function_can_id}, " + \
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
            obj_flash = self.obj_flash
            self.print_detail('======启动下载流程======')
            self.print_detail('------设备初始化------')
            if obj_flash.initialize_device().is_success:
                self.__has_open_device = True
                self.print_detail(f"设备初始化成功", 'done')
            else:
                self.print_detail(f"设备初始化失败", 'error')

            self.print_detail('------测试ID映射关系------')
            # 测试映射关系
            _, _, tester_can_id, ecu_can_id, broadcast_can_id = \
                self.__deal_comm_para()
            obj_flash.set_mapping('tester')
            obj_flash.set_mapping('ecu')
            obj_flash.get_mapping(tester_can_id)
            obj_flash.get_mapping(ecu_can_id)
            obj_flash.remove_mapping_by_can_id(tester_can_id)
            obj_flash.remove_mapping_by_can_id(broadcast_can_id)

            # 刷写流程
            obj_flash.set_mapping('tester')

            # 建立连接
            self.print_detail('------连接中------')
            if not obj_flash.create_connect(10000):
                msg = f'连接超时'
                raise EcoPudsException(msg)
            self.print_detail('------连接成功------','done')

            # 切换到默认会话
            self.print_detail('------诊断会话控制:切换到默认会话------')
            obj_flash.diagnostic_session_control(obj_flash.obj_puds.PUDS_SVC_PARAM_DSC_DS)
            obj_flash.reset()
            obj_flash.remove_mapping_by_can_id(tester_can_id)
            obj_flash.set_mapping('broadcast')

            # 广播切换到扩展会话
            self.print_detail('------诊断会话控制:广播切换到扩展会话------')
            obj_flash.diagnostic_session_control(obj_flash.obj_puds.PUDS_SVC_PARAM_DSC_ECUEDS)
            obj_flash.remove_mapping_by_can_id(broadcast_can_id)

            obj_flash.set_mapping('tester')
            # 例行程序控制，RID=0x0203
            self.print_detail('------例行程序控制:检查是否满足编程条件------')
            exec_result = obj_flash.routine_control(obj_flash.obj_puds.PUDS_SVC_PARAM_RC_STR, 0x0203)
            obj_flash.remove_mapping_by_can_id(tester_can_id)

            obj_flash.set_mapping('broadcast')
            # 广播禁用DTC更新
            self.print_detail('------控制DTC设置:广播禁用DTC更新------')
            obj_flash.control_dtc_setting(obj_flash.obj_puds.PUDS_SVC_PARAM_CDTCS_OFF)
            # 通讯控制，广播抑制应用报文和网络管理报文
            self.print_detail('------通讯控制:广播抑制应用报文和网络管理报文------')
            obj_flash.communication_control(obj_flash.obj_puds.PUDS_SVC_PARAM_CC_DRXTX,
                                            obj_flash.obj_puds.PUDS_SVC_PARAM_CC_FLAG_APPL
                                            | obj_flash.obj_puds.PUDS_SVC_PARAM_CC_FLAG_NWM)
            obj_flash.remove_mapping_by_can_id(broadcast_can_id)

            obj_flash.set_mapping('tester')
            # 通过ID读数据，制造商备件编号
            self.print_detail('------通过ID读数据:制造商备件编号------')
            obj_flash.read_data_by_id(obj_flash.obj_puds.PUDS_SVC_PARAM_DI_VMSPNDID)
            # 切换到编程会话
            self.print_detail('------诊断会话控制:切换到编程会话------')
            obj_flash.diagnostic_session_control(obj_flash.obj_puds.PUDS_SVC_PARAM_DSC_ECUPS)
            # 安全访问，申请Seed
            self.print_detail('------安全访问:申请Seed------')
            exec_result = obj_flash.security_access(obj_flash.obj_puds.PUDS_SVC_PARAM_SA_RSD_3)
            if exec_result.is_success and exec_result.data:
                seed_data = exec_result.data
                self.print_detail(f'已获取Seed：{[hex(v) for v in seed_data]}', 'done')
            else:
                self.print_detail(f'获取Seed失败', 'error')
                return
            self.print_detail(f'根据Seed2Key文件{self.__seed2key_filepath}计算Key中')
            key_data = get_key_of_seed(seed2key_filepath=self.__seed2key_filepath, seed_data=seed_data)
            self.print_detail(f'已生成Key：{[hex(v) for v in key_data]}', 'done')
            # 安全访问，发送Key
            self.print_detail('------安全访问:发送Key------')
            obj_flash.security_access(obj_flash.obj_puds.PUDS_SVC_PARAM_SA_SK_4, data=key_data)
            # 擦写数据
            self.print_detail('------擦写数据------')
            self.__ew_time = obj_flash.erase_write_data(self.__obj_srecord)
            # 检查数据完整性
            self.print_detail('------检查数据完整性------')
            obj_flash.routine_control(obj_flash.obj_puds.PUDS_SVC_PARAM_RC_STR,
                                      routine_id=0x0202,
                                      data=self.__obj_srecord.crc32_values)
            # 检查编程依赖关系
            self.print_detail('------检查编程依赖关系------')
            obj_flash.routine_control(obj_flash.obj_puds.PUDS_SVC_PARAM_RC_STR,
                                      obj_flash.obj_puds.PUDS_SVC_PARAM_RC_RID_CPD_)
            # 硬复位
            self.print_detail('------ECU硬复位------')
            exec_result = obj_flash.ecu_reset(obj_flash.obj_puds.PUDS_SVC_PARAM_ER_HR)
            obj_flash.remove_mapping_by_can_id(tester_can_id)
            self.__has_ecu_reset = exec_result.is_success
        except Exception as e:
            self.print_detail(f'发生异常 {e}', 'error')
            self.print_detail(f"{traceback.format_exc()}", 'error')
            # msg = f"下载失败"
            # raise EcoPudsException(msg) from e
        finally:
            # self.__del__()
            pass


if __name__ == '__main__':
    pass
    # try:
    #     # 节点CAN_ID
    #     tester_can_id = 0x791
    #     ecu_can_id = 0x799
    #     broadcast_can_id = 0x7df
    #     channel = pcanuds.PCANTP_HANDLE_USBBUS1
    #     baudrate = pcanuds.PCANTP_BAUDRATE_250K
    #     obj_flash = EcoPudsFunc(channel=channel,
    #                              baudrate=baudrate,
    #                              tester_can_id=tester_can_id,
    #                              ecu_can_id=ecu_can_id,
    #                              broadcast_can_id=broadcast_can_id)
    #
    #     # she
    #     obj_flash.set_mapping('tester')
    #     obj_flash.set_mapping('ecu')
    #     obj_flash.get_mapping(tester_can_id)
    #     obj_flash.get_mapping(ecu_can_id)
    #     obj_flash.remove_mapping_by_can_id(tester_can_id)
    #     obj_flash.remove_mapping_by_can_id(broadcast_can_id)
    #
    #     # The following functions call UDS Services
    #     obj_flash.set_mapping('tester')
    #     # 切换到默认会话
    #     obj_flash.diagnostic_session_control(pcanuds.PCAN_UDS_2013.PUDS_SVC_PARAM_DSC_DS)
    #     obj_flash.remove_mapping_by_can_id(tester_can_id)
    #
    #     obj_flash.set_mapping('broadcast')
    #     # 广播切换到扩展会话
    #     obj_flash.diagnostic_session_control(pcanuds.PCAN_UDS_2013.PUDS_SVC_PARAM_DSC_ECUEDS)
    #     obj_flash.remove_mapping_by_can_id(broadcast_can_id)
    #
    #     obj_flash.set_mapping('tester')
    #     # 例行程序控制，RID=0x0203
    #     obj_flash.routine_control(pcanuds.PCAN_UDS_2013.PUDS_SVC_PARAM_RC_STR, 0x0203)
    #     obj_flash.remove_mapping_by_can_id(tester_can_id)
    #
    #     obj_flash.set_mapping('broadcast')
    #     # 广播禁用DTC更新
    #     obj_flash.control_dtc_setting(pcanuds.PCAN_UDS_2013.PUDS_SVC_PARAM_CDTCS_OFF)
    #     # 通讯控制，广播抑制应用报文和网络管理报文
    #     obj_flash.communication_control(pcanuds.PCAN_UDS_2013.PUDS_SVC_PARAM_CC_DRXTX,
    #                                     pcanuds.PCAN_UDS_2013.PUDS_SVC_PARAM_CC_FLAG_APPL | pcanuds.PCAN_UDS_2013.PUDS_SVC_PARAM_CC_FLAG_NWM)
    #     obj_flash.remove_mapping_by_can_id(broadcast_can_id)
    #
    #     obj_flash.set_mapping('tester')
    #     # 通过ID读数据，制造商备件编号
    #     obj_flash.read_data_by_id(pcanuds.PCAN_UDS_2013.PUDS_SVC_PARAM_DI_VMSPNDID)
    #     # 切换到编程会话
    #     obj_flash.diagnostic_session_control(pcanuds.PCAN_UDS_2013.PUDS_SVC_PARAM_DSC_ECUPS)
    #     # 安全访问，申请Seed
    #     obj_flash.security_access(pcanuds.PCAN_UDS_2013.PUDS_SVC_PARAM_SA_RSD_3)
    #     # 安全访问，发送Key
    #     data = [0x02, 0x02, 0x02, 0x02]
    #     obj_flash.security_access(pcanuds.PCAN_UDS_2013.PUDS_SVC_PARAM_SA_SK_4, data=data)
    #     # 擦写数据
    #     filepath = './xjmain.mot'
    #     obj_flash.erase_write_data(filepath)
    #     # 内存检查
    #     obj_flash.routine_control(pcanuds.PCAN_UDS_2013.PUDS_SVC_PARAM_RC_STR,
    #                               pcanuds.PCAN_UDS_2013.PUDS_SVC_PARAM_RC_RID_CPD_)
    #     # 硬复位
    #     obj_flash.ecu_reset(pcanuds.PCAN_UDS_2013.PUDS_SVC_PARAM_ER_HR)
    #     obj_flash.remove_mapping_by_can_id(tester_can_id)
    #
    #     # 显示报告并退出
    #     if obj_flash.transmission_error_number > 0:
    #         print_exec_detail("\n\nERROR: %d errors occurred." % obj_flash.transmission_error_number)
    #     else:
    #         print_exec_detail("\n\nALL Transmissions succeeded !")
    #     if obj_flash.response_error_number > 0:
    #         print_exec_detail("ERROR: %d response errors occurred." % obj_flash.response_error_number)
    #     else:
    #         print_exec_detail("ALL Responses expected !")
    # except Exception as e:
    #     print_exec_detail(f'异常 {e}')
    # else:
    #     pass
    # finally:
    #     # 关闭设备
    #     status = pcanuds.PCAN_UDS_2013.Uninitialize_2013(obj_flash.obj_puds, channel)
    #     if pcanuds.PCAN_UDS_2013.StatusIsOk_2013(obj_flash.obj_puds, status):
    #         print_exec_detail("\n\nSuccess Unitialize channel: %i" % status.value)
    #     else:
    #         print_exec_detail("\n\nFail Unitialize channel: %i" % status.value)
