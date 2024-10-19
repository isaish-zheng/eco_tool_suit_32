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
from struct import unpack  # 解析浮点数
import time
from tkinter import Event, filedialog  # 类型提示
import traceback  # 用于获取异常详细信息
from typing import Dict, List, Tuple, Set  # 类型提示

from apscheduler.schedulers.background import BackgroundScheduler
from xba2l.a2l_base import Options as OptionsParseA2l  # 解析a2l文件
from xba2l.a2l_util import parse_a2l  # 解析a2l文件

from eco import eco_pccp
from eco.pcandrive import pcanbasic
from srecord import Srecord
from utils import singleton, pad_hex

from .model import MeasureModel, TableItem, MonitorItem, Measurement
from .view import MeasureView, TkTreeView
from ..download.model import DownloadModel


##############################
# Controller API function declarations
##############################

# @singleton
class MeasureCtrl(object):
    """
    测量界面的业务逻辑处理

    :param model: 测量视图的数据模型
    :type model: MeasureModel
    :param view: 测量视图
    :type view: MeasureView
    :param extra_model: 其它界面的数据模型，用于当前窗口使用其它窗口的数据
    :type extra_model: DownloadModel
    :param text_log: 日志输出函数
    :type text_log: callable
    :param cfg_path: 下载程序、监视测量对象的配置文件路径
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
        self.__cfg_measure_path = cfg_path[1]

        # 创建一个线程池，最大线程数为1，用于执行窗口事件
        self.__pool = ThreadPoolExecutor(max_workers=1, thread_name_prefix='task_measure_')
        # 创建一个线程池，最大线程数为1，用于执行接收daq_dto数据
        self.__pool_recv = ThreadPoolExecutor(max_workers=1, thread_name_prefix='task_recv_')
        self.__after_id = None  # 窗口定时器id

        # 初始化配置
        self.ini_config()
        # 加载配置
        self.load_config()

        # 将eco_pccp模块中的打印执行结果内容重定向为text_log，把信息打印到ui显示
        eco_pccp.Measure.print_detail = self.text_log  # 打印执行信息

    def try_reset_pcan_device(self) -> None:
        """
        尝试复位pcan设备

        """
        try:
            obj_pcan = pcanbasic.PCANBasic()
            channel = pcanbasic.PCAN_USBBUS1
            if self.extra_model.device_channel == '0x1':
                channel = pcanbasic.PCAN_USBBUS1
            elif self.extra_model.device_channel == '0x2':
                channel = pcanbasic.PCAN_USBBUS2
            status = obj_pcan.Uninitialize(Channel=channel)
            if status == pcanbasic.PCAN_ERROR_OK:
                self.text_log('pcan设备复位成功')
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

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
            if not os.path.isfile(self.__cfg_measure_path):
                conf = configparser.ConfigParser()
                section = 'user'
                conf.add_section(section)
                conf.set(section, 'opened_pgm_filepath', '')
                conf.set(section, 'opened_a2l_filepath', '')
                conf.set(section, 'refresh_monitor_time_ms', '100')
                with open(self.__cfg_measure_path, 'w', encoding='utf-8') as f:
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
            conf.read(filenames=self.__cfg_measure_path, encoding='utf-8')
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
            conf.read(self.__cfg_measure_path, encoding='utf-8')
            sections = conf.sections()
            for section in sections:
                for option in conf.options(section):
                    if hasattr(self.model, option):
                        conf.set(section, option, str(getattr(self.model, option)))
            with open(self.__cfg_measure_path, 'w', encoding='utf-8') as f:
                conf.write(f)

            # 保存监视表格数据
            with open(self.model.monitor_data_path, 'wb') as f:
                monitor_data = {'table_monitor_items': self.model.table_monitor_items,
                                'his_epk': self.model.a2l_epk}
                pickle.dump(monitor_data, f)
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def deal_file(self) -> None:
        """
        从数据模型中获取PGM和A2L文件路径，解析文件，显示文件信息，并将所需数据存储到视图的数据模型中

        """
        try:
            msg_his = ''
            msg_pgm = ''
            msg_a2l = ''

            # 打开监视表格历史数据
            if os.path.isfile(self.model.monitor_data_path):
                with open(self.model.monitor_data_path, 'rb') as f:
                    monitor_data = pickle.load(f)
                    self.model.table_monitor_items = monitor_data['table_monitor_items']
                    self.model.his_epk = monitor_data['his_epk']
                    msg_his = (f"his信息 -> 历史测量对象监视数据, his_epk -> {self.model.his_epk}, "
                               f"文件路径 -> {self.model.monitor_data_path}")

            if self.model.opened_a2l_filepath:
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
                self.model.a2l_epk_addr = hex(module.mod_par.addr_epks[0])
                self.model.a2l_epk = module.mod_par.epk

                # 获取a2l测量对象，保存到视图数据模型中
                # 筛选指定数据项，filter返回的是浅拷贝的迭代器，每次迭代的元素内容指向module.measurements列表中的元素内容
                measurements = filter(lambda item: item.data_type != "FLOAT64_IEEE",
                                        module.measurements)
                measurements = copy.deepcopy(list(measurements))
                measurements.sort(key=lambda item: item.name)
                self.model.a2l_measurements = measurements

                # 获取a2l转换方法，保存到视图数据模型中
                compu_methods = copy.deepcopy(module.compu_methods)
                compu_methods.sort(key=lambda item: item.name)
                self.model.a2l_conversions = compu_methods

                # 获取a2l转换映射表
                compu_vtabs = copy.deepcopy(module.compu_vtabs)
                compu_vtabs.sort(key=lambda item: item.name)
                self.model.a2l_compu_vtabs = compu_vtabs

                # 初始化选择表格数据项内容，保存到视图数据模型
                self.model.table_measurement_raw_items.clear()
                for index in range(len(self.model.a2l_measurements)):
                    table_item = TableItem(is_selected='',
                                           name=self.model.a2l_measurements[index].name,
                                           is_selected_20ms='□',
                                           is_selected_100ms='□')
                    self.model.table_measurement_raw_items.append(table_item)
                self.model.table_measurement_filter_items = self.model.table_measurement_raw_items

                # 若his_epk存在且和当前a2l_epk一致，则使用历史测量对象监视数据
                if self.model.a2l_epk and self.model.a2l_epk == self.model.his_epk:
                    pass
                else:
                    self.model.table_monitor_items.clear()

                # 刷新
                # self.__flush_table_selection()
                # self.__flush_label_selection_number()
                self.__flush_table_monitor()
                self.__flush_label_monitor_number()
                self.handler_on_cancel_selected_measurements()
                msg_a2l = (f"a2l信息 -> {project_name}, V{version}, a2l_epk -> {self.model.a2l_epk}, "
                           f"文件路径 -> {self.model.opened_a2l_filepath}")
            # 打开程序文件
            if self.model.opened_pgm_filepath:
                obj_srecord = Srecord(self.model.opened_pgm_filepath)
                epk_data = obj_srecord.get_epk(self.model.a2l_epk_addr)  # 获取程序文件epk信息
                if epk_data:
                    self.model.pgm_epk = bytes.fromhex(epk_data).decode(encoding='utf-8').rstrip('\x00')
                msg_pgm = (f"pgm信息 -> {obj_srecord.describe_info}, pgm_epk -> {self.model.pgm_epk}, "
                           f"文件路径 -> {self.model.opened_pgm_filepath}")

            # 显示文件信息
            if msg_his:
                self.text_log(msg_his)
            if msg_pgm:
                self.text_log(msg_pgm)
            if msg_a2l:
                self.text_log(msg_a2l)
            if self.model.pgm_epk == self.model.a2l_epk:
                self.text_log('pgm、a2l双方epk匹配成功！', 'done')
            else:
                self.text_log('pgm、a2l双方epk匹配失败！', 'error')
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

    def handler_on_search_measurement_item(self) -> None:
        """
        输入搜索框时触发的回调函数，筛选包含指定字符的数据项显示

        """
        try:
            # 筛选数据项，filter返回的是浅拷贝的迭代器，每次迭代的元素内容指向对应原始数据项的内容
            self.model.table_measurement_filter_items = (
                filter(lambda item: self.model.entry_search_table_items.get().strip() in item.name,
                       self.model.table_measurement_raw_items))
            # 刷新
            self.__flush_table_selection()
            self.__flush_label_selection_number()
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_select_measurement_item(self, event: Event) -> None:
        """
        鼠标点击选择数据项的回调函数，根据鼠标点选时所在的列，设置通道选择标识

        :param event: 事件
        :type event: Event
        """

        def _get_idx_from_id(item_id: str) -> tuple[int, TableItem]:
            """
            根据表格item_id获取此数据项对应的测量数据项选择列表中的索引

            :param item_id: 表格数据项id
            :type item_id: str
            :return: (index,当前数据项TableItem对象)
            :rtype: tuple[int, TableItem]
            """
            # 获取最新选中数据项的值
            item_values = self.view.table_measurement.item(item_id, "values")
            # 获取更改的数据项
            table_item = TableItem(*item_values)
            # 查找更改数据项在原始数据项列表中的索引
            idx = [item.name for item in self.model.table_measurement_raw_items].index(table_item.name)
            return idx, table_item

        try:
            # 获取选中数据项时鼠标指针所在的列索引
            x = self.view.table_measurement.winfo_pointerx() - self.view.table_measurement.winfo_rootx()
            selected_column_index = self.view.table_measurement.identify_column(x=x)  # 结果为字符串，例如'#1'
            if not selected_column_index:
                return
            selected_column_index = int(selected_column_index[1:]) - 1
            # 获取数据表列名组成的元组
            column_names = tuple(self.view.table_measurement["columns"])
            # 获取选中数据项的id
            # selected_item_id = event.widget.selection()[0]
            selected_item_id = self.view.table_measurement.focus()
            # 无选中元素，则返回
            if not selected_item_id:
                return
            # 显示选中数据项的属性
            idx, _ = _get_idx_from_id(selected_item_id)
            self.__show_property(self.model.a2l_measurements[idx], self.view.table_property)

            # 若鼠标点击数据项时的位置非通道选择框所处的列，则直接返回
            if not (column_names[selected_column_index] == "20ms" or column_names[selected_column_index] == "100ms"):
                return

            # 获取选中数据项的值
            item_values = self.view.table_measurement.item(selected_item_id, "values")
            # 设置速率通道选中标识
            if column_names[selected_column_index] == "20ms":
                self.view.table_measurement.set(selected_item_id, column_names.index('100ms'), '□')
                set_value = item_values[column_names.index('20ms')] == '□' and '√' or '□'
                self.view.table_measurement.set(selected_item_id, selected_column_index, set_value)
            if column_names[selected_column_index] == "100ms":
                self.view.table_measurement.set(selected_item_id, column_names.index('20ms'), '□')
                set_value = item_values[column_names.index('100ms')] == '□' and '√' or '□'
                self.view.table_measurement.set(selected_item_id, selected_column_index, set_value)
            # 获取最新选中数据项的值
            item_values = self.view.table_measurement.item(selected_item_id, "values")
            set_value = (item_values[column_names.index('20ms')] == '√' or
                         item_values[column_names.index('100ms')] == '√') and '☆' or ''
            self.view.table_measurement.set(selected_item_id, column_names.index('is_selected'), set_value)

            # 存储原始数据项列表的内容到数据模型
            idx, table_item = _get_idx_from_id(selected_item_id)
            self.model.table_measurement_raw_items[idx] = table_item

            # 刷新
            self.__flush_label_selection_number()
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_ack_selected_measurements(self) -> None:
        """
        添加选中测量项到监视表格，并获取监视数据项属性

        """
        try:
            # 清空数据模型中监视数据项列表
            self.model.table_monitor_items.clear()
            # 筛选被选择的数据项，filter返回的是浅拷贝的迭代器，每次迭代的元素内容指向table_measurement_raw_items列表中的元素内容
            selected_items = filter(lambda item: item.is_selected,
                                    self.model.table_measurement_raw_items)
            # 添加被选择的数据项到监视表格
            for item in selected_items:
                monitor_item = MonitorItem(name=item.name,
                                           rate=item.is_selected_20ms == '√' and '20ms' or '100ms', )
                self.model.table_monitor_items.append(monitor_item)

            # 获取转换方法名称列表
            conversion_names = [conversion.name for conversion in self.model.a2l_conversions]
            # 获取转换映射表名称列表
            compu_vtab_names = [compu_vtab.name for compu_vtab in self.model.a2l_compu_vtabs]
            # 获取监视表格数据项与原始测量对象的索引映射List[Tuple(idx_in_monitor_items,idx_in_a2l_measurements)]
            idx_map_list: List[Tuple[int, int]] = []
            for idx_in_monitor_items in range(len(self.model.table_monitor_items)):
                for idx_in_a2l_measurements in range(len(self.model.a2l_measurements)):
                    if (self.model.table_monitor_items[idx_in_monitor_items].name ==
                            self.model.a2l_measurements[idx_in_a2l_measurements].name):
                        idx_map_list.append((idx_in_monitor_items, idx_in_a2l_measurements))
                    if idx_in_a2l_measurements >= len(self.model.a2l_measurements):
                        msg = f'监视列表中的数据项{self.model.table_monitor_items[idx_in_monitor_items].name}不存在于原始测量对象列表中'
                        raise ValueError(msg)

            # 根据索引映射，从原始测量对象中获取对应监视数据项的属性
            for idx_in_monitor_items, idx_in_a2l_measurements in idx_map_list:
                # 获取原始测量对象
                obj_msr = self.model.a2l_measurements[idx_in_a2l_measurements]
                # 索引属性
                self.model.table_monitor_items[idx_in_monitor_items].idx_in_monitor_items = idx_in_monitor_items
                self.model.table_monitor_items[
                    idx_in_monitor_items].idx_in_a2l_measurements = idx_in_a2l_measurements
                # 数据类型属性
                self.model.table_monitor_items[idx_in_monitor_items].data_type = obj_msr.data_type
                print(f"数据类型：{obj_msr.data_type}")
                # 转换方法属性
                self.model.table_monitor_items[idx_in_monitor_items].conversion = obj_msr.conversion
                print(f"转换方法：{obj_msr.conversion}")
                print(self.model.a2l_conversions[conversion_names.index(obj_msr.conversion)])
                # 转换类型属性
                self.model.table_monitor_items[idx_in_monitor_items].conversion_type = (
                    self.model.a2l_conversions[conversion_names.index(obj_msr.conversion)].conversion_type)
                print(f"转换类型：{self.model.table_monitor_items[idx_in_monitor_items].conversion_type}")
                # 转换映射名称属性
                self.model.table_monitor_items[idx_in_monitor_items].compu_tab_ref = (
                    self.model.a2l_conversions[conversion_names.index(obj_msr.conversion)].compu_tab_ref)
                print(
                    f"转换映射名称：{self.model.table_monitor_items[idx_in_monitor_items].compu_tab_ref}")
                # 转换映射表属性
                # 对于数值类型没有转换映射表，所以先确定转换映射名称存在，再获取转换映射表
                if self.model.table_monitor_items[idx_in_monitor_items].compu_tab_ref in compu_vtab_names:
                    self.model.table_monitor_items[idx_in_monitor_items].compu_vtab = (
                        self.model.a2l_compu_vtabs[
                            compu_vtab_names.index(
                                self.model.table_monitor_items[idx_in_monitor_items].compu_tab_ref)].read_dict)
                print(
                    f"转换映射表：{self.model.table_monitor_items[idx_in_monitor_items].compu_vtab}")

                # 单位属性
                self.model.table_monitor_items[idx_in_monitor_items].unit = (
                    self.model.a2l_conversions[conversion_names.index(obj_msr.conversion)].unit)
                # 转换系数
                self.model.table_monitor_items[idx_in_monitor_items].coeffs = (
                    self.model.a2l_conversions[conversion_names.index(obj_msr.conversion)].coeffs)
                # 显示格式
                fm = self.model.a2l_conversions[conversion_names.index(obj_msr.conversion)].format
                if '%' in fm:
                    fm = tuple(fm[1:].split('.'))
                    fm0 = int(fm[0])
                    fm1 = int(fm[1])
                    self.model.table_monitor_items[idx_in_monitor_items].format = (fm0, fm1)

                # odt元素大小属性
                self.model.table_monitor_items[idx_in_monitor_items].element_size = self.model.ASAP2_TYPE_SIZE[
                    obj_msr.data_type]
                # odt元素地址属性
                self.model.table_monitor_items[idx_in_monitor_items].element_addr = hex(obj_msr.ecu_address)

                # daq列表序号属性，1:20ms,2:100ms
                if self.model.table_monitor_items[idx_in_monitor_items].rate == '20ms':
                    self.model.table_monitor_items[idx_in_monitor_items].daq_number = 1
                elif self.model.table_monitor_items[idx_in_monitor_items].rate == '100ms':
                    self.model.table_monitor_items[idx_in_monitor_items].daq_number = 2

            # 刷新
            self.__flush_table_monitor()
            self.__flush_label_monitor_number()

        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_cancel_selected_measurements(self) -> None:
        """
        取消选中测量项

        """
        try:
            # 清除所有原始数据项的选中状态
            for item in self.model.table_measurement_raw_items:
                item.is_selected = ''
                item.is_selected_20ms = '□'
                item.is_selected_100ms = '□'
            # 获取所有原始数据项的名字
            raw_item_names = [item.name for item in self.model.table_measurement_raw_items]
            # 将监视表格数据项状态写入到原始数据项的状态
            for monitor_item in self.model.table_monitor_items:
                table_item = TableItem(is_selected='☆',
                                       name=monitor_item.name,
                                       is_selected_20ms=monitor_item.rate == '20ms' and '√' or '□',
                                       is_selected_100ms=monitor_item.rate == '100ms' and '√' or '□', )
                # 获取监视数据项名字在原始数据项列表中索引
                idx = raw_item_names.index(monitor_item.name)
                # 更新原始数据项内容
                self.model.table_measurement_raw_items[idx] = table_item

            # 刷新
            self.handler_on_search_measurement_item()
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_delete_minitor_item(self) -> None:
        """
        删除监视项

        """
        # 若已启动测量，则不允许删除
        if hasattr(self.model.obj_measure, 'has_measured') and self.model.obj_measure.has_measured:
            return

        # 获取选中数据项的id元祖
        selected_item_iids = self.view.table_monitor.selection()
        # 获取数据表列名组成的元组
        column_names = tuple(self.view.table_monitor["columns"])

        # 从监视数据项列表中删除选择的数据项
        if selected_item_iids:
            for iid in selected_item_iids:
                name = self.view.table_monitor.item(iid, "values")[column_names.index("Name")]
                monitor_items_names = [item.name for item in self.model.table_monitor_items]
                self.model.table_monitor_items.pop(monitor_items_names.index(name))
        # 刷新
        self.handler_on_cancel_selected_measurements()
        self.handler_on_ack_selected_measurements()

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
                    self.view.btn_connect.config(state='disabled')
                    self.view.btn_disconnect.config(state='normal')
                    self.view.btn_start_measure.config(state='normal')
                    self.view.btn_stop_measure.config(state='disabled')
                    self.view.btn_open.config(state='disabled')
                if future.result():
                    epk = future.result()
                    if epk == self.model.a2l_epk and \
                            epk == self.model.pgm_epk:
                        self.text_log(f'pgm、a2l、ecu三方epk匹配成功！', 'done')
                    else:
                        self.text_log(f'pgm、a2l、ecu三方epk匹配失败！', 'done')
            except Exception as e:
                self.text_log(f'发生异常 {e}', 'error')
                self.text_log(f"{traceback.format_exc()}", 'error')

        try:
            self.text_log(f'======建立连接======', 'done')
            # 创建测量对象
            self.__create_measure_obj()
            # 建立连接
            self.__pool.submit(self.model.obj_measure.connect, self.model.a2l_epk_addr, len(self.model.a2l_epk)).add_done_callback(_callback)
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
                    self.view.btn_connect.config(state='normal')
                    self.view.btn_disconnect.config(state='disabled')
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
                    self.view.btn_connect.config(state='disabled')
                    self.view.btn_disconnect.config(state='disabled')
                    self.view.btn_start_measure.config(state='disabled')
                    self.view.btn_stop_measure.config(state='normal')
                    self.view.btn_ack.config(state='disabled')
                    self.view.btn_cancel.config(state='disabled')

                    # 清空can接收消息缓冲区
                    self.model.obj_measure.clear_recv_queue()
                    # 启动测量后，开始接收daq_dto数据，并刷新显示数据
                    self.__pool_recv.submit(self.__recv_daq_dto).add_done_callback(_done)
                    self.__after_id = self.view.after(ms=int(self.model.refresh_monitor_time_ms),
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
            # 若监视数据项为空，则返回
            if not self.model.table_monitor_items:
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
                    self.view.btn_connect.config(state='disabled')
                    self.view.btn_disconnect.config(state='normal')
                    self.view.btn_start_measure.config(state='normal')
                    self.view.btn_stop_measure.config(state='disabled')
                    self.view.btn_ack.config(state='normal')
                    self.view.btn_cancel.config(state='normal')
            except Exception as e:
                self.text_log(f'发生异常 {e}', 'error')
                self.text_log(f"{traceback.format_exc()}", 'error')

        try:
            self.text_log(f'======停止测量======', 'done')
            self.__pool.submit(self.model.obj_measure.stop_measure).add_done_callback(_callback)
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def __create_measure_obj(self) -> None:
        """
        创建测量对象

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
                                                      obj_srecord=Srecord(
                                                          self.model.opened_pgm_filepath)
                                                      )
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

    def __flush_table_selection(self) -> None:
        """
        从数据模型中刷新显示选择数据表

        """
        # 清空所有数据项
        self.view.table_measurement.delete(*self.view.table_measurement.get_children())
        # 刷新选择表格数据项
        for table_item in self.model.table_measurement_filter_items:
            values = (table_item.is_selected,
                      table_item.name,
                      table_item.is_selected_20ms,
                      table_item.is_selected_100ms)
            self.view.table_measurement.insert(parent="",
                                               index="end",
                                               text="",
                                               values=values)

    def __flush_table_monitor(self) -> None:
        """
        从数据模型中刷新显示监视数据表

        """
        # 清空所有数据项
        self.view.table_monitor.delete(*self.view.table_monitor.get_children())
        # 刷新显示数据表
        for table_item in self.model.table_monitor_items:
            values = (table_item.name,
                      table_item.value,
                      table_item.rate,
                      table_item.unit)
            self.view.table_monitor.insert(parent="",
                                           index="end",
                                           text="",
                                           values=values)

    def __flush_label_selection_number(self):
        """
        刷新显示已选数据项数目和当前筛选出的数据项数目

        """
        selected_num = len([item for item in self.model.table_measurement_raw_items if item.is_selected])
        filter_num = len(self.view.table_measurement.get_children())  # 不能根据数据模型中filter_items计算，因为其为迭代器，可能已被遍历过
        text = str(selected_num) + '/' + str(filter_num)
        self.view.label_selection_number.config(text=text)

    def __flush_label_monitor_number(self) -> None:
        """
        刷新显示监视数据项数目

        """
        monitor_num = len([item for item in self.model.table_monitor_items])
        self.view.label_monitor_number.config(text=monitor_num)

    @staticmethod
    def __show_property(from_obj: Measurement, to_table: TkTreeView) -> None:
        """
        显示对象的属性到表格控件

        :param from_obj: 待显示属性的对象
        :type from_obj: Measurement
        :param to_table: 显示属性内容的表格控件
        :type to_table: TkTreeView
        """

        def _get_attributes(obj: Measurement) -> list[str]:
            """
            获取对象的所有属性，过滤掉以'__'开头和结尾的特殊属性，并且排除方法

            :param obj: 对象
            :type obj: Measurement
            :return: 属性列表
            :rtype: list[str]
            """
            return [attr for attr in dir(obj) if not attr.startswith("__") and not callable(getattr(obj, attr))]

        # 清空所有数据项
        to_table.delete(*to_table.get_children())
        # 获取属性
        if from_obj:
            attributes = _get_attributes(from_obj)
            for attribute in attributes:
                to_table.insert(parent="",
                                index="end",
                                text="",
                                values=(attribute, getattr(from_obj, attribute)),
                                )

    def __get_daqs(self, daqs_cfg: dict[int, dict[str, int]]) -> dict[int, dict[int, list[MonitorItem]]]:
        """
        将监视数据项按daq分配到各odt，得到daq分配列表

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
        :rtype: dict[int, dict[int, list[MonitorItem]]]
        :raises Exception: 数据项的转换系数不被支持；分配daq超过odt列表允许的最大范围；
        """

        def _write_odts(group_of_daq: list[MonitorItem]) -> dict[int, list[MonitorItem]]:
            """
            将指定daq的监视数据项分配到各odt中

            :param group_of_daq: 指定daq的监视数据项列表
            :type group_of_daq: list[MonitorItem]
            :return: odts，指定daq的odt列表，例如{0: [item0, item1], 1: [item2, item3, item4]}，
                键0是本daq的odt列表序号为0的odt，值[item0, item1]为该odt中包含的监视数据项列表
            :rtype: dict[int, list[MonitorItem]]
            :raises ValueError: 数据项的元素大小属性值不是1,2,4中的一个
            """

            def _get_free_memory_of_odt(odt: list[MonitorItem]) -> int:
                """
                获取odt空闲容量

                :param odt: 元素为MonitorItem对象的列表，元素大小总和不超过7字节
                :type odt: list[MonitorItem]
                :return: 空闲容量，单位字节
                :rtype: int
                """
                res = 0
                for element in odt:
                    res += element.element_size
                return 7 - res

            # 声明变量
            odts: dict[int, list[MonitorItem]] = {}  # odt列表
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

        # 根据速率对监视数据项分组
        group_by_daq: dict[int, list[MonitorItem]] = {}  # 根据daq对监视数据项分组的结果
        for key, group in groupby(sorted(self.model.table_monitor_items, key=lambda x: x.daq_number),
                                  key=lambda x: x.daq_number):
            group_by_daq[key] = list(group)

        # 写入daq列表
        daqs: dict[int, dict[int, list[MonitorItem]]] = {}  # daq列表
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

        # 获取监视数据项的属性，打印odt列表
        self.text_log('分配完成')
        for daq_number, odts in daqs.items():
            for odt_number, odt in odts.items():
                for element_number in range(len(odt)):
                    item = odt[element_number]  # 获取监视数据项
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

        def _get_physical_value(item: MonitorItem, element_data: list[int]) -> str:
            """
            根据元素的字节序列，求其物理值;
            raw_value = f(physical_value);
            f(x) = (A*x^2 + B*x + C) / (D*x^2 + E*x + F);

            :param item: 监视数据项
            :type item: MonitorItem
            :param element_data: 字节序列
            :type element_data: list[int]
            :return: 物理值
            :rtype: str
            """

            # def _solve_data(item: MonitorItem, element_data: List[int], signed: bool):
            #     """
            #     根据元素的字节序列，求BYTE、WORD、LONG基类型的物理值
            #     :param item: 监视数据项
            #     :param element_data: 字节序列
            #     :param signed: 数据的符号,True:有符号；False:无符号
            #     :return: 物理值(str)
            #     """
            #
            #     # 转换系数
            #     A, B, C, D, E, F = item.coeffs
            #     # 转换函数
            #     x = Symbol('x')
            #     fx = (A * x * x + B * x + C) / (D * x * x + E * x + F)
            #
            #     raw_value = int.from_bytes(bytes(element_data), 'big', signed=signed)  # 原始值
            #     if 'fix' in item.conversion:
            #         eq = Eq(fx, raw_value)  # 创建等式
            #         res_value = solve(eq, x)[0]  # 求解等式得到物理值
            #     else:
            #         res_value = raw_value
            #     return res_value

            # 根据不同类型和转换方法求解物理值

            value = '-333333333.3'
            raw_value = None
            if item.data_type == 'UBYTE':
                raw_value = int.from_bytes(bytes(element_data), 'big', signed=False)  # 原始值
            elif item.data_type == 'SBYTE':
                raw_value = int.from_bytes(bytes(element_data), 'big', signed=True)  # 原始值
            elif item.data_type == 'UWORD':
                raw_value = int.from_bytes(bytes(element_data), 'big', signed=False)  # 原始值
            elif item.data_type == 'SWORD':
                raw_value = int.from_bytes(bytes(element_data), 'big', signed=True)  # 原始值
            elif item.data_type == 'ULONG':
                raw_value = int.from_bytes(bytes(element_data), 'big', signed=False)  # 原始值
            elif item.data_type == 'SLONG':
                raw_value = int.from_bytes(bytes(element_data), 'big', signed=True)  # 原始值
            elif item.data_type == 'FLOAT32_IEEE':
                # 确保bytes的长度与浮点数的字节数对应。
                # 对于32位浮点数，使用'f'；
                # 对于64位浮点数，使用'd'。
                # 如果bytes表示的是大端序，可以使用'!'作为格式字符串的前缀来指定字节顺序。
                value = unpack('!f', bytes(element_data))[0]

            # 若是转换类型为映射表
            if (raw_value is not None) and (item.conversion_type == "TAB_VERB"):
                value = raw_value
                return ''.join([item.compu_vtab[value], ':', pad_hex(hex(value), self.model.ASAP2_TYPE_SIZE[item.data_type])])

            # 若是转换类型为普通数值
            if (raw_value is not None) and (item.conversion_type == "RAT_FUNC"):
                value = (raw_value - item.coeffs[2]) / item.coeffs[1]
            # 格式化
            fm = item.format
            if fm:
                value = f"{value: <{fm[0]}.{fm[1]}f}"
            # 返回
            return value

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

        # 待显示的值{在监视数据项列表中的索引:int，物理值:str}
        display_values: dict[int, str] = {}
        # 创建后台执行的 schedulers
        scheduler_recv = BackgroundScheduler()
        # 添加调度任务
        scheduler_recv.add_job(func=_put_to_queue,
                               trigger='interval',
                               seconds=int(self.model.refresh_monitor_time_ms) / 1000,
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
        AVAILABLE_PIDS_BY_DAQ: Dict[int, Set[int]] = {}
        for daq_number in _DAQS_CFG.keys():
            first_pid = _DAQS_CFG[daq_number]['first_pid']
            last_pid = first_pid + _DAQS_CFG[daq_number]['odts_size'] - 1
            AVAILABLE_PIDS_BY_DAQ[daq_number] = set([x for x in range(first_pid, last_pid + 1)])

        # 清空队列
        while not _q.empty():
            _q.get()

        while True:
            # 若停止监视，将线程池的最大线程由3变为1，并退出，后续提交的任务将是排队等待有序执行
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
                physical_value = _get_physical_value(item=item,
                                                     element_data=element_data)
                display_values[item.idx_in_monitor_items] = physical_value

    def __display_monitor_value(self) -> None:
        """
        显示value值到监视表格
        """

        def _disp(iid, value):
            """
            显示value值到监视表格数据项
            """
            _table_monitor.set(iid, _column_names.index('Value'), value)

        # 建立局部变量，加快访问速度
        _q = self.model.q  # 显示值队列
        _obj_measure = self.model.obj_measure  # 是否已测量
        _table_monitor = self.view.table_monitor  # 监视表格
        # 获取监视表格中所有的item_id列表
        _table_monitor_iids = _table_monitor.get_children()
        # 获取监视表格列名组成的元组
        _column_names = tuple(_table_monitor["columns"])

        if not _obj_measure.has_measured:  # 点击停止按钮后若成功停止，则在停止任务中会复位此标识
            self.view.after_cancel(self.__after_id)
            return
        try:
            display_values = _q.get_nowait()
            for idx, value in display_values.items():
                item_id = _table_monitor_iids[idx]
                _disp(item_id, value)
        except:
            pass
        self.__after_id = self.view.after(ms=int(self.model.refresh_monitor_time_ms),
                                          func=self.__display_monitor_value)
