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
import tkinter
from pprint import pformat  # 格式化输出模块
from typing import Any

from tkui import icon
from tkui.tktypes import *
from utils import singleton, pad_hex

from .model import *


##############################
# View API function declarations
##############################

class SubPropertyTipView(GetDpiMixIn):
    """
    属性悬浮显示窗

    :param master: 属性表格，悬浮窗将显示在此表格上
    :type master: TkTreeView
    :param text: 提示内容
    :type text: str
    :param bg: 背景颜色
    :type bg: str
    """

    def __init__(self,
                 master: TkTreeView,
                 text: str = '默认信息',
                 bg: str = '#fafdc2'):
        """构造函数"""
        # 操作系统使用程序自身的dpi适配
        ctypes.windll.shcore.SetProcessDpiAwareness(1)

        self.master = master
        self.text = text
        self.bg = bg

        # 窗口
        self.window = None

        # 绑定事件
        self.master.bind("<Double-1>", lambda e: (self.set_root(e)))
        self.master.bind("<Motion>", lambda e: self.leave())

    def set_root(self, e: tk.Event = None) -> None:
        """
        创建根窗口

        :param e: 事件
        :type e: tk.Event
        """
        # 选中数据项为空则退出
        if not self.master.selection():
            return

        selected_iid = self.master.selection()[0]  # 选中的数据项id
        col_names = self.master['columns']  # 表列名列表
        # 判断鼠标点击事件的位置, 是否在选中数据项的边界内, 如果在, 则获取该列的列名和数据项值，否则退出
        for idx, col_name in enumerate(col_names):
            # 获取选中数据项的边界（相对于控件窗口的坐标），形式为 (x, y, width, height)
            x, y, w, h = self.master.bbox(selected_iid, col_name)
            if x < e.x < x + w and y < e.y < y + h:
                selected_col = col_name  # 选中的数据项所在列的列名
                value = self.master.item(selected_iid, 'values')[idx]  # 选中的数据项的值
                break
        else:
            return
        # 若不是Content列则退出
        if selected_col != 'Content':
            return

        x = e.x_root + super().get_dpi(18)
        y = e.y_root + super().get_dpi(18)
        self.window = tk.Toplevel(self.master)
        self.window.wm_overrideredirect(True)  # 去边框
        self.window.wm_attributes("-topmost", 1)  # 置顶
        self.window.wm_geometry("+%d+%d" % (x, y))

        self.text = pformat(value)
        label = tk.Label(self.window,
                         text=self.text,
                         bg=self.bg,
                         relief=tk.SOLID,
                         borderwidth=1,
                         justify=tk.LEFT)
        label.pack(ipadx=1)

    def leave(self):
        # 销毁窗口
        if self.window:
            self.window.destroy()


class SubPropertyView(tk.Toplevel, GetDpiMixIn):
    """
    属性界面

    :param master: 父窗口
    :type master: tk.Toplevel
    :param obj: 待显示属性的对象
    :type obj: Any
    :param target: 目标，'measure':测量数据，'calibrate':标定数据
    :type target: str
    """

    WIDTH_ROOT_WINDOW = 400
    HEIGHT_ROOT_WINDOW = 600

    WIDTH_FRAME = 400
    HEIGHT_FRAME = 600

    def __init__(self,
                 master: tk.Toplevel,
                 obj: Any,
                 target: str,
                 ) -> None:
        """构造函数"""
        # 操作系统使用程序自身的dpi适配
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        super().__init__(master=master)

        self.obj = obj
        self.set_root(target)
        # 子窗口捕捉所有事件
        # self.grab_set()
        self.transient(master)

        self.set_property_frame()
        self.show_property()

    def set_root(self, target: str) -> None:
        """
        设置根窗口

        :param target: 目标，'measure':测量数据，'calibrate':标定数据
        :type target: str
        """
        # root = tk.Tk()
        self.title(target.title() + ':' + self.obj.name)
        # 窗口尺寸和位置
        x_pos = int((self.winfo_screenwidth() -
                     super().get_dpi(self.WIDTH_ROOT_WINDOW)) / 2)
        y_pos = int((self.winfo_screenheight() -
                     super().get_dpi(self.HEIGHT_ROOT_WINDOW)) / 2)
        self.wm_attributes("-topmost", 1)  # 置顶
        self.geometry(
            f"{super().get_dpi(self.WIDTH_ROOT_WINDOW)}x"
            f"{super().get_dpi(self.HEIGHT_ROOT_WINDOW)}"
            f"+{x_pos}+{y_pos}")
        self.resizable(width=False, height=False)
        # root.overrideredirect(True)  # 去除标题栏
        with open('tmp.ico', 'wb') as tmp:
            tmp.write(base64.b64decode(icon.img))
        self.iconbitmap('tmp.ico')
        os.remove('tmp.ico')

    def set_property_frame(self) -> None:
        # 设置区域容器
        property_frame = TkFrame(master=self,
                                 bg=COLOR_FRAME_BG, borderwidth=1,
                                 x=0,
                                 y=0,
                                 width=self.WIDTH_FRAME,
                                 height=self.HEIGHT_FRAME)

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
                                         y=0,
                                         width=self.WIDTH_FRAME - WIDTH_SCROLLER_BAR,
                                         height=self.HEIGHT_FRAME - WIDTH_SCROLLER_BAR)
        # self.table_property.column("#0", width=420, minwidth=100)
        # 设置滚动条
        self.table_property.create_scrollbar()
        # 设置表头
        self.table_property["columns"] = ("Property", "Content")
        self.table_property.column("Property", anchor='w', width=super().get_dpi(200))  # 表示列,不显示
        self.table_property.column("Content", anchor='w', width=super().get_dpi(200))
        self.table_property.heading("Property", anchor='w', text="Property")  # 显示表头
        self.table_property.heading("Content", anchor='w', text="Content")

        # 设置属性值悬浮窗
        self.__tip = SubPropertyTipView(master=self.table_property, bg=COLOR_LABEL_BG)

    def show_property(self) -> None:
        """
        显示对象的属性到表格控件

        """

        def _get_attributes(obj: Any) -> list[str]:
            """
            获取对象的所有属性，过滤掉以'__'开头和结尾的特殊属性，并且排除方法

            :param obj: 对象
            :type obj: Any
            :return: 属性列表
            :rtype: list[str]
            """
            return [attr for attr in dir(obj) if not attr.startswith("__") and not callable(getattr(obj, attr))]

        # 清空所有数据项
        self.table_property.delete(*self.table_property.get_children())
        # 获取属性
        if self.obj:
            attributes = _get_attributes(self.obj)
            for attribute in attributes:
                if attribute == "data":
                    self.table_property.insert(parent="",
                                               index="end",
                                               text="",
                                               values=(attribute, "".join(["0x", getattr(self.obj, attribute).hex()])),
                                               tags=['tag_1', ],
                                               )
                else:
                    self.table_property.insert(parent="",
                                               index="end",
                                               text="",
                                               values=(attribute, getattr(self.obj, attribute)),
                                               tags=['tag_1', ],
                                               )



