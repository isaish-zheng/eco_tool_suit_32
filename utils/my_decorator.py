#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Author  : ZYD
# @Time    : 2024/7/20 上午11:23
# @version : V1.0.0
# @function: 装饰器


def singleton(cls):
    """
    单例模式装饰器
    :param cls: 被装饰的类
    :return: 单例对象
    """
    instances = {}

    def _singleton(*args, **kwargs):
        # 创建字典保存被装饰类的实例对象
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return _singleton
