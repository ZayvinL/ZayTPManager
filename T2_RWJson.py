# -*- coding: UTF-8 -*-
# 读写 json 文件内容
import os
import json
import sys
import nuke
import nukescripts


if nuke.NUKE_VERSION_MAJOR < 13:
    stdi,stdo,stde=sys.stdin,sys.stdout,sys.stderr 
    reload(sys)    
    sys.stdin,sys.stdout,sys.stderr=stdi,stdo,stde 
    sys.setdefaultencoding('utf-8')



def WriteJson(path=None, dict_data={}):
    # Json write
    if nuke.NUKE_VERSION_MAJOR < 13:
        data = json.dumps(dict_data, ensure_ascii=False, sort_keys=False, indent=4)
        with open(path, "w") as f:
            f.write(data)
    else:
        Writedata = json.dumps(dict_data, ensure_ascii=False, sort_keys=True, indent=4)
        with open(path, "w", encoding='utf-8') as f:
            f.write(Writedata)

def ReadJson(path=None):
    # Json Read
    if nuke.NUKE_VERSION_MAJOR < 13:
        if os.path.exists(path):
            with open(path, 'r') as load_f:
                load_dict_lll = json.load(load_f, encoding='utf-8')
        return load_dict_lll
    else:
        with open(path, 'r', encoding='utf-8') as load_f:
            load_dict = json.load(load_f)
        return load_dict    