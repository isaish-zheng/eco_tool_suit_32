#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : ZYD
# @Time    : 2024/7/11 上午10:02
# @version : V1.0.0
# @function:

##############################
# Module imports
##############################
import base64  # Base64编码解码模块
import ctypes  # 操作系统接口模块
import os
from typing import Any

from tkui import icon
from tkui.tktypes import tk, GetDpiMixIn, messagebox, \
    TkFrame, TkLabel, TkButton, TkEntry, TkCombobox ,TkText, \
    FONT_BUTTON,  FONT_LABEL, \
    COLOR_FRAME_BG, COLOR_LABEL_BG, COLOR_LABEL_FG, \
    COLOR_BUTTON_BG, COLOR_BUTTON_FG, COLOR_BUTTON_ACTIVE_BG, COLOR_BUTTON_ACTIVE_FG, \
    WIDTH_LABEL, WIDTH_BUTTON, WIDTH_ROOT_WINDOW, WIDTH_COMBOBOX, WIDTH_ENTRY, \
    HEIGHT_BUTTON, HEIGHT_ENTRY, HEIGHT_ROOT_WINDOW, HEIGHT_WINDOW_MENU_BAR, \
    HEIGHT_LABEL, HEIGHT_COMBOBOX
from .model import DownloadModel


##############################
# View API function declarations
##############################

