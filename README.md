# ZayTPManager 使用说明

Nuke 节点模版管理面板，把常用节点组合按 **项目 / 条目 / 版本** 三级归档，支持图片预览（含 GIF 动画）、版本说明、搜索过滤。数据以相对路径存储，可整体搬移，适配 Windows / Linux / macOS 多系统及多用户共享。

A Nuke template manager that organizes node groups by Project / Item / Version with image preview (GIF supported), version notes, and search. Relative-path storage makes the data portable across Windows / Linux / macOS and shareable among multiple users.

- 环境要求 / Requirements：**Nuke 13+** (Python 3, PySide2 5.12+ or PySide6, bundled with Nuke)
- 作者 / Author：Zayvin  QQ: 971346144
- 仓库 / Repos：[GitHub](https://github.com/ZayvinL/ZayTPManager) ｜ [Gitee](https://gitee.com/q-wuan90/ZayTPManager)

---

## 一、部署安装 / Installation

### 1. 随 ZaneTpack 使用 / With ZaneTpack

工具目录位于 `~/.nuke/ZaneTpack/ZayTPManager/`，
由 `ZaneTpack/init.py` 中的这行代码加载：

The tool lives under `~/.nuke/ZaneTpack/ZayTPManager/` and is loaded by this line in `ZaneTpack/init.py`:

```python
nuke.pluginAddPath("ZayTPManager")
```

### 2. 独立部署 / Standalone

把整个 `ZayTPManager` 文件夹放到任意位置，然后在 `~/.nuke/init.py` 里加入：

Put the `ZayTPManager` folder anywhere, then add this line to `~/.nuke/init.py`:

```python
nuke.pluginAddPath(r"D:/your/path/ZayTPManager")
```

重启 Nuke 后，菜单 **Z > pipline > ZayTPManager** 即可打开面板（面板会停靠到 Properties 面板所在区域）。

After restarting Nuke, open the panel via **Z > pipline > ZayTPManager** (it docks to the Properties panel area).

### 3. 多用户共享部署 / Multi-user Sharing

两种方案任选 / Two approaches:

| 方案 / Approach           | 做法 / How                                                                                                                                      |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------- |
| 共享整个工具 / Share the tool | 把工具文件夹放到网络共享盘，每个用户的 `init.py` 中 `pluginAddPath` 指向该共享路径。Place the tool folder on a network share and point each user's `pluginAddPath` to it. |
| 只共享数据 / Share data only | 工具装在各自本机，把数据根目录改到共享盘（见下方「配置方案」）。Install the tool locally on each machine, change the data root to a network share (see Configuration below).  |

多用户注意：工具写文件时会尽量放开权限（POSIX 下 chmod 777/666），json 采用
原子写入，多人同时新建版本时版本号会自动避让，不会互相覆盖。

Multi-user note: the tool uses permissive permissions (POSIX chmod 777/666) and atomic JSON writes. Concurrent version creation auto-avoids collisions.

---

## 二、配置方案 / Configuration

### 1. 数据根目录 / Data Root —— `paths.py` 的 `data_root_get()`

默认数据存在工具目录下的 `templateWork/`。要把数据迁到共享盘，只改这一个函数：

By default data is stored under `templateWork/` inside the tool directory. To move data to a network share, only change this function:

```python
def data_root_get():
    # root = local_path_get() + "templateWork/"          # 默认 / Default: under tool dir
    root = "//server/share/nuke_tp/templateWork/"        # 共享盘 / Network share (forward slash, trailing /)
    if not os.path.exists(root):
        os.makedirs(root)
        ensure_writable(root)
    return root
```

数据内部全部用相对路径记录，整个 `templateWork/` 文件夹可以直接拷贝 / 搬移到任何机器、任何系统继续使用。

All paths inside the data are relative, so the entire `templateWork/` folder can be copied or moved to any machine or OS.

### 2. 其他可调项 / Other Configurable Items

| 位置 / Location                                            | 内容 / What                                                                               |
| -------------------------------------------------------- | --------------------------------------------------------------------------------------- |
| `paths.py` → `local_path_get()`                          | 工具自身目录（一般不需要改）。Tool directory (usually no need to change).                              |
| `zay_tp_manager.py` top: `THUMB_W / THUMB_H`             | 缩略图尺寸（默认 120x80）。Thumbnail size (default 120x80).                                       |
| `zay_tp_manager.py` top: `NOTE_MIN_W`                    | 版本说明列最小宽度（默认 450）。Note column min width (default 450).                                  |
| `zay_tp_manager.py` → `image_tooltip(max_size=800)`      | 悬浮放大图长边尺寸。Tooltip image max dimension.                                                  |
| `zay_tp_manager.py` bottom: `setStyleSheet`              | 界面字体大小（默认 25px）。UI font size (default 25px).                                            |
| `zay_tp_manager.py` bottom: `registerWidgetAsPanel(...)` | 面板注册名 / ID。Panel registration name / ID.                                                |
| `zay_tp_data.py` top: `NK_FILE / IMAGE_EXTS` etc.        | 节点文件名、支持的图片扩展名。Node file name, supported image extensions.                              |
| `menu.py`                                                | 菜单位置（默认 Z > pipline > ZayTPManager）。Menu location (default Z > pipline > ZayTPManager). |

### 3. 模块说明 / Module Overview

| 文件 / File                    | 职责 / Role                                                                           |
| ---------------------------- | ----------------------------------------------------------------------------------- |
| `zayTPManager_qt_imports.py` | 统一管理 Qt 导入，自动适配 PySide6 / PySide2。Shared Qt imports, auto-adapts PySide6 / PySide2. |
| `paths.py`                   | 路径与权限：工具目录、数据根目录、相对/绝对路径换算。Paths & permissions.                                     |
| `json_io.py`                 | json 读写（utf-8、原子写入）。JSON read/write (UTF-8, atomic writes).                         |
| `zay_tp_data.py`             | 数据层：项目/条目/版本的扫描、创建、记录、删除（不依赖 nuke/Qt）。Data layer (no nuke/Qt dependency).           |
| `zay_tp_manager.py`          | 主面板界面与交互。Main panel UI & interaction.                                               |
| `menu.py`                    | Nuke 菜单注册。Nuke menu registration.                                                   |

---

## 三、数据结构 / Data Structure

```
templateWork/                     # 数据根目录 / Data root
└── ProjectName/                  # 项目名 / Project
    └── ItemName/                 # 条目名 / Item
        ├── cover.png|.gif        # 条目封面图（可选）/ Cover image (optional)
        └── v0001/                # 版本目录 / Version dir, v + 4 digits, auto-increment
            ├── tlenuke.nk        # Nuke 节点文件 / Saved Nuke nodes
            ├── preview.png|.gif  # 版本图片（可选）/ Preview image (optional)
            └── info.json         # 版本记录 / Version metadata
```

`info.json` 记录内容：版本号、说明、日期时间、创建用户、系统平台、节点名称列表、图片文件名。
文件内只存文件名，不存绝对路径，因此数据可整体搬移。

`info.json` stores: version number, note, date/time, creator, platform, node name list, image file name. Only file names are stored (no absolute paths), so the data is fully portable.

---

## 四、使用方法 / Usage

### 顶部按钮 / Top Buttons

| 按钮 / Button              | 功能 / Purpose                                                                            |
| ------------------------ | --------------------------------------------------------------------------------------- |
| 项目下拉框 / Project dropdown | 切换当前项目。Switch current project.                                                          |
| 添加项目 / Add Project       | 新建项目（名称不能包含 `\ / : * ? " < > \|`）。Create project (illegal chars: `\ / : * ? " < > \|`). |
| 数据地址 / Data Folder       | 在系统文件管理器中打开数据根目录。Open data root in file manager.                                        |
| 刷新界面 / Refresh           | 重新扫描磁盘数据（他人新增内容后点这里）。Re-scan disk (use after others add content).                       |
| 使用说明 / Help              | 打开本说明页面。Open this help page.                                                            |

### 搜索与条目列表（左侧）/ Search & Item List (Left)

- **搜索框 / Search**：按关键字过滤条目（不区分大小写）。Filter items by keyword (case-insensitive).
- **显示图片 / Show Images**：勾选后条目以「封面图 + 名字」显示，GIF 封面会播放动画；没设置封面时自动用最新版本的图片，都没有则显示"无图"。When checked, items show cover image + name, GIF covers animate. Falls back to latest version image, then "No Image".
- **添加条目 / 删除条目 / Add & Delete Item**：底部按钮（删除会连同其所有版本一起删除，需确认）。Bottom buttons (delete removes all versions, confirmation required).
- **条目右键菜单 / Item Right-click Menu**：
  - `添加nuke节点 / Add Nuke Nodes`：把 Nuke 里当前选中的节点存为该条目的新版本（版本号自动 +1）。Save selected nodes as a new version (auto-increment).
  - `粘贴条目图片 / Paste Item Image`：从剪贴板设置封面。Set cover image from clipboard.

### 版本表格（右侧，版本号从高到低）/ Version Table (Right, Newest First)

| 列 / Column   | 说明 / Description                                                                                                       |
| ------------ | ---------------------------------------------------------------------------------------------------------------------- |
| 版本 / Version | v0001 格式；悬浮显示创建用户和节点列表；**双击 = 导入节点**。v0001 format; tooltip shows creator & node list; **double-click = import nodes**. |
| 图片 / Image   | 缩略图，GIF 播放动画；悬浮放大展示；**双击 = 粘贴图片**。Thumbnail, GIF animates; enlarge on hover; **double-click = paste image**.           |
| 版本说明 / Note  | **双击可直接编辑**，悬浮显示全文。**Double-click to edit**, hover to see full text.                                                   |
| 版本日期 / Date  | 创建日期。Creation date.                                                                                                    |
| 相对地址 / Path  | 相对数据根的路径；悬浮显示绝对路径。Path relative to data root; tooltip shows absolute path.                                             |

- **版本右键菜单 / Version Right-click Menu**：
  - `导入nuke节点 / Import Nodes`：把该版本的节点粘贴进当前 Nuke 工程。Paste nodes into current Nuke script.
  - `复制绝对路径 / Copy Absolute Path`：把 nk 文件的绝对路径复制到系统剪贴板。Copy the .nk file's absolute path to clipboard.
  - `粘贴图片 / Paste Image`：从剪贴板设置该版本的图片。Set version image from clipboard.
  - `编辑说明 / Edit Note`：多行对话框编辑版本说明。Multi-line dialog to edit the note.
  - `删除选中版本 / Delete Selected`：删除表格中选中的行（可 Ctrl / Shift 多选，需确认）。Delete selected rows (Ctrl/Shift multi-select, confirmation required).

### 粘贴图片的规则 / Image Paste Rules

从剪贴板读取，两种内容都支持 / Reads from clipboard, two formats supported：

1. **复制的图片文件 / Copied image files**（在文件管理器里对 png/jpg/jpeg/gif 文件 Ctrl+C）→ 直接拷贝文件，**GIF 保留动画**。Ctrl+C on image files in file manager → copies file directly, **GIF animation preserved**.
2. **截图 / 位图内容 / Screenshot / bitmap**（截图工具、网页图片复制等）→ 自动存为 png。Screenshot tools, web image copy, etc. → saved as PNG.

剪贴板里没有图片时会给出提示。Shows a message when no image is on clipboard.

### 推荐工作流 / Recommended Workflow

1. 添加项目（如 `项目A`）→ 添加条目（如 `合成模版`）。Add a project → add an item.
2. 在 Nuke 节点图中选中要保存的节点 → 条目右键 → `添加nuke节点`，生成 `v0001`。Select nodes in Nuke → right-click item → `Add Nuke Nodes`, creates `v0001`.
3. 截一张效果图 → 版本行双击图片列粘贴 → 双击说明列写用途。Take a screenshot → double-click image cell to paste → double-click note cell to describe.
4. 之后迭代同一条目，重复第 2 步生成 v0002、v0003…… Iterate by repeating step 2 to create v0002, v0003, etc.
5. 使用时双击版本号导入，或右键 `复制绝对路径` 找到 nk 文件。To use: double-click version to import, or right-click `Copy Absolute Path`.

---

## 五、常见问题 / FAQ

- **面板打不开 / 菜单里没有 / Panel won't open**：确认 `init.py` 里 `pluginAddPath` 路径正确，且 Nuke 版本 >= 13。Verify `pluginAddPath` in `init.py` is correct and Nuke >= 13.
- **Nuke 13 里说明页面没有排版 / Help page looks plain in Nuke 13**：Qt 5.12 不支持 markdown 渲染，会以纯文本显示，属正常现象。Qt 5.12 doesn't support markdown rendering — falls back to plain text, this is expected.
- **旧版工具的数据不显示 / Old data not showing**：旧格式（`0001_2025_04_23` 目录）不再识别，仅识别 `v0001` 格式；旧数据仍保留在磁盘上，可手动整理。Old format (`0001_2025_04_23` dirs) is no longer recognized — only `v0001` format is. Old data remains on disk and can be manually migrated.
- **别人新加的模版看不到 / Can't see others' new templates**：点「刷新界面」重新扫描。Click `Refresh` to re-scan.
- **GIF 悬浮放大时不动 / GIF tooltip doesn't animate**：悬浮大图显示的是首帧，缩略图处正常播放动画。The enlarged tooltip shows the first frame only; thumbnails animate normally.
- **同一 Nuke 环境有多份同名模块 / Duplicate module names**：模块已改名为 `zayTPManager_qt_imports.py` 以避免与 `sys.path` 上其他插件的 `qt_imports.py` 冲突。Module renamed to `zayTPManager_qt_imports.py` to avoid collisions with other plugins' `qt_imports.py` on `sys.path`.
- **数据备份 / Data backup**：`templateWork/` 不在 git 跟踪范围内，请自行定期备份该文件夹。`templateWork/` is not tracked by git — back it up regularly on your own.

---

## License / 许可

Copyright 2026 LIUXIAOBO (刘晓波).

Licensed under the Apache License, Version 2.0.
See [LICENSE](./LICENSE) for the full license text.
See [NOTICE](./NOTICE) for copyright attribution.
