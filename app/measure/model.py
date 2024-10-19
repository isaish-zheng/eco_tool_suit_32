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

from xba2l.a2l_lib import Module, Measurement, CompuMethod, CompuVtab

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
    测量选择表格中的数据项类
    '□' '√' '☆'

    :param is_selected: 选择标识，''或'☆'
    :type is_selected: str
    :param name: 测量对象名称
    :type name: str
    :param is_selected_20ms: 20ms刷新标识，'□'或'√'
    :type is_selected_20ms: str
    :param is_selected_100ms: 100ms刷新标识，'□'或'√'
    :type is_selected_100ms: str
    """
    is_selected: str = ''
    name: str = ''
    is_selected_20ms: str = '□'
    is_selected_100ms: str = '□'


@dataclass
class MonitorItem(object):
    """
    测量监视表格中的数据项类

    :param name: 测量对象名称
    :type name: str
    :param value: 物理值
    :type value: str
    :param rate: 速率
    :type rate: str
    :param unit: 单位
    :type unit: str

    :param idx_in_monitor_items: 当前对象在监视列表中的索引
    :type idx_in_monitor_items: int
    :param idx_in_a2l_measurements: 当前对象在原始测量对象列表中索引
    :type idx_in_a2l_measurements: int

    :param data_type: 数据类型
    :type data_type: str
    :param conversion: 转换方法
    :type conversion: str
    :param conversion_type: 转换类型('RAT_FUNC':数值类型；'TAB_VERB':映射表，例如枚举)
    :type conversion_type: str
    :param compu_tab_ref: 转换映射名称
    :type compu_tab_ref: str
    :param compu_vtab: 转换映射表
    :type compu_vtab: dict[int,str]
    :param coeffs: 转换系数(A,B,C,D,E,F)
    :type coeffs: Tuple[float, float, float, float, float, float]
    :param format: 显示格式(整数位数，小数位数)
    :type format: Tuple[int, int]

    :param element_size: odt元素大小
    :type element_size: int
    :param element_addr: odt元素地址
    :type element_addr: str

    :param daq_number: daq列表序号
    :type daq_number: int
    :param odt_number: odt列表序号
    :type odt_number: int
    :param element_number: odt元素序号
    :type element_number: int

    :param pid: odt列表对应的pid
    """
    name: str = ''  # 名称
    value: str = ''  # 物理值值
    rate: str = ''  # 速率
    unit: str = ''  # 单位

    idx_in_monitor_items: int = -1  # 监视列表中索引
    idx_in_a2l_measurements: int = -1  # 原始测量对象列表中索引

    data_type: str = ''  # 数据类型
    conversion: str = ''  # 转换方法
    conversion_type: str = ''  # 转换类型('RAT_FUNC':普通数值类型；'TAB_VERB':映射表，例如枚举)
    compu_tab_ref: str = ''  # 转换映射名称
    compu_vtab: dict[int,str] = None  # 转换映射表
    coeffs: Tuple[float, float, float, float, float, float] = ()  # 转换系数(A,B,C,D,E,F)
    format: Tuple[int, int] = ()  # 显示格式(整数位数，小数位数)

    element_size: int = -1  # odt元素大小
    element_addr: str = ''  # odt元素地址

    daq_number: int = -1  # daq列表序号,1:20ms;2:100ms
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
        'FLOAT32_IEEE': 4,
        'FLOAT64_IEEE': 8 # 不支持，此类型数据会被过滤掉
    }

    def __init__(self):
        """构造函数"""
        # 持久数据
        self.opened_pgm_filepath = ''  # 存储打开的PGM文件路径
        self.opened_a2l_filepath = ''  # 存储打开的A2L文件路径
        self.refresh_monitor_time_ms = '100'  # 存储监视表格数值刷新时间，默认100ms
        self.his_epk = ''  # 存储历史数据epk
        self.table_monitor_items: list[MonitorItem] = []  # 存储监视表格当前显示的数据项内容
        self.monitor_data_path: str = 'history.dat'  # 监视表格历史数据保存的文件路径

        self.obj_measure: eco_pccp.Measure = None  # 存储测量对象，用于与ecu通信

        self.entry_search_table_items = StringVar()  # 存储选择表格搜索框输入的内容

        self.ecu_epk = ''  # 存储ECU内存中的epk
        self.pgm_epk = ''  # 存储PGM文件解析后的epk
        self.a2l_epk_addr: str = ''  # 存储A2L文件解析后的epk地址,16进制
        self.a2l_epk = ''  # 存储A2L文件解析后的epk
        self.a2l_module: Module = None  # 存储A2L文件解析后的模块对象
        self.a2l_measurements: list[Measurement] = []  # 存储A2L文件解析后的测量对象列表
        self.a2l_conversions: list[CompuMethod] = []  # 存储A2L文件解析后的转换方法列表
        self.a2l_compu_vtabs: list[CompuVtab] = []  # 存储A2L文件解析后的转换映射列表

        # 下面列表中元素实际指向的内容是相同的，即filter_items由raw_items经浅拷贝得到
        self.table_measurement_raw_items: list[TableItem] = []  # 存储选择表格所有的数据项内容
        self.table_measurement_filter_items: list[TableItem] = []  # 存储选择表格当前显示的数据项内容（筛选后的数据项）

        # 存储daq列表配置字典{daq通道：{'first_pid':int,'odts_size':int},}
        # 例如{1: {'first_pid': 0x3c, 'odts_size': 0x20},
        #     2: {'first_pid': 0x78, 'odts_size': 0x30}}
        self.daqs_cfg: dict[int, dict[str, int]] = {}
        # 存储daq列表的数据项内容{daq_number: {odt_number: [item, ...]}}
        # 例如{ 1: {0: [item0, item1],
        #          1: [item2, item3, item4]
        #         },
        #      2: {0: [item5, item6, item7],
        #          1: [item8, item9, item10, item11]
        #         }
        #     }
        self.daqs: dict[int, dict[int, list[MonitorItem]]] = {}

        self.q = Queue()  # 存储线程间通信的队列,待显示数据