class SubCalibrateValueView(GetDpiMixIn):
    """
    VALUE类型标定对象输入框

    :param master: 标定表格，输入框将显示在此表格上
    :type master: TkTreeView | ttk.Treeview
    :param item: 标定数据项
    :type item: ASAP2Calibrate
    :param geometry: 输入框几何位置(x,y,width,height)
    :type geometry: tuple[int, int, int, int]
    :param presenter: presenter中含一系列方法，用于处理界面事件
    :type presenter: Any
    """

    def __init__(self,
                 master: TkTreeView | ttk.Treeview,
                 item: ASAP2Calibrate,
                 geometry: tuple[int, int, int, int],
                 presenter: Any):
        """构造函数"""
        # 操作系统使用程序自身的dpi适配
        ctypes.windll.shcore.SetProcessDpiAwareness(1)

        self.master = master
        self.item = item
        self.x, self.y, self.width, self.height = geometry
        self.presenter = presenter

        # 内容编辑控件
        self.edit_widget = None
        # 内容编辑变量
        self.edit_var = None

        self.set_root()

    def set_root(self) -> None:
        """
        设置输入框

        """
        # 判断是否为可处理类型
        conversion_type = self.item.conversion.conversion_type
        if conversion_type != ASAP2EnumConversionType.RAT_FUNC and conversion_type != ASAP2EnumConversionType.TAB_VERB:
            msg = f"尚未支持{self.item.name}的类型(转换类型{conversion_type})"
            self.presenter.text_log(msg, 'error')
            self.presenter.view.show_warning(msg)
            return
        address_type = self.item.record_layout.fnc_values.address_type
        if address_type != ASAP2EnumAddrType.DIRECT:
            msg = f"尚未支持{self.item.name}的类型(寻址类型{address_type})"
            self.presenter.text_log(msg, 'error')
            self.presenter.view.show_warning(msg)
            return

        # 创建内容编辑变量，设置内容编辑变量的初始值
        self.edit_var = tk.StringVar(value=self.item.value.strip())
        # 根据选择的列和数据项属性，进行不同的处理
        if conversion_type == ASAP2EnumConversionType.RAT_FUNC:
            # 标量，普通数值
            self.edit_widget = tk.Entry(self.master,
                                        font=FONT_BUTTON,
                                        textvariable=self.edit_var,
                                        width=self.width // 11,
                                        relief=tkinter.SOLID,
                                        borderwidth=1,
                                        justify=tk.LEFT)
            self.edit_widget.bind('<FocusOut>',
                                  lambda e: self.presenter.handler_on_calibrate_value(self.edit_widget, self.item))
        elif conversion_type == ASAP2EnumConversionType.TAB_VERB:
            # 标量，数值映射
            self.edit_widget = ttk.Combobox(self.master,
                                            font=FONT_BUTTON,
                                            textvariable=self.edit_var,
                                            width=self.width // 11,
                                            state='readonly',
                                            values=list(self.item.conversion.compu_tab_ref.write_dict.keys()),
                                            justify=tk.LEFT)
            self.edit_widget.bind('<<ComboboxSelected>>',
                                  lambda e: self.presenter.handler_on_calibrate_value(self.edit_widget, self.item))
            self.edit_widget.bind('<FocusOut>', lambda e: self.leave())
        # 将widget放到self.table_calibrate的单元格中
        self.edit_widget.place(x=self.x, y=self.y, width=self.width, height=self.height)
        self.edit_widget.focus()

    def leave(self):
        # 销毁
        if self.edit_widget:
            self.edit_widget.place_forget()


