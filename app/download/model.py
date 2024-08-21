#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : ZYD
# @Time    : 2024/7/11 上午9:56
# @version : V1.0.0
# @function:

"""
下载程序界面(mvc)的model模块

"""

##############################
# Module imports
##############################

from tkinter import BooleanVar, StringVar


##############################
# Model API function declarations
##############################

class DownloadModel(object):
    """
    负责保存下载程序界面所需的数据

    """
    def __init__(self):
        """
        构造函数

        """
        self.PROTOCAOL = ('uds',
                          'ccp')
        self.DEVICES = ('PeakCAN',)
        self.CHANNELS = ('0x1', '0x2')
        self.BAUDRATES = ('50kbps',
                          '100kbps',
                          '125kbps',
                          '250kbps',
                          '500kbps',
                          '800kbps',
                          '1000kbps')

        self.combobox_mode_protocol = StringVar()
        self.combobox_device_type = StringVar()
        self.combobox_device_channel = StringVar()
        self.combobox_baudrate = StringVar()
        self.entry_request_id = StringVar()
        self.entry_response_id = StringVar()
        self.entry_function_id = StringVar()
        self.check_uds_is_show_map_detail = BooleanVar()
        self.check_uds_is_show_msg_detail = BooleanVar()
        self.check_ccp_is_show_map_detail = BooleanVar()
        self.check_ccp_is_show_msg_detail = BooleanVar()

        # uds和ccp共用路径变量
        self.opened_pgm_filepath = ''
        self.opened_seed2key_filepath = ''

    # mode
    @property
    def mode_protocol(self) -> str:
        """
        当前刷写协议

        :return: 当前刷写协议
        :rtype: str
        """
        return self.combobox_mode_protocol.get().strip()

    @mode_protocol.setter
    def mode_protocol(self, value: str) -> None:
        """
        设置当前刷写协议

        :param value: 协议名称
        :type value: str
        """
        self.combobox_mode_protocol.set(value.strip())

    # device
    @property
    def device_type(self) -> str:
        """
        当前can设备类型

        :return: 当前can设备类型
        :rtype: str
        """
        return self.combobox_device_type.get().strip()

    @device_type.setter
    def device_type(self, value: str) -> None:
        """
        设置当前can设备类型

        :param value: can设备类型
        :type value: str
        """
        self.combobox_device_type.set(value.strip())

    @property
    def device_channel(self) -> str:
        """
        当前can设备通道

        :return: 当前can设备通道
        :rtype: str
        """
        return self.combobox_device_channel.get().strip()

    @device_channel.setter
    def device_channel(self, value: str) -> None:
        """
        设置当前can设备通道

        :param value: can设备通道
        :type value: str
        """
        self.combobox_device_channel.set(''.join(['0x', value[2:].upper()]))

    # uds
    @property
    def uds_baudrate(self) -> str:
        """
        当前uds刷写波特率

        :return: 当前uds刷写波特率
        :rtype: str
        """
        return self.combobox_baudrate.get().strip()

    @uds_baudrate.setter
    def uds_baudrate(self, value: str) -> None:
        """
        设置当前uds刷写波特率

        :param value: 波特率
        :type value: str
        """
        self.combobox_baudrate.set(value.strip())

    @property
    def uds_request_id(self) -> str:
        """
        当前uds刷写请求id

        :return: 当前uds刷写请求id
        :rtype: str
        """
        return self.entry_request_id.get().strip()

    @uds_request_id.setter
    def uds_request_id(self, value: str) -> None:
        """
        设置当前uds刷写请求id

        :param value: 请求id
        :type value: str
        """
        self.entry_request_id.set(''.join(['0x', value[2:].upper()]))

    @property
    def uds_response_id(self) -> str:
        """
        当前uds刷写响应id

        :return: 当前uds刷写响应id
        :rtype: str
        """
        return self.entry_response_id.get().strip()

    @uds_response_id.setter
    def uds_response_id(self, value: str) -> None:
        """
        设置当前uds刷写响应id

        :param value: 响应id
        :type value: str
        """
        self.entry_response_id.set(''.join(['0x', value[2:].upper()]))

    @property
    def uds_function_id(self) -> str:
        """
        当前uds刷写功能id

        :return: 当前uds刷写功能id
        :rtype: str
        """
        return self.entry_function_id.get().strip()

    @uds_function_id.setter
    def uds_function_id(self, value: str) -> None:
        """
        设置当前uds刷写功能id

        :param value: 功能id
        :type value: str
        """
        self.entry_function_id.set(''.join(['0x', value[2:].upper()]))

    @property
    def uds_is_show_map_detail(self) -> bool:
        """
        是否显示uds刷写过程中的id映射详情

        :return: 是否显示uds刷写过程中的id映射详情
        :rtype: bool
        """
        return self.check_uds_is_show_map_detail.get()

    @uds_is_show_map_detail.setter
    def uds_is_show_map_detail(self, value: bool) -> None:
        """
        设置是否显示uds刷写过程中的id映射详情

        :param value: True or False
        :type value: bool
        """
        self.check_uds_is_show_map_detail.set(value)

    @property
    def uds_is_show_msg_detail(self) -> bool:
        """
        是否显示uds刷写过程中的消息详情

        :return: 是否显示uds刷写过程中的消息详情
        :rtype: bool
        """
        return self.check_uds_is_show_msg_detail.get()

    @uds_is_show_msg_detail.setter
    def uds_is_show_msg_detail(self, value: bool) -> None:
        """
        设置是否显示uds刷写过程中的消息详情

        :param value: True or False
        :type value: bool
        """
        self.check_uds_is_show_msg_detail.set(value)

    @property
    def uds_opened_pgm_filepath(self) -> str:
        """
        当前打开的uds刷写的pgm文件路径

        :return: 当前打开的uds刷写的pgm文件路径
        :rtype: str
        """
        return self.opened_pgm_filepath.strip()

    @uds_opened_pgm_filepath.setter
    def uds_opened_pgm_filepath(self, value: str) -> None:
        """
        设置当前打开的uds刷写的pgm文件路径

        :param value: pgm文件路径
        :type value: str
        """
        self.opened_pgm_filepath = value.strip()

    @property
    def uds_opened_seed2key_filepath(self) -> str:
        """
        当前打开的uds刷写的seed2key文件路径

        :return: 当前打开的uds刷写的seed2key文件路径
        :rtype: str
        """
        return self.opened_seed2key_filepath.strip()

    @uds_opened_seed2key_filepath.setter
    def uds_opened_seed2key_filepath(self, value: str) -> None:
        """
        设置当前打开的uds刷写的seed2key文件路径

        :param value: seed2key文件路径
        :type value: str
        """
        self.opened_seed2key_filepath = value.strip()

    # ccp
    @property
    def ccp_baudrate(self) -> str:
        """
        当前ccp刷写波特率

        :return: 当前ccp刷写波特率
        :rtype: str
        """
        return self.combobox_baudrate.get().strip()

    @ccp_baudrate.setter
    def ccp_baudrate(self, value: str) -> None:
        """
        设置当前ccp刷写波特率

        :param value: 波特率
        :type value: str
        """
        self.combobox_baudrate.set(value.strip())

    @property
    def ccp_request_id(self) -> str:
        """
        当前ccp刷写的请求id

        :return: 当前ccp刷写的请求id
        :rtype: str
        """
        return self.entry_request_id.get().strip()

    @ccp_request_id.setter
    def ccp_request_id(self, value: str) -> None:
        """
        设置当前ccp刷写的请求id

        :param value: 请求id
        :type value: str
        """
        self.entry_request_id.set(''.join(['0x', value[2:].upper()]))

    @property
    def ccp_response_id(self) -> str:
        """
        当前ccp刷写的响应id

        :return: 当前ccp刷写的响应id
        :rtype: str
        """
        return self.entry_response_id.get().strip()

    @ccp_response_id.setter
    def ccp_response_id(self, value: str) -> None:
        """
        设置当前ccp刷写的响应id

        :param value: 响应id
        :type value: str
        """
        self.entry_response_id.set(''.join(['0x', value[2:].upper()]))

    @property
    def ccp_ecu_addr(self) -> str:
        """
        当前ccp刷写的ecu地址

        :return: 当前ccp刷写的ecu地址
        :rtype: str
        """
        return self.entry_function_id.get().strip()

    @ccp_ecu_addr.setter
    def ccp_ecu_addr(self, value: str) -> None:
        """
        设置当前ccp刷写的ecu地址

        :param value: ecu地址
        :type value: str
        """
        self.entry_function_id.set(''.join(['0x', value[2:].upper()]))

    @property
    def ccp_is_show_map_detail(self) -> bool:
        """
        是否显示ccp刷写时的id映射详情（未使用）

        :return: 是否显示ccp刷写时的id映射详情（未使用）
        :rtype: bool
        """
        return self.check_ccp_is_show_map_detail.get()

    @ccp_is_show_map_detail.setter
    def ccp_is_show_map_detail(self, value: bool) -> None:
        """
        设置是否显示ccp刷写时的id映射详情（未使用）

        :param value: True or False
        :type value: bool
        """
        self.check_ccp_is_show_map_detail.set(value)

    @property
    def ccp_is_show_msg_detail(self) -> bool:
        """
        是否显示ccp刷写时的消息详情（未使用）

        :return: 是否显示ccp刷写时的消息详情（未使用）
        :rtype: bool
        """
        return self.check_ccp_is_show_msg_detail.get()

    @ccp_is_show_msg_detail.setter
    def ccp_is_show_msg_detail(self, value: bool) -> None:
        """
        设置是否显示ccp刷写时的消息详情（未使用）

        :param value: True or False
        :type value: bool
        """
        self.check_ccp_is_show_msg_detail.set(value)

    @property
    def ccp_opened_pgm_filepath(self) -> str:
        """
        当前ccp刷写的pgm文件路径

        :return: 当前ccp刷写的pgm文件路径
        :rtype: str
        """
        return self.opened_pgm_filepath.strip()

    @ccp_opened_pgm_filepath.setter
    def ccp_opened_pgm_filepath(self, value: str) -> None:
        """
        设置当前ccp刷写的pgm文件路径

        :param value: pgm文件路径
        :type value: str
        """
        self.opened_pgm_filepath = value.strip()

    @property
    def ccp_opened_seed2key_filepath(self) -> str:
        """
        当前ccp刷写的seed2key文件路径

        :return: 当前ccp刷写的seed2key文件路径
        :rtype: str
        """
        return self.opened_seed2key_filepath.strip()

    @ccp_opened_seed2key_filepath.setter
    def ccp_opened_seed2key_filepath(self, value: str) -> None:
        """
        设置当前ccp刷写的seed2key文件路径

        :param value: seed2key文件路径
        :type value: str
        """
        self.opened_seed2key_filepath = value.strip()
