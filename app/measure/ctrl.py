#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : ZYD
# @Time    : 2024/7/12 上午8:35
# @version : V1.0.0
# @function:

##############################
# Module imports
##############################

from concurrent.futures import ThreadPoolExecutor  # 多线程
import configparser  # 读写配置文件
import copy  # 拷贝可变类型
from itertools import groupby  # 分组
import os
import pickle
from pprint import pprint
from struct import unpack, pack  # 数值转换

from tkinter import filedialog
import traceback  # 用于获取异常详细信息
from typing import Union

from apscheduler.schedulers.background import BackgroundScheduler
from xba2l.a2l_base import Options as OptionsParseA2l  # 解析a2l文件
from xba2l.a2l_lib import AxisPts
from xba2l.a2l_util import parse_a2l  # 解析a2l文件

from eco import eco_pccp
from srecord import Srecord
from utils import singleton, pad_hex

from .model import MeasureModel, \
    SelectMeasureItem, MeasureItem, SelectCalibrateItem, \
    ASAP2Calibrate, ASAP2RecordLayout, ASAP2CompuMethod, ASAP2AxisDescr, \
    ASAP2FncValues, ASAP2AxisPtsXYZ45, ASAP2CompuVtab, ASAP2AxisPts, \
    ASAP2EnumCalibrateType, ASAP2EnumDataType, ASAP2EnumConversionType, ASAP2EnumByteOrder, \
    ASAP2EnumIndexMode,  ASAP2EnumAddrType, ASAP2EnumIndexOrder, ASAP2EnumAxisType
from .view import tk, ttk, MeasureView, TkTreeView, \
    SubPropertyView, SubCalibrateCurveView, SubCalibrateValueView, SubCalibrateMapView
from ..download.model import DownloadModel


##############################
# Controller API function declarations
##############################

