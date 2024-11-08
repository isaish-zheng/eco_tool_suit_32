#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : ZYD
# @Time    : 2024/7/11 下午2:58
# @version : V1.0.0
# @function:

##############################
# Module imports
##############################

import traceback  # 用于获取异常详细信息

from app import DownloadModel, DownloadView, DownloadCtrl


if __name__ == '__main__':
    # 配置文件路径
    CONFIG_PATH = ('cfg_download.ini', 'cfg_a2l.ini',)
    try:
        # 创建view
        download_view = DownloadView()
        # 创建model
        download_model = DownloadModel()
        # 创建controller
        download_ctrl = DownloadCtrl(model=download_model,
                                     view=download_view,
                                     cfg_path=CONFIG_PATH)

        # 显示根窗口内容
        download_view.set_root_menu(download_model)
        download_view.set_operation_frame(download_model)
        download_view.set_setting_frame(download_model)

        # 启动时尝试复位pcan设备
        download_ctrl.try_reset_pcan_device()

        download_view.mainloop()
    except Exception as e:
        download_ctrl.text_log(f'发生异常 {e}', 'error')
        download_ctrl.text_log(f"{traceback.format_exc()}", 'error')
        print(f'发生异常 {e}')
        print(f"{traceback.format_exc()}")
    finally:
        pass
        # time.sleep(2)
        # print("当前线程数量为", threading.active_count())
        # print("所有线程的具体信息", threading.enumerate())
        # print("当前线程具体信息", threading.current_thread())
