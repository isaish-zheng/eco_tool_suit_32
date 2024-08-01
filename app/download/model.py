#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : ZYD
# @Time    : 2024/7/11 上午9:56
# @version : V1.0.0
# @function:


##############################
# Module imports
##############################

from tkinter import BooleanVar, StringVar


##############################
# Model API function declarations
##############################

class DownloadModel(object):
    """
    下载界面的数据模型
    """
    def __init__(self):
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
    def mode_protocol(self):
        return self.combobox_mode_protocol.get().strip()

    @mode_protocol.setter
    def mode_protocol(self, value: str):
        self.combobox_mode_protocol.set(value.strip())

    # device
    @property
    def device_type(self):
        return self.combobox_device_type.get().strip()

    @device_type.setter
    def device_type(self, value: str):
        self.combobox_device_type.set(value.strip())

    @property
    def device_channel(self):
        return self.combobox_device_channel.get().strip()

    @device_channel.setter
    def device_channel(self, value: str):
        self.combobox_device_channel.set(''.join(['0x', value[2:].upper()]))

    # uds
    @property
    def uds_baudrate(self):
        return self.combobox_baudrate.get().strip()

    @uds_baudrate.setter
    def uds_baudrate(self, value: str):
        self.combobox_baudrate.set(value.strip())

    @property
    def uds_request_id(self):
        return self.entry_request_id.get().strip()

    @uds_request_id.setter
    def uds_request_id(self, value: str):
        self.entry_request_id.set(''.join(['0x', value[2:].upper()]))

    @property
    def uds_response_id(self):
        return self.entry_response_id.get().strip()

    @uds_response_id.setter
    def uds_response_id(self, value: str):
        self.entry_response_id.set(''.join(['0x', value[2:].upper()]))

    @property
    def uds_function_id(self):
        return self.entry_function_id.get().strip()

    @uds_function_id.setter
    def uds_function_id(self, value: str):
        self.entry_function_id.set(''.join(['0x', value[2:].upper()]))

    @property
    def uds_is_show_map_detail(self):
        return self.check_uds_is_show_map_detail.get()

    @uds_is_show_map_detail.setter
    def uds_is_show_map_detail(self, value: bool):
        self.check_uds_is_show_map_detail.set(value)

    @property
    def uds_is_show_msg_detail(self):
        return self.check_uds_is_show_msg_detail.get()

    @uds_is_show_msg_detail.setter
    def uds_is_show_msg_detail(self, value: bool):
        self.check_uds_is_show_msg_detail.set(value)

    @property
    def uds_opened_pgm_filepath(self):
        return self.opened_pgm_filepath.strip()

    @uds_opened_pgm_filepath.setter
    def uds_opened_pgm_filepath(self, value: str):
        self.opened_pgm_filepath = value.strip()

    @property
    def uds_opened_seed2key_filepath(self):
        return self.opened_seed2key_filepath.strip()

    @uds_opened_seed2key_filepath.setter
    def uds_opened_seed2key_filepath(self, value: str):
        self.opened_seed2key_filepath = value.strip()

    # ccp
    @property
    def ccp_baudrate(self):
        return self.combobox_baudrate.get().strip()

    @ccp_baudrate.setter
    def ccp_baudrate(self, value: str):
        self.combobox_baudrate.set(value.strip())

    @property
    def ccp_request_id(self):
        return self.entry_request_id.get().strip()

    @ccp_request_id.setter
    def ccp_request_id(self, value: str):
        self.entry_request_id.set(''.join(['0x', value[2:].upper()]))

    @property
    def ccp_response_id(self):
        return self.entry_response_id.get().strip()

    @ccp_response_id.setter
    def ccp_response_id(self, value: str):
        self.entry_response_id.set(''.join(['0x', value[2:].upper()]))

    @property
    def ccp_ecu_addr(self):
        return self.entry_function_id.get().strip()

    @ccp_ecu_addr.setter
    def ccp_ecu_addr(self, value: str):
        self.entry_function_id.set(''.join(['0x', value[2:].upper()]))

    @property
    def ccp_is_show_map_detail(self):
        return self.check_ccp_is_show_map_detail.get()

    @ccp_is_show_map_detail.setter
    def ccp_is_show_map_detail(self, value: bool):
        self.check_ccp_is_show_map_detail.set(value)

    @property
    def ccp_is_show_msg_detail(self):
        return self.check_ccp_is_show_msg_detail.get()

    @ccp_is_show_msg_detail.setter
    def ccp_is_show_msg_detail(self, value: bool):
        self.check_ccp_is_show_msg_detail.set(value)

    @property
    def ccp_opened_pgm_filepath(self):
        return self.opened_pgm_filepath.strip()

    @ccp_opened_pgm_filepath.setter
    def ccp_opened_pgm_filepath(self, value: str):
        self.opened_pgm_filepath = value.strip()

    @property
    def ccp_opened_seed2key_filepath(self):
        return self.opened_seed2key_filepath.strip()

    @ccp_opened_seed2key_filepath.setter
    def ccp_opened_seed2key_filepath(self, value: str):
        self.opened_seed2key_filepath = value.strip()
