#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : ZYD
# @Time    : 2024/7/12 上午8:34
# @version : V1.0.0
# @function:


##############################
# Module imports
##############################
from dataclasses import dataclass
from enum import Enum
from queue import Queue
from tkinter import StringVar

from xba2l.a2l_lib import Module, MemorySegment, Measurement, Characteristic, \
    CompuMethod, CompuVtab,  RecordLayout, AxisPts

from eco import eco_pccp
from srecord import Srecord


##############################
# Constant definitions
##############################


##############################
# Type definitions
##############################
class ASAP2EnumDataType(Enum):
    """
    用于描述基本数据类型

    Attributes:
        UBYTE (int): 无符号整型1字节
        SBYTE (int): 有符号整型1字节
        UWORD (int): 无符号整型2字节
        SWORD (int): 有符号整型2字节
        ULONG (int): 无符号整型4字节
        SLONG (int): 有符号整型4字节
        FLOAT32_IEEE (int): IEEE 32位浮点数
        FLOAT64_IEEE (int): IEEE 64位浮点数
    """
    UBYTE: int = 0
    SBYTE: int = 1
    UWORD: int = 2
    SWORD: int = 3
    ULONG: int = 4
    SLONG: int = 5
    FLOAT32_IEEE: int = 6
    FLOAT64_IEEE: int = 7

    @classmethod
    def creat(cls, v: str | int):
        """
        通过名称或数值创建枚举

        Args:
            v (str | int): 名称或数值
        Returns:
            ASAP2EnumDataType: 枚举
        Raises:
            ValueError: 无效输入值
            TypeError: 无效输入类型
        """
        if isinstance(v, int):
            for attr in cls:
                if attr.value == v:
                    return attr
            raise ValueError(f"Invalid input value in {cls.__name__}: {v}")
        elif isinstance(v, str):
            for attr in cls:
                if attr.name == v:
                    return attr
            raise ValueError(f"Invalid input name in {cls.__name__}: {v}")
        else:
            raise TypeError(f"Invalid input type in {cls.__name__}: {v}")

    @classmethod
    def get_size(cls, v: str) -> int:
        """
        获取数据类型的大小(字节)

        Args:
            v (str): 数据类型名称
        Returns:
            int: 大小
        Raises:
            TypeError: 无效输入类型
        """
        if v in ("UBYTE", "SBYTE"):
            return 1
        elif v in ("UWORD", "SWORD"):
            return 2
        elif v in ("ULONG", "SLONG", "FLOAT32_IEEE"):
            return 4
        elif v in ("FLOAT64_IEEE",):
            return 8
        raise TypeError(f"Invalid input type in {cls.__name__}: {v}")


class ASAP2EnumAddrType(Enum):
    """
    用于描述表值或轴点值寻址的枚举

    Attributes:
        PBYTE (int): 相关内存位置有一个1字节指针指向该表值或轴点值
        PWORD (int): 相关内存位置有一个2字节指针指向该表值或轴点值
        PLONG (int): 相关内存位置有一个4字节指针指向该表值或轴点值
        DIRECT (int): 相关的存储位置有第一个表格值或轴点值，所有其他存储位置均跟随递增地址
    """
    PBYTE: int = 1
    PWORD: int = 2
    PLONG: int = 4
    DIRECT: int = 0

    @classmethod
    def creat(cls, v: str | int):
        """
        通过名称或数值值创建枚举

        Args:
            v (str | int): 名称或数值
        Returns:
            ASAP2EnumAddrType: 枚举
        Raises:
            ValueError: 无效输入值
            TypeError: 无效输入类型
        """
        if isinstance(v, int):
            for attr in cls:
                if attr.value == v:
                    return attr
            raise ValueError(f"Invalid input value in {cls.__name__}: {v}")
        elif isinstance(v, str):
            for attr in cls:
                if attr.name == v:
                    return attr
            raise ValueError(f"Invalid input name in {cls.__name__}: {v}")
        else:
            raise TypeError(f"Invalid input type in {cls.__name__}: {v}")


