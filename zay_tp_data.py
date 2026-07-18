# -*- coding: utf-8 -*-
"""ZayTPManager 数据层 - 纯文件系统操作, 不依赖 nuke / Qt

数据结构:
    templateWork/<项目>/<条目>/cover.*           条目封面图 (可选)
    templateWork/<项目>/<条目>/v0001/tlenuke.nk  节点文件
    templateWork/<项目>/<条目>/v0001/preview.*   版本图片 (可选)
    templateWork/<项目>/<条目>/v0001/info.json   版本记录

info.json 内部只存本目录内的文件名, 对外地址一律是相对数据根的正斜杠路径,
整棵数据树可在不同系统/用户间整体搬移。
"""

import getpass
import os
import platform
import re
import shutil
from datetime import datetime

import json_io as RWJ
import paths

VERSION_RE = re.compile(r"^v(\d{4})$")
IMAGE_EXTS = (".png", ".jpg", ".jpeg", ".gif")
NK_FILE = "tlenuke.nk"
INFO_FILE = "info.json"
COVER_NAME = "cover"
PREVIEW_NAME = "preview"
INVALID_CHARS = set('\\/:*?"<>|')


def name_ok(name):
    """项目/条目名校验: 非空, 不以点开头, 不含各系统的非法路径字符"""
    name = name.strip()
    if not name or name.startswith("."):
        return False
    return not any(c in INVALID_CHARS for c in name)


def _list_dirs(path):
    if not os.path.isdir(path):
        return []
    return [i for i in os.listdir(path) if os.path.isdir(os.path.join(path, i))]


def list_projects():
    return sorted(_list_dirs(paths.data_root_get()))


def list_entries(project):
    if not project:
        return []
    return sorted(_list_dirs(paths.to_abs(project)))


def entry_dir(project, entry):
    return paths.to_abs(f"{project}/{entry}")


def version_dirs(project, entry):
    """返回 (版本号int, 目录名) 列表, 版本号降序"""
    out = []
    for dname in _list_dirs(entry_dir(project, entry)):
        m = VERSION_RE.match(dname)
        if m:
            out.append((int(m.group(1)), dname))
    out.sort(reverse=True)
    return out


def _read_info(vdir):
    info_pt = f"{vdir}/{INFO_FILE}"
    if os.path.exists(info_pt):
        try:
            return RWJ.ReadJson(info_pt)
        except (ValueError, OSError):
            pass
    return {}


def list_versions(project, entry):
    """返回版本记录列表 (降序)

    每条记录: version / num / note / date / user / nodenamelist
              dir_abs / nk_rel(相对数据根) / nk_abs / image_abs
    """
    records = []
    for num, dname in version_dirs(project, entry):
        vdir = f"{entry_dir(project, entry)}/{dname}"
        info = _read_info(vdir)
        nk_name = info.get("nk", NK_FILE)
        image_name = info.get("image", "")
        image_abs = f"{vdir}/{image_name}" if image_name else ""
        if image_abs and not os.path.exists(image_abs):
            image_abs = ""
        records.append({
            "version": info.get("version", dname),
            "num": num,
            "note": info.get("note", ""),
            "date": info.get("date", ""),
            "user": info.get("user", ""),
            "nodenamelist": info.get("nodenamelist", []),
            "dir_abs": vdir,
            "nk_rel": f"{project}/{entry}/{dname}/{nk_name}",
            "nk_abs": f"{vdir}/{nk_name}",
            "image_abs": image_abs,
        })
    return records


def next_version_dir(project, entry):
    """分配并创建下一个版本目录, 返回 (版本名, 目录绝对路径)

    多用户同时新建版本时 makedirs 会抢占失败, 自动 +1 重试。
    """
    nums = [n for n, _ in version_dirs(project, entry)]
    num = max(nums) + 1 if nums else 1
    for _ in range(50):
        vname = "v%04d" % num
        vdir = f"{entry_dir(project, entry)}/{vname}"
        try:
            os.makedirs(vdir)
        except FileExistsError:
            num += 1
            continue
        paths.ensure_writable(vdir)
        return vname, vdir
    raise RuntimeError("版本目录分配失败: 重试次数过多")


def write_version_info(vdir, version_name, nodenamelist, note=""):
    now = datetime.now()
    info = {
        "version": version_name,
        "note": note,
        "date": now.strftime("%Y-%m-%d"),
        "time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "user": getpass.getuser(),
        "platform": platform.system(),
        "nk": NK_FILE,
        "image": "",
        "nodenamelist": list(nodenamelist),
    }
    RWJ.WriteJson(f"{vdir}/{INFO_FILE}", info)
    return info


def update_version_note(vdir, note):
    info = _read_info(vdir)
    info["note"] = note
    RWJ.WriteJson(f"{vdir}/{INFO_FILE}", info)


def clear_images(dst_dir, base_name):
    """清掉同名不同扩展名的旧图, 避免替换图片后残留"""
    for e in IMAGE_EXTS:
        old = os.path.join(dst_dir, base_name + e)
        if os.path.exists(old):
            os.remove(old)


def copy_image(src, dst_dir, base_name):
    """复制图片文件到目标目录并统一命名, 返回新文件名"""
    ext = os.path.splitext(src)[1].lower()
    if ext not in IMAGE_EXTS:
        raise ValueError(f"不支持的图片格式: {ext}")
    clear_images(dst_dir, base_name)
    dst = f"{dst_dir}/{base_name}{ext}"
    shutil.copy2(src, dst)
    paths.ensure_writable(dst)
    return base_name + ext


def register_version_image(vdir, image_name):
    """把图片文件名记录进版本 info.json"""
    info = _read_info(vdir)
    info["image"] = image_name
    RWJ.WriteJson(f"{vdir}/{INFO_FILE}", info)


def entry_cover_get(project, entry):
    """条目封面: cover.* 优先, 缺失回退最新版本的图片, 再缺失返回空"""
    edir = entry_dir(project, entry)
    for e in IMAGE_EXTS:
        pt = f"{edir}/{COVER_NAME}{e}"
        if os.path.exists(pt):
            return pt
    for rec in list_versions(project, entry):
        if rec["image_abs"]:
            return rec["image_abs"]
    return ""


def add_project(name):
    pt = paths.to_abs(name)
    if os.path.exists(pt):
        return False
    os.makedirs(pt)
    paths.ensure_writable(pt)
    return True


def add_entry(project, name):
    pt = f"{paths.to_abs(project)}/{name}"
    if os.path.exists(pt):
        return False
    os.makedirs(pt)
    paths.ensure_writable(pt)
    return True


def delete_path(path):
    try:
        shutil.rmtree(path)
    except OSError as e:
        print(f"删除失败: {e}")
        return False
    return not os.path.exists(path)
