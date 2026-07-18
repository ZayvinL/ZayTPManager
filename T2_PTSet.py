# -*- coding: UTF-8 -*-
# 路径设定
import os
import nuke
import nukescripts
import T2_RWJson as RWJ

    
# 本地路径
def local_path_get():
    currentPath = os.path.dirname(os.path.abspath(__file__)) + "/"
    currentPath = currentPath.replace(os.sep,"/")
    return currentPath

    
    
    