class ASAP2EnumByteOrder(Enum):
    """
    用于描述字节顺序的枚举

    Attributes:
        MSB_FIRST (int): 大端序
        MSB_LAST (int): 小端序
    """
    MSB_FIRST: int = 0
    MSB_LAST: int = 1

    @classmethod
    def creat(cls, v: str | int):
        """
        通过名称或数值值创建枚举

        Args:
            v (str | int): 名称或数值
        Returns:
            ASAP2EnumByteOrder: 枚举
        Raises:
            ValueError: 无效输入值
            TypeError: 无效输入类型
        """
        if isinstance(v, int):
            for attr in cls:
                if attr.value == v:
                    return attr
            raise ValueError(f"Invalid input value in {cls.__name__}: {v}")
        elif isinstance(v, str):
            for attr in cls:
                if attr.name == v:
                    return attr
            raise ValueError(f"Invalid input name in {cls.__name__}: {v}")
        else:
            raise TypeError(f"Invalid input type in {cls.__name__}: {v}")


class ASAP2EnumIndexOrder(Enum):
    """
    用于描述轴点序列的枚举

    Attributes:
        INDEX_INCR (int): 随地址增加而增加索引
        INDEX_DECR (int): 随地址增加而减少索引
    """
    INDEX_INCR: int = 0
    INDEX_DECR: int = 1

    @classmethod
    def creat(cls, v: str | int):
        """
        通过名称或数值值创建枚举

        Args:
            v (str | int): 名称或数值
        Returns:
            ASAP2EnumIndexOrder: 枚举
        Raises:
            ValueError: 无效输入值
            TypeError: 无效输入类型
        """
        if isinstance(v, int):
            for attr in cls:
                if attr.value == v:
                    return attr
            raise ValueError(f"Invalid input value in {cls.__name__}: {v}")
        elif isinstance(v, str):
            for attr in cls:
                if attr.name == v:
                    return attr
            raise ValueError(f"Invalid input name in {cls.__name__}: {v}")
        else:
            raise TypeError(f"Invalid input type in {cls.__name__}: {v}")


class ASAP2EnumIndexMode(Enum):
    """
    用于描述二维表值值映射到一维地址空间

    Attributes:
        COLUMN_DIR (int): 列优先
        ROW_DIR (int): 行优先
    """
    COLUMN_DIR: int = 0
    ROW_DIR: int = 1

    @classmethod
    def creat(cls, v: str | int):
        """
        通过名称或数值值创建枚举

        Args:
            v (str | int): 名称或数值
        Returns:
            ASAP2EnumIndexMode: 枚举
        Raises:
            ValueError: 无效输入值
            TypeError: 无效输入类型
        """
        if isinstance(v, int):
            for attr in cls:
                if attr.value == v:
                    return attr
            raise ValueError(f"Invalid input value in {cls.__name__}: {v}")
        elif isinstance(v, str):
            for attr in cls:
                if attr.name == v:
                    return attr
            raise ValueError(f"Invalid input name in {cls.__name__}: {v}")
        else:
            raise TypeError(f"Invalid input type in {cls.__name__}: {v}")


class ASAP2EnumCalibrateType(Enum):
    """
    用于描述标定类型

    Attributes:
        VALUE (int): 标量
        CURVE (int): 一维曲线
        MAP (int): 二维映射
        VAL_BLK (int): 数组
        ASCII (int): 字符串
    """
    VALUE: int = 0
    CURVE: int = 1
    MAP: int = 2
    VAL_BLK: int = 3
    ASCII: int = 4

    @classmethod
    def creat(cls, v: str | int):
        """
        通过名称或数值值创建枚举

        Args:
            v (str | int): 名称或数值
        Returns:
            ASAP2EnumCalibrateType: 枚举
        Raises:
            ValueError: 无效输入值
            TypeError: 无效输入类型
        """
        if isinstance(v, int):
            for attr in cls:
                if attr.value == v:
                    return attr
            raise ValueError(f"Invalid input value in {cls.__name__}: {v}")
        elif isinstance(v, str):
            for attr in cls:
                if attr.name == v:
                    return attr
            raise ValueError(f"Invalid input name in {cls.__name__}: {v}")
        else:
            raise TypeError(f"Invalid input type in {cls.__name__}: {v}")


