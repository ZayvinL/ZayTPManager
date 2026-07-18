# ZayTPManager 使用说明

Nuke 节点模版管理面板，把常用节点组合按 **项目 / 条目 / 版本** 三级归档，支持图片预览（含 GIF 动画）、版本说明、搜索过滤。数据以相对路径存储，可整体搬移，适配 Windows / Linux / macOS 多系统及多用户共享。

A Nuke template manager that organizes node groups by Project / Item / Version with image preview (GIF supported), version notes, and search. Relative-path storage makes the data portable across Windows / Linux / macOS and shareable among multiple users.

- 环境要求 / Requirements：**Nuke 13+** (Python 3, PySide2 5.12+ or PySide6, bundled with Nuke)
- 作者 / Author：Zayvin  QQ: 971346144

---

## 一、部署安装

### 1. 随 ZaneTpack 使用（当前方式）

工具目录位于 `~/.nuke/ZaneTpack/ZayTPManager/`，
由 `ZaneTpack/init.py` 中的这行代码加载：

```python
nuke.pluginAddPath("ZayTPManager")
```

### 2. 独立部署

把整个 `ZayTPManager` 文件夹放到任意位置，然后在 `~/.nuke/init.py` 里加入：

```python
nuke.pluginAddPath(r"D:/你的路径/ZayTPManager")
```

重启 Nuke 后，菜单 **Z > pipline > ZayTPManager** 即可打开面板（面板会停靠到 Properties 面板所在区域）。

### 3. 多用户共享部署

两种方案任选：

| 方案 | 做法 |
|---|---|
| 共享整个工具 | 把工具文件夹放到网络共享盘，每个用户的 `init.py` 中 `pluginAddPath` 指向该共享路径 |
| 只共享数据 | 工具装在各自本机，把数据根目录改到共享盘（见下方「配置方案」） |

多用户注意：工具写文件时会尽量放开权限（POSIX 下 chmod 777/666），json 采用
原子写入，多人同时新建版本时版本号会自动避让，不会互相覆盖。

---

## 二、配置方案（修改哪些函数 / 常量）

### 1. 数据根目录 —— `paths.py` 的 `data_root_get()`

默认数据存在工具目录下的 `templateWork/`。要把数据迁到共享盘，只改这一个函数：

```python
def data_root_get():
    # root = local_path_get() + "templateWork/"          # 默认: 工具目录下
    root = "//server/share/nuke_tp/templateWork/"        # 改成: 网络共享盘 (正斜杠, 以 / 结尾)
    if not os.path.exists(root):
        os.makedirs(root)
        ensure_writable(root)
    return root
```

数据内部全部用相对路径记录，整个 `templateWork/` 文件夹可以直接拷贝 / 搬移到任何机器、任何系统继续使用。

### 2. 其他可调项

| 位置 | 内容 |
|---|---|
| `paths.py` → `local_path_get()` | 工具自身目录（一般不需要改） |
| `zay_tp_manager.py` 顶部 `THUMB_W / THUMB_H` | 缩略图尺寸（默认 120x80） |
| `zay_tp_manager.py` 顶部 `NOTE_MIN_W` | 版本说明列最小宽度（默认 450） |
| `zay_tp_manager.py` → `image_tooltip(max_size=800)` | 悬浮放大图长边尺寸 |
| `zay_tp_manager.py` 底部 `setStyleSheet` | 界面字体大小（默认 25px） |
| `zay_tp_manager.py` 底部 `registerWidgetAsPanel(...)` | 面板注册名 / ID |
| `zay_tp_data.py` 顶部 `NK_FILE / IMAGE_EXTS` 等 | 节点文件名、支持的图片扩展名 |
| `menu.py` | 菜单位置（默认 Z > pipline > ZayTPManager） |

### 3. 模块说明

| 文件 | 职责 |
|---|---|
| `zayTPManager_qt_imports.py` | 统一管理 Qt 导入，自动适配 PySide6 / PySide2 |
| `paths.py` | 路径与权限：工具目录、数据根目录、相对/绝对路径换算 |
| `json_io.py` | json 读写（utf-8、原子写入） |
| `zay_tp_data.py` | 数据层：项目/条目/版本的扫描、创建、记录、删除（不依赖 nuke/Qt） |
| `zay_tp_manager.py` | 主面板界面与交互 |
| `menu.py` | Nuke 菜单注册 |

---

## 三、数据结构