class SubCalibrateCurveView(tk.Toplevel, GetDpiMixIn):
    """
    一维数据标定界面

    :param master: 父窗口
    :type master: tk.Toplevel
    :param axis_calibrate_dict: X轴标定对象
    :type axis_calibrate_dict: dict[str, ASAP2Calibrate]
    :param value_calibrate_dict: 值标定对象
    :type value_calibrate_dict: dict[str, ASAP2Calibrate]
    :param presenter: presenter中含一系列方法，用于处理界面事件
    :type presenter: Any
    """

    def __init__(self,
                 master: tk.Toplevel,
                 axis_calibrate_dict: dict[str, ASAP2Calibrate],
                 value_calibrate_dict: dict[str, ASAP2Calibrate],
                 presenter: Any
                 ) -> None:
        """构造函数"""
        # 操作系统使用程序自身的dpi适配
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        super().__init__(master=master)

        self.master = master
        self.axis_calibrate_dict = axis_calibrate_dict
        self.value_calibrate_dict = value_calibrate_dict
        self.presenter = presenter

        self.table_calibrate = None

        self.set_root()
        # 子窗口捕捉所有事件
        # self.grab_set()
        # self.transient(master)

        self.set_calibrate_frame()

    def __del__(self):
        """
        析构函数，窗口销毁时，将table_calibrate置为None

        """
        self.table_calibrate = None
        self.destroy()

    def set_root(self) -> None:
        """
        设置根窗口

        """
        # 窗口标题
        self.title(f"Curve Calibrate")
        # 窗口位置
        self.wm_attributes("-topmost", 1)  # 置顶
        self.wm_geometry("+%d+%d" % (self.master.winfo_rootx(), self.master.winfo_rooty())) # 位置
        self.resizable(width=True, height=True) # 窗口大小可变
        # 窗口点击关闭触发的功能
        self.protocol('WM_DELETE_WINDOW', lambda: self.__del__())
        with open('tmp.ico', 'wb') as tmp:
            tmp.write(base64.b64decode(icon.img))
        self.iconbitmap('tmp.ico')
        os.remove('tmp.ico')

    def set_calibrate_frame(self):
        """
        设置标定数据项界面
           |  0|  1|  2|  *|
          X| x0| x1| x*|  *|
          Y| y0| y1| y*|  *|

        """
        # 设置区域容器_表格
        frame2 = tk.Frame(master=self,
                         bg=COLOR_FRAME_BG,
                         borderwidth=1)
        # frame.pack_propagate(tk.FALSE) # 禁用传递几何位置
        frame2.pack(expand=tk.FALSE,
                   fill=tk.X,
                   side=tk.TOP,
                   anchor=tk.N)
        # 设置区域容器_滚动条
        frame = tk.Frame(master=self,
                         bg=COLOR_FRAME_BG,
                         borderwidth=1,
                         height=super().get_dpi(WIDTH_SCROLLER_BAR))
        # frame2.pack_propagate(tk.FALSE)  # 禁用传递几何位置
        frame.pack(expand=tk.FALSE,
                   fill=tk.X,
                   side=tk.TOP,
                   anchor=tk.N)


        # 设置表格风格
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        font=FONT_BUTTON,
                        rowheight=super().get_dpi(18))
        # 创建表格
        self.table_calibrate = ttk.Treeview(master=frame2,
                                            show=["tree", "headings"],
                                            selectmode="extended",
                                            style="Custom.Treeview",
                                            height=3)
        # 设置表头
        self.table_calibrate.column("#0", stretch=True, anchor='w',
                                    minwidth=super().get_dpi(50),
                                    width=super().get_dpi(300))
        self.table_calibrate.heading("#0", anchor='w', text="Name\Index")
        columns = [str(idx) for idx in range(len(self.axis_calibrate_dict))]
        self.table_calibrate["columns"] = columns
        for col in columns:
            self.table_calibrate.column(col, stretch=True, anchor='w',
                                        minwidth=super().get_dpi(80),
                                        width=super().get_dpi(100))
            self.table_calibrate.heading(col, anchor='w', text=str(col))

        self.table_calibrate.pack(expand=tk.TRUE,
                                  fill=tk.X,
                                  side=tk.LEFT,
                                  anchor=tk.N)
        # 创建一个水平滚动条组件，并将它与组件绑定
        x_scrollbar = ttk.Scrollbar(master=frame,
                                    orient='horizontal',
                                    command=self.table_calibrate.xview)
        x_scrollbar.pack(expand=tk.TRUE,
                         fill=tk.X,
                         side=tk.LEFT,
                         anchor=tk.N)
        self.table_calibrate.config(xscrollcommand=x_scrollbar.set)

        # 鼠标事件
        self.table_calibrate.bind("<Double-3>",
                                  lambda e: self.__show_property(e))
        self.table_calibrate.bind('<Double-1>',
                                  lambda e: self.presenter.handler_on_table_curve_edit(e, self.table_calibrate))

    def __show_property(self, e: tk.Event):
        """
        根据鼠标所处单元格，显示其标定对象的属性

        Args:
            e (tk.Event): 鼠标事件
        """

        # 获取选中的单元格
        selected_iid, selected_col, _, _ =(
            self.presenter.get_selected_cell_in_table(e=e, table=self.table_calibrate))
        # 未选中单元格则退出
        if not selected_iid or not selected_col:
            return
        # 获取标定对象的名字
        name = self.table_calibrate.item(selected_iid, "text")
        names = [self.table_calibrate.item(iid, "text") for iid in self.table_calibrate.get_children()]
        suffix = f"_X({selected_col})" if \
            names.index(name) == 0 else f"_Y({selected_col})"
        # 获取标定对象
        cal_item = self.axis_calibrate_dict.get(name + suffix) if \
            names.index(name) == 0 else self.value_calibrate_dict.get(name + suffix)
        # 显示属性
        SubPropertyView(master=self,
                        obj=cal_item,
                        target='calibrate')


