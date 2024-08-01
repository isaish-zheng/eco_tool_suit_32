#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author  : ZYD
# @version : V1.0.0
# @function: V1.0.0：将.ico文件转换为.py文件


##############################
# Module imports
##############################

import base64


##############################
# Function definitions
##############################

def dealicon(open_path: str, save_path: str):
    """
    将.ico文件转换为.py文件
    :param open_path: .ico文件路径
    :param save_path: .py文件路径
    """
    open_icon = open(open_path, "rb")
    b64str = base64.b64encode(open_icon.read())
    open_icon.close()
    write_data = "img = %s" % b64str
    f = open(save_path, "w+")
    f.write(write_data)
    f.close()


##############################
# main
##############################
if __name__ == '__main__':
    open_path = "../icons/Z.ico"
    save_path = "../tkui/icon.py"
    dealicon(open_path, save_path)