class ASAP2EnumConversionType(Enum):
    """
    用于描述转换方法类型

    Attributes:
        RAT_FUNC (int): 由可选的COEFFS关键字指定的公式转换
        TAB_VERB (int): 文字转换表
        TAB_INTP (int): 带插值的表
        TAB_NOINTP (int): 无插值的表
        FORM (int): 基于可选FORMULA关键字指定的公式转换
    """
    RAT_FUNC: int = 0
    TAB_VERB: int = 1
    TAB_INTP: int = 2
    TAB_NOINTP: int = 3
    FORM: int= 4

    @classmethod
    def creat(cls, v: str | int):
        """
        通过名称或数值值创建枚举

        Args:
            v (str | int): 名称或数值
        Returns:
            ASAP2EnumConversionType: 枚举
        Raises:
            ValueError: 无效输入值
            TypeError: 无效输入类型
        """
        if isinstance(v, int):
            for attr in cls:
                if attr.value == v:
                    return attr
            raise ValueError(f"Invalid input value in {cls.__name__}: {v}")
        elif isinstance(v, str):
            for attr in cls:
                if attr.name == v:
                    return attr
            raise ValueError(f"Invalid input name in {cls.__name__}: {v}")
        else:
            raise TypeError(f"Invalid input type in {cls.__name__}: {v}")


class ASAP2EnumAxisType(Enum):
    """
    用于描述轴的类型

    Attributes:
        FIX_AXIS (int): 对于curve或map,其中包含未在EPROM中存放的虚拟轴点,
            轴点可以根据关键字FIX_AXIS_PAR、FIX_AXIS_PAR_DIST和 FIX_AXIS_PAR_LIST定义的参数计算，轴点无法修改
        COM_AXIS (int): curve或map的轴点值分组存放,必须由AXIS_PTS数据记录进行描述,
            对此记录的引用与关键字AXIS_PTS_REF一起出现
        RES_AXIS (int): 重新缩放轴,curve或map的轴点值分组存放,必须由AXIS_PTS数据记录进行描述,
            对此记录的引用与关键字AXIS_PTS_REF一起出现
        CURVE_AXIS (int): 曲线轴,此轴类型使用单独的CURVE CHARACTERISTIC重新缩放轴,
            引用的CURVE用于查找轴索引,控制器使用索引值来确定CURVE或MAP中的操作点
    """
    FIX_AXIS: int = 0
    COM_AXIS: int = 1
    RES_AXIS: int = 2
    CURVE_AXIS: int = 3

    @classmethod
    def creat(cls, v: str | int):
        """
        通过名称或数值值创建枚举

        Args:
            v (str | int): 名称或数值
        Returns:
            ASAP2EnumAxisType: 枚举
        Raises:
            ValueError: 无效输入值
            TypeError: 无效输入类型
        """
        if isinstance(v, int):
            for attr in cls:
                if attr.value == v:
                    return attr
            raise ValueError(f"Invalid input value in {cls.__name__}: {v}")
        elif isinstance(v, str):
            for attr in cls:
                if attr.name == v:
                    return attr
            raise ValueError(f"Invalid input name in {cls.__name__}: {v}")
        else:
            raise TypeError(f"Invalid input type in {cls.__name__}: {v}")


##############################
# Model API function declarations
##############################

