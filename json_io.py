# -*- coding: utf-8 -*-
"""读写 json 文件 - utf-8 原子写入, 适配多用户共享存储"""

import json
import os
import tempfile

import paths


def WriteJson(path, dict_data):
    """先写临时文件再原子替换, 避免其他用户读到写了一半的文件"""
    data = json.dumps(dict_data, ensure_ascii=False, sort_keys=True, indent=4)
    fd, tmp_path = tempfile.mkstemp(suffix=".jsontmp", dir=os.path.dirname(path))
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(data)
        os.replace(tmp_path, path)
    except Exception:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        raise
    paths.ensure_writable(path)


def ReadJson(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