class SubCalibrateMapView(tk.Toplevel, GetDpiMixIn):
    """
    二维数据标定界面

    :param master: 父窗口
    :type master: tk.Toplevel
    :param axis_calibrate_dict: X轴标定对象
    :type axis_calibrate_dict: dict[str, ASAP2Calibrate]
    :param axis2_calibrate_dict: Y轴标定对象
    :type axis2_calibrate_dict: dict[str, ASAP2Calibrate]
    :param value_calibrate_dict: 值标定对象
    :type value_calibrate_dict: dict[str, ASAP2Calibrate]
    :param presenter: presenter中含一系列方法，用于处理界面事件
    :type presenter: Any
    """

    def __init__(self,
                 master: tk.Toplevel,
                 axis_calibrate_dict: dict[str, ASAP2Calibrate],
                 axis2_calibrate_dict: dict[str, ASAP2Calibrate],
                 value_calibrate_dict: dict[str, ASAP2Calibrate],
                 presenter: Any
                 ) -> None:
        """构造函数"""
        # 操作系统使用程序自身的dpi适配
        ctypes.windll.shcore.SetProcessDpiAwareness(1)
        super().__init__(master=master)

        self.master = master
        self.axis_calibrate_dict = axis_calibrate_dict
        self.axis2_calibrate_dict = axis2_calibrate_dict
        self.value_calibrate_dict = value_calibrate_dict
        self.presenter = presenter

        self.table_calibrate = None

        self.set_root()
        # 子窗口捕捉所有事件
        # self.grab_set()
        # self.transient(master)

        self.set_calibrate_frame()

    def __del__(self):
        """
        析构函数，窗口销毁时，将table_calibrate置为None

        """
        self.table_calibrate = None
        self.destroy()

    def set_root(self) -> None:
        """
        设置根窗口

        """
        # 窗口标题
        self.title(f"Map Calibrate")
        # 窗口位置
        self.wm_attributes("-topmost", 1)  # 置顶
        self.wm_geometry("+%d+%d" % (self.master.winfo_rootx(), self.master.winfo_rooty())) # 位置
        self.resizable(width=True, height=True) # 窗口大小可变
        # 窗口点击关闭触发的功能
        self.protocol('WM_DELETE_WINDOW', lambda: self.__del__())
        with open('tmp.ico', 'wb') as tmp:
            tmp.write(base64.b64decode(icon.img))
        self.iconbitmap('tmp.ico')
        os.remove('tmp.ico')

    def set_calibrate_frame(self):
        """
        设置标定数据项界面
            |  X|  0|  1|  2|
           Y|   | x0| x1| x*|
           0| y0|z00|z01|  *|
           1| y1|z10|z11|  *|
           *| y*|  *|  *|  *|
        """
        # 设置区域容器_滚动条
        frame = tk.Frame(master=self,
                          bg=COLOR_FRAME_BG,
                          borderwidth=1,
                          height=super().get_dpi(WIDTH_SCROLLER_BAR))
        # frame2.pack_propagate(tk.FALSE)  # 禁用传递几何位置
        frame.pack(expand=tk.FALSE,
                    fill=tk.X,
                    side=tk.BOTTOM,
                    anchor=tk.N)
        # 设置区域容器_表格
        frame2 = tk.Frame(master=self,
                         bg=COLOR_FRAME_BG,
                         borderwidth=1)
        # frame.pack_propagate(tk.FALSE) # 禁用传递几何位置
        frame2.pack(expand=tk.TRUE,
                   fill=tk.BOTH,
                   side=tk.TOP,
                   anchor=tk.N)



        # 设置表格风格
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        font=FONT_BUTTON,
                        rowheight=super().get_dpi(18))
        # 创建表格
        self.table_calibrate = ttk.Treeview(master=frame2,
                                            show=["headings"],
                                            selectmode="extended",
                                            style="Custom.Treeview",
                                            height=len(self.axis2_calibrate_dict)+1)
        # 设置表头
        columns = ["Index", "X"] + [str(idx) for idx in range(len(self.axis_calibrate_dict))]
        self.table_calibrate["columns"] = columns
        for col in columns:
            self.table_calibrate.column(col, stretch=True, anchor='w',
                                        minwidth=super().get_dpi(80),
                                        width=super().get_dpi(100))
            self.table_calibrate.heading(col, anchor='w', text=col)
        self.table_calibrate.column("Index", stretch=False, anchor='w',
                                    minwidth=super().get_dpi(40),
                                    width=super().get_dpi(40))

        self.table_calibrate.pack(expand=tk.TRUE,
                                  fill=tk.BOTH,
                                  side=tk.LEFT,
                                  anchor=tk.N)
        # 创建一个水平滚动条组件，并将它与组件绑定
        x_scrollbar = ttk.Scrollbar(master=frame,
                                    orient='horizontal',
                                    command=self.table_calibrate.xview)
        x_scrollbar.pack(expand=tk.TRUE,
                         fill=tk.X,
                         side=tk.LEFT,
                         anchor=tk.N)
        self.table_calibrate.config(xscrollcommand=x_scrollbar.set)

        # 鼠标事件
        self.table_calibrate.bind("<Double-3>",
                                  lambda e: self.__show_property(e))
        self.table_calibrate.bind('<Double-1>',
                                  lambda e: self.presenter.handler_on_table_map_edit(e, self.table_calibrate))

    def __show_property(self,e):
        # 获取选中的单元格
        selected_iid, selected_col, name, (x, y, w, h) =(
            self.presenter.get_selected_cell_in_table(e=e, table=self.table_calibrate))
        # 未选中单元格则退出
        if not selected_iid or not selected_col:
            return
        # 获取行名
        item_index = self.table_calibrate.set(selected_iid, "Index")

        cal_item = None
        if item_index == "Y":
            # X轴标定对象
            if selected_col != "X" and int(selected_col) >= 0:
                names = list(self.axis_calibrate_dict.keys())
                cal_item = self.axis_calibrate_dict[names[int(selected_col)]]
        elif selected_col == "X":
            # Y轴标定对象
            if int(item_index) >= 0:
                names = list(self.axis2_calibrate_dict.keys())
                cal_item = self.axis2_calibrate_dict[names[int(item_index)]]
        elif int(selected_col) >= 0 and int(item_index) >= 0:
            # 值标定对象
            name = list(self.value_calibrate_dict.keys())[0]
            name = name[:name.find("_Z(")] + f"_Z({int(item_index)},{int(selected_col)})"
            cal_item = self.value_calibrate_dict[name]
        else:
            return
        # 显示属性
        SubPropertyView(master=self,
                        obj=cal_item,
                        target='calibrate')