@dataclass(slots=True)
class ASAP2FncValues(object):
    """
    用于描述标定对象的表值(函数值)如何存入内存，被RecordLayout对象引用

    Attributes:
        position (int): 轴点值的位置(数据记录中元素序列的描述)
        data_type (ASAP2EnumDataType): 数据类型
        index_mode (ASAP2EnumIndexMode): 描述二维表值值映射到一维地址空间
        address_type (ASAP2EnumAddrType): 轴点寻址方式
    """
    position: int | None = None
    data_type: ASAP2EnumDataType | None = None
    index_mode: ASAP2EnumIndexMode | None = None
    address_type: ASAP2EnumAddrType | None = None


@dataclass(slots=True)
class ASAP2AxisPtsXYZ45(object):
    """
    用于描述轴点在内存中的存放位置，被RecordLayout对象引用

    Attributes:
        position (int): 轴点值的位置(数据记录中元素序列的描述)
        data_type (ASAP2EnumDataType): 数据类型
        index_order (ASAP2EnumIndexOrder): 轴点序列，随着地址的增加而减少或增加索引
        address_type (ASAP2EnumAddrType): 轴点寻址方式
    """
    position: int | None = None
    data_type: ASAP2EnumDataType | None = None
    index_order: ASAP2EnumIndexOrder | None = None
    address_type: ASAP2EnumAddrType | None = None


@dataclass(slots=True)
class ASAP2RecordLayout:
    """
    用于指定内存中可调整对象的各种记录布局;
    如果ALTERNATE选项与FNC_VALUES一起使用,则position参数将确定值和轴点的顺序

    Attributes:
        name (str): 名称
        fnc_values (ASAP2FncValues): 描述标定对象的表值(函数值)如何存入内存
        axis_pts_x (ASAP2AxisPtsXYZ45): 轴点在内存中的存放位置
    """
    name: str | None = None
    # 可选
    fnc_values: ASAP2FncValues | None = None
    axis_pts_x: ASAP2AxisPtsXYZ45 | None = None


@dataclass(slots=True)
class ASAP2CompuVtab:
    """
    用于位模式可视化的转换表，被TypeConversion对象引用

    Attributes:
        name (str): 名称
        long_identifier (str): 描述
        number_value_pairs (int): 值对个数
        read_dict (dict[int, str]): 读值时转换表
        write_dict (dict[str, int]): 写值时转换表
    """
    name: str | None = None
    long_identifier: str | None = None
    number_value_pairs: int | None = None
    read_dict: dict[int, str] | None = None
    write_dict: dict[str, int] | None = None


@dataclass(slots=True)
class ASAP2CompuMethod(object):
    """
    用于描述转换方法

    Attributes:
        name (str): 名称
        long_identifier (str): 描述
        conversion_type (ASAP2EnumConversionType): 转换类型
        format (str): %[length].[layout]，length表示总长度;layout表示小数位
        unit (str): 物理单位
        coeffs (tuple[float, float, float, float, float, float]): 有理函数的系数,raw_value = f(physical_value),
            f(x) = (A*x^2 + B*x + C) / (D*x^2 + E*x + F)
        compu_tab_ref (ASAP2CompuVtab): 对包含转化表的数据记录的引用,
            只能引用COMPU_TAB、COMPU_VTAB或COMPU_VTAB_RANGE类型的对象
    """

    name: str | None = None
    long_identifier: str | None = None
    conversion_type: ASAP2EnumConversionType | None = None
    format: str | None = None
    unit: str | None = None
    # 可选
    coeffs: tuple[float, float, float, float, float, float] | None = None
    compu_tab_ref: ASAP2CompuVtab | None = None

