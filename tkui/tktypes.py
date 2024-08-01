#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : ZYD
# @Time    : 2024/6/19 下午1:47
# @version : V1.0.0
# @function: V1.0.0：封装的tkinter控件，统一风格


##############################
# Module imports
##############################

import ctypes
import os
import tkinter as tk
from tkinter import messagebox, ttk

##############################
# Constant definitions
##############################

COLOR_FRAME_BG = '#fefefe'
COLOR_BUTTON_BG = '#368fff'
COLOR_BUTTON_FG = '#fefefe'
COLOR_BUTTON_ACTIVE_BG = '#1b80ff'
COLOR_BUTTON_ACTIVE_FG = '#e6e6e6'
COLOR_BUTTON_DISABLED_FG = '#c7c4b9'
COLOR_LABEL_BG = '#efefef'
COLOR_LABEL_FG = '#787878'

FONT_BUTTON = ('微软雅黑', 9)
FONT_LABEL = ('微软雅黑', 8)

WIDTH_ROOT_WINDOW = 800
HEIGHT_ROOT_WINDOW = 480

HEIGHT_WINDOW_MENU_BAR = 20

WIDTH_TEXT_INFO = 440
HEIGHT_TEXT_INFO = 390

WIDTH_BUTTON = 80
HEIGHT_BUTTON = 30

WIDTH_LABEL = 100
HEIGHT_LABEL = 20

WIDTH_COMBOBOX = 100
HEIGHT_COMBOBOX = 25

WIDTH_ENTRY = 100
HEIGHT_ENTRY = 25

WIDTH_SCROLLER_BAR = 20


##############################
# Auxiliary type definitions
##############################

class GetDpiMixIn(object):
    """
    混入类：获取屏幕的缩放因子
    """

    @staticmethod
    def get_dpi(pixel):
        """
        根据dpi缩放因子，计算缩放后的像素
        :param pixel: 像素
        :return: 缩放后的像素
        """
        # 获取屏幕的缩放因子
        scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        return int(pixel * scale_factor)


##############################
# Type definitions
##############################

class TkFrame(tk.Frame, GetDpiMixIn):
    """
    自定义Frame容器类，继承tk.Frame
    """

    def __init__(self, *args, **kwargs):
        master = kwargs.get('master', None)
        bg = kwargs.get('bg', COLOR_FRAME_BG)
        borderwidth = kwargs.get('borderwidth', 0)

        x = super().get_dpi(kwargs.get('x', 0))
        y = super().get_dpi(kwargs.get('y', 0))
        width = super().get_dpi(kwargs.get('width', 100))
        height = super().get_dpi(kwargs.get('height', 50))

        super().__init__(master=master, bg=bg, borderwidth=borderwidth)
        self.place(x=x, y=y, width=width, height=height)
        self.bind("<Leave>", lambda e: master.focus_set())


class TkButton(tk.Button, GetDpiMixIn):
    """
    自定义Button按钮类，继承tk.Button
    """

    def __init__(self, *args, **kwargs):
        master = kwargs.get('master', None)
        bg = kwargs.get('bg', COLOR_BUTTON_BG)
        fg = kwargs.get('fg', COLOR_BUTTON_FG)
        activebackground = kwargs.get('activebackground', COLOR_BUTTON_ACTIVE_BG)
        activeforeground = kwargs.get('activeforeground', COLOR_BUTTON_ACTIVE_FG)
        borderwidth = kwargs.get('borderwidth', 0)
        text = kwargs.get('text', '')
        font = kwargs.get('font', FONT_BUTTON)
        command = kwargs.get('command', None)
        state = kwargs.get('state', 'normal')

        x = super().get_dpi(kwargs.get('x', 0))
        y = super().get_dpi(kwargs.get('y', 0))
        width = super().get_dpi(kwargs.get('width', 100))
        height = super().get_dpi(kwargs.get('height', 50))

        super().__init__(master=master, bg=bg, fg=fg, activebackground=activebackground,
                         activeforeground=activeforeground,
                         disabledforeground=COLOR_BUTTON_DISABLED_FG,
                         borderwidth=borderwidth, text=text, font=font, command=command,
                         state=state)
        self.place(x=x, y=y, width=width, height=height)