# @singleton
class MeasureView(tk.Toplevel, GetDpiMixIn):
    """
    测量标定视图，子窗口

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
        super().__init__(master=master, bg=COLOR_FRAME_BG)

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

    def show_warning(self, msg: str) -> None:
        """
        显示警告弹窗

        :param msg: 警告信息
        :type msg: str
        """
        messagebox.showwarning(parent=self, title='警告', message=msg)

    def set_root(self) -> None:
        """
        设置根窗口

        """
        # root = tk.Tk()
        self.title("Eco Measure&Calibrate")
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

        # 选择数据项窗口管理器
        self.select_notebook = TkNotebook(master=self,
                                          x=0,
                                          y=0,
                                          width=self.WIDTH_SELECTION_FRAME,
                                          height=self.HEIGHT_SELECTION_FRAME
                                          )

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

    def set_select_measure_frame(self, model: MeasureModel) -> None:
        """
        设置测量数据项选择界面

        :param model: 视图的数据模型
        :type model: MeasureModel
        """

        # 设置区域容器
        selection_frame = TkFrame(master=self.select_notebook,
                                  bg=COLOR_FRAME_BG, borderwidth=1,
                                  # x=10,
                                  # y=10,
                                  # width=self.WIDTH_SELECTION_FRAME-30,
                                  # height=self.HEIGHT_SELECTION_FRAME-300
                                  )
        # 添加到窗口管理器
        self.select_notebook.add(selection_frame, text="测量")
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
                               textvariable=model.entry_search_measure_item,
                               relief="sunken", justify='left',
                               x=100,
                               y=2.5,
                               width=self.WIDTH_SELECTION_FRAME - 100 - WIDTH_BUTTON - WIDTH_SCROLLER_BAR,
                               height=HEIGHT_ENTRY)
        # 输入内容变化时的绑定事件
        model.entry_search_measure_item.trace('w',
                                              lambda *args: self.presenter.handler_on_search_item(target='measure'))
        # 输入框准备输入时的事件
        # entry_search.bind('<FocusIn>', lambda e: self.presenter.handler_prepare_search_table_items())

        # 设置显示数目标签
        self.label_select_measure_number = TkLabel(master=selection_frame,
                                                   bg=COLOR_LABEL_BG, fg=COLOR_LABEL_FG, borderwidth=0,
                                                   text='', font=FONT_BUTTON,
                                                   relief="sunken", justify='left',
                                                   anchor='c', wraplength=WIDTH_LABEL,
                                                   x=self.WIDTH_SELECTION_FRAME - 10 - WIDTH_BUTTON,
                                                   y=0,
                                                   width=WIDTH_BUTTON,
                                                   height=HEIGHT_BUTTON)

        # 设置添加按钮
        self.btn_ack_select_measure = TkButton(master=selection_frame,
                                               bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                               activebackground=COLOR_BUTTON_ACTIVE_BG,
                                               activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                               borderwidth=0,
                                               text="确定", font=FONT_BUTTON,
                                               command=lambda: self.presenter.handler_on_ack_select(target='measure'),
                                               x=WIDTH_BUTTON,
                                               y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON - 25,
                                               width=WIDTH_BUTTON,
                                               height=HEIGHT_BUTTON,
                                               state='normal')

        # 设置取消按钮
        self.btn_cancel_select_measure = TkButton(master=selection_frame,
                                                  bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                                  activebackground=COLOR_BUTTON_ACTIVE_BG,
                                                  activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                                  borderwidth=0,
                                                  text="取消", font=FONT_BUTTON,
                                                  command=lambda: self.presenter.handler_on_cancel_select(
                                                      target='measure'),
                                                  x=self.WIDTH_SELECTION_FRAME - WIDTH_BUTTON * 2,
                                                  y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON - 25,
                                                  width=WIDTH_BUTTON,
                                                  height=HEIGHT_BUTTON,
                                                  state='normal')

        # 设置表格风格
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        font=FONT_BUTTON,
                        rowheight=super().get_dpi(18), )
        # 设置表格
        self.table_select_measure = TkTreeView(master=selection_frame,
                                               show="headings",
                                               selectmode="browse",
                                               style="Custom.Treeview",
                                               x=0,
                                               y=HEIGHT_ENTRY * 2 - WIDTH_SCROLLER_BAR,
                                               width=self.WIDTH_SELECTION_FRAME - WIDTH_SCROLLER_BAR,
                                               height=self.HEIGHT_SELECTION_FRAME - HEIGHT_ENTRY * 4 + WIDTH_SCROLLER_BAR - 30)
        # self.table_select_measure.column("#0", width=420, minwidth=100)
        # 设置滚动条
        self.table_select_measure.create_scrollbar()
        # 绑定数据项选择事件
        self.table_select_measure.bind("<<TreeviewSelect>>",
                                       lambda e: self.presenter.handler_on_select_item(e, target='measure'))
        # 设置表头
        self.table_select_measure["columns"] = ("is_selected", "Name", "20ms", "100ms")
        self.table_select_measure.column("is_selected", anchor='c', width=super().get_dpi(15), )  # 表示列,不显示
        self.table_select_measure.column("Name", anchor='w', width=super().get_dpi(275))
        self.table_select_measure.column("20ms", anchor='c', width=super().get_dpi(45))
        self.table_select_measure.column("100ms", anchor='c', width=super().get_dpi(45))
        # self.table_select_measure.heading("is_selected", anchor='w', text="is_selected")  # 显示表头
        self.table_select_measure.heading("Name", anchor='w', text="Name")
        self.table_select_measure.heading("20ms", anchor='w', text="20ms")
        self.table_select_measure.heading("100ms", anchor='w', text="100ms")

        # 鼠标右键菜单
        table_menu = tk.Menu(master=self.master, tearoff=False, font=FONT_BUTTON,
                             bg=COLOR_FRAME_BG, fg='black',
                             activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG)
        table_menu.add_command(label="属性",
                               command=lambda: self.presenter.handler_on_show_property(
                                   table=self.table_select_measure, target='select_measure'),
                               )
        self.table_select_measure.bind("<Button-3>", lambda e: table_menu.post(e.x_root + 10, e.y_root))

    def set_measure_frame(self, model: MeasureModel):
        """
        设置测量数据项界面

        :param model: 视图的数据模型
        :type model: MeasureModel
        """

        # 设置区域容器
        self.__measure_frame = TkFrame(master=self,
                                       bg=COLOR_FRAME_BG, borderwidth=1,
                                       x=self.WIDTH_SELECTION_FRAME,
                                       y=HEIGHT_WINDOW_MENU_BAR + 1,
                                       width=self.WIDTH_SELECTION_FRAME,
                                       height=self.HEIGHT_SELECTION_FRAME)

        # 设置显示数目标签
        self.label_measure_number = TkLabel(master=self.__measure_frame,
                                            bg=COLOR_LABEL_BG, fg=COLOR_LABEL_FG, borderwidth=0,
                                            text='', font=FONT_BUTTON,
                                            relief="sunken", justify='left',
                                            anchor='c', wraplength=WIDTH_LABEL,
                                            x=self.WIDTH_SELECTION_FRAME - 10 - WIDTH_BUTTON,
                                            y=0,
                                            width=WIDTH_BUTTON,
                                            height=HEIGHT_BUTTON)

        label_title = TkLabel(master=self.__measure_frame,
                              bg=COLOR_FRAME_BG, fg='black', borderwidth=0,
                              text='测量', font=FONT_BUTTON,
                              relief="sunken", justify='left',
                              anchor='c', wraplength=WIDTH_LABEL,
                              x=(self.WIDTH_SELECTION_FRAME - WIDTH_BUTTON - WIDTH_SCROLLER_BAR) / 2,
                              y=0,
                              width=WIDTH_BUTTON,
                              height=HEIGHT_BUTTON)

        # 设置连接按钮
        self.btn_connect_measure = TkButton(master=self.__measure_frame,
                                            bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                            activebackground=COLOR_BUTTON_ACTIVE_BG,
                                            activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                            borderwidth=0,
                                            text="连接", font=FONT_BUTTON,
                                            command=lambda: self.presenter.handler_on_connect(),
                                            x=20,
                                            y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON - 25,
                                            width=WIDTH_BUTTON,
                                            height=HEIGHT_BUTTON,
                                            state='normal')

        # 设置断开按钮
        self.btn_disconnect_measure = TkButton(master=self.__measure_frame,
                                               bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                               activebackground=COLOR_BUTTON_ACTIVE_BG,
                                               activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                               borderwidth=0,
                                               text="断开", font=FONT_BUTTON,
                                               command=lambda: self.presenter.handler_on_disconnect(),
                                               x=110,
                                               y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON - 25,
                                               width=WIDTH_BUTTON,
                                               height=HEIGHT_BUTTON,
                                               state='disabled')

        # 设置启动测量按钮
        self.btn_start_measure = TkButton(master=self.__measure_frame,
                                          bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                          activebackground=COLOR_BUTTON_ACTIVE_BG,
                                          activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                          borderwidth=0,
                                          text="启动", font=FONT_BUTTON,
                                          command=lambda: self.presenter.handler_on_start_measure(),
                                          x=210,
                                          y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON - 25,
                                          width=WIDTH_BUTTON,
                                          height=HEIGHT_BUTTON,
                                          state='disabled')

        # 设置停止测量按钮
        self.btn_stop_measure = TkButton(master=self.__measure_frame,
                                         bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                         activebackground=COLOR_BUTTON_ACTIVE_BG,
                                         activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                         borderwidth=0,
                                         text="停止", font=FONT_BUTTON,
                                         command=lambda: self.presenter.handler_on_stop_measure(),
                                         x=300,
                                         y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON - 25,
                                         width=WIDTH_BUTTON,
                                         height=HEIGHT_BUTTON,
                                         state='disabled')

        # 设置表格风格
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        font=FONT_BUTTON,
                        rowheight=super().get_dpi(18), )
        # 设置表格
        self.table_measure = TkTreeView(master=self.__measure_frame,
                                        show="headings",
                                        selectmode="extended",
                                        style="Custom.Treeview",
                                        x=0,
                                        y=HEIGHT_ENTRY * 2 - WIDTH_SCROLLER_BAR,
                                        width=self.WIDTH_SELECTION_FRAME - WIDTH_SCROLLER_BAR,
                                        height=self.HEIGHT_SELECTION_FRAME - HEIGHT_ENTRY * 4 + WIDTH_SCROLLER_BAR - 30)
        # self.table_measure.column("#0", width=420, minwidth=100)
        # 设置滚动条
        self.table_measure.create_scrollbar()
        # 绑定数据项选择事件
        # self.table_measure.bind("<<TreeviewSelect>>",
        #                         lambda e: _pop_menu(e))
        # 设置表头
        self.table_measure["columns"] = ("Name", "Value", "Rate", "Unit")
        self.table_measure.column("Name", anchor='w', width=super().get_dpi(210))  # 表示列,不显示
        self.table_measure.column("Value", anchor='w', width=super().get_dpi(95))
        self.table_measure.column("Rate", anchor='w', width=super().get_dpi(45))
        self.table_measure.column("Unit", anchor='w', width=super().get_dpi(29))
        self.table_measure.heading("Name", anchor='w', text="Name")  # 显示表头
        self.table_measure.heading("Value", anchor='w', text="Value")
        self.table_measure.heading("Rate", anchor='w', text="Rate")
        self.table_measure.heading("Unit", anchor='w', text="Unit")

        # 鼠标右键菜单
        table_menu = tk.Menu(master=self.master, tearoff=False, font=FONT_BUTTON,
                             bg=COLOR_FRAME_BG, fg='black',
                             activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG)
        table_menu.add_command(label="删除",
                               command=lambda: self.presenter.handler_on_delete_item(target='measure'),
                               )
        table_menu.add_command(label="属性",
                               command=lambda: self.presenter.handler_on_show_property(
                                   table=self.table_measure, target='measure'),
                               )
        self.table_measure.bind("<Button-3>", lambda e: table_menu.post(e.x_root + 10, e.y_root))

    def set_select_calibrate_frame(self, model: MeasureModel) -> None:
        """
        设置标定数据项选择界面

        :param model: 视图的数据模型
        :type model: MeasureModel
        """

        # 设置区域容器
        selection_frame = TkFrame(master=self,
                                  bg=COLOR_FRAME_BG, borderwidth=1,
                                  # x=0,
                                  # y=0,
                                  # width=self.WIDTH_SELECTION_FRAME,
                                  # height=self.HEIGHT_SELECTION_FRAME
                                  )
        # 添加到窗口管理器
        self.select_notebook.add(selection_frame, text="标定")
        # 设置搜索框
        entry_search = TkEntry(master=selection_frame,
                               bg=COLOR_FRAME_BG, fg='black',
                               borderwidth=1,
                               font=FONT_BUTTON,
                               textvariable=model.entry_search_calibrate_item,
                               relief="sunken", justify='left',
                               x=100,
                               y=2.5,
                               width=self.WIDTH_SELECTION_FRAME - 100 - WIDTH_BUTTON - WIDTH_SCROLLER_BAR,
                               height=HEIGHT_ENTRY)
        # 输入内容变化时的绑定事件
        model.entry_search_calibrate_item.trace('w',
                                                lambda *args: self.presenter.handler_on_search_item(target='calibrate'))
        # 输入框准备输入时的事件
        # entry_search.bind('<FocusIn>', lambda e: self.presenter.handler_prepare_search_table_items())

        # 设置显示数目标签
        self.label_select_calibrate_number = TkLabel(master=selection_frame,
                                                     bg=COLOR_LABEL_BG, fg=COLOR_LABEL_FG, borderwidth=0,
                                                     text='', font=FONT_BUTTON,
                                                     relief="sunken", justify='left',
                                                     anchor='c', wraplength=WIDTH_LABEL,
                                                     x=self.WIDTH_SELECTION_FRAME - 10 - WIDTH_BUTTON,
                                                     y=0,
                                                     width=WIDTH_BUTTON,
                                                     height=HEIGHT_BUTTON)

        # 设置添加按钮
        self.btn_ack_select_calibrate = TkButton(master=selection_frame,
                                                 bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                                 activebackground=COLOR_BUTTON_ACTIVE_BG,
                                                 activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                                 borderwidth=0,
                                                 text="确定", font=FONT_BUTTON,
                                                 command=lambda: self.presenter.handler_on_ack_select(
                                                     target='calibrate'),
                                                 x=WIDTH_BUTTON,
                                                 y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON - 25,
                                                 width=WIDTH_BUTTON,
                                                 height=HEIGHT_BUTTON,
                                                 state='normal')

        # 设置取消按钮
        self.btn_cancel_select_calibrate = TkButton(master=selection_frame,
                                                    bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                                    activebackground=COLOR_BUTTON_ACTIVE_BG,
                                                    activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                                    borderwidth=0,
                                                    text="取消", font=FONT_BUTTON,
                                                    command=lambda: self.presenter.handler_on_cancel_select(
                                                        target='calibrate'),
                                                    x=self.WIDTH_SELECTION_FRAME - WIDTH_BUTTON * 2,
                                                    y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON - 25,
                                                    width=WIDTH_BUTTON,
                                                    height=HEIGHT_BUTTON,
                                                    state='normal')

        # 设置表格风格
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        font=FONT_BUTTON,
                        rowheight=super().get_dpi(18), )
        # 设置表格
        self.table_select_calibrate = TkTreeView(master=selection_frame,
                                                 show="headings",
                                                 selectmode="browse",
                                                 style="Custom.Treeview",
                                                 x=0,
                                                 y=HEIGHT_ENTRY * 2 - WIDTH_SCROLLER_BAR,
                                                 width=self.WIDTH_SELECTION_FRAME - WIDTH_SCROLLER_BAR,
                                                 height=self.HEIGHT_SELECTION_FRAME - HEIGHT_ENTRY * 4 + WIDTH_SCROLLER_BAR - 30)
        # self.table_select_calibrate.column("#0", width=420, minwidth=100)
        # 设置滚动条
        self.table_select_calibrate.create_scrollbar()
        # 绑定数据项选择事件
        self.table_select_calibrate.bind("<<TreeviewSelect>>",
                                         lambda e: self.presenter.handler_on_select_item(e, target='calibrate'))
        # 设置表头
        self.table_select_calibrate["columns"] = ("is_selected", "Name", "Check")
        self.table_select_calibrate.column("is_selected", anchor='c', width=super().get_dpi(15))  # 表示列,不显示
        self.table_select_calibrate.column("Name", anchor='w', width=super().get_dpi(325))
        self.table_select_calibrate.column("Check", anchor='c', width=super().get_dpi(40))
        # self.table_select_calibrate.heading("is_selected", anchor='w', text="is_selected")  # 显示表头
        self.table_select_calibrate.heading("Name", anchor='w', text="Name")
        self.table_select_calibrate.heading("Check", anchor='w', text="Check")

        # 鼠标右键菜单
        table_menu = tk.Menu(master=self.master, tearoff=False, font=FONT_BUTTON,
                             bg=COLOR_FRAME_BG, fg='black',
                             activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG)
        table_menu.add_command(label="属性",
                               command=lambda: self.presenter.handler_on_show_property(
                                   table=self.table_select_calibrate, target='select_calibrate'),
                               )
        self.table_select_calibrate.bind("<Button-3>", lambda e: table_menu.post(e.x_root + 10, e.y_root))

    def set_calibrate_frame(self, model: MeasureModel):
        """
        设置标定数据项界面

        :param model: 视图的数据模型
        :type model: MeasureModel
        """

        # 设置区域容器
        self.__calibrate_frame = TkFrame(master=self,
                                         bg=COLOR_FRAME_BG, borderwidth=1,
                                         x=self.WIDTH_SELECTION_FRAME * 2,
                                         y=HEIGHT_WINDOW_MENU_BAR + 1,
                                         width=self.WIDTH_SELECTION_FRAME,
                                         height=self.HEIGHT_SELECTION_FRAME)

        # 设置显示数目标签
        self.label_calibrate_number = TkLabel(master=self.__calibrate_frame,
                                              bg=COLOR_LABEL_BG, fg=COLOR_LABEL_FG, borderwidth=0,
                                              text='', font=FONT_BUTTON,
                                              relief="sunken", justify='left',
                                              anchor='c', wraplength=WIDTH_LABEL,
                                              x=self.WIDTH_SELECTION_FRAME - 10 - WIDTH_BUTTON,
                                              y=0,
                                              width=WIDTH_BUTTON,
                                              height=HEIGHT_BUTTON)

        label_title = TkLabel(master=self.__calibrate_frame,
                              bg=COLOR_FRAME_BG, fg='black', borderwidth=0,
                              text='标定', font=FONT_BUTTON,
                              relief="sunken", justify='left',
                              anchor='c', wraplength=WIDTH_LABEL,
                              x=(self.WIDTH_SELECTION_FRAME - WIDTH_BUTTON - WIDTH_SCROLLER_BAR) / 2,
                              y=0,
                              width=WIDTH_BUTTON,
                              height=HEIGHT_BUTTON)

        # 设置保存按钮
        self.btn_save_calibrate = TkButton(master=self.__calibrate_frame,
                                           bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                           activebackground=COLOR_BUTTON_ACTIVE_BG,
                                           activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                           borderwidth=0,
                                           text="保存至文件", font=FONT_BUTTON,
                                           command=lambda: self.presenter.handler_on_save_calibrate(),
                                           x=20,
                                           y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON - 25,
                                           width=WIDTH_BUTTON,
                                           height=HEIGHT_BUTTON,
                                           state='normal')

        # 设置保存按钮
        self.btn_upload_calibrate = TkButton(master=self.__calibrate_frame,
                                             bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                             activebackground=COLOR_BUTTON_ACTIVE_BG,
                                             activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                             borderwidth=0,
                                             text="从RAM上传", font=FONT_BUTTON,
                                             command=lambda: self.presenter.handler_on_upload_calibrate(),
                                             x=210,
                                             y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON - 25,
                                             width=WIDTH_BUTTON,
                                             height=HEIGHT_BUTTON,
                                             state='normal')

        # 设置保存按钮
        self.btn_program_calibrate = TkButton(master=self.__calibrate_frame,
                                              bg=COLOR_BUTTON_BG, fg=COLOR_BUTTON_FG,
                                              activebackground=COLOR_BUTTON_ACTIVE_BG,
                                              activeforeground=COLOR_BUTTON_ACTIVE_FG,
                                              borderwidth=0,
                                              text="刷写至ROM", font=FONT_BUTTON,
                                              command=lambda: self.presenter.handler_on_program_calibrate(),
                                              x=300,
                                              y=self.HEIGHT_SELECTION_FRAME - HEIGHT_BUTTON - 25,
                                              width=WIDTH_BUTTON,
                                              height=HEIGHT_BUTTON,
                                              state='normal')

        # 设置表格风格
        style = ttk.Style()
        style.configure("Custom.Treeview",
                        font=FONT_BUTTON,
                        rowheight=super().get_dpi(18), )
        # 设置表格
        self.table_calibrate = TkTreeView(master=self.__calibrate_frame,
                                          show="headings",
                                          selectmode="extended",
                                          style="Custom.Treeview",
                                          x=0,
                                          y=HEIGHT_ENTRY * 2 - WIDTH_SCROLLER_BAR,
                                          width=self.WIDTH_SELECTION_FRAME - WIDTH_SCROLLER_BAR,
                                          height=self.HEIGHT_SELECTION_FRAME - HEIGHT_ENTRY * 4 + WIDTH_SCROLLER_BAR - 30)
        # self.table_calibrate.column("#0", width=420, minwidth=100)
        # 设置滚动条
        self.table_calibrate.create_scrollbar()
        # 绑定数据项选择事件
        # self.table_calibrate.bind("<<TreeviewSelect>>",
        #                         lambda e: _pop_menu(e))
        # 设置表头
        self.table_calibrate["columns"] = ("Name", "Value", "Unit")
        self.table_calibrate.column("Name", anchor='w', width=super().get_dpi(255))  # 表示列,不显示
        self.table_calibrate.column("Value", anchor='w', width=super().get_dpi(95))
        self.table_calibrate.column("Unit", anchor='w', width=super().get_dpi(29))
        self.table_calibrate.heading("Name", anchor='w', text="Name")  # 显示表头
        self.table_calibrate.heading("Value", anchor='w', text="Value")
        self.table_calibrate.heading("Unit", anchor='w', text="Unit")

        # 鼠标右键菜单
        table_menu = tk.Menu(master=self.master, tearoff=False, font=FONT_BUTTON,
                             bg=COLOR_FRAME_BG, fg='black',
                             activebackground=COLOR_BUTTON_ACTIVE_BG, activeforeground=COLOR_BUTTON_ACTIVE_FG)
        table_menu.add_command(label="删除",
                               command=lambda: self.presenter.handler_on_delete_item(target='calibrate'),
                               )
        table_menu.add_command(label="属性",
                               command=lambda: self.presenter.handler_on_show_property(
                                   table=self.table_calibrate, target='calibrate'),
                               )
        self.table_calibrate.bind("<Button-3>",
                                  lambda e:table_menu.post(e.x_root + 10, e.y_root))
        self.table_calibrate.bind('<Double-1>',
                                  lambda e: self.presenter.handler_on_table_calibrate_edit(e, self.table_calibrate))
