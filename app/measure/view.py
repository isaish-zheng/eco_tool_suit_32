#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : ZYD
# @Time    : 2024/7/11 下午5:31
# @version : V1.0.0
# @function:


##############################
# Module imports
##############################

import base64  # Base64编码解码模块
from typing import Any

from tkui import icon
from tkui.tktypes import *
from utils import singleton

from .model import MeasureModel


##############################
# View API function declarations
##############################

# @singleton
class MeasureView(tk.Toplevel, GetDpiMixIn):
    """
    测量视图，子窗口

    :param master: 父窗口
    :type master: tk.Tk
    """

    WIDTH_ROOT_WINDOW = 1200
    HEIGHT_ROOT_WINDOW = 600

    WIDTH_SELECTION_FRAME = 400
    HEIGHT_SELECTION_FRAME = 600

    def __init__(self,
                 master: tk.Tk,
                 ) -> None:
        """构造函数"""
        # 操作系统使用程序自身的dpi适配
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        super().__init__(master=master)

        self.set_root()
        # 子窗口捕捉所有事件
        # self.grab_set()
        self.transient(master)

    def set_presenter(self, presenter: Any) -> None:
        """
        设置presenter，presenter中含一系列方法，用于处理界面事件

        :param presenter: presenter
        :type presenter: Any
        """
        self.presenter = presenter
        # 窗口点击关闭触发的功能
        self.protocol('WM_DELETE_WINDOW', lambda: self.presenter.handler_on_closing())

    @staticmethod
    def show_warning(msg: str) -> None:
        """
        显示警告弹窗

        :param msg: 警告信息
        :type msg: str
        """
        messagebox.showwarning(title='警告', message=msg)

    def set_root(self) -> None:
        """
        设置根窗口

        """
        # root = tk.Tk()
        self.title("Eco Viewer")
        # 窗口尺寸和位置
        x_pos = int((self.winfo_screenwidth() -
                     super().get_dpi(self.WIDTH_ROOT_WINDOW)) / 2)
        y_pos = int((self.winfo_screenheight() -
                     super().get_dpi(self.HEIGHT_ROOT_WINDOW + HEIGHT_WINDOW_MENU_BAR)) / 2)
        self.geometry(
            f"{super().get_dpi(self.WIDTH_ROOT_WINDOW)}x"
            f"{super().get_dpi(self.HEIGHT_ROOT_WINDOW + HEIGHT_WINDOW_MENU_BAR)}"
            f"+{x_pos}+{y_pos}")
        self.resizable(width=False, height=False)
        # root.overrideredirect(True)  # 去除标题栏
        with open('tmp.ico', 'wb') as tmp:
            tmp.write(base64.b64decode(icon.img))
        self.iconbitmap('tmp.ico')
        os.remove('tmp.ico')

    def set_root_menu(self) -> None:
        """
        设置根窗口菜单

        """
        # 窗口绑定菜单栏
        menu_bar = tk.Menu(self)
        self.config(menu=menu_bar)

        """菜单栏绑定文件菜单"""
        file_menu = tk.Menu(menu_bar, tearoff=False, font=FONT_BUTTON,
                            bg=COLOR_FRAME_BG, fg='black',
                            activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG)
        menu_bar.add_cascade(label="文件(F)", menu=file_menu)
        # 文件菜单绑定设置
        # file_settings_menu = tk.Menu(file_menu, tearoff=False, font=FONT_BUTTON,
        #                              bg=COLOR_FRAME_BG, fg='black',
        #                              activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG)
        # file_menu.add_cascade(menu=file_settings_menu, label="设置")

        # 文件菜单绑定退出按钮
        file_menu.add_command(label="退出", command=lambda: self.presenter.handler_on_closing())

    def set_measure_selection_frame(self, model: MeasureModel) -> None:
        """
        设置测量数据项选择界面

        :param model: 测量视图的数据模型
        :type model: MeasureModel
        """

        # 设置区域容器
        selection_frame = TkFrame(master=self,
                                  bg=COLOR_FRAME_BG, borderwidth=1,
                                  x=0,
                                  y=0,
                                  width=self.WIDTH_SELECTION_FRAME,
                                  height=self.HEIGHT_SELECTION_FRAME)

        # 设置打开按钮
        self.btn_open = TkButton(master=selection_frame,
                                 bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                 activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                 borderwidth=0,
                                 text="打开", font=FONT_BUTTON,
                                 command=lambda: self.presenter.handler_on_open_file(),
                                 x=10,
                                 y=0,
                                 width=WIDTH_BUTTON,
                                 height=HEIGHT_BUTTON,
                                 state='normal')

        # 设置搜索框
        entry_search = TkEntry(master=selection_frame,
                               bg=COLOR_FRAME_BG, fg='black',
                               borderwidth=1,
                               font=FONT_BUTTON,
                               textvariable=model.entry_search_table_items,
                               relief="sunken", justify='left',
                               x=100,
                               y=2.5,
                               width=self.WIDTH_SELECTION_FRAME - 100 - WIDTH_BUTTON - WIDTH_SCROLLER_BAR,
                               height=HEIGHT_ENTRY)
        # 输入内容变化时的绑定事件
        model.entry_search_table_items.trace('w', lambda *args: self.presenter.handler_on_search_measurement_item())
        # 输入框准备输入时的事件
        # entry_search.bind('<FocusIn>', lambda e: self.presenter.handler_prepare_search_table_items())

        # 设置显示数目标签
        self.label_selection_number = TkLabel(master=selection_frame,
                                              bg=COLOR_LABEL_BG, fg=COLOR_LABEL_FG, borderwidth=0,
                                              text='', font=FONT_BUTTON,
                                              relief="sunken", justify='left',
                                              anchor='c', wraplength=WIDTH_LABEL,
                                              x=self.WIDTH_SELECTION_FRAME - 10 - WIDTH_BUTTON,
                                              y=0,
                                              width=WIDTH_BUTTON,
                                              height=HEIGHT_BUTTON)

        # 设置添加按钮
        self.btn_ack = TkButton(master=selection_frame,
                                bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                borderwidth=0,
                                text="确定", font=FONT_BUTTON,
                                command=lambda: self.presenter.handler_on_ack_selected_measurements(),
                                x=WIDTH_BUTTON,
                                y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON,
                                width=WIDTH_BUTTON,
                                height=HEIGHT_BUTTON,
                                state='normal')

        # 设置取消按钮
        self.btn_cancel = TkButton(master=selection_frame,
                                   bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                   activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                   borderwidth=0,
                                   text="取消", font=FONT_BUTTON,
                                   command=lambda: self.presenter.handler_on_cancel_selected_measurements(),
                                   x=self.WIDTH_SELECTION_FRAME - WIDTH_BUTTON * 2,
                                   y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON,
                                   width=WIDTH_BUTTON,
                                   height=HEIGHT_BUTTON,
                                   state='normal')

        # 设置表格风格
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        font=FONT_BUTTON,
                        rowheight=super().get_dpi(18), )
        # 设置表格
        self.table_measurement = TkTreeView(master=selection_frame,
                                            show="headings",
                                            selectmode="browse",
                                            style="Custom.Treeview",
                                            x=0,
                                            y=HEIGHT_ENTRY * 2 - WIDTH_SCROLLER_BAR,
                                            width=self.WIDTH_SELECTION_FRAME - WIDTH_SCROLLER_BAR,
                                            height=self.HEIGHT_SELECTION_FRAME - HEIGHT_ENTRY * 4 + WIDTH_SCROLLER_BAR)
        # self.table_measurement.column("#0", width=420, minwidth=100)
        # 设置滚动条
        self.table_measurement.create_scrollbar()
        # 绑定数据项选择事件
        self.table_measurement.bind("<<TreeviewSelect>>",
                                    lambda e: self.presenter.handler_on_select_measurement_item(e))
        # 设置表头
        self.table_measurement["columns"] = ("is_selected", "Name", "20ms", "100ms")
        self.table_measurement.column("is_selected", anchor='c', width=super().get_dpi(10), )  # 表示列,不显示
        self.table_measurement.column("Name", anchor='w', width=super().get_dpi(200))
        self.table_measurement.column("20ms", anchor='c', width=super().get_dpi(10))
        self.table_measurement.column("100ms", anchor='c', width=super().get_dpi(10))
        # self.table_measurement.heading("is_selected", anchor='w', text="is_selected")  # 显示表头
        self.table_measurement.heading("Name", anchor='w', text="Name")
        self.table_measurement.heading("20ms", anchor='w', text="20ms")
        self.table_measurement.heading("100ms", anchor='w', text="100ms")

    def set_measure_monitor_frame(self, model: MeasureModel):
        """
        设置数据项监视界面

        :param model: 测量视图的数据模型
        :type model: MeasureModel
        """

        # 设置区域容器
        self.__monitor_frame = TkFrame(master=self,
                                       bg=COLOR_FRAME_BG, borderwidth=1,
                                       x=self.WIDTH_SELECTION_FRAME,
                                       y=0,
                                       width=self.WIDTH_SELECTION_FRAME,
                                       height=self.HEIGHT_SELECTION_FRAME)

        # 设置显示数目标签
        self.label_monitor_number = TkLabel(master=self.__monitor_frame,
                                            bg=COLOR_LABEL_BG, fg=COLOR_LABEL_FG, borderwidth=0,
                                            text='', font=FONT_BUTTON,
                                            relief="sunken", justify='left',
                                            anchor='c', wraplength=WIDTH_LABEL,
                                            x=self.WIDTH_SELECTION_FRAME - 10 - WIDTH_BUTTON,
                                            y=0,
                                            width=WIDTH_BUTTON,
                                            height=HEIGHT_BUTTON)

        # 设置连接按钮
        self.btn_connect = TkButton(master=self.__monitor_frame,
                                    bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                    activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                    borderwidth=0,
                                    text="连接", font=FONT_BUTTON,
                                    command=lambda: self.presenter.handler_on_connect(),
                                    x=20,
                                    y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON,
                                    width=WIDTH_BUTTON,
                                    height=HEIGHT_BUTTON,
                                    state='normal')

        # 设置断开按钮
        self.btn_disconnect = TkButton(master=self.__monitor_frame,
                                       bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                       activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                       borderwidth=0,
                                       text="断开", font=FONT_BUTTON,
                                       command=lambda: self.presenter.handler_on_disconnect(),
                                       x=110,
                                       y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON,
                                       width=WIDTH_BUTTON,
                                       height=HEIGHT_BUTTON,
                                       state='disabled')

        # 设置启动测量按钮
        self.btn_start_measure = TkButton(master=self.__monitor_frame,
                                          bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                          activebackground=COLOR_BUTTON_ACTIVE_BG,
                                          activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                          borderwidth=0,
                                          text="启动", font=FONT_BUTTON,
                                          command=lambda: self.presenter.handler_on_start_measure(),
                                          x=210,
                                          y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON,
                                          width=WIDTH_BUTTON,
                                          height=HEIGHT_BUTTON,
                                          state='disabled')

        # 设置停止测量按钮
        self.btn_stop_measure = TkButton(master=self.__monitor_frame,
                                         bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                         activebackground=COLOR_BUTTON_ACTIVE_BG,
                                         activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                         borderwidth=0,
                                         text="停止", font=FONT_BUTTON,
                                         command=lambda: self.presenter.handler_on_stop_measure(),
                                         x=300,
                                         y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON,
                                         width=WIDTH_BUTTON,
                                         height=HEIGHT_BUTTON,
                                         state='disabled')

        # 设置表格风格
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        font=FONT_BUTTON,
                        rowheight=super().get_dpi(18), )
        # 设置表格
        self.table_monitor = TkTreeView(master=self.__monitor_frame,
                                        show="headings",
                                        selectmode="extended",
                                        style="Custom.Treeview",
                                        x=0,
                                        y=HEIGHT_ENTRY * 2 - WIDTH_SCROLLER_BAR,
                                        width=self.WIDTH_SELECTION_FRAME - WIDTH_SCROLLER_BAR,
                                        height=self.HEIGHT_SELECTION_FRAME - HEIGHT_ENTRY * 4 + WIDTH_SCROLLER_BAR)
        # self.table_monitor.column("#0", width=420, minwidth=100)
        # 设置滚动条
        self.table_monitor.create_scrollbar()
        # 绑定数据项选择事件
        # self.table_monitor.bind("<<TreeviewSelect>>",
        #                         lambda e: _pop_menu(e))
        # 设置表头
        self.table_monitor["columns"] = ("Name", "Value", "Rate", "Unit")
        self.table_monitor.column("Name", anchor='w', width=super().get_dpi(200))  # 表示列,不显示
        self.table_monitor.column("Value", anchor='w', width=super().get_dpi(10))
        self.table_monitor.column("Rate", anchor='w', width=super().get_dpi(10))
        self.table_monitor.column("Unit", anchor='w', width=super().get_dpi(10))
        self.table_monitor.heading("Name", anchor='w', text="Name")  # 显示表头
        self.table_monitor.heading("Value", anchor='w', text="Value")
        self.table_monitor.heading("Rate", anchor='w', text="Rate")
        self.table_monitor.heading("Unit", anchor='w', text="Unit")

        # 鼠标右键菜单
        table_monitor_menu = tk.Menu(master=self.master, tearoff=False, font=FONT_BUTTON,
                                     bg=COLOR_FRAME_BG, fg='black',
                                     activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG)
        table_monitor_menu.add_command(label="删除",
                                       command=lambda: self.presenter.handler_on_delete_minitor_item(),
                                       )
        self.table_monitor.bind("<Button-3>", lambda e: table_monitor_menu.post(e.x_root + 10, e.y_root))

    def set_measure_property_frame(self, model: MeasureModel):
        """
        设置数据项属性界面

        :param model: 测量视图的数据模型
        :type model: MeasureModel
        """

        # 设置区域容器
        property_frame = TkFrame(master=self,
                                 bg=COLOR_FRAME_BG, borderwidth=1,
                                 x=self.WIDTH_SELECTION_FRAME * 2,
                                 y=0,
                                 width=self.WIDTH_SELECTION_FRAME,
                                 height=self.HEIGHT_SELECTION_FRAME)

        # 设置表格风格
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        font=FONT_BUTTON,
                        rowheight=super().get_dpi(18), )
        # 设置表格
        self.table_property = TkTreeView(master=property_frame,
                                         show="headings",
                                         selectmode="browse",
                                         style="Custom.Treeview",
                                         x=0,
                                         y=HEIGHT_ENTRY * 2 - WIDTH_SCROLLER_BAR,
                                         width=self.WIDTH_SELECTION_FRAME - WIDTH_SCROLLER_BAR,
                                         height=self.HEIGHT_SELECTION_FRAME - HEIGHT_ENTRY * 4 + WIDTH_SCROLLER_BAR)
        # self.table_property.column("#0", width=420, minwidth=100)
        # 设置滚动条
        self.table_property.create_scrollbar()
        # 绑定数据项选择事件
        # self.table_property.bind("<<TreeviewSelect>>",
        #                          lambda e: self.presenter.handler_on_measurement_item_selected(e))
        # 设置表头
        self.table_property["columns"] = ("Property", "Content")
        self.table_property.column("Property", anchor='w', width=super().get_dpi(200))  # 表示列,不显示
        self.table_property.column("Content", anchor='w', width=super().get_dpi(200))
        self.table_property.heading("Property", anchor='w', text="Property")  # 显示表头
        self.table_property.heading("Content", anchor='w', text="Content")
