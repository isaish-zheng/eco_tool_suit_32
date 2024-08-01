#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : ZYD
# @Time    : 2024/7/12 上午8:34
# @version : V1.0.0
# @function:
from queue import Queue
##############################
# Module imports
##############################

from tkinter import StringVar
from dataclasses import dataclass
from typing import List, Dict, Tuple

from xba2l.a2l_lib import Module, Measurement, CompuMethod

from eco import eco_pccp
from utils import singleton


##############################
# Constant definitions
##############################


##############################
# Model API function declarations
##############################

@dataclass
class TableItem(object):
    """
    测量选择表格数据项类
    '□' '√' '☆'
    """
    is_selected: str = ''
    name: str = ''
    is_selected_20ms: str = '□'
    is_selected_100ms: str = '□'


@dataclass
class MonitorItem(object):
    """
    测量监视表格数据项类
    """
    name: str = ''  # 名称
    value: str = ''  # 物理值值
    rate: str = ''  # 速率
    unit: str = ''  # 单位

    idx_in_monitor_items: int = -1  # 监视列表中索引
    idx_in_a2l_measurements: int = -1  # 原始测量对象列表中索引

    data_type: str = ''  # 数据类型
    conversion: str = ''  # 转换方法
    coeffs: Tuple[float, float, float, float, float, float] = ()  # 转换系数(A,B,C,D,E,F)
    format: Tuple[int, int] = ()  # 显示格式(正数位数，小数位数)

    element_size: int = -1  # odt元素大小
    element_addr: str = ''  # odt元素地址

    daq_number: int = -1  # daq列表序号
    odt_number: int = -1  # odt列表序号
    element_number: int = -1  # odt元素序号

    pid: str = ''  # odt列表对应的pid


##############################
# Model API function declarations
##############################

# @singleton
class MeasureModel(object):
    """
    测量界面的数据模型
    """

    ASAP2_TYPE_SIZE = {
        'UBYTE': 1,
        'SBYTE': 1,
        'UWORD': 2,
        'SWORD': 2,
        'ULONG': 4,
        'SLONG': 4,
        'FLOAT32_IEEE': 4
    }

    def __init__(self):
        # 持久数据
        self.opened_pgm_filepath = ''  # 存储打开的PGM文件路径
        self.opened_a2l_filepath = ''  # 存储打开的A2L文件路径
        self.refresh_monitor_time_ms = '100'  # 存储监视表格数值刷新时间，默认100ms
        self.his_epk = ''  # 存储历史数据epk
        self.table_monitor_items: List[MonitorItem] = []  # 存储监视表格当前显示的数据项内容
        self.monitor_data_path: str = 'history.dat'  # 监视表格历史数据保存的文件路径

        self.obj_measure: eco_pccp.Measure = None  # 存储测量对象，用于与ecu通信

        self.entry_search_table_items = StringVar()  # 存储选择表格搜索框输入的内容

        self.ecu_epk = ''  # 存储ECU内存中的epk
        self.pgm_epk = ''  # 存储PGM文件解析后的epk
        self.a2l_epk_addr: str = ''  # 存储A2L文件解析后的epk地址,16进制
        self.a2l_epk = ''  # 存储A2L文件解析后的epk
        self.a2l_module: Module = None  # 存储A2L文件解析后的模块对象
        self.a2l_measurements: List[Measurement] = []  # 存储A2L文件解析后的测量对象列表
        self.a2l_conversions: List[CompuMethod] = []  # 存储A2L文件解析后的转换方法列表

        # 下面列表中元素实际指向的内容是相同的，即filter_items由raw_items经浅拷贝得到
        self.table_measurement_raw_items: List[TableItem] = []  # 存储选择表格所有的数据项内容
        self.table_measurement_filter_items: List[TableItem] = []  # 存储选择表格当前显示的数据项内容（筛选后的数据项）

        self.daqs_cfg: Dict[int, Dict[str, int]] = {}  # 存储daq列表配置字典{daq通道：{'first_pid':int,'odts_size':int},}
        self.daqs: Dict[int, Dict[int, List[MonitorItem]]] = {}  # 存储daq列表的数据项内容

        self.q = Queue()  # 存储线程间通信的队列,待显示数据
