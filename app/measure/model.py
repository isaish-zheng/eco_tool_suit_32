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

from xba2l.a2l_lib import Module, MemorySegment, Measurement, CompuMethod, CompuVtab, Characteristic, RecordLayout

from eco import eco_pccp
from srecord import Srecord
from utils import singleton


##############################
# Constant definitions
##############################


##############################
# Model API function declarations
##############################
@dataclass(slots=True)
class RecordLayoutElement:
    """
    标定变量的存储结构

    :param name: 名称
    :type name: str
    :param type: 类型
    :type type: str
    :param position: 位置
    :type position: int
    :param data_type: 数据类型
    :type data_type: str
    :param address_type: 寻址方式
    :type address_type: str
    :param index_mode: 索引模式
    :type index_mode: str
    """
    name: str = '' # 名称
    type: str = '' # 类型，FNC_VALUES、AXIS_PTS_X
    position: int = -1 # 位置
    data_type: str = '' # 数据类型
    address_type: str = '' # 寻址方式，DIRECT
    index_mode: str = '' # 索引模式，COLUMN_DIR、INDEX_INCR、


@dataclass(slots=True)
class SelectMeasureItem(object):
    """
    测量选择表格中的数据项类
    '□' '√' '☆' '★'

    :param is_selected: 选择状态标识，''-未选择；'☆'-已选未确定；'★'-已选已确定
    :type is_selected: str
    :param name: 测量对象名称
    :type name: str
    :param is_selected_20ms: 20ms刷新通道选择标识，'□'-未选择；'√'-选择
    :type is_selected_20ms: str
    :param is_selected_100ms: 100ms刷新通道选择标识，'□'或'√'
    :type is_selected_100ms: str
    """
    is_selected: str = ''
    name: str = ''
    is_selected_20ms: str = '□'
    is_selected_100ms: str = '□'


@dataclass(slots=True)
class SelectCalibrateItem(object):
    """
    标定选择表格中的数据项类
    '□' '√' '☆' '★'

    :param name: 标定对象名称
    :type name: str
    :param is_selected: 选择状态标识，''-未选择；'☆'-已选未确定；'★'-已选已确定
    :type is_selected: str
    :param is_selected_check: 选择标识，'□'-未选择；'√'-选择
    :type is_selected_check: str
    """
    is_selected: str = ''
    name: str = ''
    is_selected_check: str = '□'