```
templateWork/                     # 数据根目录
└── 项目名/
    └── 条目名/
        ├── cover.png|.gif        # 条目封面图 (可选)
        └── v0001/                # 版本目录, v + 4位数字, 逐次递增
            ├── tlenuke.nk        # 保存的 nuke 节点
            ├── preview.png|.gif  # 版本图片 (可选)
            └── info.json         # 版本记录
```

`info.json` 记录内容：版本号、说明、日期时间、创建用户、系统平台、节点名称列表、图片文件名。
文件内只存文件名，不存绝对路径，因此数据可整体搬移。

---

## 四、使用方法

### 顶部按钮

| 按钮 | 功能 |
|---|---|
| 项目下拉框 | 切换当前项目 |
| 添加项目 | 新建项目（名称不能包含 `\ / : * ? " < > \|`） |
| 数据地址 | 在系统文件管理器中打开数据根目录 |
| 刷新界面 | 重新扫描磁盘数据（他人新增内容后点这里） |
| 使用说明 | 打开本说明页面 |

### 搜索与条目列表（左侧）

- **搜索框**：按关键字过滤条目（不区分大小写）
- **显示图片**：勾选后条目以「封面图 + 名字」显示，GIF 封面会播放动画；
  没设置封面时自动用最新版本的图片，都没有则显示"无图"
- **添加条目 / 删除条目**：底部按钮（删除会连同其所有版本一起删除，需确认）
- **条目右键菜单**：
  - `添加nuke节点`：把 Nuke 里当前选中的节点存为该条目的新版本（版本号自动 +1）
  - `粘贴条目图片`：从剪贴板设置封面

### 版本表格（右侧，版本号从高到低）

| 列 | 说明 |
|---|---|
| 版本 | v0001 格式；悬浮显示创建用户和节点列表；**双击 = 导入节点** |
| 图片 | 缩略图，GIF 播放动画；悬浮放大展示；**双击 = 粘贴图片** |
| 版本说明 | **双击可直接编辑**，悬浮显示全文 |
| 版本日期 | 创建日期 |
| 相对地址 | 相对数据根的路径；悬浮显示绝对路径 |

- **版本右键菜单**：
  - `导入nuke节点`：把该版本的节点粘贴进当前 Nuke 工程
  - `复制绝对路径`：把 nk 文件的绝对路径复制到系统剪贴板，方便定位文件
  - `粘贴图片`：从剪贴板设置该版本的图片
  - `编辑说明`：多行对话框编辑版本说明
  - `删除选中版本`：删除表格中选中的行（可 Ctrl / Shift 多选，需确认）

### 粘贴图片的规则

从剪贴板读取，两种内容都支持：

1. **复制的图片文件**（在文件管理器里对 png/jpg/jpeg/gif 文件 Ctrl+C）→ 直接拷贝文件，**GIF 保留动画**
2. **截图 / 位图内容**（截图工具、网页图片复制等）→ 自动存为 png

剪贴板里没有图片时会给出提示。

### 推荐工作流

1. 添加项目（如 `项目A`）→ 添加条目（如 `合成模版`）
2. 在 Nuke 节点图中选中要保存的节点 → 条目右键 → `添加nuke节点`，生成 `v0001`
3. 截一张效果图 → 版本行双击图片列粘贴 → 双击说明列写用途
4. 之后迭代同一条目，重复第 2 步生成 v0002、v0003……
5. 使用时双击版本号导入，或右键 `复制绝对路径` 找到 nk 文件

---

## 五、常见问题

- **面板打不开 / 菜单里没有**：确认 `init.py` 里 `pluginAddPath` 路径正确，且 Nuke 版本 >= 13
- **Nuke 13 里说明页面没有排版**：Qt 5.12 不支持 markdown 渲染，会以纯文本显示，属正常现象
- **旧版工具的数据不显示**：旧格式（`0001_2025_04_23` 目录）不再识别，仅识别 `v0001` 格式；旧数据仍保留在磁盘上，可手动整理
- **别人新加的模版看不到**：点「刷新界面」重新扫描
- **GIF 悬浮放大时不动**：悬浮大图显示的是首帧，缩略图处正常播放动画
- **同一 Nuke 环境有多份同名模块**：模块已改名为 `zayTPManager_qt_imports.py` 以避免与 `sys.path` 上其他插件的 `qt_imports.py` 冲突
- **数据备份**：`templateWork/` 不在 git 跟踪范围内，请自行定期备份该文件夹