class TkLabel(tk.Label, GetDpiMixIn):
    """
    自定义Label标签类，继承tk.Label
    """

    def __init__(self, *args, **kwargs):
        master = kwargs.get('master', None)
        bg = kwargs.get('bg', COLOR_FRAME_BG)
        fg = kwargs.get('fg', 'black')
        borderwidth = kwargs.get('borderwidth', 0)
        text = kwargs.get('text', '')
        font = kwargs.get('font', FONT_LABEL)
        relief = kwargs.get('relief', 'sunken')
        justify = kwargs.get('justify', 'left')
        anchor = kwargs.get('anchor', 'w')
        wraplength = super().get_dpi(kwargs.get('wraplength', 0))

        x = super().get_dpi(kwargs.get('x', 0))
        y = super().get_dpi(kwargs.get('y', 0))
        width = super().get_dpi(kwargs.get('width', 100))
        height = super().get_dpi(kwargs.get('height', 50))

        super().__init__(master=master, bg=bg, fg=fg,
                         borderwidth=borderwidth,
                         text=text, font=font,
                         relief=relief, justify=justify, anchor=anchor, wraplength=wraplength)
        self.place(x=x, y=y, width=width, height=height)


class TkCombobox(ttk.Combobox, GetDpiMixIn):
    """
    自定义Combobox下拉列表类，继承ttk.Combobox
    """

    def __init__(self, *args, **kwargs):
        master = kwargs.get('master', None)
        bg = kwargs.get('bg', COLOR_FRAME_BG)
        fg = kwargs.get('fg', 'black')
        values = kwargs.get('values', ())
        font = kwargs.get('font', FONT_BUTTON)
        textvariable = kwargs.get('textvariable', None)
        command = kwargs.get('command', None)
        state = kwargs.get('state', 'normal')

        x = super().get_dpi(kwargs.get('x', 0))
        y = super().get_dpi(kwargs.get('y', 0))
        width = super().get_dpi(kwargs.get('width', 100))
        height = super().get_dpi(kwargs.get('height', 50))

        super().__init__(master=master, background=bg, foreground=fg,
                         values=values, font=font,
                         textvariable=textvariable,
                         state=state)
        self.place(x=x, y=y, width=width, height=height)
        self.bind("<Leave>", lambda e: master.focus_set())  # 焦点定位到其它控件，这样下拉控件选中背景会消失
        self.bind('<<ComboboxSelected>>', lambda e: command and command())


class TkEntry(tk.Entry, GetDpiMixIn):
    """
    自定义Entry输入框类，继承tk.Entry
    """

    def __init__(self, *args, **kwargs):
        master = kwargs.get('master', None)
        bg = kwargs.get('bg', COLOR_FRAME_BG)
        fg = kwargs.get('fg', 'black')
        borderwidth = kwargs.get('borderwidth', 1)
        font = kwargs.get('font', FONT_BUTTON)
        textvariable = kwargs.get('textvariable', None)
        relief = kwargs.get('relief', 'sunken')
        justify = kwargs.get('justify', 'left')

        x = super().get_dpi(kwargs.get('x', 0))
        y = super().get_dpi(kwargs.get('y', 0))
        width = super().get_dpi(kwargs.get('width', 100))
        height = super().get_dpi(kwargs.get('height', 50))

        super().__init__(master=master, bg=bg, fg=fg,
                         borderwidth=borderwidth,
                         font=font,
                         textvariable=textvariable,
                         relief=relief, justify=justify)
        self.place(x=x, y=y, width=width, height=height)
        self.bind("<Leave>", lambda e: master.focus_set())


