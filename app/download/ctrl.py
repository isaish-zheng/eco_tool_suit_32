#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : ZYD
# @Time    : 2024/7/11 上午10:02
# @version : V1.0.0
# @function:

"""
下载程序界面(mvc)的controller模块

"""

##############################
# Module imports
##############################

import configparser  # 用于读写配置文件
import os
import traceback  # 用于获取异常详细信息
import threading
import time
from tkinter import END, filedialog

from eco import eco_puds
from eco import eco_pccp
from eco.pcandrive import pcanbasic
from srecord import Srecord

from .model import DownloadModel
from .view import DownloadView
from ..measure.ctrl import MeasureModel, MeasureView, MeasureCtrl


##############################
# Controller API function declarations
##############################

class DownloadCtrl(object):
    """
    负责处理下载程序界面事件

    :param model: 界面的数据模型
    :type model: DownloadModel
    :param view: 界面的视图
    :type view: DownloadView
    :param cfg_path: 下载程序、监视测量对象的配置文件路径
    :type cfg_path: tuple[str, str]
    """

    def __init__(self,
                 model: DownloadModel,
                 view: DownloadView,
                 cfg_path: tuple[str, str]) -> None:
        """
        构造函数

        """
        self.model = model
        self.view = view
        self.view.set_presenter(self)

        self.__cfg_path = cfg_path
        self.__cfg_download_path = cfg_path[0]
        # self.__cfg_a2l_path = cfg_path[1]

        # 初始化配置
        self.ini_config()
        # 加载配置
        self.load_config()
        # 根据菜单设置执行一次是否显示指定内容，否则只有当在界面点击时才会更新是否显示
        self.handler_on_show_uds_map_detail()
        self.handler_on_show_uds_msg_detail()
        # 将eco_puds模块中的打印执行结果内容重定向为text_log，把信息打印到ui显示
        eco_puds.print_exec_detail = self.text_log  # 打印服务的执行信息
        eco_puds.DownloadThread.print_detail = self.text_log  # 打印下载任务的执行信息
        # 将eco_pccp模块中的打印执行结果内容重定向为text_log，把信息打印到ui显示
        eco_pccp.print_exec_detail = self.text_log  # 打印服务的执行信息
        eco_pccp.DownloadThread.print_detail = self.text_log  # 打印下载任务的执行信息

    def try_reset_pcan_device(self) -> None:
        """
        尝试复位pcan设备

        """
        try:
            obj_pcan = pcanbasic.PCANBasic()
            channel = pcanbasic.PCAN_USBBUS1
            if self.model.device_channel == '0x1':
                channel = pcanbasic.PCAN_USBBUS1
            elif self.model.device_channel == '0x2':
                channel = pcanbasic.PCAN_USBBUS2
            status = obj_pcan.Uninitialize(Channel=channel)
            if status == pcanbasic.PCAN_ERROR_OK:
                self.text_log('pcan设备复位成功')
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def text_log(self, txt: str, *args, **kwargs) -> None:
        """
        向文本显示框写入信息

        :param txt: 待写入的信息
        :type txt: str
        :param args: 位置参数，第一个参数为文字颜色
                    None-灰色,'done'-绿色,'warning'-黄色,'error'-红色
        :param kwargs: 关键字参数（未使用）
        """

        def get_str_time() -> str:
            """
            获取当前时间，格式化字符串"%Y/%m/%d %H:%M:%S"

            :return: 当前时间
            :rtype: str
            """
            time_now = time.strftime("%Y/%m/%d %H:%M:%S", time.localtime())  # 时间戳
            return str(time_now)

        # color = COLOR_LABEL_FG
        color = '#787878'
        if args:
            if args[0] == 'done':
                color = 'green'
            elif args[0] == 'warning':
                color = '#cc5d20'
            elif args[0] == 'error':
                color = 'red'
        self.view.text_info.config(state='normal')
        self.view.text_info.insert(END, get_str_time() + ' ' + txt + '\n', color)
        self.view.text_info.config(state='disabled')
        self.view.text_info.see(END)
        self.view.text_info.tag_config(tagName=color, foreground=color)

    def ini_config(self) -> None:
        """
        初始化配置文件，若配置文件不存在，则新建配置

        """
        try:
            if not os.path.isfile(self.__cfg_download_path):
                conf = configparser.ConfigParser()
                conf.add_section('mode')
                conf.set('mode', 'mode_protocol', 'uds')  # 默认uds
                conf.add_section('device')
                conf.set('device', 'device_type', 'PeakCAN')
                conf.set('device', 'device_channel', '0x1')
                # uds
                protocol = 'uds'
                conf.add_section(protocol)
                conf.set(protocol, 'uds_baudrate', '250kbps')
                conf.set(protocol, 'uds_request_id', '0x791')
                conf.set(protocol, 'uds_response_id', '0x799')
                conf.set(protocol, 'uds_function_id', '0x7DF')
                conf.set(protocol, 'uds_opened_pgm_filepath', '')
                conf.set(protocol, 'uds_opened_seed2key_filepath', '')
                conf.set(protocol, 'uds_is_show_map_detail', 'False')
                conf.set(protocol, 'uds_is_show_msg_detail', 'False')
                # ccp
                protocol = 'ccp'
                conf.add_section(protocol)
                conf.set(protocol, 'ccp_baudrate', '500kbps')
                conf.set(protocol, 'ccp_request_id', '0x100')
                conf.set(protocol, 'ccp_response_id', '0x101')
                conf.set(protocol, 'ccp_ecu_addr', '0x0235')
                conf.set(protocol, 'ccp_opened_pgm_filepath', '')
                conf.set(protocol, 'ccp_opened_seed2key_filepath', '')
                conf.set(protocol, 'ccp_is_show_map_detail', 'False')
                conf.set(protocol, 'ccp_is_show_msg_detail', 'False')
                conf.set(protocol, 'ccp_is_intel_format', 'True')
                conf.set(protocol, 'ccp_response_timeout_ms', '10000')
                with open(self.__cfg_download_path, 'w', encoding='utf-8') as f:
                    conf.write(f)
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def load_config(self) -> None:
        """
        加载配置文件中的配置保存到界面的model中

        """
        try:
            conf = configparser.ConfigParser()
            # 读取配置文件中的各项配置,通过ui显示
            conf.read(filenames=self.__cfg_download_path, encoding='utf-8')
            sections = conf.sections()

            self.model.device_type = conf.get('device', 'device_type')
            self.model.device_channel = conf.get('device', 'device_channel')
            protocol = conf.get('mode', 'mode_protocol')
            if protocol in self.model.PROTOCAOL:
                self.model.mode_protocol = protocol
                # 根据不同的mode，加载指定参数
                if protocol == self.model.PROTOCAOL[0]:
                    # 当前为uds
                    sections.remove(self.model.PROTOCAOL[1])
                elif self.model.mode_protocol == self.model.PROTOCAOL[1]:
                    # 当前为ccp
                    sections.remove(self.model.PROTOCAOL[0])
                for section in sections:
                    for option in conf.options(section):
                        if hasattr(self.model, option):
                            setattr(self.model, option, conf.get(section, option))
            else:
                msg = f'当前协议为{protocol}，必须为{self.model.PROTOCAOL}'
                raise ValueError(msg)
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def save_config(self, is_old: bool = False) -> None:
        """
        保存需要的配置项到配置文件

        :param is_old: 是否保存上一配置，eg：若True，则当前为CCP时，执行保存UDS配置
        :type is_old: bool
        """
        try:
            conf = configparser.ConfigParser()
            conf.read(self.__cfg_download_path, encoding='utf-8')
            sections = conf.sections()
            if self.model.mode_protocol == self.model.PROTOCAOL[0]:
                # 当前为uds
                sections.remove(self.model.PROTOCAOL[0]) if is_old else sections.remove(self.model.PROTOCAOL[1])
            elif self.model.mode_protocol == self.model.PROTOCAOL[1]:
                # 当前为ccp
                sections.remove(self.model.PROTOCAOL[1]) if is_old else sections.remove(self.model.PROTOCAOL[0])
            for section in sections:
                for option in conf.options(section):
                    if hasattr(self.model, option):
                        conf.set(section, option, str(getattr(self.model, option)))
            with open(self.__cfg_download_path, 'w', encoding='utf-8') as f:
                conf.write(f)
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_closing(self) -> None:
        """
        关闭界面窗口前执行，若有任务未结束，则不执行关闭窗口

        """
        try:
            # print("当前线程数量为", threading.active_count())
            # print("所有线程的具体信息", threading.enumerate())
            # print("当前线程具体信息", threading.current_thread())
            # 检查当前线程中是否有download任务，若有则不关闭程序
            current_threads = threading.enumerate()
            for t in current_threads:
                if 'task_download' in t.name:
                    self.view.show_warning(f'{t.name}任务执行中. . .\n请在任务结束后关闭 !')
                    return
                if 'task_measure' in t.name:
                    self.view.show_warning(f'请先关闭测量窗口 !')
                    return
            self.save_config(False)
            self.view.quit()
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_show_uds_map_detail(self) -> None:
        """
        点击窗口中文件菜单下的‘uds->显示id映射详情’时执行，开启时，在文本显示框将显示uds刷写过程中的id映射详情，关闭时，将不显示

        """
        try:
            # 若为uds刷写则允许操作,否则保持为配置文件中参数
            if self.model.mode_protocol == self.model.PROTOCAOL[0]:
                if self.model.uds_is_show_map_detail:
                    eco_puds.print_map_detail = self.text_log
                else:
                    eco_puds.print_map_detail = self.__text_none
            else:
                conf = configparser.ConfigParser()
                conf.read(filenames=self.__cfg_download_path, encoding='utf-8')
                self.model.uds_is_show_map_detail = conf.get('uds', 'uds_is_show_map_detail')
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_show_uds_msg_detail(self) -> None:
        """
        点击窗口中文件文件菜单下的‘uds->显示消息详情’时执行，开启时，在文本显示框将显示uds刷写过程中的消息详情，关闭时，将不显示

        """
        try:
            # 若为uds刷写则允许操作,否则保持为配置文件中参数
            if self.model.mode_protocol == self.model.PROTOCAOL[0]:
                if self.model.uds_is_show_msg_detail:
                    eco_puds.print_msg_detail = self.text_log
                else:
                    eco_puds.print_msg_detail = self.__text_none
            else:
                conf = configparser.ConfigParser()
                conf.read(filenames=self.__cfg_download_path, encoding='utf-8')
                self.model.uds_is_show_msg_detail = conf.get('uds', 'uds_is_show_msg_detail')
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_select_mode_protocol(self) -> None:
        """
        改变窗口中刷写协议下拉控件中内容时执行，会切换刷写协议并将改变前的配置保存到配置文件中

        """
        self.save_config(True)
        self.load_config()

    def handler_on_open_download_file(self) -> None:
        """
        点击窗口中打开按钮时执行，选择程序文件后会在文本显示框显示程序的信息

        """
        try:
            # 打开下载文件路径
            self.__open_file(filetype='下载',
                             dir=os.path.dirname(self.model.opened_pgm_filepath))
            # 打开程序文件
            if self.model.opened_pgm_filepath:
                obj_srecord = Srecord(self.model.opened_pgm_filepath)
                # 获取程序信息
                msg_pgm = (f"程序信息 -> {obj_srecord.describe_info}"
                           f"\n\t文件路径 -> {self.model.opened_pgm_filepath}")
                for em in obj_srecord.erase_memory_infos:
                    msg_pgm += f"\n\t数据段{em.erase_number}信息 -> 地址:{em.erase_start_address32},长度:{em.erase_length}"
                msg_pgm += f"\n\t所有数据段CRC校验结果 -> {[hex(b) for b in obj_srecord.crc32_values]}"
                self.text_log(msg_pgm)
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_open_seed2key_file(self) -> None:
        """
        点击窗口中秘钥按钮时执行，选择秘钥文件后会在文本显示框显示秘钥的信息

        """
        try:
            # 打开文件路径
            self.__open_file(filetype='秘钥',
                             dir=os.path.dirname(self.model.opened_seed2key_filepath))
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_download_thread(self) -> None:
        """
        点击窗口中下载按钮时执行，会根据当前刷写协议启动相应的下载线程

        """
        try:
            conf = configparser.ConfigParser()
            conf.read(filenames=self.__cfg_download_path, encoding='utf-8')
            if self.model.opened_pgm_filepath:
                if self.model.mode_protocol == self.model.PROTOCAOL[0]:
                    # uds
                    obj_download = eco_puds.DownloadThread(request_can_id=self.model.uds_request_id,
                                                           response_can_id=self.model.uds_response_id,
                                                           function_can_id=self.model.uds_function_id,
                                                           device_channel=self.model.device_channel,
                                                           device_baudrate=self.model.uds_baudrate,
                                                           download_filepath=self.model.opened_pgm_filepath,
                                                           seed2key_filepath=self.model.uds_opened_seed2key_filepath,
                                                           obj_srecord=Srecord(
                                                               self.model.opened_pgm_filepath)
                                                           )
                else:
                    # ccp
                    is_intel_format = conf.getboolean('ccp', 'ccp_is_intel_format')
                    timeout = conf.getint('ccp', 'ccp_response_timeout_ms')
                    obj_download = eco_pccp.DownloadThread(request_can_id=self.model.ccp_request_id,
                                                           response_can_id=self.model.ccp_response_id,
                                                           ecu_addr=self.model.ccp_ecu_addr,
                                                           is_intel_format=is_intel_format,
                                                           timeout=timeout,
                                                           device_channel=self.model.device_channel,
                                                           device_baudrate=self.model.ccp_baudrate,
                                                           download_filepath=self.model.opened_pgm_filepath,
                                                           seed2key_filepath=self.model.ccp_opened_seed2key_filepath,
                                                           obj_srecord=Srecord(
                                                               self.model.opened_pgm_filepath)
                                                           )
                obj_download.name = 'task_download'
                obj_download.start()
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def handler_on_open_measure_ui(self) -> None:
        """
        点击窗口中文件菜单下的CCP测量时执行，将打开测量界面

        """
        try:
            # 创建view
            measure_view = MeasureView(master=self.view, )
            # 创建model
            measure_model = MeasureModel()
            # 创建controller
            measure_ctrl = MeasureCtrl(model=measure_model,
                                       view=measure_view,
                                       extra_model=self.model,
                                       text_log=self.text_log,
                                       cfg_path=self.__cfg_path)

            # 显示子窗口内容
            measure_view.set_root_menu()
            measure_view.set_select_measure_frame(model=measure_model)
            measure_view.set_measure_frame(model=measure_model)
            measure_view.set_select_calibrate_frame(model=measure_model)
            # measure_view.set_calibrate_frame(model=measure_model)

            # 启动时显示上一次打开的文件信息和数据
            measure_ctrl.deal_file()
        except Exception as e:
            self.text_log(f'发生异常 {e}', 'error')
            self.text_log(f"{traceback.format_exc()}", 'error')

    def __open_file(self, filetype: str, **kwargs) -> None:
        """
        弹出文件对话框，打开指定类型的文件

        :param filetype: 文件类型
        :type filetype: str
        :param kwargs: 关键字参数，lbl为显示已打开文件路径的标签控件，dir为要打开文件的初始路径
        """
        if filetype == '下载':
            fileformat = '.mot'
        elif filetype == '秘钥':
            fileformat = '.dll'
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
        if filetype == '下载':
            self.model.opened_pgm_filepath = openpath
        elif filetype == '秘钥':
            self.model.opened_seed2key_filepath = openpath
        if openpath:
            # 输出日志
            self.text_log('已打开' + filetype + '文件' + openpath, 'done')
        else:
            # 输出日志
            self.text_log('路径无效，未选择' + filetype + '文件' + openpath, 'warning')

    @staticmethod
    def __text_none(txt: str, *args, **kwargs) -> None:
        """
        空函数，
        用于重载text_log等输出文本信息功能的重载函数，无操作

        :param txt: 待写入的信息
        :type txt: str
        :param args: 位置参数列表，第一个参数为文字颜色
            None-灰色,'done'-绿色,'warning'-黄色,'error'-红色
        :param kwargs: 关键字参数列表，未用
        """
        pass
