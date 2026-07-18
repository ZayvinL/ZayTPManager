# -*- coding: utf-8 -*-
"""路径与权限管理 - 数据地址统一用正斜杠相对路径, 适配多用户/多系统"""

import os


def local_path_get():
    """工具所在目录, 正斜杠结尾"""
    current_path = os.path.dirname(os.path.abspath(__file__)) + "/"
    return current_path.replace(os.sep, "/")


def data_root_get():
    """数据根目录 templateWork/, 不存在则创建"""
    root = local_path_get() + "templateWork/"
    if not os.path.exists(root):
        os.makedirs(root)
        ensure_writable(root)
    return root


def ensure_writable(path):
    """best-effort 放开权限, 保证共享存储上其他用户可读写 (失败静默忽略)"""
    try:
        if os.path.isdir(path):
            os.chmod(path, 0o777)
        else:
            os.chmod(path, 0o666)
    except OSError:
        pass


def to_rel(abs_path, root=None):
    """绝对路径 -> 相对数据根的正斜杠路径"""
    root = root or data_root_get()
    return os.path.relpath(abs_path, root).replace(os.sep, "/")


def to_abs(rel_path, root=None):
    """相对数据根的路径 -> 绝对路径 (正斜杠)"""
    root = root or data_root_get()
    return (root + rel_path.lstrip("/")).replace(os.sep, "/")