class TkText(tk.Text, GetDpiMixIn):
    """
    自定义Text多行文本框类，继承tk.Text，可添加滚动条
    """

    def __init__(self, *args, **kwargs):
        self.master = kwargs.get('master', None)
        bg = kwargs.get('bg', COLOR_LABEL_BG)
        fg = kwargs.get('fg', COLOR_LABEL_FG)
        borderwidth = kwargs.get('borderwidth', 1)
        font = kwargs.get('font', FONT_LABEL)
        relief = kwargs.get('relief', 'sunken')
        wrap = kwargs.get('wrap', 'none')
        state = kwargs.get('state', 'normal')

        self.x = super().get_dpi(kwargs.get('x', 0))
        self.y = super().get_dpi(kwargs.get('y', 0))
        self.width = super().get_dpi(kwargs.get('width', 100))
        self.height = super().get_dpi(kwargs.get('height', 50))

        super().__init__(master=self.master, bg=bg, fg=fg,
                         borderwidth=borderwidth,
                         font=font,
                         relief=relief, wrap=wrap, state=state)
        self.place(x=self.x, y=self.y, width=self.width, height=self.height)

        # 绑定鼠标右键菜单
        text_info_menu = tk.Menu(master=self.master, tearoff=False, font=FONT_BUTTON,
                                 bg=COLOR_FRAME_BG, fg='black',
                                 activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG)
        text_info_menu.add_command(label="清空",
                                   command=lambda: (self.config(state='normal'),
                                                    self.delete('1.0', 'end'),
                                                    self.config(state='disabled')
                                                    ),
                                   )
        text_info_menu.add_command(label="保存",
                                   command=lambda: (self.config(state='normal'),
                                                    self.__save_log(),
                                                    self.config(state='disabled')
                                                    ),
                                   )

        self.bind("<Button-3>", lambda e: text_info_menu.post(e.x_root + 10, e.y_root))

    def __save_log(self):
        """
        保存flash日志
        """
        try:
            filepath = r'.\logging.log'
            with open(filepath, "w", encoding='utf-8') as f:
                f.write(self.get(1.0, tk.END))
            msg = f'保存成功 {os.path.abspath(filepath)}'
            messagebox.showinfo("提示", msg)
            return msg
        except Exception as e:
            msg = f'保存失败 {os.path.abspath(filepath)}'
            raise Exception(msg)

    def creat_scrollbar(self):
        # 创建样式
        style = ttk.Style()
        style.theme_use('vista')
        # print(style.theme_names())
        # print(style.element_options('Horizontal.TScrollbar.thumb'))
        # 创建一个Text组件显示运行信息，带有滚动条
        style.configure('Vertical.TScrollbar',
                        background=COLOR_FRAME_BG,  # 滑块和边框颜色
                        troughcolor=COLOR_LABEL_BG,  # 滑槽颜色
                        arrowcolor=COLOR_LABEL_FG  # 箭头颜色
                        )
        style.configure('Horizontal.TScrollbar',
                        background=COLOR_LABEL_BG,  # 滑块和边框颜色
                        troughcolor=COLOR_LABEL_BG,  # 滑槽颜色
                        arrowcolor=COLOR_LABEL_FG  # 箭头颜色
                        )
        style.map("TScrollbar",
                  background=[('active', COLOR_FRAME_BG)],  # 鼠标位于滑块和边框上方的颜色
                  # bordercolor=[('active', "blue")],
                  troughcolor=[('active', COLOR_LABEL_BG)],  # 鼠标位于滑槽上方的颜色
                  # lightcolor=[('active', "red")],
                  # darkcolor=[('active', "pink")],
                  arrowcolor=[('active', COLOR_BUTTON_BG)],
                  )
        # 创建一个垂直滚动条组件，并将它与Text组件绑定
        y_scrollbar = ttk.Scrollbar(master=self.master, orient='vertical',
                                    command=self.yview)
        y_scrollbar.place(x=self.width + self.x, y=self.y,
                          width=super().get_dpi(WIDTH_SCROLLER_BAR),
                          height=self.height + super().get_dpi(WIDTH_SCROLLER_BAR))
        self.config(yscrollcommand=y_scrollbar.set)
        # 创建一个水平滚动条组件，并将它与Text组件绑定
        x_scrollbar = ttk.Scrollbar(master=self.master, orient='horizontal',
                                    command=self.xview)
        x_scrollbar.place(x=self.x, y=self.height + self.y,
                          width=self.width, height=super().get_dpi(WIDTH_SCROLLER_BAR))
        self.config(xscrollcommand=x_scrollbar.set)