# @singleton
class MeasureCtrl(object):
    """
    测量界面的业务逻辑处理

    :param model: 视图的数据模型
    :type model: MeasureModel
    :param view: 视图
    :type view: MeasureView
    :param extra_model: 其它界面的数据模型，用于当前窗口使用其它窗口的数据
    :type extra_model: DownloadModel
    :param text_log: 日志输出函数
    :type text_log: callable
    :param cfg_path: 下载程序、A2L文件路径
    :type cfg_path: tuple[str, str]
    """

    def __init__(self,
                 model: MeasureModel,
                 view: MeasureView,
                 extra_model: DownloadModel,
                 text_log: callable,
                 cfg_path: tuple[str, str]) -> None:
        """
        构造函数
        """
        self.model = model
        self.view = view
        self.view.set_presenter(self)

        self.extra_model = extra_model

        self.__text_log = text_log

        self.__cfg_path = cfg_path
        self.__cfg_download_path = cfg_path[0]
        self.__cfg_a2l_path = cfg_path[1]

        # 创建一个线程池，最大线程数为1，用于执行窗口事件
        self.__pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='task_measure_')
        # 创建一个线程池，最大线程数为1，用于执行接收daq_dto数据
        self.__pool_recv = ThreadPoolExecutor(max_workers=1, thread_name_prefix='task_recv_')
        self.__after_id = None  # 窗口定时器id

        self.__curve_view = None  # Curve标定界面
        self.__map_view = None  # Map标定界面

        # 初始化配置
        self.ini_config()
        # 加载配置
        self.load_config()

        # 将eco_pccp模块中的打印执行结果内容重定向为text_log，把信息打印到ui显示
        eco_pccp.Measure.print_detail = self.text_log  # 打印执行信息

    def text_log(self, txt: str, *args, **kwargs) -> None:
        """
        text_log打印日志到根界面的日志窗口

        :param txt: 待写入的信息
        :param args: 位置参数列表，第一个参数为文字颜色
            None-灰色,'done'-绿色,'warning'-黄色,'error'-红色
        :param kwargs: 关键字参数列表，未用
        """
        self.__text_log(txt, *args, **kwargs)

    def ini_config(self) -> None:
        """
        初始化配置文件，若配置文件不存在，则新建配置

        """
        try:
            if not os.path.isfile(self.__cfg_a2l_path):
                conf = configparser.ConfigParser()
                section = 'user'
                conf.add_section(section)
                conf.set(section, 'opened_pgm_filepath', '')
                conf.set(section, 'opened_a2l_filepath', '')
                conf.set(section, 'refresh_operate_measure_time_ms', '100')
                with open(self.__cfg_a2l_path, 'w', encoding='utf-8') as f:
                    conf.write(f)
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def load_config(self) -> None:
        """
        加载配置文件到视图数据模型

        """
        try:
            conf = configparser.ConfigParser()
            # 读取配置文件中的各项配置,通过ui显示
            conf.read(filenames=self.__cfg_a2l_path, encoding='utf-8')
            sections = conf.sections()
            for section in sections:
                for option in conf.options(section):
                    if hasattr(self.model, option):
                        setattr(self.model, option, conf.get(section, option))
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def save_config(self) -> None:
        """
        保存配置到配置文件

        """
        try:
            # 保存配置
            conf = configparser.ConfigParser()
            conf.read(self.__cfg_a2l_path, encoding='utf-8')
            sections = conf.sections()
            for section in sections:
                for option in conf.options(section):
                    if hasattr(self.model, option):
                        conf.set(section, option, str(getattr(self.model, option)))
            with open(self.__cfg_a2l_path, 'w', encoding='utf-8') as f:
                conf.write(f)

            # 保存操作表格数据
            with open(self.model.table_history_filepath, 'wb') as f:
                monitor_data = {'table_measure_items': self.model.table_measure_items,
                                'table_calibrate_dict': self.model.table_calibrate_dict,
                                'history_epk': self.model.a2l_epk}
                pickle.dump(monitor_data, f)
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def deal_file(self) -> None:
        """
        从数据模型中获取PGM和A2L文件路径，解析文件，显示文件信息，并将所需原始数据存储到视图的数据模型中

        """
        try:
            msg_a2l = ''
            msg_pgm = ''
            msg_his = ''

            if self.model.opened_a2l_filepath:
                if not os.path.exists(self.model.opened_a2l_filepath):
                    msg = f"不存在A2L文件 -> {self.model.opened_a2l_filepath}"
                    self.text_log(msg, 'warning')
                    return
                # 读取a2l文件
                with open(self.model.opened_a2l_filepath, 'rb') as f:
                    a2l_string = f.read()

                # 解析a2l文件
                option = OptionsParseA2l()
                option.calculate_memory_size = True
                option.ignore_measurements = False
                option.read_instance = True
                err, asap2, module = parse_a2l(a2l_string, encoding='utf-8', options=option)
                if err:
                    raise err

                # 获取a2l模块，保存到视图数据模型中
                self.model.a2l_module = module

                # 获取a2l项目名称和版本号
                project_name = asap2.project.name
                version = str(asap2.asap2_version.version_no) + '.' + str(asap2.asap2_version.upgrade_no)

                # 获取a2l文件的epk信息
                self.model.a2l_epk = module.mod_par.epk
                # 获取a2l文件的内存段信息
                for memory_segment in module.mod_par.memory_segments:
                    self.model.a2l_memory_code = memory_segment.name == '_CODE' and memory_segment or \
                                                 self.model.a2l_memory_code
                    self.model.a2l_memory_epk_data = memory_segment.name == '_epk_data' and memory_segment or \
                                                     self.model.a2l_memory_epk_data
                    self.model.a2l_memory_ram_cal = memory_segment.name == '_RAMCAL' and memory_segment or \
                                                    self.model.a2l_memory_ram_cal
                    self.model.a2l_memory_rom_cal = memory_segment.name == '_ROMCAL' and memory_segment or \
                                                    self.model.a2l_memory_rom_cal

                # 获取a2l测量对象，保存到视图数据模型中
                # 筛选指定数据项，filter返回的是浅拷贝的迭代器，每次迭代的元素内容指向module.measurements列表中的元素内容
                measurements = filter(lambda item: item.data_type != "FLOAT64_IEEE",
                                        module.measurements)
                measurements = copy.deepcopy(list(measurements))
                measurements.sort(key=lambda item: item.name)
                self.model.a2l_measurements = measurements

                # 获取a2l标定对象，保存到视图数据模型中
                calibration_names = list(module.characteristic_dict.keys())
                calibration_names.sort(key=lambda item: item)
                self.model.a2l_calibration_dict.clear()
                for name in calibration_names:
                    self.model.a2l_calibration_dict[name] = copy.deepcopy(module.characteristic_dict[name])
                # 获取a2l标定变量存储结构，保存到视图数据模型中
                self.model.a2l_record_layout_dict = copy.deepcopy(module.record_layout_dict)
                # 获取a2l转换方法，保存到视图数据模型中
                self.model.a2l_conversion_dict = copy.deepcopy(module.compu_method_dict)
                # 获取a2l转换表
                self.model.a2l_compu_vtab_dict = copy.deepcopy(module.compu_vtab_dict)
                # 获取a2l轴类型参考
                self.model.a2l_axis_pts_dict = copy.deepcopy(module.axis_pts_dict)

                # 初始化测量选择表格数据项内容，保存到视图数据模型
                self.model.table_select_measure_raw_items.clear()
                for index in range(len(self.model.a2l_measurements)):
                    table_item = SelectMeasureItem(is_selected='',
                                                   name=self.model.a2l_measurements[index].name,
                                                   is_selected_20ms='□',
                                                   is_selected_100ms='□')
                    self.model.table_select_measure_raw_items.append(table_item)
                self.model.table_select_measure_filter_items = self.model.table_select_measure_raw_items
                # 初始化标定选择表格数据项内容，保存到视图数据模型
                self.model.table_select_calibrate_raw_items.clear()
                for name in self.model.a2l_calibration_dict:
                    table_item = SelectCalibrateItem(is_selected='',
                                                     name=name,
                                                     is_selected_check='□')
                    self.model.table_select_calibrate_raw_items.append(table_item)
                self.model.table_select_calibrate_filter_items = self.model.table_select_calibrate_raw_items
                msg_a2l = (f"a2l信息 -> {project_name}, V{version}"
                           f"\n\ta2l_epk -> {self.model.a2l_epk} "
                           f"\n\t文件路径 -> {self.model.opened_a2l_filepath}")
            else:
                self.text_log('未打开A2L文件', 'warning')
                return

            # 打开程序文件
            if self.model.opened_pgm_filepath:
                if not os.path.exists(self.model.opened_pgm_filepath):
                    msg = f"不存在程序文件 -> {self.model.opened_pgm_filepath}"
                    self.text_log(msg, 'warning')
                    return
                # 获取程序文件处理对象
                self.model.obj_srecord = Srecord(self.model.opened_pgm_filepath)
                # 获取程序文件epk信息
                epk_data = self.model.obj_srecord.get_epk(self.model.a2l_memory_epk_data.address)
                if epk_data:
                    self.model.pgm_epk = bytes.fromhex(epk_data).decode(encoding='utf-8').rstrip('\x00')
                # 获取程序信息
                msg_pgm = (f"程序信息 -> {self.model.obj_srecord.describe_info}"
                           f"\n\tpgm_epk -> {self.model.pgm_epk}"
                           f"\n\t文件路径 -> {self.model.opened_pgm_filepath}")
                for em in self.model.obj_srecord.erase_memory_infos:
                    msg_pgm += f"\n\t数据段{em.erase_number}信息 -> 地址:{em.erase_start_address32},长度:{em.erase_length}"
                # 获取程序中的标定数据
                self.model.obj_srecord.assign_cal_data(addr=self.model.a2l_memory_rom_cal.address)
            else:
                self.text_log('未打开程序文件', 'warning')
                return

            # 打开历史数据
            if self.model.table_history_filepath and os.path.isfile(self.model.table_history_filepath):
                with open(self.model.table_history_filepath, 'rb') as f:
                    monitor_data = pickle.load(f)
                    self.model.table_measure_items = monitor_data['table_measure_items']
                    self.model.table_calibrate_dict = monitor_data['table_calibrate_dict']
                    self.model.history_epk = monitor_data['history_epk']
                    msg_his = (f"历史信息 -> 历史操作数据对象"
                               f"\n\thistory_epk -> {self.model.history_epk}"
                               f"\n\t文件路径 -> {self.model.table_history_filepath}")

            # 显示文件信息
            self.text_log(' ======文件信息======', 'done')
            if msg_a2l:
                self.text_log(msg_a2l)
            if msg_pgm:
                self.text_log(msg_pgm)
            if msg_his:
                self.text_log(msg_his)
            if self.model.a2l_epk and self.model.pgm_epk:
                if self.model.a2l_epk == self.model.pgm_epk:
                    self.text_log('a2l、pgm双方epk匹配成功', 'done')
                else:
                    self.text_log('a2l、pgm双方epk匹配失败', 'error')
                    self.view.show_warning('a2l、pgm双方epk匹配失败')

            # 若history_epk存在且和当前a2l_epk一致，则使用历史数据中的epk
            if self.model.a2l_epk and self.model.a2l_epk == self.model.history_epk:
                pass
            else:
                self.model.table_measure_items.clear()
                self.model.table_calibrate_dict.clear()

            # 刷新
            # self.__flush_table_select()
            # self.__flush_label_select_number()
            self.__flush_table_operate(target='all')
            self.__flush_label_operate_number(target='all')
            self.handler_on_cancel_select(target='all')

        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_closing(self) -> None:
        """
        关闭topui窗口时触发的功能

        """

        def _callback(future):
            """
            断开连接任务完成后退出

            """
            try:
                if future and future.exception():
                    raise future.exception()
                filepath = self.handler_on_save_calibrate() # 保存标定数据
                if filepath:
                    self.model.opened_pgm_filepath = filepath # 更新打开的pgm文件路径，以便下次打开最新的文件
                self.save_config()  # 保存配置
                self.__pool_recv.shutdown(wait=False)  # 关闭线程池
                self.__pool.shutdown(wait=False)  # 关闭线程池
                self.view.destroy()  # 关闭窗口
            except Exception as e:
                self.text_log(f'发生异常 {e}', 'error')
                self.text_log(f"{traceback.format_exc()}", 'error')

        try:
            if self.model.obj_measure:
                self.__pool.submit(self.model.obj_measure.disconnect).add_done_callback(_callback)
            else:
                _callback(None)
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_open_file(self) -> None:
        """
        打开按钮的回调函数，打开PGM和A2L文件并解析，获取需要的数据保存至数据模型

        """
        try:
            # 打开程序文件路径
            self.__open_file(filetype='程序',
                             dir=os.path.dirname(self.model.opened_pgm_filepath))
            # 打开测量标定文件路径
            self.__open_file(filetype='测量标定',
                             dir=os.path.dirname(self.model.opened_pgm_filepath))
            # 处理文件
            self.deal_file()
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_show_property(self, table: TkTreeView, target:str) -> None:
        """
        显示对象属性

        :param table: 待显示属性的数据项所在的表格
        :type table: TkTreeView
        :param target: 目标，'select_measure':测量选择数据；'measure':测量数据；
        'select_calibrate':标定选择数据；'calibrate':标定数据
        :type target: str
        """
        try:
            # 获取选中数据项的id元祖
            selected_iids = table.selection()
            # 获取数据表列名组成的元组
            column_names = tuple(table["columns"])
            for iid in selected_iids:
                name = table.item(iid, "values")[column_names.index("Name")]
                if target == 'select_measure' and selected_iids:
                    names = [item.name for item in self.model.a2l_measurements]
                    SubPropertyView(master=self.view,
                                    obj=self.model.a2l_measurements[names.index(name)],
                                    target='measure')
                if target == 'measure' and selected_iids:
                    names = [item.name for item in self.model.table_measure_items]
                    SubPropertyView(master=self.view,
                                    obj=self.model.table_measure_items[names.index(name)],
                                    target='measure')
                if target == 'calibrate' and selected_iids:
                    SubPropertyView(master=self.view,
                                    obj=self.model.table_calibrate_dict[name],
                                    target='calibrate')
                if target == 'select_calibrate' and selected_iids:
                    SubPropertyView(master=self.view,
                                    obj=self.model.a2l_calibration_dict[name],
                                    target='calibrate')
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_search_item(self, target:str) -> None:
        """
        输入搜索框时触发的回调函数，筛选包含指定字符的数据项显示

        :param target: 目标，'all':所有，'measure':测量数据，'calibrate':标定数据
        :type target: str
        """
        try:
            if target == 'all' or target == 'measure':
                # 筛选数据项，filter返回的是浅拷贝的迭代器，每次迭代的元素内容指向对应原始数据项的内容
                self.model.table_select_measure_filter_items = (
                    filter(lambda item: self.model.entry_search_measure_item.get().strip() in item.name,
                           self.model.table_select_measure_raw_items))
                # 刷新
                self.__flush_table_select(target='measure')
                self.__flush_label_select_number(target='measure')
            if target == 'all' or target == 'calibrate':
                # 筛选数据项，filter返回的是浅拷贝的迭代器，每次迭代的元素内容指向对应原始数据项的内容
                self.model.table_select_calibrate_filter_items = (
                    filter(lambda item: self.model.entry_search_calibrate_item.get().strip() in item.name,
                           self.model.table_select_calibrate_raw_items))
                # 刷新
                self.__flush_table_select(target='calibrate')
                self.__flush_label_select_number(target='calibrate')
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_select_item(self, event: tk.Event, target:str) -> None:
        """
        鼠标点击选择数据项的回调函数，根据鼠标点选时所在的列，设置选择标识

        :param event: 事件
        :type event: tk.Event
        :param target: 目标，'all':所有，'measure':测量数据，'calibrate':标定数据
        :type target: str
        """

        try:
            if target == 'all' or target == 'measure':
                # 获取选中数据项时鼠标指针所在的列索引
                x = self.view.table_select_measure.winfo_pointerx() - self.view.table_select_measure.winfo_rootx()
                selected_column_index = self.view.table_select_measure.identify_column(x=x)  # 结果为字符串，例如'#1'
                if not selected_column_index:
                    return
                selected_column_index = int(selected_column_index[1:]) - 1
                # 获取数据表列名组成的元组
                column_names = tuple(self.view.table_select_measure["columns"])
                # 获取选中数据项的id
                # selected_item_id = event.widget.selection()[0]
                selected_item_id = self.view.table_select_measure.focus()
                # 无选中元素，则返回
                if not selected_item_id:
                    return

                # 若鼠标点击数据项时的位置非通道选择框所处的列，则直接返回
                if not (column_names[selected_column_index] == "20ms" or column_names[selected_column_index] == "100ms"):
                    return

                # 获取选中数据项的值
                item_values = self.view.table_select_measure.item(selected_item_id, "values")
                # 设置速率通道选中标识
                if column_names[selected_column_index] == "20ms":
                    self.view.table_select_measure.set(selected_item_id, column_names.index('100ms'), '□')
                    set_value = item_values[column_names.index('20ms')] == '□' and '√' or '□'
                    self.view.table_select_measure.set(selected_item_id, selected_column_index, set_value)
                if column_names[selected_column_index] == "100ms":
                    self.view.table_select_measure.set(selected_item_id, column_names.index('20ms'), '□')
                    set_value = item_values[column_names.index('100ms')] == '□' and '√' or '□'
                    self.view.table_select_measure.set(selected_item_id, selected_column_index, set_value)
                # 获取最新选中数据项的值
                item_values = self.view.table_select_measure.item(selected_item_id, "values")
                set_value = (item_values[column_names.index('20ms')] == '√' or
                             item_values[column_names.index('100ms')] == '√') and '☆' or ''
                self.view.table_select_measure.set(selected_item_id, column_names.index('is_selected'), set_value)

                # 存储原始数据项列表的内容到数据模型
                idx, table_item = self.__iid2idx_in_select_table(iid=selected_item_id,
                                                                 table_widget=self.view.table_select_measure,
                                                                 raw_items=self.model.table_select_measure_raw_items)
                self.model.table_select_measure_raw_items[idx] = table_item

                # 刷新
                self.__flush_label_select_number(target='measure')
            if target == 'all' or target == 'calibrate':
                # 获取选中数据项时鼠标指针所在的列索引
                x = self.view.table_select_calibrate.winfo_pointerx() - self.view.table_select_calibrate.winfo_rootx()
                selected_column_index = self.view.table_select_calibrate.identify_column(x=x)  # 结果为字符串，例如'#1'
                if not selected_column_index:
                    return
                selected_column_index = int(selected_column_index[1:]) - 1
                # 获取数据表列名组成的元组
                column_names = tuple(self.view.table_select_calibrate["columns"])
                # 获取选中数据项的id
                # selected_item_id = event.widget.selection()[0]
                selected_item_id = self.view.table_select_calibrate.focus()
                # 无选中元素，则返回
                if not selected_item_id:
                    return

                # 若鼠标点击数据项时的位置非选择框所处的列，则直接返回
                if not (column_names[selected_column_index] == "Check"):
                    return

                # 获取选中数据项的值
                item_values = self.view.table_select_calibrate.item(selected_item_id, "values")
                # 设置选中标识
                if column_names[selected_column_index] == "Check":
                    self.view.table_select_calibrate.set(selected_item_id, column_names.index('Check'), '□')
                    set_value = item_values[column_names.index('Check')] == '□' and '√' or '□'
                    self.view.table_select_calibrate.set(selected_item_id, selected_column_index, set_value)
                # 获取最新选中数据项的值
                item_values = self.view.table_select_calibrate.item(selected_item_id, "values")
                set_value = (item_values[column_names.index('Check')] == '√') and '☆' or ''
                self.view.table_select_calibrate.set(selected_item_id, column_names.index('is_selected'), set_value)

                # 存储原始数据项列表的内容到数据模型
                idx, table_item = self.__iid2idx_in_select_table(iid=selected_item_id,
                                                                 table_widget=self.view.table_select_calibrate,
                                                                 raw_items=self.model.table_select_calibrate_raw_items)
                self.model.table_select_calibrate_raw_items[idx] = table_item

                # 刷新
                self.__flush_label_select_number(target='calibrate')
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_ack_select(self, target:str) -> None:
        """
        添加选中数据项到操作表格，并获取数据项属性

        :param target: 目标，'all':所有，'measure':测量数据，'calibrate':标定数据
        :type target: str
        """
        def _get_idx_map(target:str) -> list[tuple[int, int]]:
            """
            获取操作表格数据项与A2L对象的索引映射list[tuple(idx_in_table,idx_in_a2l)]

            :param target: 'measure':测量数据，'calibrate':标定数据
            :type target: str
            """
            idx_map_list: list[tuple[int, int]] = []
            if target == 'measure':
                for idx_in_table in range(len(self.model.table_measure_items)):
                    for idx_in_a2l in range(len(self.model.a2l_measurements)):
                        if (self.model.table_measure_items[idx_in_table].name ==
                                self.model.a2l_measurements[idx_in_a2l].name):
                            idx_map_list.append((idx_in_table, idx_in_a2l))
                        if idx_in_a2l >= len(self.model.a2l_measurements):
                            msg = f'数据项{self.model.table_measure_items[idx_in_table].name}不存在于A2L数据对象列表中'
                            raise ValueError(msg)
            return idx_map_list

        try:
            if target == 'all' or target == 'measure':
                # 清空数据模型中测量数据项列表
                self.model.table_measure_items.clear()
                # 筛选被选择的数据项，filter返回的是浅拷贝的迭代器，每次迭代的元素内容指向table_measurement_raw_items列表中的元素内容
                selected_items = filter(lambda item: item.is_selected,
                                        self.model.table_select_measure_raw_items)
                # 添加被选择的数据项到测量表格
                for item in selected_items:
                    measure_item = MeasureItem(name=item.name,
                                               rate=item.is_selected_20ms == '√' and '20ms' or '100ms')
                    self.model.table_measure_items.append(measure_item)

                idx_map_list = _get_idx_map(target='measure')
                # 根据索引映射，从原始测量对象中获取对应测量数据项的属性
                for idx_in_table, idx_in_a2l in idx_map_list:
                    # 获取原始测量对象
                    obj_msr = self.model.a2l_measurements[idx_in_a2l]
                    # 索引属性
                    self.model.table_measure_items[idx_in_table].idx_in_table_measure_items = idx_in_table
                    self.model.table_measure_items[
                        idx_in_table].idx_in_a2l_measurements = idx_in_a2l
                    # 数据类型属性
                    self.model.table_measure_items[idx_in_table].data_type = obj_msr.data_type
                    # 转换方法属性
                    self.model.table_measure_items[idx_in_table].conversion = obj_msr.conversion
                    # 转换类型属性
                    self.model.table_measure_items[idx_in_table].conversion_type = (
                        self.model.a2l_conversion_dict[obj_msr.conversion].conversion_type)
                    # 转换映射名称属性
                    self.model.table_measure_items[idx_in_table].compu_tab_ref = (
                        self.model.a2l_conversion_dict[obj_msr.conversion].compu_tab_ref)
                    # 转换映射表属性
                    # 对于数值类型没有转换映射表，所以先确定转换映射名称存在，再获取转换映射表
                    if self.model.table_measure_items[idx_in_table].compu_tab_ref in self.model.a2l_compu_vtab_dict:
                        self.model.table_measure_items[idx_in_table].compu_vtab = (
                            self.model.a2l_compu_vtab_dict[
                                self.model.table_measure_items[idx_in_table].compu_tab_ref].read_dict)

                    # 单位属性
                    self.model.table_measure_items[idx_in_table].unit = (
                        self.model.a2l_conversion_dict[obj_msr.conversion].unit)
                    # 转换系数
                    self.model.table_measure_items[idx_in_table].coeffs = (
                        self.model.a2l_conversion_dict[obj_msr.conversion].coeffs)
                    # 显示格式
                    fm = self.model.a2l_conversion_dict[obj_msr.conversion].format
                    if '%' in fm:
                        fm = tuple(fm[1:].split('.'))
                        fm0 = int(fm[0])
                        fm1 = int(fm[1])
                        self.model.table_measure_items[idx_in_table].format = (fm0, fm1)

                    # odt元素大小属性
                    self.model.table_measure_items[idx_in_table].element_size = self.model.ASAP2_TYPE_SIZE[
                        obj_msr.data_type]
                    # odt元素地址属性
                    self.model.table_measure_items[idx_in_table].element_addr = hex(obj_msr.ecu_address)

                    # daq列表序号属性，1:20ms,2:100ms
                    if self.model.table_measure_items[idx_in_table].rate == '20ms':
                        self.model.table_measure_items[idx_in_table].daq_number = 1
                    elif self.model.table_measure_items[idx_in_table].rate == '100ms':
                        self.model.table_measure_items[idx_in_table].daq_number = 2
                # 刷新
                self.__flush_table_operate(target='measure')
                self.__flush_label_operate_number(target='measure')
                self.handler_on_cancel_select(target='measure')
            if target == 'all' or target == 'calibrate':
                # 筛选被选择的数据项，filter返回的是浅拷贝的迭代器，每次迭代的元素内容指向table_calibrate_raw_items列表中的元素内容
                selected_items = list(filter(lambda item: item.is_selected,
                                        self.model.table_select_calibrate_raw_items))
                names = [item.name for item in selected_items]
                self.__assign_calibration_dict(tuple(names), self.model.table_calibrate_dict)
                for item in self.model.table_calibrate_dict.values():
                    # 对于非VALUE类型的标定变量，如一维表、二维表，不能直接赋单个值
                    if item.cal_type.name == ASAP2EnumCalibrateType.VALUE.name:
                        # 获取原始值，将其转为物理值
                        rom_cal_addr = self.model.a2l_memory_rom_cal.address
                        offset = item.address - rom_cal_addr
                        length = ASAP2EnumDataType.get_size(item.record_layout.fnc_values.data_type.name)
                        raw_data =(self.model.obj_srecord.get_raw_data_from_cal_data(offset=offset,
                                                                                     length=length))
                        item.data = raw_data
                        value = self.__get_physical_value(item=item,
                                                          raw_data=raw_data)
                        item.value = value
                    else:
                        item.data = b''
                        item.value = '双击进行标定'
                # 刷新
                self.__flush_table_operate(target='calibrate')
                self.__flush_label_operate_number(target='calibrate')
                self.handler_on_cancel_select(target='calibrate')
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_cancel_select(self, target:str) -> None:
        """
        取消选中数据项，将操作表(测量/标定)中的数据项属性刷新到选择表

        :param target: 目标，'all':所有，'measure':测量数据，'calibrate':标定数据
        :type target: str
        """
        try:
            if target == 'all' or target == 'measure':
                # 清除所有原始数据项的选中状态
                for msr_item in self.model.table_select_measure_raw_items:
                    msr_item.is_selected = ''
                    msr_item.is_selected_20ms = '□'
                    msr_item.is_selected_100ms = '□'
                # 获取所有原始数据项的名字
                measure_raw_item_names = [item.name for item in self.model.table_select_measure_raw_items]
                # 将测量表格数据项状态写入到原始数据项的状态
                for measure_item in self.model.table_measure_items:
                    table_item = SelectMeasureItem(is_selected='★',
                                                   name=measure_item.name,
                                                   is_selected_20ms=measure_item.rate == '20ms' and '√' or '□',
                                                   is_selected_100ms=measure_item.rate == '100ms' and '√' or '□', )
                    # 获取测量数据项名字在原始数据项列表中索引
                    idx = measure_raw_item_names.index(measure_item.name)
                    # 更新原始数据项内容
                    self.model.table_select_measure_raw_items[idx] = table_item
                # 刷新
                self.handler_on_search_item(target='measure')
            if target == 'all' or target == 'calibrate':
                # 清除所有原始数据项的选中状态
                for cal_item in self.model.table_select_calibrate_raw_items:
                    cal_item.is_selected = ''
                    cal_item.is_selected_check = '□'
                # 获取所有原始数据项的名字
                calibrate_raw_item_names = [item.name for item in self.model.table_select_calibrate_raw_items]
                # 将标定表格数据项状态写入到原始数据项的状态
                for k, v in self.model.table_calibrate_dict.items():
                    table_item = SelectCalibrateItem(is_selected='★',
                                                     name=k,
                                                     is_selected_check='√')
                    # 获取标定数据项名字在原始数据项列表中索引
                    idx = calibrate_raw_item_names.index(k)
                    # 更新原始数据项内容
                    self.model.table_select_calibrate_raw_items[idx] = table_item
                # 刷新
                self.handler_on_search_item(target='calibrate')
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_delete_item(self, target:str) -> None:
        """
        删除操作表(测量/标定)中的数据项

        :param target: 目标，'all':所有，'measure':测量数据，'calibrate':标定数据
        :type target: str
        """
        if target == 'all' or target == 'measure':
            # 若已启动测量，则不允许删除
            if hasattr(self.model.obj_measure, 'has_measured') and self.model.obj_measure.has_measured:
                return

            # 获取选中数据项的id元祖
            selected_item_iids = self.view.table_measure.selection()
            # 获取数据表列名组成的元组
            column_names = tuple(self.view.table_measure["columns"])

            # 从测量数据项列表中删除选择的数据项
            if selected_item_iids:
                for iid in selected_item_iids:
                    name = self.view.table_measure.item(iid, "values")[column_names.index("Name")]
                    measure_items_names = [item.name for item in self.model.table_measure_items]
                    self.model.table_measure_items.pop(measure_items_names.index(name))
            # 刷新
            self.handler_on_cancel_select(target='measure')
            self.handler_on_ack_select(target='measure') # 更新表格及表格数据项
        if target == 'all' or target == 'calibrate':
            # 若已启动标定，则不允许删除
            # if hasattr(self.model.obj_measure, 'has_measured') and self.model.obj_measure.has_measured:
            #     return

            # 获取选中数据项的id元祖
            selected_item_iids = self.view.table_calibrate.selection()
            # 获取数据表列名组成的元组
            column_names = tuple(self.view.table_calibrate["columns"])

            # 从标定表数据项列表中删除选择的数据项
            if selected_item_iids:
                for iid in selected_item_iids:
                    name = self.view.table_calibrate.item(iid, "values")[column_names.index("Name")]
                    self.model.table_calibrate_dict.pop(name)
            # 刷新
            self.handler_on_cancel_select(target='calibrate')
            self.handler_on_ack_select(target='calibrate') # 更新表格及表格数据项

    def handler_on_connect(self) -> None:
        """
        连接

        """

        def _callback(future):
            """
            线程执行结束的回调函数、
            :param future: 线程执行结束返回的future对象
            """
            try:
                # 若线程执行中存在异常，则抛出此异常信息
                if future.exception():
                    raise Exception(future.exception())
                if self.model.obj_measure.has_connected:
                    msg = f"连接成功！"
                    self.text_log(msg, 'done')
                    # 更新按钮状态
                    self.view.btn_connect_measure.config(state='disabled')
                    self.view.btn_disconnect_measure.config(state='normal')
                    self.view.btn_start_measure.config(state='normal')
                    self.view.btn_stop_measure.config(state='disabled')
                    self.view.btn_open.config(state='disabled')
                if future.result():
                    epk = future.result()[0]
                    if epk == self.model.a2l_epk and \
                            epk == self.model.pgm_epk:
                        self.text_log(f'pgm、a2l、ecu三方epk匹配成功', 'done')
                    else:
                        self.text_log(f'pgm、a2l、ecu三方epk匹配失败', 'error')
                        self.view.show_warning('pgm、a2l、ecu三方epk匹配失败')
                    is_cal_matched = future.result()[1]
                    if not is_cal_matched:
                        self.view.show_warning('ecu标定数据区与pgm标定数据区不一致')
            except Exception as e:
                self.text_log(f'发生异常 {e}', 'error')
                self.text_log(f"{traceback.format_exc()}", 'error')

        try:
            self.text_log(f'======建立连接======', 'done')
            # 创建测量对象
            self.__create_measure_obj()
            # 建立连接
            self.__pool.submit(self.model.obj_measure.connect,
                               self.model.a2l_memory_epk_data.address,
                               len(self.model.a2l_epk)).add_done_callback(_callback)
            # print("当前线程数量为", threading.active_count())
            # print("所有线程的具体信息", threading.enumerate())
            # print("当前线程具体信息", threading.current_thread())
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_disconnect(self) -> None:
        """
        断开连接

        """

        def _callback(future):
            """
            线程执行结束的回调函数、
            :param future: 线程执行结束返回的future对象
            """
            try:
                # 若线程执行中存在异常，则抛出此异常信息
                if future.exception():
                    raise Exception(future.exception())
                if not self.model.obj_measure.has_connected:
                    msg = f"断开成功！"
                    self.text_log(msg, 'done')
                    # 更新按钮状态
                    self.view.btn_connect_measure.config(state='normal')
                    self.view.btn_disconnect_measure.config(state='disabled')
                    self.view.btn_start_measure.config(state='disabled')
                    self.view.btn_stop_measure.config(state='disabled')
                    self.view.btn_open.config(state='normal')
            except Exception as e:
                self.text_log(f'发生异常 {e}', 'error')
                self.text_log(f"{traceback.format_exc()}", 'error')

        try:
            self.text_log(f'======断开连接======', 'done')
            self.__pool.submit(self.model.obj_measure.disconnect).add_done_callback(_callback)
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_start_measure(self) -> None:
        """
        启动测量

        """

        def _get_daqs_cfg():
            """
            获取daq列表信息任务

            """
            try:
                # daq列表信息
                # 例如{1: {'first_pid': 0x3c, 'odts_size': 0x20},
                #     2: {'first_pid': 0x78, 'odts_size': 0x30}}
                daqs_cfg: dict[int, dict[str, int]] = {}

                # 获取daq的信息
                daq_cfg_list = [self.model.obj_measure.get_daq_cfg(daq_number=1),
                                self.model.obj_measure.get_daq_cfg(daq_number=2)]
                for daq_cfg in daq_cfg_list:
                    daq_number = daq_cfg[0]  # daq列表序号
                    first_pid = daq_cfg[1]  # daq中首个odt的pid
                    odts_size = daq_cfg[2]  # daq中odt列表的的大小
                    daqs_cfg[daq_number] = {'first_pid': int(first_pid, 16), 'odts_size': int(odts_size, 16)}
                # 保存daq列表信息到数据模型
                self.model.daqs_cfg = copy.deepcopy(daqs_cfg)
                return True
            except Exception as e:
                self.text_log(f'发生异常 {e}', 'error')
                self.text_log(f"{traceback.format_exc()}", 'error')

        def _get_daqs(future):
            """
            获取daq列表任务

            :param future: 任务执行结束返回的future对象
            """
            try:
                # 若线程执行中存在异常，则抛出此异常信息
                if future.exception():
                    raise Exception(future.exception())
                if future.result():
                    self.__pool.submit(self.__get_daqs, self.model.daqs_cfg).add_done_callback(
                        _start_measure)
                return True
            except Exception as e:
                self.text_log(f'发生异常 {e}', 'error')
                self.text_log(f"{traceback.format_exc()}", 'error')

        def _start_measure(future):
            """
            启动测量任务

            :param future: 任务执行结束返回的future对象
            """
            try:
                # 若线程执行中存在异常，则抛出此异常信息
                if future.exception():
                    raise Exception(future.exception())
                if future.result():
                    self.model.daqs = copy.deepcopy(future.result())  # 保存daq列表到数据模型
                    self.__pool.submit(self.model.obj_measure.start_measure, self.model.daqs).add_done_callback(
                        _recv_daq_dto)
                return True
            except Exception as e:
                self.text_log(f'发生异常 {e}', 'error')
                self.text_log(f"{traceback.format_exc()}", 'error')

        def _recv_daq_dto(future):
            """
            解析daq_dto任务

            :param future: 任务执行结束返回的future对象
            """
            try:
                if future.exception():
                    raise Exception(future.exception())
                if self.model.obj_measure.has_measured:
                    msg = f"启动测量成功！"
                    self.text_log(msg, 'done')
                    # 更新按钮状态
                    self.view.btn_connect_measure.config(state='disabled')
                    self.view.btn_disconnect_measure.config(state='disabled')
                    self.view.btn_start_measure.config(state='disabled')
                    self.view.btn_stop_measure.config(state='normal')
                    self.view.btn_ack_select_measure.config(state='disabled')
                    self.view.btn_cancel_select_measure.config(state='disabled')

                    # 清空can接收消息缓冲区
                    self.model.obj_measure.clear_recv_queue()
                    # 启动测量后，开始接收daq_dto数据，并刷新显示数据
                    self.__pool_recv.submit(self.__recv_daq_dto).add_done_callback(_done)
                    self.__after_id = self.view.after(ms=int(self.model.refresh_operate_measure_time_ms),
                                                      func=self.__display_monitor_value)
            except Exception as e:
                self.text_log(f'发生异常 {e}', 'error')
                self.text_log(f"{traceback.format_exc()}", 'error')

        def _done(future):
            """
            结束

            :param future: 任务执行结束返回的future对象
            """
            try:
                if future.exception():
                    raise Exception(future.exception())
            except Exception as e:
                self.text_log(f'发生异常 {e}', 'error')
                self.text_log(f"{traceback.format_exc()}", 'error')

        try:
            # 若测量数据项为空，则返回
            if not self.model.table_measure_items:
                return
            self.text_log(f'======启动测量======', 'done')
            # 获取daq列表的信息
            self.__pool.submit(_get_daqs_cfg).add_done_callback(_get_daqs)
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_stop_measure(self) -> None:
        """
        停止测量

        """

        def _callback(future):
            """
            线程执行结束的回调函数

            :param future: 线程执行结束返回的future对象
            """
            try:
                if not self.model.obj_measure.has_measured:
                    msg = f"停止成功！"
                    self.text_log(msg, 'done')
                    # 更新按钮状态
                    self.view.btn_connect_measure.config(state='disabled')
                    self.view.btn_disconnect_measure.config(state='normal')
                    self.view.btn_start_measure.config(state='normal')
                    self.view.btn_stop_measure.config(state='disabled')
                    self.view.btn_ack_select_measure.config(state='normal')
                    self.view.btn_cancel_select_measure.config(state='normal')
            except Exception as e:
                self.text_log(f'发生异常 {e}', 'error')
                self.text_log(f"{traceback.format_exc()}", 'error')

        try:
            self.text_log(f'======停止测量======', 'done')
            self.__pool.submit(self.model.obj_measure.stop_measure).add_done_callback(_callback)
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_table_calibrate_edit(self, e: tk.Event, table: ttk.Treeview):
        """
        双击标定表格进行标定

        :param e: 事件
        :type e: tk.Event
        :param table: 表格
        :type table: ttk.Treeview
        """

        # 获取选中的单元格
        try:
            selected_iid, selected_col, selected_name, (x, y, w, h) = (self.get_selected_cell_in_table(e=e,
                                                                                                       table=table))
            # 未选中单元格则退出
            if not selected_iid or not selected_col:
                return

            # 若不是修改Value列则退出
            if selected_col != 'Value':
                return
            # 根据表格数据项iid获取此填充此表格数据项列表的相应索引及其数据
            cal_item = self.model.table_calibrate_dict[selected_name]
            # 根据标定类型进行相应处理
            if cal_item.cal_type == ASAP2EnumCalibrateType.VALUE:
                # 显示输入框
                SubCalibrateValueView(master=table,
                                      item=cal_item,
                                      geometry=(x,y,w,h),
                                      presenter=self)
            elif cal_item.cal_type == ASAP2EnumCalibrateType.CURVE:
                # 值数据点标定对象存储字典
                value_calibrate_dict: dict[str, ASAP2Calibrate] = {}

                # 获取X轴的信息
                axis_pts_ref = cal_item.axis_descrs[0].axis_pts_ref
                # 获取X轴的点数(1基)
                max_axis_points = axis_pts_ref.max_axis_points

                #############################################################################
                # 值数据点对象
                #############################################################################
                for i in range(max_axis_points):
                    value_calibrate = copy.deepcopy(cal_item)
                    value_calibrate.name += f"_Y({i})" # 名称
                    # value_calibrate.long_identifier = value_calibrate.long_identifier # 描述
                    value_calibrate.cal_type = ASAP2EnumCalibrateType.VALUE # 标定类型
                    inc = i
                    value_calibrate.address = (cal_item.address +
                                               inc * ASAP2EnumDataType.get_size(
                                cal_item.record_layout.fnc_values.data_type.name))  # 数据地址
                    # value_calibrate.record_layout = value_calibrate.record_layout # 数据记录内存布局
                    # value_calibrate.max_diff = value_calibrate.max_diff # 值调整的最大浮点数
                    # value_calibrate.conversion = value_calibrate.conversion # 转换方法
                    # value_calibrate.lower_limit = value_calibrate.lower_limit # 物理值下限
                    # value_calibrate.upper_limit = value_calibrate.upper_limit # 物理值上限
                    value_calibrate.array_size = None # 对于VAL_BLK和ASCII类型的标定对象，指定固定值或字符的数量
                    value_calibrate.axis_descrs = None # 对于CURVE和MAP类型的标定对象,用于指定轴描述的参数,第一个参数块描述X轴,第二个参数块描述Y轴

                    # 获取原始值，将其转为物理值
                    rom_cal_addr = self.model.a2l_memory_rom_cal.address
                    offset = value_calibrate.address - rom_cal_addr
                    length = ASAP2EnumDataType.get_size(value_calibrate.record_layout.fnc_values.data_type.name)
                    raw_data = (self.model.obj_srecord.get_raw_data_from_cal_data(offset=offset,
                                                                                  length=length))
                    value_calibrate.data = raw_data # value字段的原始数据序列
                    value = self.__get_physical_value(item=value_calibrate,
                                                      raw_data=raw_data)
                    value_calibrate.value = value # 物理值
                    # 添加数据项
                    value_calibrate_dict[value_calibrate.name] = value_calibrate

                #############################################################################
                # 轴数据对象
                #############################################################################
                axis_calibrate_dict = self.__assign_calibrate_axis_dict(curve_or_map_item=cal_item,
                                                                        axis='X')

                # 存储到数据模型
                self.model.table_calibrate_axis_dict = axis_calibrate_dict
                self.model.table_calibrate_value_dict = value_calibrate_dict
                # 显示Curve标定界面
                self.__curve_view = SubCalibrateCurveView(master=self.view,
                                                          axis_calibrate_dict=self.model.table_calibrate_axis_dict ,
                                                          value_calibrate_dict=self.model.table_calibrate_value_dict,
                                                          presenter=self)
                # 刷新
                self.__flush_table_operate(target='calibrate')
            elif cal_item.cal_type == ASAP2EnumCalibrateType.MAP:
                index_mode = cal_item.record_layout.fnc_values.index_mode
                if index_mode != ASAP2EnumIndexMode.COLUMN_DIR:
                    msg = f"尚未支持{cal_item.name}的类型(顺序存储类型{index_mode})"
                    self.text_log(msg, 'error')
                    self.view.show_warning(msg)
                    return
                # 值数据点标定对象存储字典
                value_calibrate_dict: dict[str, ASAP2Calibrate] = {}
                # 获取X轴的信息
                axis_pts_ref = cal_item.axis_descrs[0].axis_pts_ref
                # 获取X轴的点数(1基),col
                max_axis_points = axis_pts_ref.max_axis_points
                # 获取Y轴的信息
                axis2_pts_ref = cal_item.axis_descrs[1].axis_pts_ref
                # 获取Y轴的点数(1基),row
                max_axis2_points = axis2_pts_ref.max_axis_points

                #############################################################################
                # 值数据点对象
                #############################################################################
                for i in range(max_axis2_points):
                    for j in range(max_axis_points):
                        value_calibrate = copy.deepcopy(cal_item)
                        value_calibrate.name += f"_Z({i},{j})" # 名称
                        # value_calibrate.long_identifier = value_calibrate.long_identifier # 描述
                        value_calibrate.cal_type = ASAP2EnumCalibrateType.VALUE # 标定类型
                        inc = i+ j * max_axis2_points # 列优先
                        value_calibrate.address = (cal_item.address +
                                                   inc * ASAP2EnumDataType.get_size(
                                    cal_item.record_layout.fnc_values.data_type.name))  # 数据地址
                        # value_calibrate.record_layout = value_calibrate.record_layout # 数据记录内存布局
                        # value_calibrate.max_diff = value_calibrate.max_diff # 值调整的最大浮点数
                        # value_calibrate.conversion = value_calibrate.conversion # 转换方法
                        # value_calibrate.lower_limit = value_calibrate.lower_limit # 物理值下限
                        # value_calibrate.upper_limit = value_calibrate.upper_limit # 物理值上限
                        value_calibrate.array_size = None # 对于VAL_BLK和ASCII类型的标定对象，指定固定值或字符的数量
                        value_calibrate.axis_descrs = None # 对于CURVE和MAP类型的标定对象,用于指定轴描述的参数,第一个参数块描述X轴,第二个参数块描述Y轴

                        # 获取原始值，将其转为物理值
                        rom_cal_addr = self.model.a2l_memory_rom_cal.address
                        offset = value_calibrate.address - rom_cal_addr
                        length = ASAP2EnumDataType.get_size(value_calibrate.record_layout.fnc_values.data_type.name)
                        raw_data = (self.model.obj_srecord.get_raw_data_from_cal_data(offset=offset,
                                                                                      length=length))
                        value_calibrate.data = raw_data # value字段的原始数据序列
                        value = self.__get_physical_value(item=value_calibrate,
                                                          raw_data=raw_data)
                        value_calibrate.value = value # 物理值
                        # 添加数据项
                        value_calibrate_dict[value_calibrate.name] = value_calibrate

                #############################################################################
                # 轴数据对象
                #############################################################################
                axis_calibrate_dict = self.__assign_calibrate_axis_dict(curve_or_map_item=cal_item,
                                                                        axis='X')
                axis2_calibrate_dict = self.__assign_calibrate_axis_dict(curve_or_map_item=cal_item,
                                                                        axis='Y')
                # 存储到数据模型
                self.model.table_calibrate_axis_dict = axis_calibrate_dict
                self.model.table_calibrate_axis2_dict = axis2_calibrate_dict
                self.model.table_calibrate_value_dict = value_calibrate_dict
                # 显示Map标定界面
                self.__map_view = SubCalibrateMapView(master=self.view,
                                                      axis_calibrate_dict=self.model.table_calibrate_axis_dict,
                                                      axis2_calibrate_dict=self.model.table_calibrate_axis2_dict,
                                                      value_calibrate_dict=self.model.table_calibrate_value_dict,
                                                      presenter=self)
                # 刷新
                self.__flush_table_operate(target='calibrate')
            else:
                msg = f"尚未支持{cal_item.name}的类型(标定类型{cal_item.cal_type})"
                self.text_log(msg, 'error')
                self.view.show_warning(msg)
                return
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_table_curve_edit(self, e: tk.Event, table: ttk.Treeview):
        """
        双击标定表格更改Curve标定对象的值

        :param e: 事件
        :type e: tk.Event
        :param table: 表格
        :type table: ttk.Treeview
        """
        try:
            # 获取选中的单元格
            selected_iid, selected_col, selected_name, (x, y, w, h) = (self.get_selected_cell_in_table(e=e,
                                                                                                       table=table))
            # 未选中单元格则退出
            if not selected_iid or not selected_col:
                return

            # 获取标定对象的名字
            name = table.item(selected_iid, "text")
            names = [table.item(iid, "text") for iid in table.get_children()]
            suffix = f"_X({selected_col})" if \
            names.index(name) == 0 else f"_Y({selected_col})"
            # 获取标定对象
            cal_item = self.model.table_calibrate_axis_dict.get(name + suffix) if \
            names.index(name) == 0 else self.model.table_calibrate_value_dict.get(name + suffix)
            # 显示输入框
            if cal_item.cal_type == ASAP2EnumCalibrateType.VALUE:
                SubCalibrateValueView(master=table,
                                      item=cal_item,
                                      geometry=(x,y,w,h),
                                      presenter=self)
            else:
                msg = f"尚未支持{cal_item.name}的类型(标定类型{cal_item.cal_type})"
                self.text_log(msg, 'error')
                self.view.show_warning(msg)
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_table_map_edit(self, e: tk.Event, table: ttk.Treeview):
        """
        双击标定表格更改Map标定对象的值

        :param e: 事件
        :type e: tk.Event
        :param table: 表格
        :type table: ttk.Treeview
        """
        try:
            # 获取选中的单元格
            selected_iid, selected_col, selected_name, (x, y, w, h) = (self.get_selected_cell_in_table(e=e,
                                                                                                       table=table))
            # 未选中单元格则退出
            if not selected_iid or not selected_col:
                return
            # 若选中单元格为Index列则退出
            if selected_col == "Index":
                return

            # 获取行名
            item_index = table.set(selected_iid, "Index")

            cal_item = None
            if item_index == "Y":
                # X轴标定对象
                if selected_col != "X" and int(selected_col) >= 0:
                    names = list(self.model.table_calibrate_axis_dict.keys())
                    cal_item = self.model.table_calibrate_axis_dict[names[int(selected_col)]]
            elif selected_col == "X":
                # Y轴标定对象
                if int(item_index) >= 0:
                    names = list(self.model.table_calibrate_axis2_dict.keys())
                    cal_item = self.model.table_calibrate_axis2_dict[names[int(item_index)]]
            elif int(selected_col) >= 0 and int(item_index) >= 0:
                # 值标定对象
                name = list(self.model.table_calibrate_value_dict.keys())[0]
                name = name[:name.find("_Z(")] + f"_Z({int(item_index)},{int(selected_col)})"
                cal_item = self.model.table_calibrate_value_dict[name]
            else:
                return
            # 显示输入框
            if cal_item.cal_type == ASAP2EnumCalibrateType.VALUE:
                SubCalibrateValueView(master=table,
                                      item=cal_item,
                                      geometry=(x,y,w,h),
                                      presenter=self)
            else:
                msg = f"尚未支持{cal_item.name}的类型(标定类型{cal_item.cal_type})"
                self.text_log(msg, 'error')
                self.view.show_warning(msg)
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_calibrate_value(self, widget: tk.Entry | ttk.Combobox, item: ASAP2Calibrate):
        """
        验证标定数据数据符合规则后，将数据写入ECU，并刷新数据及表格

        :param widget: 编辑控件
        :type widget: tk.Entry | ttk.Combobox
        :param item: 标定数据项
        :type item: ASAP2Calibrate
        """
        def _calibrate(item: ASAP2Calibrate, value: str) -> None:
            """
            修改值

            :param item: 标定数据项
            :type item: ASAP2Calibrate
            :param value: 标定值(字符串显示形式,对于映射为显示名称)
            :type value: str
            """
            def _callback(future, item: ASAP2Calibrate, value: str, data: bytes):
                """
                线程执行结束的回调函数，执行成功则标定数据显示，刷新程序标定区

                :param future: 线程执行结束返回的future对象
                :type future: concurrent.futures.Future
                :param item: 标定数据项
                :type item: ASAP2Calibrate
                :param value: 标定值(数字字符串显示形式,对于映射则为显示名称)
                :type value: str
                :param data: 标定数据序列(大端)
                :type data: bytes
                """
                try:
                    # 若线程执行中存在异常，则抛出此异常信息
                    if future.exception():
                        self.view.show_warning('修改失败')
                        raise Exception(future.exception())
                    if future.result():
                        self.text_log(f'修改成功', 'done')
                        rom_cal_addr = self.model.a2l_memory_rom_cal.address
                        addr = item.address - rom_cal_addr
                        item.value = value # 更新单元格为标定后的值
                        item.data = data
                        self.__flush_table_operate(target='calibrate')
                        self.model.obj_srecord.flush_cal_data(offset = addr, data = data) # 更新PGM对象的标定区
                    else:
                        self.text_log(f'修改失败', 'error')
                        self.view.show_warning('修改失败')
                except Exception as e:
                    self.text_log(f'发生异常 {e}', 'error')
                    self.text_log(f"{traceback.format_exc()}", 'error')

            try:
                self.text_log(f'======修改RAM区标定数据======', 'done')
                rom_cal_addr = self.model.a2l_memory_rom_cal.address
                ram_cal_addr = self.model.a2l_memory_ram_cal.address
                # 计算标定地址和标定值
                addr = ram_cal_addr + item.address - rom_cal_addr
                val, data = self.__get_raw_data(item=item,
                                                physical_value=value)
                if val is None or data is None:
                    self.text_log(f'标定值未知', 'error')
                    self.view.show_warning('标定值未知')
                    return
                msg = (f"标定变量->{item.name},"
                       f"\n\t物理值->{item.value},"
                       f"\n\t原始值->0x{item.data.hex()},"
                       f"\n\t标定物理值->{val},"
                       f"\n\t标定原始值->0x{data.hex()},"
                       f"\n\t地址->{hex(addr)},"
                       f"\n\t数据类型->{item.record_layout.fnc_values.data_type}")
                self.text_log(msg)
                if item.data == data:
                    self.text_log(f'标定值未变化，无需修改', 'warning')
                    return
                (self.__pool.submit(self.model.obj_measure.write_ram_cal, addr, data).
                 add_done_callback(lambda f: _callback(f,
                                                       item=item,
                                                       value=val,
                                                       data=data))
                 )
            except Exception as e:
                self.text_log(f'发生异常 {e}', 'error')
                self.text_log(f"{traceback.format_exc()}", 'error')
        try:
            text = widget.get().strip()
            lower_limit = item.lower_limit
            upper_limit = item.upper_limit
            if type(widget).__name__ == 'Entry':  # 若控件为数值输入框
                # 验证是否为数值
                try:
                    float(text)
                except ValueError:
                    widget.place_forget()
                    msg = f"变量{item.name}的值必须是数字"
                    self.text_log(msg, 'error')
                    self.view.show_warning(msg)
                    return
                # 格式化
                fm = item.conversion.format[1:]
                if fm:
                    text = f"{float(text): <{fm}f}"
                # 验证是否在指定范围内
                if float(text) - upper_limit > 1E-6 or \
                        float(text) - lower_limit < -1e-6:
                    widget.place_forget()
                    msg = f"变量{item.name}的设定值{text}不在范围[{lower_limit},{upper_limit}]内"
                    self.text_log(msg, 'error')
                    self.view.show_warning(msg)
                    return
            elif type(widget).__name__ == 'Combobox':  # 若控件为下拉选择框
                pass
            widget.place_forget()  # 网格布局中移除编辑控件
            _calibrate(item, text)  # 调用标定任务
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_save_calibrate(self) -> str | None:
        """
        保存标定数据

        :returns: 保存文件的路径
        :rtype: str | None
        """
        try:
            if not self.model.obj_srecord:
                return
            if self.model.obj_srecord.is_modify_cal_data():
                self.text_log(f'======标定数据已修改,保存到下载文件======', 'done')
                filepath = self.model.obj_srecord.creat_file_from_cal_data(filetype='program')
                if filepath:
                    self.text_log(f'保存成功->{filepath}')
                    return filepath
                else:
                    self.text_log(f'保存失败', 'error')
                    self.view.show_warning('保存失败')
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_upload_calibrate(self) -> None:
        """
        从RAM上传标定数据到指定PGM标定数据区

        """

        def _callback(future):
            """
            线程执行结束的回调函数

            :param future: 线程执行结束返回的future对象
            """
            try:
                # 若线程执行中存在异常，则抛出此异常信息
                if future.exception():
                    self.text_log(f'上传失败', 'error')
                    raise Exception(future.exception())
                if future.result():
                    upd_data: bytes = future.result()
                    if upd_data.hex().upper().endswith('1122334455667788'):
                        msg = (f"上传成功"
                               f"\n\t长度 -> {hex(len(upd_data))},"
                               f"\n\t数据结尾 -> {upd_data[-8:].hex().upper()}")
                        self.text_log(msg, 'done')
                        self.model.obj_srecord.flush_cal_data(offset=0,data=upd_data) # 更新指定PGM对象的标定区
                        self.handler_on_ack_select(target='calibrate') # 更新表格及表格数据项
                        # 校验ecu_ram中的标定数据区
                        self.text_log('------校验标定数据区------')
                        cal_page_addr = self.model.a2l_memory_ram_cal.address # 标定区校验首地址
                        cal_page_checksum_length = 0x4000  # 标定区校验长度
                        ecu_cal_1, ecu_cal_2 =(
                            self.model.obj_measure.check_ecu_ram_cal(cal_page_addr, cal_page_checksum_length))
                        # 校验pgm中的标定数据区
                        pgm_cal_1, pgm_cal_2 =(
                            self.model.obj_measure.check_pgm_cal(self.model.obj_srecord, cal_page_checksum_length))
                        # 比对校验结果
                        if ecu_cal_1 == pgm_cal_1 and ecu_cal_2 == pgm_cal_2:
                            self.text_log('ecu标定数据区与pgm标定数据区一致', 'done')
                        else:
                            self.text_log('ecu标定数据区与pgm标定数据区不一致', 'error')
                            self.view.show_warning('ecu标定数据区与pgm标定数据区不一致')
                    else:
                        msg = (f"上传失败，"
                               f"\n\t数据结尾 -> {upd_data[-8:].hex().upper()}")
                        self.text_log(msg, 'error')
                else:
                    self.text_log(f'上传失败', 'error')
                self.view.btn_upload_calibrate.config(state='normal')
            except Exception as e:
                self.text_log(f'发生异常 {e}', 'error')
                self.text_log(f"{traceback.format_exc()}", 'error')
                self.view.btn_upload_calibrate.config(state='normal')

        try:
            # 若未连接设备则退出
            if not (self.model.obj_measure and self.model.obj_measure.has_connected):
                self.view.show_warning('请先连接设备')
                return
            # 若未连接设备则退出
            if self.model.obj_measure.has_measured:
                self.view.show_warning('请先停止测量')
                return
            self.text_log(f'======从RAM上传标定数据======', 'done')
            addr = self.model.a2l_memory_ram_cal.address
            _, length, _ = self.model.obj_srecord.get_cal_data()
            self.__pool.submit(self.model.obj_measure.read_ram_cal, addr, length).add_done_callback(_callback)
            self.text_log(f'上传中 . . .', 'done')
            self.view.btn_upload_calibrate.config(state='disabled')
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')
            self.view.btn_upload_calibrate.config(state='normal')

    def handler_on_program_calibrate(self) -> None:
        """
        将指定PGM标定数据区刷写至ROM

        """

        def _callback(future):
            """
            线程执行结束的回调函数

            :param future: 线程执行结束返回的future对象
            """
            try:
                # 若线程执行中存在异常，则抛出此异常信息
                if future.exception():
                    self.text_log(f'刷写失败', 'error')
                    raise Exception(future.exception())
                if future.result():
                    msg = f"刷写成功"
                    self.text_log(msg, 'done')
                    self.handler_on_ack_select(target='calibrate')  # 更新表格及表格数据项
                    self.handler_on_disconnect()
                    self.handler_on_connect()
                else:
                    self.text_log(f'刷写失败', 'error')
                self.view.btn_program_calibrate.config(state='normal')
            except Exception as e:
                self.text_log(f'发生异常 {e}', 'error')
                self.text_log(f"{traceback.format_exc()}", 'error')
                self.view.btn_program_calibrate.config(state='normal')

        try:
            # 若未连接设备则退出
            if not (self.model.obj_measure and self.model.obj_measure.has_connected):
                self.view.show_warning('请先连接设备')
                return
            # 若未连接设备则退出
            if self.model.obj_measure.has_measured:
                self.view.show_warning('请先停止测量')
                return
            self.text_log(f'======刷写标定数据至ROM======', 'done')
            addr_ram = self.model.a2l_memory_ram_cal.address
            length = self.model.a2l_memory_ram_cal.size
            addr_rom, _, data = self.model.obj_srecord.get_cal_data()
            (self.__pool.submit(self.model.obj_measure.write_rom_cal, addr_rom, addr_ram, length, data).
             add_done_callback(_callback))
            self.text_log(f'刷写中 . . .', 'done')
            self.view.btn_program_calibrate.config(state='disabled')
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')
            self.view.btn_program_calibrate.config(state='normal')

    def __create_measure_obj(self) -> None:
        """
        创建测量标定对象

        """
        try:
            # 借用cfg_download的一些配置
            conf = configparser.ConfigParser()  # 加载配置
            conf.read(filenames=self.__cfg_download_path, encoding='utf-8')
            is_intel_format = conf.getboolean('ccp', 'ccp_is_intel_format')
            timeout = conf.getint('ccp', 'ccp_response_timeout_ms')
            # 创建测量对象
            self.model.obj_measure = eco_pccp.Measure(request_can_id=self.extra_model.ccp_request_id,
                                                      response_can_id=self.extra_model.ccp_response_id,
                                                      ecu_addr=self.extra_model.ccp_ecu_addr,
                                                      is_intel_format=is_intel_format,
                                                      timeout=timeout,
                                                      device_channel=self.extra_model.device_channel,
                                                      device_baudrate=self.extra_model.ccp_baudrate,
                                                      pgm_filepath=self.model.opened_pgm_filepath,
                                                      a2l_filepath=self.model.opened_a2l_filepath,
                                                      obj_srecord=self.model.obj_srecord)
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def __open_file(self, filetype: str, **kwargs) -> None:
        """
        打开文件，将文件路径存储到数据模型

        :param filetype: 文件类型:'程序'，'测量标定'
        :param kwargs: 关键字参数，lbl为显示已打开文件路径的标签控件，dir为要打开文件的初始路径
        """
        if filetype == '程序':
            fileformat = '.mot'
        elif filetype == '测量标定':
            fileformat = '.a2l'
        else:
            fileformat = '.mot'
        lbl = kwargs.get('lbl')
        dir = kwargs.get('dir')

        # 输出日志
        self.text_log(f'打开{filetype}文件中...')
        # 打开文件对话框
        openpath = filedialog.askopenfilename(
            # 默认扩展名，.号可带可不带
            defaultextension=fileformat,
            # 文件类型选项
            filetypes=[(filetype + '文件', fileformat)],
            # 初始目录，默认当前目录
            initialdir=dir if dir else os.getcwd(),
            # 初始文件名，默认为空
            # initialfile='test',
            # 打开的位置，默认是根窗口
            parent=self.view,
            # 窗口标题
            title='打开' + filetype + '文件')
        # 将打开的文件路径写入标签
        if lbl:
            lbl.config(text=openpath)
        if filetype == '程序':
            self.model.opened_pgm_filepath = openpath
        elif filetype == '测量标定':
            self.model.opened_a2l_filepath = openpath
        if openpath:
            # 输出日志
            self.text_log('已打开' + filetype + '文件' + openpath, 'done')
        else:
            # 输出日志
            self.text_log('路径无效，未选择' + filetype + '文件' + openpath, 'warning')

    def __flush_table_select(self, target:str) -> None:
        """
        从数据模型中刷新选择表

        :param target: 目标，'all':所有，'measure':测量数据，'calibrate':标定数据
        :type target: str
        """
        if target == 'all' or target == 'measure':
            # 清空所有数据项
            self.view.table_select_measure.delete(*self.view.table_select_measure.get_children())
            # 刷新选择表格数据项
            for table_item in self.model.table_select_measure_filter_items:
                values = (table_item.is_selected,
                          table_item.name,
                          table_item.is_selected_20ms,
                          table_item.is_selected_100ms)
                self.view.table_select_measure.insert(parent="",
                                                      index="end",
                                                      text="",
                                                      values=values)
        if target == 'all' or target == 'calibrate':
            # 清空所有数据项
            self.view.table_select_calibrate.delete(*self.view.table_select_calibrate.get_children())
            # 刷新选择表格数据项
            for table_item in self.model.table_select_calibrate_filter_items:
                values = (table_item.is_selected,
                          table_item.name,
                          table_item.is_selected_check)
                self.view.table_select_calibrate.insert(parent="",
                                                        index="end",
                                                        text="",
                                                        values=values)

    def __flush_table_operate(self, target:str) -> None:
        """
        从数据模型中刷新操作表(测量/标定)

        :param target: 目标，'all':所有，'measure':测量数据，'calibrate':标定数据
        :type target: str
        """
        if target == 'all' or target == 'measure':
            # 清空所有数据项
            self.view.table_measure.delete(*self.view.table_measure.get_children())
            # 刷新显示测量表
            for table_item in self.model.table_measure_items:
                values = (table_item.name,
                          table_item.value,
                          table_item.rate,
                          table_item.unit)
                self.view.table_measure.insert(parent="",
                                               index="end",
                                               text="",
                                               values=values)
        if target == 'all' or target == 'calibrate':
            # 清空所有数据项
            self.view.table_calibrate.delete(*self.view.table_calibrate.get_children())
            # 刷新显示标定表
            for k, v in self.model.table_calibrate_dict.items():
                values = (k,
                          v.value,
                          v.conversion.unit)
                self.view.table_calibrate.insert(
                    parent="", index="end", text="", values=values)
            if self.__curve_view and self.__curve_view.table_calibrate:
                # 清空所有数据项
                self.__curve_view.table_calibrate.delete(*self.__curve_view.table_calibrate.get_children())
                # 刷新显示Curve标定表
                name = list(self.model.table_calibrate_axis_dict.keys())[0]
                x_name = name[:name.find('_X(')]
                x_values = [item.value for item in self.model.table_calibrate_axis_dict.values()]
                self.__curve_view.table_calibrate.insert(
                    parent="", index="end", text=x_name, values=x_values)
                name = list(self.model.table_calibrate_value_dict.keys())[0]
                y_name = name[:name.find('_Y(')]
                y_values = [item.value for item in self.model.table_calibrate_value_dict.values()]
                self.__curve_view.table_calibrate.insert(
                    parent="", index="end", text=y_name, values=y_values)
            if self.__map_view and self.__map_view.table_calibrate:
                # 清空所有数据项
                self.__map_view.table_calibrate.delete(*self.__map_view.table_calibrate.get_children())
                # 刷新显示Map标定表
                x_values = [item.value for item in self.model.table_calibrate_axis_dict.values()]
                y_values = [item.value for item in self.model.table_calibrate_axis2_dict.values()]
                z_values = [item.value for item in self.model.table_calibrate_value_dict.values()]
                values = ['Y', 'Value'] + x_values
                self.__map_view.table_calibrate.insert(
                    parent="", index="end", text="", values=values)
                for i in range(len(y_values)):
                    values = [str(i), y_values[i]] + z_values[i*len(x_values):(i+1)*len(x_values)] # 按行存储
                    self.__map_view.table_calibrate.insert(
                        parent="", index="end", text="", values=values)

    def __flush_label_select_number(self, target:str):
        """
        刷新显示已选数据项数目和当前筛选出的数据项数目

        :param target: 目标，'all':所有，'measure':测量数据，'calibrate':标定数据
        :type target: str
        """
        if target == 'all' or target == 'measure':
            measure_selected_num = len([item for item in self.model.table_select_measure_raw_items if item.is_selected])
            measure_filter_num = len(self.view.table_select_measure.get_children())  # 不能根据数据模型中filter_items计算，因为其为迭代器，可能已被遍历过
            text = str(measure_selected_num) + '/' + str(measure_filter_num)
            self.view.label_select_measure_number.config(text=text)
        if target == 'all' or target == 'calibrate':
            calibrate_selected_num = len([item for item in self.model.table_select_calibrate_raw_items if item.is_selected])
            calibrate_filter_num = len(self.view.table_select_calibrate.get_children())  # 不能根据数据模型中filter_items计算，因为其为迭代器，可能已被遍历过
            text = str(calibrate_selected_num) + '/' + str(calibrate_filter_num)
            self.view.label_select_calibrate_number.config(text=text)

    def __flush_label_operate_number(self, target:str) -> None:
        """
        刷新显示操作表(测量/标定)数据项数目

        :param target: 目标，'all':所有，'measure':测量数据，'calibrate':标定数据
        :type target: str
        """
        if target == 'all' or target == 'measure':
            measure_num = len(self.model.table_measure_items)
            self.view.label_measure_number.config(text=measure_num)
        if target == 'all' or target == 'calibrate':
            calibrate_num = len(self.model.table_calibrate_dict)
            self.view.label_calibrate_number.config(text=calibrate_num)

    def __get_physical_value(self,
                             item: MeasureItem | ASAP2Calibrate,
                             raw_data: Union[list[int], bytes, bytearray]) -> str:
        """
        根据原始值字节序列，求其物理值;
        raw_value = f(physical_value);
        f(x) = (A*x^2 + B*x + C) / (D*x^2 + E*x + F);

        :param item: 测量/标定数据项
        :type item: MeasureItem | ASAP2Calibrate
        :param raw_data: 原始值字节序列
        :type raw_data: Union[list[int], bytes, bytearray]
        :return: 物理值(数字字符串显示形式，映射则为名称)
        :rtype: str
        """
        if isinstance(item, MeasureItem):
            # 根据不同类型和转换方法求解物理值
            value = '!ParseError'
            data_type = item.data_type
            if data_type == 'UBYTE':
                raw_value = int.from_bytes(bytes(raw_data), 'big', signed=False)  # 原始值
            elif data_type == 'SBYTE':
                raw_value = int.from_bytes(bytes(raw_data), 'big', signed=True)  # 原始值
            elif data_type == 'UWORD':
                raw_value = int.from_bytes(bytes(raw_data), 'big', signed=False)  # 原始值
            elif data_type == 'SWORD':
                raw_value = int.from_bytes(bytes(raw_data), 'big', signed=True)  # 原始值
            elif data_type == 'ULONG':
                raw_value = int.from_bytes(bytes(raw_data), 'big', signed=False)  # 原始值
            elif data_type == 'SLONG':
                raw_value = int.from_bytes(bytes(raw_data), 'big', signed=True)  # 原始值
            elif data_type == 'FLOAT32_IEEE':
                # 确保bytes的长度与浮点数的字节数对应。
                # 对于32位浮点数，使用'f'；
                # 对于64位浮点数，使用'd'。
                # 如果bytes表示的是大端序，可以使用'!'作为格式字符串的前缀来指定字节顺序。
                raw_value = unpack('!f', bytes(raw_data))[0]
            else:
                msg = f"无法解析{item.name}的物理值,尚未支持类型{data_type}"
                self.text_log(msg, 'error')
                return value

            # 若是转换类型为映射表
            conversion_type = item.conversion_type
            if conversion_type == 'TAB_VERB':
                if raw_value in item.compu_vtab.keys():
                    value = raw_value
                    return ''.join(
                        [item.compu_vtab[value], ':',
                         pad_hex(hex(value), self.model.ASAP2_TYPE_SIZE[data_type])])
                else:
                    msg = f"无法解析{item.name}的物理值,{raw_value}的映射不存在"
                    self.text_log(msg, 'error')
                    return value
            # 若是转换类型为普通数值(线性转换)
            elif conversion_type == 'RAT_FUNC':
                # raw_value = f(physical_value);
                # f(x) = B*x + C;
                coeffs = item.coeffs
                value = (raw_value - coeffs[2]) / coeffs[1]
            else:
                msg = f"无法解析{item.name}的物理值,尚未支持类型{conversion_type}"
                self.text_log(msg, 'error')
                return value
            # 格式化
            fm = item.format  # 去掉%,%8.2->8.2
            if fm:
                value = f"{value: <{fm[0]}.{fm[1]}f}"
            # 返回
            return value.strip()

        elif isinstance(item, ASAP2Calibrate):
            # 根据不同类型和转换方法求解物理值
            value = '!ParseError'
            data_type = item.record_layout.fnc_values.data_type
            if data_type == ASAP2EnumDataType.UBYTE:
                raw_value = int.from_bytes(bytes(raw_data), 'big', signed=False)  # 原始值
            elif data_type == ASAP2EnumDataType.SBYTE:
                raw_value = int.from_bytes(bytes(raw_data), 'big', signed=True)  # 原始值
            elif data_type == ASAP2EnumDataType.UWORD:
                raw_value = int.from_bytes(bytes(raw_data), 'big', signed=False)  # 原始值
            elif data_type == ASAP2EnumDataType.SWORD:
                raw_value = int.from_bytes(bytes(raw_data), 'big', signed=True)  # 原始值
            elif data_type == ASAP2EnumDataType.ULONG:
                raw_value = int.from_bytes(bytes(raw_data), 'big', signed=False)  # 原始值
            elif data_type == ASAP2EnumDataType.SLONG:
                raw_value = int.from_bytes(bytes(raw_data), 'big', signed=True)  # 原始值
            elif data_type == ASAP2EnumDataType.FLOAT32_IEEE:
                # 确保bytes的长度与浮点数的字节数对应。
                # 对于32位浮点数，使用'f'；
                # 对于64位浮点数，使用'd'。
                # 如果bytes表示的是大端序，可以使用'!'作为格式字符串的前缀来指定字节顺序。
                raw_value = unpack('!f', bytes(raw_data))[0]
            else:
                msg = f"无法解析{item.name}的物理值,尚未支持类型{data_type}"
                self.text_log(msg, 'error')
                return value

            # 若是转换类型为映射表
            conversion_type = item.conversion.conversion_type
            if conversion_type == ASAP2EnumConversionType.TAB_VERB:
                if raw_value in item.conversion.compu_tab_ref.read_dict:
                    value = raw_value
                    return ''.join(
                        [item.conversion.compu_tab_ref.read_dict[value], ':',
                         pad_hex(hex(value), ASAP2EnumDataType.get_size(data_type.name))])
                else:
                    msg = f"无法解析{item.name}的物理值,{raw_value}的映射不存在"
                    self.text_log(msg, 'error')
                    return value
            # 若是转换类型为普通数值(线性转换)
            elif conversion_type == ASAP2EnumConversionType.RAT_FUNC:
                # raw_value = f(physical_value);
                # f(x) = B*x + C;
                coeffs = item.conversion.coeffs
                value = (raw_value - coeffs[2]) / coeffs[1]
            else:
                msg = f"无法解析{item.name}的物理值,尚未支持类型{conversion_type}"
                self.text_log(msg, 'error')
                return value
            # 格式化
            fm = item.conversion.format[1:] # 去掉%,%8.2->8.2
            if fm:
                value = f"{value: <{fm}f}"
            # 返回
            return value.strip()

    def __get_raw_data(self,
                       item: ASAP2Calibrate,
                       physical_value: str) -> tuple[str | None, bytes | None]:
        """
        根据物理值，求标定对象的原始值字节序列;
        raw_value = f(physical_value);
        f(x) = (A*x^2 + B*x + C) / (D*x^2 + E*x + F);

        :param item: 测量/标定数据项
        :type item: ASAP2Calibrate
        :param physical_value: 物理值(数字的字符串显示形式，对于映射为显示名称)
        :type physical_value: str
        :return: 物理值(数字的字符串显示形式，对于映射则为显示的名称)，原始值字节序列(大端)
        :rtype: tuple[str | None, bytes | None]
        """
        conversion_type = item.conversion.conversion_type
        # 若是转换类型为映射表
        if (physical_value is not None) and (conversion_type == ASAP2EnumConversionType.TAB_VERB):
            vtab_write_dict = item.conversion.compu_tab_ref.write_dict  # 数值映射字典，名称->数值
            value = vtab_write_dict[physical_value]
        # 若是转换类型为普通数值
        elif (physical_value is not None) and (conversion_type == ASAP2EnumConversionType.RAT_FUNC):
            # raw_value = f(physical_value);
            # f(x) = B*x + C;
            coeffs = item.conversion.coeffs
            value = float(physical_value) * coeffs[1] + coeffs[2] # 线性转换
        else:
            msg = f"无法解析{item.name}的原始值,尚未支持类型{conversion_type}"
            self.text_log(msg, 'error')
            self.view.show_warning(msg)
            return None, None
        # 根据不同类型和转换方法求解原始值
        data_type = item.record_layout.fnc_values.data_type
        if data_type == ASAP2EnumDataType.UBYTE:
            value = int(value)
            raw_data = int.to_bytes(value,
                                    length=ASAP2EnumDataType.get_size(data_type.name),
                                    byteorder='big',
                                    signed=False) # 原始值
        elif data_type == ASAP2EnumDataType.SBYTE:
            value = int(value)
            raw_data = int.to_bytes(value,
                                    length=ASAP2EnumDataType.get_size(data_type.name),
                                    byteorder='big',
                                    signed=True)  # 原始值
        elif data_type == ASAP2EnumDataType.UWORD:
            value = int(value)
            raw_data = int.to_bytes(value,
                                    length=ASAP2EnumDataType.get_size(data_type.name),
                                    byteorder='big',
                                    signed=False)  # 原始值
        elif data_type == ASAP2EnumDataType.SWORD:
            value = int(value)
            raw_data = int.to_bytes(value,
                                    length=ASAP2EnumDataType.get_size(data_type.name),
                                    byteorder='big',
                                    signed=True)  # 原始值
        elif data_type == ASAP2EnumDataType.ULONG:
            value = int(value)
            raw_data = int.to_bytes(value,
                                    length=ASAP2EnumDataType.get_size(data_type.name),
                                    byteorder='big',
                                    signed=False)  # 原始值
        elif data_type == ASAP2EnumDataType.SLONG:
            value = int(value)
            raw_data = int.to_bytes(value,
                                    length=ASAP2EnumDataType.get_size(data_type.name),
                                    byteorder='big',
                                    signed=True)  # 原始值
        elif data_type == ASAP2EnumDataType.FLOAT32_IEEE:
            raw_data = pack('!f', value)  # 原始值
        else:
            msg = f"无法解析{item.name}的原始值,尚未支持类型{data_type}"
            self.text_log(msg, 'error')
            self.view.show_warning(msg)
            return None, None
        # 返回
        return self.__get_physical_value(item, raw_data), raw_data

    def __get_daqs(self, daqs_cfg: dict[int, dict[str, int]]) -> dict[int, dict[int, list[MeasureItem]]]:
        """
        将测量数据项按daq分配到各odt，得到daq分配列表

        :param daqs_cfg: daq配置，{daq_number: {first_pid: int, odts_size: int}}
        :type daqs_cfg: dict[int, dict[str, int]]
        :return: daqs，daq列表，{daq_number: {odt_number: [item, ...]}}，
            例如{ 1: {0: [item0, item1],
                     1: [item2, item3, item4]
                     },
                 2: {0: [item5, item6, item7],
                     1: [item8, item9, item10, item11]
                    }
                }
        :rtype: dict[int, dict[int, list[MeasureItem]]]
        :raises Exception: 数据项的转换系数不被支持；分配daq超过odt列表允许的最大范围；
        """

        def _write_odts(group_of_daq: list[MeasureItem]) -> dict[int, list[MeasureItem]]:
            """
            将指定daq的测量数据项分配到各odt中

            :param group_of_daq: 指定daq的测量数据项列表
            :type group_of_daq: list[MonitorItem]
            :return: odts，指定daq的odt列表，例如{0: [item0, item1], 1: [item2, item3, item4]}，
                键0是本daq的odt列表序号为0的odt，值[item0, item1]为该odt中包含的测量数据项列表
            :rtype: dict[int, list[MeasureItem]]
            :raises ValueError: 数据项的元素大小属性值不是1,2,4中的一个
            """

            def _get_free_memory_of_odt(odt: list[MeasureItem]) -> int:
                """
                获取odt空闲容量

                :param odt: 元素为MonitorItem对象的列表，元素大小总和不超过7字节
                :type odt: list[MeasureItem]
                :return: 空闲容量，单位字节
                :rtype: int
                """
                res = 0
                for element in odt:
                    res += element.element_size
                return 7 - res

            # 声明变量
            odts: dict[int, list[MeasureItem]] = {}  # odt列表
            ptr_4byte = 0  # 4字节odt指针，大小为4字节的元素所在odt的列表索引
            ptr_2byte = 0  # 2字节odt指针，大小为2字节的元素所在odt的列表索引
            ptr_1byte = 0  # 1字节odt指针，大小为1字节的元素所在odt的列表索引

            # 处理每项数据
            for item in group_of_daq:
                if item.element_size == 4:
                    # 若odts中不存在key为ptr_4byte的odt，则新建key为ptr_4byte的odt，并存入数据项
                    # 若key为ptr_4byte的odt空闲容量大于4，则存入数据项
                    # 否则ptr_4byte指向下一odt，重复上述步骤
                    while True:
                        if ptr_4byte not in odts:
                            odts[ptr_4byte] = [item]
                            break
                        elif _get_free_memory_of_odt(odts[ptr_4byte]) >= 4:
                            odts[ptr_4byte].append(item)
                            break
                        else:
                            ptr_4byte += 1
                elif item.element_size == 2:
                    # 若odts中不存在key为ptr_2byte的odt，则新建key为ptr_2byte的odt，并存入数据项
                    # 若key为ptr_2byte的odt空闲容量大于2，则存入数据项
                    # 否则ptr_2byte指向下一odt，重复上述步骤
                    while True:
                        if ptr_2byte not in odts:
                            odts[ptr_2byte] = [item]
                            break
                        elif _get_free_memory_of_odt(odts[ptr_2byte]) >= 2:
                            odts[ptr_2byte].append(item)
                            break
                        else:
                            ptr_2byte += 1
                elif item.element_size == 1:
                    # 若odts中不存在key为ptr_1byte的odt，则新建key为ptr_1byte的odt，并存入数据项
                    # 若key为ptr_1byte的odt空闲容量大于1，则存入数据项
                    # 否则ptr_1byte指向下一odt，重复上述步骤
                    while True:
                        if ptr_1byte not in odts:
                            odts[ptr_1byte] = [item]
                            break
                        elif _get_free_memory_of_odt(odts[ptr_1byte]) >= 1:
                            odts[ptr_1byte].append(item)
                            break
                        else:
                            ptr_1byte += 1
                else:
                    msg = f'数据项{item.name}的element_size不在1、2、4中'
                    raise ValueError(msg)
            return odts  # 返回odt列表

        self.text_log('------分配daq------')

        # 根据速率对测量数据项分组
        group_by_daq: dict[int, list[MeasureItem]] = {}  # 根据daq对测量数据项分组的结果
        for key, group in groupby(sorted(self.model.table_measure_items, key=lambda x: x.daq_number),
                                  key=lambda x: x.daq_number):
            group_by_daq[key] = list(group)

        # 写入daq列表
        daqs: dict[int, dict[int, list[MeasureItem]]] = {}  # daq列表
        for daq_number in group_by_daq.keys():
            daqs[daq_number] = _write_odts(group_of_daq=group_by_daq[daq_number])

        # 判断转换系数是否被支持，以及odt列表是否超出允许的长度
        msg_exception_coeffs = ''
        msg_exception_outrange = ''
        for daq_number, odts in daqs.items():
            # 若odt列表中存在转换系数不被支持的数据项，则抛出异常
            for _, odt in odts.items():
                for item in odt:
                    # 普通数值转换类型
                    # raw_value = f(physical_value)
                    # f(x) = (A*x^2 + B*x + C) / (D*x^2 + E*x + F)
                    if item.conversion_type == "RAT_FUNC":
                        A, B, C, D, E, F = item.coeffs
                        if (A > 1e-6) or (D > 1e-6) or (E > 1e-6) or (F - 1.0 > 1e-6):
                            msg_exception_coeffs += f"{item.name}的转换系数{item.coeffs}不支持\n"
            if msg_exception_coeffs:
                continue
            # 若odt列表超出允许的长度，则抛出异常
            if len(odts) >= daqs_cfg[daq_number]['odts_size']:
                msg_exception_outrange = f"daq{daq_number}中odt至多为{daqs_cfg[daq_number]['odts_size']},无法容纳以下对象:\n"
                for idx in range(daqs_cfg[daq_number]['odts_size'], len(odts)):
                    for item in odts[idx]:
                        msg_exception_outrange += f"   {item.name}\n"
        if msg_exception_coeffs:
            raise Exception(msg_exception_coeffs)
        if msg_exception_outrange:
            raise Exception(msg_exception_outrange)

        # 获取测量数据项的属性，打印odt列表
        self.text_log('分配完成')
        for daq_number, odts in daqs.items():
            for odt_number, odt in odts.items():
                for element_number in range(len(odt)):
                    item = odt[element_number]  # 获取测量数据项
                    item.daq_number = daq_number  # daq列表序号属性
                    item.odt_number = odt_number  # odt列表序号属性
                    item.element_number = element_number  # odt元素序号属性
                    item.pid = hex(daqs_cfg[daq_number]['first_pid'] + odt_number)  # odt的pid属性

                    # msg = f"daq:{daq_number}->odt:{odt_number}->name:{item.name}/size:{item.element_size}"
                    # self.text_log(msg)
        return daqs  # 返回daq列表

    def __recv_daq_dto(self) -> None:
        """
        解析daq_dto数据为显示格式的数据，将其压入队列
        """

        def _put_to_queue(data):
            """
            将数据放入队列

            :param data: 待放入队列的数据
            """
            try:
                _q.put_nowait(copy.deepcopy(data))
            except:
                pass

        self.text_log("接收数据中 . . .", 'done')

        # 待显示的值{在测量数据项列表中的索引:int，物理值:str}
        display_values: dict[int, str] = {}
        # 创建后台执行的 schedulers
        scheduler_recv = BackgroundScheduler()
        # 添加调度任务
        scheduler_recv.add_job(func=_put_to_queue,
                               trigger='interval',
                               seconds=int(self.model.refresh_operate_measure_time_ms) / 1000,
                               id='job_id_recv',
                               max_instances=1,
                               args=(display_values,))
        # 启动调度任务
        if not scheduler_recv.state:
            scheduler_recv.start()
            pass

        # 建立局部变量，加快访问速度
        _q = self.model.q  # 队列
        _DAQS_CFG = self.model.daqs_cfg  # daq列表信息
        _DAQS = self.model.daqs  # daq列表
        _obj_measure = self.model.obj_measure  # 测量对象
        _read_dto_msg = self.model.obj_measure.read_dto_msg  # 读取dto消息方法

        # 各通道可能的pid集合初始值
        AVAILABLE_PIDS_BY_DAQ: dict[int, set[int]] = {}
        for daq_number in _DAQS_CFG.keys():
            first_pid = _DAQS_CFG[daq_number]['first_pid']
            last_pid = first_pid + _DAQS_CFG[daq_number]['odts_size'] - 1
            AVAILABLE_PIDS_BY_DAQ[daq_number] = set([x for x in range(first_pid, last_pid + 1)])

        # 清空队列
        while not _q.empty():
            _q.get()

        while True:
            # 若停止测量，将线程池的最大线程由3变为1，并退出，后续提交的任务将是排队等待有序执行
            if not _obj_measure.has_measured:  # 点击停止按钮后若成功停止，则在停止任务中会复位此标识
                if scheduler_recv.state:
                    scheduler_recv.shutdown(wait=False)  # 关闭定时任务
                break

            msg_data = _read_dto_msg()  # 读取dto消息数据
            # 若消息数据为空，则跳过
            if not msg_data:
                # print('无数据')
                continue

            is_exist_in_pids = False  # 是否存在pid
            pid = msg_data[0]  # dto的pid
            odt_data = msg_data[1:]  # odt数据

            for daq_number in _DAQS_CFG.keys():
                # 若pid不在daq支持的pid范围内，则跳过
                if pid not in AVAILABLE_PIDS_BY_DAQ[daq_number]:
                    continue
                is_exist_in_pids = True
                break  # 若pid在某个daq的pid范围内，则跳出for循环

            # 若pid不存在，则跳过
            if not is_exist_in_pids:
                continue

            # 添加到显示数据集合
            element_number = 0  # odt元素索引
            element_offset = 0  # odt元素偏移量
            for item in _DAQS[daq_number][pid - _DAQS_CFG[daq_number]['first_pid']]:
                element_size = item.element_size  # odt元素大小，占用字节数
                element_data = odt_data[element_offset:element_offset + element_size]  # odt元素数据
                element_offset += element_size  # 更新odt元素偏移量
                element_number += 1  # 更新odt元素索引

                # 获取物理值
                physical_value = self.__get_physical_value(item=item,
                                                           raw_data=element_data)
                display_values[item.idx_in_table_measure_items] = physical_value

    def __display_monitor_value(self) -> None:
        """
        显示value值到测量表格
        """

        def _disp(iid, value):
            """
            显示value值到测量表格数据项
            """
            _table_monitor.set(iid, _column_names.index('Value'), value)

        # 建立局部变量，加快访问速度
        _q = self.model.q  # 显示值队列
        _obj_measure = self.model.obj_measure  # 是否已测量
        _table_monitor = self.view.table_measure  # 测量表格
        _table_measure_items = self.model.table_measure_items # 测量表格数据项
        # 获取测量表格中所有的item_id列表
        _table_monitor_iids = _table_monitor.get_children()
        # 获取测量表格列名组成的元组
        _column_names = tuple(_table_monitor["columns"])

        if not _obj_measure.has_measured:  # 点击停止按钮后若成功停止，则在停止任务中会复位此标识
            self.view.after_cancel(self.__after_id)
            return
        try:
            display_values = _q.get_nowait()
            for idx, value in display_values.items():
                item_id = _table_monitor_iids[idx]
                _disp(item_id, value)
                _table_measure_items[idx].value = value
        except:
            pass
        self.__after_id = self.view.after(ms=int(self.model.refresh_operate_measure_time_ms),
                                          func=self.__display_monitor_value)

    @staticmethod
    def __iid2idx_in_select_table(iid: str,
                                  table_widget: TkTreeView | ttk.Treeview,
                                  raw_items: list[SelectMeasureItem | SelectCalibrateItem],
                                  ) -> tuple[int, SelectMeasureItem | SelectCalibrateItem]:
        """
        根据选择表格数据项iid查询Name列的值，根据Name追溯填充此表格数据项列表的相应索引及其数据

        :param iid: 表格数据项id
        :type iid: str
        :param table_widget: 表格控件
        :type table_widget: TkTreeView | ttk.Treeview
        :param raw_items: 填充表格数据项的列表
        :type raw_items: list[SelectMeasureItem | SelectCalibrateItem]
        :return: (index,数据项对象)
        :rtype: tuple[int, SelectMeasureItem | SelectCalibrateItem]
        :raises TypeError: 不支持raw_items元素的类型
        """

        # 查找更改数据项在原始数据项列表中的索引
        name = table_widget.set(iid, 'Name')
        idx = [item.name for item in raw_items].index(name)
        # 获取最新选中数据项的值
        item_values = table_widget.item(iid, "values")
        # 获取数据项
        if isinstance(raw_items[0], SelectMeasureItem):
            table_item = SelectMeasureItem(*item_values)
        elif isinstance(raw_items[0], SelectCalibrateItem):
            table_item = SelectCalibrateItem(*item_values)
        else:
            raise TypeError(f'iid2idx尚未支持类型{type(raw_items[0])}')
        # 返回
        return idx, table_item

    @staticmethod
    def get_selected_cell_in_table(e: tk.Event,
                                   table: ttk.Treeview, ) -> tuple[str, str, str, tuple[int, int, int, int]]:
        """
        获取表格中选中的单元格，返回（iid，列名，'Name'列名称，几何位置）

        :param e: 事件
        :type e: tk.Event
        :param table: 表格
        :type table: ttk.Treeview
        :return: (iid，列名，'Name'列名称，几何位置)
        :rtype: tuple[str,str,str,tuple[int,int,int,int]]
        """
        iid = ''
        col = ''
        name = ''
        x = y = w = h = 0
        # 选中数据项为空则退出
        if not table.selection():
            return iid, col, name, (x, y, w, h)
        iid = table.selection()[0]  # 选中的数据项id
        col_names = table['columns']  # 表列名列表
        # 判断鼠标点击事件的位置, 是否在选中数据项的边界内, 如果在, 则获取该列的列名和数据项值，否则退出
        for col_name in col_names:
            # 获取选中单元格的边界（相对于控件窗口的坐标），形式为 (x, y, width, height)
            x, y, w, h = table.bbox(iid, col_name)
            if x < e.x < x + w and y < e.y < y + h:
                col = col_name  # 选中的数据项所在列的列名
                if 'Name' in col_names:
                    name = table.set(iid, 'Name')
                break
        return iid, col, name, (x, y, w, h)

    def __assign_calibration_dict(self,
                                  names: tuple[str,...],
                                  dest: dict[str, ASAP2Calibrate]) -> None:
        """
        根据标定对象名称从a2l_calibration_dict获取其属性，并填充到指定的标定对象字典中

        Args:
            names (tuple[str]): 存储标定名称的元组
            dest (dict[str, ASAP2Calibrate]): 存储标定对象的字典
        """
        dest.clear()
        for name in names:
            dest[name] = ASAP2Calibrate(name=name)
        for cal_item in dest.values():
            # ->获取a2l标定对象,以下属性直接或间接来自于此对象
            a2l_item = self.model.a2l_calibration_dict[cal_item.name]

            # ->描述
            cal_item.long_identifier = a2l_item.long_identifier

            # ->标定类型
            cal_item.cal_type = ASAP2EnumCalibrateType.creat(a2l_item.type)

            # ->内存地址
            cal_item.address = a2l_item.address

            # ->数据记录内存布局
            a2l_record_layout = self.model.a2l_record_layout_dict[a2l_item.record_layout]
            # -->表值(函数值)内存布局
            if a2l_record_layout.fnc_values:
                fnc_values = ASAP2FncValues(
                    position=a2l_record_layout.fnc_values.position,
                    data_type=ASAP2EnumDataType.creat(a2l_record_layout.fnc_values.data_type) if
                    a2l_record_layout.fnc_values.data_type else None,
                    index_mode=ASAP2EnumIndexMode.creat(a2l_record_layout.fnc_values.index_mode) if
                    a2l_record_layout.fnc_values.index_mode else None,
                    address_type=ASAP2EnumAddrType.creat(a2l_record_layout.fnc_values.address_type) if
                    a2l_record_layout.fnc_values.address_type else None
                )
            else:
                fnc_values = None
            # -->轴点内存布局
            if a2l_record_layout.axis_pts_x:
                axis_pts_x = ASAP2AxisPtsXYZ45(
                    position=a2l_record_layout.axis_pts_x.position,
                    data_type=ASAP2EnumDataType.creat(a2l_record_layout.axis_pts_x.data_type) if
                    a2l_record_layout.axis_pts_x.data_type else None,
                    index_order=ASAP2EnumIndexOrder.creat(a2l_record_layout.axis_pts_x.index_incr) if
                    a2l_record_layout.axis_pts_x.index_incr else None,
                    address_type=ASAP2EnumAddrType.creat(a2l_record_layout.axis_pts_x.addressing) if
                    a2l_record_layout.axis_pts_x.addressing else None
                )
            else:
                axis_pts_x = None
            # -->内存布局
            cal_item.record_layout = ASAP2RecordLayout(name=a2l_record_layout.name,
                                                       fnc_values=fnc_values,
                                                       axis_pts_x=axis_pts_x)
            # ->值调整的最大浮点数
            cal_item.max_diff = a2l_item.max_diff

            # ->转换方法
            a2l_conversion = self.model.a2l_conversion_dict[a2l_item.conversion]
            # -->转换表
            if a2l_conversion.compu_tab_ref:
                a2l_compu_vtab = self.model.a2l_compu_vtab_dict[a2l_conversion.compu_tab_ref]
                compu_vtab = ASAP2CompuVtab(
                    name=a2l_compu_vtab.name,
                    long_identifier=a2l_compu_vtab.long_identifier,
                    number_value_pairs=a2l_compu_vtab.number_value_pairs,
                    read_dict=a2l_compu_vtab.read_dict,
                    write_dict=a2l_compu_vtab.write_dict
                )
            else:
                compu_vtab = None
            # -->转换方法
            cal_item.conversion = ASAP2CompuMethod(
                name=a2l_conversion.name,
                long_identifier=a2l_conversion.long_identifier,
                conversion_type=ASAP2EnumConversionType.creat(a2l_conversion.conversion_type) if
                a2l_conversion.conversion_type else None,
                format=a2l_conversion.format,
                unit=a2l_conversion.unit,
                coeffs=a2l_conversion.coeffs,
                compu_tab_ref=compu_vtab
            )

            # ->物理值下限
            cal_item.lower_limit = a2l_item.lower_limit

            # ->物理值上限
            cal_item.upper_limit = a2l_item.upper_limit

            # ->对于VAL_BLK和ASCII类型的标定对象，指定固定值或字符的数量
            cal_item.array_size = a2l_item.number

            # ->坐标轴描述
            if a2l_item.axis_descrs:
                cal_item.axis_descrs = []
                for axis_descr in a2l_item.axis_descrs:
                    a2l_axis_pts: AxisPts = self.model.a2l_axis_pts_dict[axis_descr.axis_pts_ref]
                    # --> 数据记录内存布局
                    a2l_axis_record_layout = self.model.a2l_record_layout_dict[a2l_axis_pts.record_layout]
                    # --->表值(函数值)内存布局
                    if a2l_axis_record_layout.fnc_values:
                        fnc_values = ASAP2FncValues(
                            position=a2l_axis_record_layout.fnc_values.position,
                            data_type=ASAP2EnumDataType.creat(a2l_axis_record_layout.fnc_values.data_type) if
                            a2l_axis_record_layout.fnc_values.data_type else None,
                            index_mode=ASAP2EnumIndexMode.creat(a2l_axis_record_layout.fnc_values.index_mode) if
                            a2l_axis_record_layout.fnc_values.index_mode else None,
                            address_type=ASAP2EnumAddrType.creat(a2l_axis_record_layout.fnc_values.address_type) if
                            a2l_axis_record_layout.fnc_values.address_type else None
                        )
                    else:
                        fnc_values = None
                    # --->轴点内存布局
                    if a2l_axis_record_layout.axis_pts_x:
                        axis_pts_x = ASAP2AxisPtsXYZ45(
                            position=a2l_axis_record_layout.axis_pts_x.position,
                            data_type=ASAP2EnumDataType.creat(a2l_axis_record_layout.axis_pts_x.data_type) if
                            a2l_axis_record_layout.axis_pts_x.data_type else None,
                            index_order=ASAP2EnumIndexOrder.creat(a2l_axis_record_layout.axis_pts_x.index_incr) if
                            a2l_axis_record_layout.axis_pts_x.index_incr else None,
                            address_type=ASAP2EnumAddrType.creat(a2l_axis_record_layout.axis_pts_x.addressing) if
                            a2l_axis_record_layout.axis_pts_x.addressing else None
                        )
                    else:
                        axis_pts_x = None
                    # --->内存布局
                    record_layout = ASAP2RecordLayout(name=a2l_axis_record_layout.name,
                                                      fnc_values=fnc_values,
                                                      axis_pts_x=axis_pts_x)

                    # -->转换方法
                    a2l_conversion = self.model.a2l_conversion_dict[a2l_axis_pts.conversion]
                    # --->转换表
                    if a2l_conversion.compu_tab_ref:
                        a2l_axis_compu_vtab = self.model.a2l_compu_vtab_dict[a2l_conversion.compu_tab_ref]
                        compu_vtab = ASAP2CompuVtab(
                            name=a2l_axis_compu_vtab.name,
                            long_identifier=a2l_axis_compu_vtab.long_identifier,
                            number_value_pairs=a2l_axis_compu_vtab.number_value_pairs,
                            read_dict=a2l_axis_compu_vtab.read_dict,
                            write_dict=a2l_axis_compu_vtab.write_dict
                        )
                    else:
                        compu_vtab = None
                    # --->转换方法
                    conversion = ASAP2CompuMethod(
                        name=a2l_conversion.name,
                        long_identifier=a2l_conversion.long_identifier,
                        conversion_type=ASAP2EnumConversionType.creat(a2l_conversion.conversion_type) if
                        a2l_conversion.conversion_type else None,
                        format=a2l_conversion.format,
                        unit=a2l_conversion.unit,
                        coeffs=a2l_conversion.coeffs,
                        compu_tab_ref=compu_vtab
                    )

                    # -->轴点参考
                    axis_pts_ref = ASAP2AxisPts(
                        name=a2l_axis_pts.name,
                        long_identifier=a2l_axis_pts.long_identifier,
                        address=a2l_axis_pts.address,
                        input_quantity=a2l_axis_pts.input_quantity,
                        record_layout=record_layout,
                        max_diff=a2l_axis_pts.max_diff,
                        conversion=conversion,
                        max_axis_points=a2l_axis_pts.max_axis_points,
                        lower_limit=a2l_axis_pts.lower_limit,
                        upper_limit=a2l_axis_pts.upper_limit
                    )

                    # -->轴描述
                    cal_item.axis_descrs.append(
                        ASAP2AxisDescr(
                            axis_type=ASAP2EnumAxisType.creat(axis_descr.attribute),
                            axis_pts_ref=axis_pts_ref)
                    )

            # 物理值
            cal_item.value = None
            # value字段的原始数据序列
            cal_item.data = None

    def __assign_calibrate_axis_dict(self,
                                     curve_or_map_item: ASAP2Calibrate,
                                     axis: str) -> dict[str, ASAP2Calibrate] | None:
        """
        获取CURVE或MAP类型的标定对象的轴标定数据,第一个参数块描述X轴,第二个参数块描述Y轴(若存在)

        Args:
            curve_or_map_item (ASAP2Calibrate): CURVE或MAP类型的标定对象
            axis (str): 轴名称,'X'或'Y'
        Returns:
            dict[str, ASAP2Calibrate] | None: 轴标定数据
        """

        axis_dict: dict[str, ASAP2Calibrate] = {}  # 轴标定数据字典
        if axis == 'X':
            axis_item_ref = curve_or_map_item.axis_descrs[0].axis_pts_ref  # X轴
        else:
            axis_item_ref = curve_or_map_item.axis_descrs[1].axis_pts_ref  # Y轴
        # 获取轴的点数
        max_axis_points = axis_item_ref.max_axis_points
        # 获取点标定数据添加至轴标定数据字典
        for idx in range(max_axis_points):
            axis_calibrate = copy.deepcopy(curve_or_map_item)
            axis_calibrate.name = axis_item_ref.name + (f"_X({idx})" if axis == 'X' else f"_Y({idx})")  # 名称
            axis_calibrate.long_identifier = axis_item_ref.long_identifier  # 描述
            axis_calibrate.cal_type = ASAP2EnumCalibrateType.VALUE  # 标定类型
            if axis_item_ref.record_layout.axis_pts_x.index_order == ASAP2EnumIndexOrder.INDEX_INCR:
                axis_calibrate.address = (axis_item_ref.address +
                                          idx * ASAP2EnumDataType.get_size(
                            axis_item_ref.record_layout.axis_pts_x.data_type.name))  # 数据地址
            else:
                msg = f"尚未支持{axis_calibrate.name}的类型(地址增长类型{axis_item_ref.record_layout.axis_pts_x.index_order})"
                self.text_log(msg, 'error')
                self.view.show_warning(msg)
                return
            # 数据记录内存布局
            fnc_values = ASAP2FncValues(
                position=axis_item_ref.record_layout.axis_pts_x.position,
                data_type=axis_item_ref.record_layout.axis_pts_x.data_type,
                index_mode=curve_or_map_item.record_layout.fnc_values.index_mode,
                address_type=axis_item_ref.record_layout.axis_pts_x.address_type)
            # ->轴点内存布局
            axis_pts_x = None
            axis_calibrate.record_layout = ASAP2RecordLayout(name=None,
                                                             fnc_values=fnc_values,
                                                             axis_pts_x=axis_pts_x)  # 数据记录内存布局
            axis_calibrate.max_diff = axis_item_ref.max_diff  # 值调整的最大浮点数
            axis_calibrate.conversion = axis_item_ref.conversion  # 转换方法
            axis_calibrate.lower_limit = axis_item_ref.lower_limit  # 物理值下限
            axis_calibrate.upper_limit = axis_item_ref.upper_limit  # 物理值上限
            axis_calibrate.array_size = None  # 对于VAL_BLK和ASCII类型的标定对象，指定固定值或字符的数量
            axis_calibrate.axis_descrs = None  # 对于CURVE和MAP类型的标定对象,用于指定轴描述的参数,第一个参数块描述X轴,第二个参数块描述Y轴

            # 获取原始值，将其转为物理值
            rom_cal_addr = self.model.a2l_memory_rom_cal.address
            offset = axis_calibrate.address - rom_cal_addr
            length = ASAP2EnumDataType.get_size(axis_calibrate.record_layout.fnc_values.data_type.name)
            raw_data = (self.model.obj_srecord.get_raw_data_from_cal_data(offset=offset,
                                                                          length=length))
            axis_calibrate.data = raw_data  # value字段的原始数据序列
            value = self.__get_physical_value(item=axis_calibrate,
                                              raw_data=raw_data)
            axis_calibrate.value = value  # 物理值
            # 添加数据项
            axis_dict[axis_calibrate.name] = axis_calibrate
        # 返回
        return axis_dict