@dataclass(slots=True)
class MeasureItem(object):
    """
    测量表格中的数据项类

    :param name: 测量对象名称
    :type name: str
    :param value: 物理值
    :type value: str
    :param rate: 速率
    :type rate: str
    :param unit: 单位
    :type unit: str

    :param idx_in_table_measure_items: 当前对象在测量表格列表中的索引
    :type idx_in_table_measure_items: int
    :param idx_in_a2l_measurements: 当前对象在A2L测量对象列表中索引
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
    :type coeffs: tuple[float, float, float, float, float, float]
    :param format: 显示格式(整数位数，小数位数)
    :type format: tuple[int, int]

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

    idx_in_table_measure_items: int = -1  # 当前对象在测量表格列表中的索引
    idx_in_a2l_measurements: int = -1  # 当前对象在A2L测量对象列表中索引

    data_type: str = ''  # 数据类型
    conversion: str = ''  # 转换方法
    conversion_type: str = ''  # 转换类型(转换方法中的conversion_type属性，'RAT_FUNC':普通数值类型；'TAB_VERB':映射表，例如枚举)
    compu_tab_ref: str = ''  # 转换映射名称，若转换类型为TAB_VERB则存在
    compu_vtab: dict[int,str] = None  # 转换映射表
    coeffs: tuple[float, float, float, float, float, float] = ()  # 转换系数(A,B,C,D,E,F)，若转换类型为RAT_FUNC则存在
    format: tuple[int, int] = ()  # 显示格式(整数位数，小数位数)

    element_size: int = -1  # odt元素大小
    element_addr: str = ''  # odt元素地址

    daq_number: int = -1  # daq列表序号,1:20ms;2:100ms
    odt_number: int = -1  # odt列表序号
    element_number: int = -1  # odt元素序号

    pid: str = ''  # odt列表对应的pid


@dataclass(slots=True)
class CalibrateItem(object):
    """
    标定表格中的数据项类

    :param name: 标定对象名称
    :type name: str
    :param value: 物理值
    :type value: str
    :param unit: 单位
    :type unit: str

    :param idx_in_table_calibrate_items: 当前对象在标定表格列表中的索引
    :type idx_in_table_calibrate_items: int
    :param idx_in_a2l_calibrations: 当前对象在A2L标定对象列表中索引
    :type idx_in_a2l_calibrations: int

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
    :type coeffs: tuple[float, float, float, float, float, float]
    :param format: 显示格式(整数位数，小数位数)
    :type format: tuple[int, int]

    :param data_size: 数据大小
    :type data_size: int
    :param data_addr: 数据地址
    :type data_addr: str
    :param lower_limit: 物理值下限
    :type lower_limit: float
    :param upper_limit: 物理值上限
    :type upper_limit: float
    :param data: value字段的原始数据序列
    :type data: bytes

    :param cal_type: 标定变量类型，有VALUE、CURVE和MAP，三者之间的区别在干该标定变量是否含有坐标轴(AXIS_DESCR)
    :type cal_type: str
    :param record_layout: 标定变量的物理存储结构名称（一维，二维表，三维表等）
    :type record_layout: RecordLayoutElement
    """
    name: str = ''  # 名称
    value: str = ''  # 物理值
    unit: str = ''  # 单位

    idx_in_table_calibrate_items: int = -1  # 当前对象在标定表格列表中的索引
    idx_in_a2l_calibrations: int = -1  # 当前对象在A2L标定对象列表中索引

    data_type: str = ''  # 数据类型
    conversion: str = ''  # 转换方法名称
    conversion_type: str = ''  # 转换类型(转换方法中的conversion_type属性，'RAT_FUNC':普通数值类型；'TAB_VERB':映射表，例如枚举)
    compu_tab_ref: str = ''  # 转换映射名称，若转换类型为TAB_VERB则存在
    compu_vtab: dict[int, str] = None  # 转换映射表
    coeffs: tuple[float, float, float, float, float, float] = ()  # 转换系数(A,B,C,D,E,F)，若转换类型为RAT_FUNC则存在
    format: tuple[int, int] = ()  # 显示格式(整数位数，小数位数)

    data_size: int = -1  # 数据大小
    data_addr: str = ''  # 数据地址
    lower_limit: float = None  # 物理值下限
    upper_limit: float = None  # 物理值上限
    data: bytes = b''  # value字段的原始数据序列

    cal_type: str = ''  # 标定变量类型，有VALUE、CURVE和MAP，三者之间的区别在干该标定变量是否含有坐标轴(AXIS_DESCR)
    record_layout: RecordLayoutElement = None  # 标定变量的物理存储结构名称（一维，二维表，三维表等）


##############################
# Model API function declarations
##############################

# @singleton
class MeasureModel(object):
    """
    测量标定界面的数据模型
    """

    ASAP2_TYPE_SIZE = {
        'UBYTE': 1,
        'SBYTE': 1,
        'UWORD': 2,
        'SWORD': 2,
        'ULONG': 4,
        'SLONG': 4,
        'FLOAT32_IEEE': 4,
        'FLOAT64_IEEE': 8 # 不支持，测量时此类型数据会被过滤掉
    }

    def __init__(self):
        """构造函数"""
        # 持久数据
        self.opened_pgm_filepath = ''  # 存储打开的PGM文件路径
        self.opened_a2l_filepath = ''  # 存储打开的A2L文件路径
        self.table_history_filepath: str = 'history.dat'  # 测量标定表格历史数据保存的文件路径
        self.refresh_operate_measure_time_ms = '100'  # 存储测量表格数值刷新时间，默认100ms
        self.history_epk = ''  # 存储历史数据epk
        self.table_measure_items: list[MeasureItem] = []  # 存储测量表格当前显示的数据项内容
        self.table_calibrate_items: list[CalibrateItem] = []  # 存储标定表格当前显示的数据项内容

        self.obj_measure: eco_pccp.Measure = None  # 存储测量对象，用于与ecu通信
        self.obj_srecord: Srecord = None  # 存储SRecord对象，用于解析PGM文件

        self.entry_search_measure_item = StringVar()  # 存储测量选择数据项表格搜索框输入的内容
        self.entry_search_calibrate_item = StringVar()  # 存储选择表格搜索框输入的内容

        self.ecu_epk = ''  # 存储ECU内存中的epk
        self.pgm_epk = ''  # 存储PGM文件解析后的epk
        self.a2l_epk_addr: str = ''  # 存储A2L文件解析后的epk地址,16进制
        self.a2l_epk = ''  # 存储A2L文件解析后的epk
        self.a2l_module: Module = None  # 存储A2L文件解析后的模块对象
        self.a2l_memory_code: MemorySegment = None # 存储A2L文件解析后的代码段内存段对象
        self.a2l_memory_epk_data: MemorySegment = None # 存储A2L文件解析后的epk数据内存段对象
        self.a2l_memory_ram_cal: MemorySegment = None # 存储A2L文件解析后的ram标定内存段对象
        self.a2l_memory_rom_cal: MemorySegment = None # 存储A2L文件解析后的rom标定内存段对象
        self.a2l_measurements: list[Measurement] = []  # 存储A2L文件解析后的测量对象列表
        self.a2l_calibrations: list[Characteristic] = []  # 存储A2L文件解析后的标定对象列表

        self.a2l_conversions: list[CompuMethod] = []  # 存储A2L文件解析后的转换方法列表
        self.a2l_compu_vtabs: list[CompuVtab] = []  # 存储A2L文件解析后的转换映射列表
        self.a2l_record_layouts: list[RecordLayout] = []  # 存储A2L文件解析后的标定变量存储结构

        # 下面列表中元素实际指向的内容是相同的，即filter_items由raw_items经浅拷贝得到
        self.table_select_measure_raw_items: list[SelectMeasureItem] = []  # 存储测量选择数据项表格所有的数据项内容
        self.table_select_measure_filter_items: list[SelectMeasureItem] = []  # 存储测量选择表格当前显示的数据项内容（筛选后的数据项）
        self.table_select_calibrate_raw_items: list[SelectCalibrateItem] = []  # 存储选择标定数据项表格所有的数据项内容
        self.table_select_calibrate_filter_items: list[SelectCalibrateItem] = []  # 存储选择表格当前显示的数据项内容（筛选后的数据项）

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
        self.daqs: dict[int, dict[int, list[MeasureItem]]] = {}

        # 存储线程间通信的队列,测量时的待显示数据
        self.q = Queue()