@dataclass(slots=True)
class ASAP2AxisPts:
    """
    用于处理轴点分布的参数规范,被AxisDescr对象引用

    Attributes:
        name (str): 名称
        long_identifier (str): 描述
        address (int): 内存地址
        input_quantity (str): 输入数量,若未分配,则应设置为NO_INPUT_QUANTITY
        record_layout (ASAP2RecordLayout): 数据记录内存布局
        max_diff (float): 值调整的最大浮点数
        conversion (ASAP2CompuMethod): 转换方法
        max_axis_points (int): 最大轴点数
        lower_limit (float): 物理值下限
        upper_limit (float): 物理值上限
    """
    name: str | None = None
    long_identifier: str | None = None
    # cal_type: ASAP2EnumCalibrateType | None = None
    address: int | None = None
    input_quantity: str | None = None
    record_layout: ASAP2RecordLayout | None = None
    max_diff: float | None = None
    conversion: ASAP2CompuMethod | None = None
    max_axis_points: int | None = None
    lower_limit: float | None = None
    upper_limit: float | None = None


@dataclass(slots=True)
class ASAP2AxisDescr:
    """
    用于对标定对象中的轴描述

    Attributes:
        axis_type (ASAP2EnumAxisType): 轴属性
        axis_pts_ref (ASAP2AxisPts): 对AXIS_PTS记录的引用,用于轴点分布的描述
    """
    axis_type: ASAP2EnumAxisType | None = None
    # 可选
    axis_pts_ref: ASAP2AxisPts | None = None


@dataclass(slots=True)
class ASAP2Calibrate(object):
    """
    标定对象类

    Attributes:
        name (str): 名称
        long_identifier (str): 描述
        cal_type (ASAP2EnumCalibrateType): 标定类型
        address (int): 内存地址
        record_layout (ASAP2RecordLayout): 数据记录内存布局
        max_diff (float): 值调整的最大浮点数
        conversion (ASAP2CompuMethod): 转换方法
        lower_limit (float): 物理值下限
        upper_limit (float): 物理值上限
        array_size (int): 对于VAL_BLK和ASCII类型的标定对象，指定固定值或字符的数量
        axis_descrs (list[ASAP2AxisDescr]): 对于CURVE和MAP类型的标定对象,用于指定轴描述的参数,第一个参数块描述X轴,第二个参数块描述Y轴
        value (str): 物理值
        data (bytes): value字段的原始数据序列
    """
    name: str | None = None
    long_identifier: str | None = None
    cal_type: ASAP2EnumCalibrateType | None = None
    address: int | None = None
    record_layout: ASAP2RecordLayout | None = None
    max_diff: float | None = None
    conversion: ASAP2CompuMethod | None = None
    lower_limit: float | None = None
    upper_limit: float | None = None

    # 可选
    array_size: int | None = None
    axis_descrs: list[ASAP2AxisDescr] | None = None

    # 自定义
    value: str | None = None
    data: bytes | None = None


@dataclass(slots=True)
class ASAP2Measure(object):
    """
    测量对象类

    Attributes:
        name (str): 名称
        long_identifier (str): 描述
        data_type (ASAP2EnumCalibrateType): 数据类型
        conversion (ASAP2CompuMethod): 转换方法
        resolution (int): 分辨率,暂未使用
        accuracy (float): 精度,暂未使用
        lower_limit (float): 物理值下限
        upper_limit (float): 物理值上限
        array_size (int): 对于VAL_BLK和ASCII类型的标定对象，指定固定值或字符的数量
        address (int): 内存地址
        value (str): 物理值
        data (bytes): value字段的原始数据序列
        rate (str): 速率
        element_size (int): odt元素大小
        element_addr (str): odt元素地址
        daq_number (int): daq列表序号,1:20ms;2:100ms
        odt_number (int): odt列表序号
        element_number (int): odt元素序号
        pid (str): odt列表对应的pid
    """
    name: str | None = None
    long_identifier: str | None = None
    data_type: ASAP2EnumDataType | None = None
    conversion: ASAP2CompuMethod | None = None
    resolution: int | None = None
    accuracy: float | None = None
    lower_limit: float | None = None
    upper_limit: float | None = None

    # 可选
    array_size: int | None = None
    address: int | None = None

    # 自定义
    value: str | None = None
    data: bytes | None = None

    rate: str | None = None # 速率

    element_size: int | None = None  # odt元素大小
    element_addr: str | None = None  # odt元素地址

    daq_number: int | None = None  # daq列表序号,1:20ms;2:100ms
    odt_number: int | None = None  # odt列表序号
    element_number: int | None = None  # odt元素序号

    pid: str | None = None  # odt列表对应的pid