class TkTreeView(ttk.Treeview, GetDpiMixIn):
    """
    自定义Treeview树形图，继承ttk.Treeview
    """

    # t = ttk.Treeview()

    def __init__(self, *args, **kwargs):
        self.master = kwargs.get('master', None)
        show = kwargs.get('show', ["tree"])
        selectmode = kwargs.get('selectmode', "browse")
        style = kwargs.get('style', None)

        self.x = super().get_dpi(kwargs.get('x', 0))
        self.y = super().get_dpi(kwargs.get('y', 0))
        self.width = super().get_dpi(kwargs.get('width', 100))
        self.height = super().get_dpi(kwargs.get('height', 50))

        super().__init__(master=self.master,
                         show=show,
                         selectmode=selectmode,
                         height=0,
                         style=style)
        self.place(x=self.x, y=self.y, width=self.width, height=self.height)
        # self.bind("<Leave>", lambda e: master.focus_set())  # 焦点定位到其它控件，这样下拉控件选中背景会消失
        # self.bind('<<ComboboxSelected>>', lambda e: command and command())

    def create_scrollbar(self):
        # 创建样式
        style = ttk.Style()
        style.theme_use('vista')
        # print(style.theme_names())
        # print(style.element_options('Horizontal.TScrollbar.thumb'))
        # 创建一个Text组件显示运行信息，带有滚动条
        style.configure('Vertical.TScrollbar',
                        background=COLOR_FRAME_BG,  # 滑块和边框颜色
                        troughcolor=COLOR_LABEL_BG,  # 滑槽颜色
                        arrowcolor=COLOR_LABEL_FG  # 箭头颜色
                        )
        style.configure('Horizontal.TScrollbar',
                        background=COLOR_LABEL_BG,  # 滑块和边框颜色
                        troughcolor=COLOR_LABEL_BG,  # 滑槽颜色
                        arrowcolor=COLOR_LABEL_FG  # 箭头颜色
                        )
        style.map("TScrollbar",
                  background=[('active', COLOR_FRAME_BG)],  # 鼠标位于滑块和边框上方的颜色
                  # bordercolor=[('active', "blue")],
                  troughcolor=[('active', COLOR_LABEL_BG)],  # 鼠标位于滑槽上方的颜色
                  # lightcolor=[('active', "red")],
                  # darkcolor=[('active', "pink")],
                  arrowcolor=[('active', COLOR_BUTTON_BG)],
                  )
        # 创建一个垂直滚动条组件，并将它与组件绑定
        y_scrollbar = ttk.Scrollbar(master=self.master, orient='vertical',
                                    command=self.yview)
        y_scrollbar.place(x=self.width + self.x, y=self.y,
                          width=super().get_dpi(WIDTH_SCROLLER_BAR),
                          height=self.height + super().get_dpi(WIDTH_SCROLLER_BAR))
        self.config(yscrollcommand=y_scrollbar.set)
        # 创建一个水平滚动条组件，并将它与组件绑定
        x_scrollbar = ttk.Scrollbar(master=self.master, orient='horizontal',
                                    command=self.xview)
        x_scrollbar.place(x=self.x, y=self.height + self.y,
                          width=self.width, height=super().get_dpi(WIDTH_SCROLLER_BAR))
        self.config(xscrollcommand=x_scrollbar.set)