class DownloadView(tk.Tk, GetDpiMixIn):
    """
    下载界面的视图，根窗口
    """

    WIDTH_OPERATION_FRAME = 660
    WIDTH_SETTING_FRAME = 140

    def __init__(self) -> None:
        """构造函数"""
        # 操作系统使用程序自身的dpi适配
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        super().__init__()

        self.presenter = None # 视图的控制器
        self.text_info = None # 信息显示
        self.btn_mc = None # 测量标定按钮

        # 显示根窗口
        self.set_root()

    def set_presenter(self, presenter: Any) -> None:
        """
        设置presenter，presenter中含一系列方法，用于处理界面事件

        :param presenter: presenter对象
        :type presenter: Any
        """
        self.presenter = presenter
        # 窗口点击关闭触发的功能
        self.protocol('WM_DELETE_WINDOW', lambda: self.presenter.handler_on_closing())

    def show_warning(self, msg: str) -> None:
        """
        显示警告弹窗

        :param msg: 警告内容
        :type msg: str
        """
        messagebox.showwarning(parent=self, title='警告', message=msg)

    def set_root(self):
        """
        设置根窗口

        """
        # root = tk.Tk()
        self.title("Eco Tool Suit")
        # 窗口尺寸和位置
        x_pos = int((self.winfo_screenwidth() -
                     super().get_dpi(WIDTH_ROOT_WINDOW)) / 2)
        y_pos = int((self.winfo_screenheight() -
                     super().get_dpi(HEIGHT_ROOT_WINDOW + HEIGHT_WINDOW_MENU_BAR)) / 2)
        self.geometry(
            f"{super().get_dpi(WIDTH_ROOT_WINDOW)}x"
            f"{super().get_dpi(HEIGHT_ROOT_WINDOW + HEIGHT_WINDOW_MENU_BAR)}"
            f"+{x_pos}+{y_pos}")
        self.resizable(width=False, height=False)
        # root.overrideredirect(True)  # 去除标题栏
        with open('tmp.ico', 'wb') as tmp:
            tmp.write(base64.b64decode(icon.img))
        self.iconbitmap('tmp.ico')
        os.remove('tmp.ico')

    def set_root_menu(self, model: DownloadModel) -> None:
        """
        设置根窗口菜单

        :param model: 下载视图的数据模型
        :type model: DownloadModel
        """
        # 窗口绑定菜单栏
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        """菜单栏绑定文件菜单"""
        file_menu = tk.Menu(menu_bar, tearoff=False, font=FONT_BUTTON,
                            bg=COLOR_FRAME_BG, fg='black',
                            activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG)
        menu_bar.add_cascade(label="文件(F)", menu=file_menu)
        # 文件菜单绑定UDS设置
        file_settings_menu = tk.Menu(file_menu, tearoff=False, font=FONT_BUTTON,
                                     bg=COLOR_FRAME_BG, fg='black',
                                     activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG)
        file_menu.add_cascade(menu=file_settings_menu, label="UDS下载设置")
        # 文件设置绑定UDS显示id映射内容
        file_settings_menu.add_checkbutton(label="显示id映射详情",
                                           variable=model.check_uds_is_show_map_detail,
                                           command=lambda: self.presenter.handler_on_show_uds_map_detail())
        # 文件设置绑定UDS显示消息内容
        file_settings_menu.add_checkbutton(label="显示消息详情",
                                           variable=model.check_uds_is_show_msg_detail,
                                           command=lambda: self.presenter.handler_on_show_uds_msg_detail())
        # 文件菜单绑定退出按钮
        file_menu.add_command(label="复位设备", command=lambda: self.presenter.try_reset_pcan_device())
        # 文件菜单绑定退出按钮
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=lambda: self.presenter.handler_on_closing())

        """菜单栏绑定帮助菜单"""
        help_menu = tk.Menu(menu_bar, tearoff=False, font=FONT_BUTTON,
                            bg=COLOR_FRAME_BG, fg='black',
                            activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG)
        menu_bar.add_cascade(label="帮助(H)", menu=help_menu)
        help_menu.add_command(label="帮助", command=self.__show_help)
        help_menu.add_command(label="关于", command=self.__show_about)

    def set_operation_frame(self, model: DownloadModel):
        """
        设置操作frame界面

        :param model: 下载视图的数据模型
        :type model: DownloadModel
        """

        # 添加一个Frame
        frame = TkFrame(master=self,
                        bg=COLOR_FRAME_BG, borderwidth=0,
                        x=0, y=0, width=self.WIDTH_OPERATION_FRAME - 2, height=HEIGHT_ROOT_WINDOW)
        # 按钮_打开文件
        TkButton(master=frame,
                 bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                 activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG,
                 borderwidth=0,
                 text="打开", font=FONT_BUTTON,
                 command=lambda: (self.presenter.handler_on_open_download_file(),
                                  btn_download.config(state=model.opened_pgm_filepath and
                                                            model.opened_seed2key_filepath and
                                                            'normal' or 'disabled')
                                  ),
                 x=10, y=15, width=WIDTH_BUTTON, height=HEIGHT_BUTTON)
        # 按钮_下载
        btn_download = TkButton(master=frame,
                                bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                borderwidth=0,
                                text="下载", font=FONT_BUTTON,
                                command=lambda: self.presenter.handler_on_download_thread(),
                                x=100, y=15, width=WIDTH_BUTTON, height=HEIGHT_BUTTON,
                                state='disabled')

        # 按钮_秘钥
        TkButton(master=frame,
                 bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                 activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG,
                 borderwidth=0,
                 text="秘钥", font=FONT_BUTTON,
                 command=lambda: (self.presenter.handler_on_open_seed2key_file(),
                                  btn_download.config(state=model.opened_pgm_filepath and
                                                            model.opened_seed2key_filepath and
                                                            'normal' or 'disabled')
                                  ),
                 x=self.WIDTH_OPERATION_FRAME - 88, y=15,
                 width=WIDTH_BUTTON, height=HEIGHT_BUTTON)
        self.text_info = TkText(master=frame,
                                bg=COLOR_LABEL_BG, fg=COLOR_LABEL_FG,
                                borderwidth=5,
                                font=FONT_LABEL,
                                relief='flat', wrap='none', state='disabled',
                                x=10, y=60, width=self.WIDTH_OPERATION_FRAME - 38, height=HEIGHT_ROOT_WINDOW - 90)
        self.text_info.creat_scrollbar()

    def set_setting_frame(self, model: DownloadModel):
        """
        设置参数设置frame界面

        :param model: 下载视图的数据模型
        :type model: DownloadModel
        """
        # 参数设置Frame
        frame = TkFrame(master=self,
                        bg=COLOR_FRAME_BG, borderwidth=0,
                        x=self.WIDTH_OPERATION_FRAME, y=60,
                        width=self.WIDTH_SETTING_FRAME, height=HEIGHT_ROOT_WINDOW-60)
        # 刷写协议
        TkLabel(master=frame,
                bg=COLOR_FRAME_BG, fg='black',
                borderwidth=0,
                relief="sunken", justify='left', anchor='w',
                text="刷写协议：", font=FONT_BUTTON,
                x=10, y=10, width=WIDTH_LABEL, height=HEIGHT_LABEL)
        TkCombobox(master=frame,
                   background=COLOR_FRAME_BG, foreground='black',
                   values=model.PROTOCAOL, font=FONT_BUTTON,
                   textvariable=model.combobox_mode_protocol,
                   command=lambda: (self.presenter.handler_on_select_mode_protocol(),
                                    lbl_function_id.config(
                                        text=model.mode_protocol == model.PROTOCAOL[
                                            0] and "功能地址：" or "ecu站地址：")),
                   x=20, y=30, width=WIDTH_COMBOBOX, height=HEIGHT_COMBOBOX,
                   state='normal')
        # 设备类型
        TkLabel(master=frame,
                bg=COLOR_FRAME_BG, fg='black',
                borderwidth=0,
                relief="sunken", justify='left', anchor='w',
                text="设备类型：", font=FONT_BUTTON,
                x=10, y=65, width=WIDTH_LABEL, height=HEIGHT_LABEL)
        TkCombobox(master=frame,
                   background=COLOR_FRAME_BG, foreground='black',
                   values=model.DEVICES, font=FONT_BUTTON,
                   textvariable=model.combobox_device_type,
                   x=20, y=85, width=WIDTH_COMBOBOX, height=HEIGHT_COMBOBOX)
        # 设备通道
        TkLabel(master=frame,
                bg=COLOR_FRAME_BG, fg='black',
                borderwidth=0,
                relief="sunken", justify='left', anchor='w',
                text="设备通道：", font=FONT_BUTTON,
                x=10, y=120, width=WIDTH_LABEL, height=HEIGHT_LABEL)
        TkCombobox(master=frame,
                   background=COLOR_FRAME_BG, foreground='black',
                   values=model.CHANNELS, font=FONT_BUTTON,
                   textvariable=model.combobox_device_channel,
                   x=20, y=140, width=WIDTH_COMBOBOX, height=HEIGHT_COMBOBOX)
        # 波特率
        TkLabel(master=frame,
                bg=COLOR_FRAME_BG, fg='black',
                borderwidth=0,
                relief="sunken", justify='left', anchor='w',
                text="波特率：", font=FONT_BUTTON,
                x=10, y=175, width=WIDTH_LABEL, height=HEIGHT_LABEL)
        TkCombobox(master=frame,
                   background=COLOR_FRAME_BG, foreground='black',
                   values=model.BAUDRATES, font=FONT_BUTTON,
                   textvariable=model.combobox_baudrate,
                   x=20, y=195, width=WIDTH_COMBOBOX, height=HEIGHT_COMBOBOX)
        # 请求地址
        TkLabel(master=frame,
                bg=COLOR_FRAME_BG, fg='black',
                borderwidth=0,
                relief="sunken", justify='left', anchor='w',
                text="请求地址：", font=FONT_BUTTON,
                x=10, y=230, width=WIDTH_LABEL, height=HEIGHT_LABEL)
        TkEntry(master=frame,
                bg=COLOR_FRAME_BG, fg='black',
                borderwidth=1,
                font=FONT_BUTTON,
                textvariable=model.entry_request_id,
                relief="sunken", justify='left',
                x=20, y=250, width=WIDTH_ENTRY, height=HEIGHT_ENTRY)
        # 响应地址
        TkLabel(master=frame,
                bg=COLOR_FRAME_BG, fg='black',
                borderwidth=0,
                relief="sunken", justify='left', anchor='w',
                text="响应地址：", font=FONT_BUTTON,
                x=10, y=285, width=WIDTH_LABEL, height=HEIGHT_LABEL)
        TkEntry(master=frame,
                bg=COLOR_FRAME_BG, fg='black',
                borderwidth=1,
                font=FONT_BUTTON,
                textvariable=model.entry_response_id,
                relief="sunken", justify='left',
                x=20, y=305, width=WIDTH_ENTRY, height=HEIGHT_ENTRY)
        # 功能地址
        lbl_function_id = TkLabel(master=frame,
                                  bg=COLOR_FRAME_BG, fg='black',
                                  borderwidth=0,
                                  relief="sunken", justify='left', anchor='w',
                                  text=("功能地址：" if (model.mode_protocol == model.PROTOCAOL[
                                      0]) else "ecu站地址："),
                                  font=FONT_BUTTON,
                                  x=10, y=340, width=WIDTH_LABEL, height=HEIGHT_LABEL)
        TkEntry(master=frame,
                bg=COLOR_FRAME_BG, fg='black',
                borderwidth=1,
                font=FONT_BUTTON,
                textvariable=model.entry_function_id,
                relief="sunken", justify='left',
                x=20, y=360, width=WIDTH_ENTRY, height=HEIGHT_ENTRY)

        # 标定测量按钮Frame
        frame2 = TkFrame(master=self,
                        bg=COLOR_FRAME_BG, borderwidth=0,
                        x=self.WIDTH_OPERATION_FRAME, y=0,
                        width=self.WIDTH_SETTING_FRAME, height=58)
        # 按钮_打开和关闭标定测量视图
        self.btn_mc = TkButton(master=frame2,
                               bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                               activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG,
                               borderwidth=0,
                               text="测量与标定>>", font=FONT_BUTTON,
                               command=lambda: (self.presenter.handler_on_open_mc_ui() if
                                                self.btn_mc["text"]=="测量与标定>>" else
                                                self.presenter.handler_on_close_mc_ui()),
                               x=(self.WIDTH_SETTING_FRAME - WIDTH_BUTTON) / 2, y=(58 - HEIGHT_BUTTON) / 2,
                               width=WIDTH_BUTTON, height=HEIGHT_BUTTON)

    def set_msr_cal_frame(self, width:int = 500) -> TkFrame:
        """
        设置测量操作界面

        :param width: 界面宽度
        :type width: int
        :return: 容器
        :rtype: TkFrame
        """
        # 右侧扩展窗口
        self.geometry(f"{self.get_dpi(self.WIDTH_OPERATION_FRAME + self.WIDTH_SETTING_FRAME + width)}"
                      f"x{self.get_dpi(HEIGHT_ROOT_WINDOW)}")
        # 添加一个Frame
        return TkFrame(master=self,
                       bg=COLOR_FRAME_BG, borderwidth=0,
                       x=self.WIDTH_OPERATION_FRAME + self.WIDTH_SETTING_FRAME,
                       y=0,
                       width=width,
                       height=HEIGHT_ROOT_WINDOW)

    def clear_msr_cal_frame(self) -> None:
        """
        清除测量操作界面

        """
        # 回收右侧扩展窗口
        self.geometry(f"{self.get_dpi(self.WIDTH_OPERATION_FRAME + self.WIDTH_SETTING_FRAME)}"
                      f"x{self.get_dpi(HEIGHT_ROOT_WINDOW)}")

    def __show_about(self):
        """
        显示关于弹窗

        """
        msg = ('产品信息: \n'
               '    Eco Tool Suit V2025.1.0\n'
               '    Author: ZYD\n\n'
               '本产品包含: \n'
               '    Eco Download\n'
               '    Eco Measure&Calibrate\n')
        messagebox.showinfo(parent=self, title='关于', message=msg)

    def __show_help(self):
        """
        显示帮助说明弹窗

        """
        messagebox.showinfo(parent=self, title='帮助', message='1、选择密钥文件\n2、打开下载文件\n3、下载')