##############################
# Model API function declarations
##############################
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
    compu_vtab: dict[int, str] = None  # 转换映射表
    coeffs: tuple[float, float, float, float, float, float] = ()  # 转换系数(A,B,C,D,E,F)，若转换类型为RAT_FUNC则存在
    format: tuple[int, int] = ()  # 显示格式(整数位数，小数位数)

    element_size: int = -1  # odt元素大小
    element_addr: str = ''  # odt元素地址

    daq_number: int = -1  # daq列表序号,1:20ms;2:100ms
    odt_number: int = -1  # odt列表序号
    element_number: int = -1  # odt元素序号

    pid: str = ''  # odt列表对应的pid


# @singleton
class MeasureModel(object):
    """
    测量标定界面的数据模型
    """
    daqs_cfg: dict[int, dict[str, int]]

    ASAP2_TYPE_SIZE = {
        'UBYTE': 1,
        'SBYTE': 1,
        'UWORD': 2,
        'SWORD': 2,
        'ULONG': 4,
        'SLONG': 4,
        'FLOAT32_IEEE': 4,
        'FLOAT64_IEEE': 8  # 不支持，测量时此类型数据会被过滤掉
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
        self.table_calibrate_dict: dict[str, ASAP2Calibrate] = {}

        self.obj_measure: eco_pccp.Measure | None= None  # 存储测量对象，用于与ecu通信
        self.obj_srecord: Srecord | None= None  # 存储SRecord对象，用于解析PGM文件

        self.entry_search_measure_item = StringVar()  # 存储测量选择数据项表格搜索框输入的内容
        self.entry_search_calibrate_item = StringVar()  # 存储选择表格搜索框输入的内容

        self.ecu_epk = ''  # 存储ECU内存中的epk
        self.pgm_epk = ''  # 存储PGM文件解析后的epk

        self.a2l_module: Module | None = None  # 存储A2L文件解析后的模块对象
        self.a2l_epk = ''  # 存储A2L文件解析后的epk

        self.a2l_memory_code: MemorySegment | None = None  # 存储A2L文件解析后的代码段内存段对象
        self.a2l_memory_epk_data: MemorySegment | None = None  # 存储A2L文件解析后的epk数据内存段对象
        self.a2l_memory_ram_cal: MemorySegment | None = None  # 存储A2L文件解析后的ram标定内存段对象
        self.a2l_memory_rom_cal: MemorySegment | None = None  # 存储A2L文件解析后的rom标定内存段对象
        self.a2l_measurements: list[Measurement] = []  # 存储A2L文件解析后的测量对象列表
        self.a2l_calibration_dict: dict[str, Characteristic] = {}  # 存储A2L文件解析后的标定(可调整)对象字典

        self.a2l_record_layout_dict: dict[str, RecordLayout] = {}  # 存储A2L文件解析后的标定变量内存布局
        self.a2l_conversion_dict: dict[str, CompuMethod] = {}  # 存储A2L文件解析后的转换方法
        self.a2l_compu_vtab_dict: dict[str, CompuVtab] = {}  # 存储A2L文件解析后的转换表
        self.a2l_axis_pts_dict: dict[str, list[AxisPts]] = {}  # 存储A2L文件解析后的标定变量的轴类型参考，被一维表、二维表等引用

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

        self.table_calibrate_axis_dict: dict[str, ASAP2Calibrate] = {} # 存储X轴点的标定对象
        self.table_calibrate_axis2_dict: dict[str, ASAP2Calibrate] = {} # 存储Y轴点的标定对象
        self.table_calibrate_value_dict: dict[str, ASAP2Calibrate] = {} # 存储值点的标定对象
