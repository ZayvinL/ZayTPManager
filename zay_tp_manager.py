# -*- coding: utf-8 -*-
# ZayTPManager - Nuke 模版管理面板
# Make : Zayvin
# QQ : 971346144
import os

import nuke
import nukescripts

import paths
import zay_tp_data as TPD
from qt_imports import (
    Qt, QUrl, QSize, QEvent,
    QApplication, QMainWindow, QWidget, QSplitter, QVBoxLayout, QHBoxLayout,
    QComboBox, QLineEdit, QPushButton, QCheckBox, QLabel,
    QListWidget, QListWidgetItem,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView,
    QMenu, QAction, QInputDialog, QMessageBox, QTextBrowser,
    QDesktopServices, QPixmap, QMovie,
    exec_dialog,
)

THUMB_W = 120      # 缩略图宽
THUMB_H = 80       # 缩略图高
NOTE_MIN_W = 450   # 版本说明列最小宽度


class ZayTPManagerPanel(QMainWindow):

    def __init__(self, parent=None):
        super(ZayTPManagerPanel, self).__init__(parent)
        self.setWindowTitle("ZayTPManager 模版管理  Made: Mr.Cheese QQ: 971346144")
        self.setUI_fun()
        self.resize(1200, 800)

    def setUI_fun(self):
        self._loading_table = False

        # --- 顶部: 项目管理 / 数据地址 / 刷新
        self.xiangmuming = QComboBox()
        self.xiangmuming.currentIndexChanged.connect(self.refresh_other_info)
        self.addpro = QPushButton("添加项目")
        self.addpro.clicked.connect(self.addpro_fun)
        self.opendata = QPushButton("数据地址")
        self.opendata.clicked.connect(self.opendata_fun)
        self.refall = QPushButton("刷新界面")
        self.refall.clicked.connect(self.refresh_info)
        self.helpbtn = QPushButton("使用说明")
        self.helpbtn.clicked.connect(self.help_fun)

        # --- 搜索 / 图文切换
        self.search_lined = QLineEdit("")
        self.search_lined.setPlaceholderText("搜索:")
        self.search_lined.textChanged.connect(self.refresh_other_info)
        self.show_image_cb = QCheckBox("显示图片")
        self.show_image_cb.toggled.connect(self.refresh_entry_info)

        # --- 条目列表 (从上到下)
        self.entry_list = QListWidget()
        self.entry_list.currentItemChanged.connect(self.refresh_version_info)
        self.entry_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.entry_list.customContextMenuRequested.connect(self.entry_menu_fun)

        self.addtiaomu = QPushButton("添加条目")
        self.addtiaomu.clicked.connect(self.addtiaomu_fun)
        self.deltiaomu = QPushButton("删除条目")
        self.deltiaomu.clicked.connect(self.deltiaomu_fun)

        # --- 版本表格: 版本 / 图片 / 说明 / 日期 / 相对地址
        self.version_table = QTableWidget()
        self.version_table.setColumnCount(5)
        self.version_table.setHorizontalHeaderLabels(
            ["版本", "图片", "版本说明", "版本日期", "相对地址"])
        self.version_table.verticalHeader().setVisible(False)
        self.version_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.version_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.version_table.setContextMenuPolicy(Qt.CustomContextMenu)
        self.version_table.customContextMenuRequested.connect(self.version_menu_fun)
        self.version_table.itemChanged.connect(self.note_changed_fun)
        self.version_table.cellDoubleClicked.connect(self.cell_double_fun)
        header = self.version_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.Fixed)
        # 说明列手动拉伸: 占满剩余空间且不小于 NOTE_MIN_W
        header.setSectionResizeMode(2, QHeaderView.Interactive)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.Interactive)
        self.version_table.setColumnWidth(1, THUMB_W + 10)
        self.version_table.setColumnWidth(4, 280)
        header.sectionResized.connect(self.section_resized_fun)
        self.version_table.installEventFilter(self)

        # --- 布局
        top_lay = QHBoxLayout()
        top_lay.addWidget(self.xiangmuming, 1)
        top_lay.addWidget(self.addpro)
        top_lay.addWidget(self.opendata)
        top_lay.addWidget(self.refall)
        top_lay.addWidget(self.helpbtn)

        search_lay = QHBoxLayout()
        search_lay.addWidget(self.search_lined, 1)
        search_lay.addWidget(self.show_image_cb)

        entry_btn_lay = QHBoxLayout()
        entry_btn_lay.addWidget(self.addtiaomu)
        entry_btn_lay.addWidget(self.deltiaomu)

        left_lay = QVBoxLayout()
        left_lay.setContentsMargins(0, 0, 0, 0)
        left_lay.addWidget(self.entry_list)
        left_lay.addLayout(entry_btn_lay)
        left_widget = QWidget()
        left_widget.setLayout(left_lay)

        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(left_widget)
        self.splitter.addWidget(self.version_table)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 3)

        master_lay = QVBoxLayout()
        master_lay.setContentsMargins(4, 4, 4, 4)
        master_lay.addLayout(top_lay)
        master_lay.addLayout(search_lay)
        master_lay.addWidget(self.splitter, 1)

        central = QWidget()
        central.setLayout(master_lay)
        self.setCentralWidget(central)

        self.refresh_info()

        self.setStyleSheet("""
            QWidget{
                font-size: 25px;
            }
        """)

    # ------------------------------------------------------------------ 当前选择
    def current_project(self):
        return self.xiangmuming.currentText()

    def current_entry(self):
        item = self.entry_list.currentItem()
        if item:
            return item.data(Qt.UserRole)
        return None

    def row_version_dir(self, row):
        item = self.version_table.item(row, 0)
        if item:
            return item.data(Qt.UserRole)
        return None

    # ------------------------------------------------------------------ 刷新
    def refresh_info(self):
        # 刷新界面
        self.refresh_pro_info()
        self.refresh_other_info()

    def refresh_pro_info(self):
        # 刷新项目下拉, 尽量保持当前选择
        cur = self.xiangmuming.currentText()
        self.xiangmuming.blockSignals(True)
        self.xiangmuming.clear()
        pros = TPD.list_projects()
        self.xiangmuming.addItems(pros)
        if cur in pros:
            self.xiangmuming.setCurrentIndex(pros.index(cur))
        self.xiangmuming.blockSignals(False)

    def refresh_other_info(self, *args):
        self.refresh_entry_info()
        self.refresh_version_info()

    def refresh_entry_info(self, *args):
        # 刷新条目列表 (文字/图片两种模式)
        cur_entry = self.current_entry()
        pro = self.current_project()
        self.entry_list.blockSignals(True)
        self.entry_list.clear()

        entries = TPD.list_entries(pro) if pro else []
        key = self.search_lined.text().strip().lower()
        if key:
            entries = [i for i in entries if key in i.lower()]

        show_img = self.show_image_cb.isChecked()
        for name in entries:
            item = QListWidgetItem()
            item.setData(Qt.UserRole, name)
            if show_img:
                self.entry_list.addItem(item)
                widget = self.entry_item_widget(pro, name)
                item.setSizeHint(widget.sizeHint())
                self.entry_list.setItemWidget(item, widget)
            else:
                item.setText(name)
                self.entry_list.addItem(item)
        self.entry_list.blockSignals(False)

        # 尽量恢复之前选中的条目
        if cur_entry:
            for i in range(self.entry_list.count()):
                if self.entry_list.item(i).data(Qt.UserRole) == cur_entry:
                    self.entry_list.setCurrentRow(i)
                    break

    def entry_item_widget(self, project, name):
        # 图片模式下的条目控件: 封面图 + 名字
        w = QWidget()
        lay = QHBoxLayout(w)
        lay.setContentsMargins(4, 4, 4, 4)
        img_label = QLabel()
        img_label.setFixedSize(THUMB_W, THUMB_H)
        img_label.setAlignment(Qt.AlignCenter)
        cover = TPD.entry_cover_get(project, name)
        if cover:
            self.set_image_label(img_label, cover)
        else:
            img_label.setText("无图")
        lay.addWidget(img_label)
        lay.addWidget(QLabel(name), 1)
        return w

    def image_tooltip(self, image_path, max_size=800):
        """悬浮提示里放大展示图片, 长边统一缩放到 max_size (gif 显示首帧)"""
        pix = QPixmap(image_path)
        if pix.isNull():
            return ""
        scale = min(max_size / pix.width(), max_size / pix.height())
        tw = max(1, int(pix.width() * scale))
        th = max(1, int(pix.height() * scale))
        return f'<img src="{image_path}" width="{tw}" height="{th}">'

    def set_image_label(self, label, image_path, w=THUMB_W, h=THUMB_H):
        # gif 用 QMovie 播放动画, 其余用缩放后的 QPixmap
        if image_path.lower().endswith(".gif"):
            movie = QMovie(image_path)
            movie.setParent(label)
            movie.setScaledSize(QSize(w, h))
            label.setMovie(movie)
            movie.start()
            label.setToolTip(self.image_tooltip(image_path))
        else:
            pix = QPixmap(image_path)
            if pix.isNull():
                label.setText("图片无效")
            else:
                label.setPixmap(pix.scaled(
                    w, h, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                label.setToolTip(self.image_tooltip(image_path))

    def refresh_version_info(self, *args):
        # 刷新版本表格 (版本号降序)
        self._loading_table = True
        self.version_table.setRowCount(0)
        pro = self.current_project()
        entry = self.current_entry()
        if not (pro and entry):
            self._loading_table = False
            return

        records = TPD.list_versions(pro, entry)
        self.version_table.setRowCount(len(records))
        for row, rec in enumerate(records):
            self.version_table.setRowHeight(row, THUMB_H + 8)

            ver_item = QTableWidgetItem(rec["version"])
            ver_item.setFlags(ver_item.flags() & ~Qt.ItemIsEditable)
            ver_item.setData(Qt.UserRole, rec["dir_abs"])
            tipv = f"创建用户: {rec['user']}\n节点列表:\n" + "\n".join(rec["nodenamelist"])
            ver_item.setToolTip(tipv)
            self.version_table.setItem(row, 0, ver_item)

            img_label = QLabel()
            img_label.setAlignment(Qt.AlignCenter)
            if rec["image_abs"]:
                self.set_image_label(img_label, rec["image_abs"])
            else:
                img_label.setText("双击粘贴")
            self.version_table.setCellWidget(row, 1, img_label)

            note_item = QTableWidgetItem(rec["note"])
            note_item.setToolTip(rec["note"])
            self.version_table.setItem(row, 2, note_item)

            date_item = QTableWidgetItem(rec["date"])
            date_item.setFlags(date_item.flags() & ~Qt.ItemIsEditable)
            self.version_table.setItem(row, 3, date_item)

            path_item = QTableWidgetItem(rec["nk_rel"])
            path_item.setFlags(path_item.flags() & ~Qt.ItemIsEditable)
            path_item.setToolTip(rec["nk_abs"])
            self.version_table.setItem(row, 4, path_item)
        self._loading_table = False
        self.fit_note_column()

    def fit_note_column(self):
        # 说明列占满剩余空间, 且不小于最小宽度 (不够时出横向滚动条)
        vp = self.version_table.viewport().width()
        others = sum(self.version_table.columnWidth(c) for c in (0, 1, 3, 4))
        self.version_table.setColumnWidth(2, max(NOTE_MIN_W, vp - others))

    def section_resized_fun(self, idx, *args):
        # 说明列自身的 setColumnWidth 也会触发本信号, 跳过避免递归
        if idx != 2:
            self.fit_note_column()

    def eventFilter(self, obj, event):
        if obj is self.version_table and event.type() == QEvent.Resize:
            self.fit_note_column()
        return super(ZayTPManagerPanel, self).eventFilter(obj, event)

    # ------------------------------------------------------------------ 条目操作
    def entry_menu_fun(self, pos):
        item = self.entry_list.itemAt(pos)
        if not item:
            return
        entry = item.data(Qt.UserRole)
        menu = QMenu(self)

        add_action = QAction("添加nuke节点", self)
        add_action.triggered.connect(lambda: self.addnk_fun(entry))
        menu.addAction(add_action)

        cover_action = QAction("粘贴条目图片", self)
        cover_action.triggered.connect(lambda: self.set_cover_fun(entry))
        menu.addAction(cover_action)

        menu.popup(self.entry_list.viewport().mapToGlobal(pos))

    def addnk_fun(self, entry=None):
        # 选中的 nuke 节点存为该条目的新版本
        pro = self.current_project()
        entry = entry or self.current_entry()
        if not pro:
            self.information("没有项目")
            return
        if not entry:
            self.information("没有选中条目")
            return
        nds = nuke.selectedNodes()
        if not nds:
            self.information("没有选中节点")
            return

        vname, vdir = TPD.next_version_dir(pro, entry)
        nk_pt = f"{vdir}/{TPD.NK_FILE}"
        try:
            nuke.nodeCopy(nk_pt)
        except RuntimeError:
            TPD.delete_path(vdir)
            self.information("复制节点失败")
            return
        paths.ensure_writable(nk_pt)
        TPD.write_version_info(vdir, vname, [n.name() for n in nds])
        self.refresh_version_info()

    def clipboard_write_image(self, dst_dir, base_name):
        """剪贴板图片落盘: 优先复制的图片文件(gif 可保留动画), 其次截图/位图存为 png

        返回写入的文件名, 剪贴板没有图片时返回空字符串
        """
        cb = QApplication.clipboard()
        md = cb.mimeData()
        if md.hasUrls():
            for url in md.urls():
                pt = url.toLocalFile()
                if (pt and os.path.exists(pt)
                        and os.path.splitext(pt)[1].lower() in TPD.IMAGE_EXTS):
                    return TPD.copy_image(pt, dst_dir, base_name)
        img = cb.image()
        if not img.isNull():
            TPD.clear_images(dst_dir, base_name)
            dst = f"{dst_dir}/{base_name}.png"
            img.save(dst, "PNG")
            paths.ensure_writable(dst)
            return f"{base_name}.png"
        return ""

    def set_cover_fun(self, entry):
        # 从剪贴板粘贴条目封面
        pro = self.current_project()
        if not pro:
            return
        image_name = self.clipboard_write_image(TPD.entry_dir(pro, entry), TPD.COVER_NAME)
        if not image_name:
            self.information("剪贴板中没有图片内容\n(可先截图, 或复制一个图片文件)")
            return
        self.refresh_entry_info()

    def addtiaomu_fun(self):
        # 添加条目
        pro = self.current_project()
        if not pro:
            self.information("没有项目")
            return
        ok, text = self.lineInput("这是什么？")
        if not ok:
            return
        text = text.strip()
        if not TPD.name_ok(text):
            self.information('名称无效 (不能为空或包含 \\ / : * ? " < > |)')
            return
        TPD.add_entry(pro, text)
        self.refresh_entry_info()

    def deltiaomu_fun(self):
        # 删除条目
        pro = self.current_project()
        entry = self.current_entry()
        if not (pro and entry):
            self.information("没有选中条目")
            return
        if self.question("删除这个条目？", entry):
            if TPD.delete_path(TPD.entry_dir(pro, entry)):
                self.information("删除成功")
            else:
                self.information("删除失败 (可能无权限)")
            self.refresh_other_info()

    # ------------------------------------------------------------------ 版本操作
    def version_menu_fun(self, pos):
        row = self.version_table.rowAt(pos.y())
        if row < 0:
            return
        menu = QMenu(self)

        imp_action = QAction("导入nuke节点", self)
        imp_action.triggered.connect(lambda: self.import_row_fun(row))
        menu.addAction(imp_action)

        copy_action = QAction("复制绝对路径", self)
        copy_action.triggered.connect(lambda: self.copy_abs_path_fun(row))
        menu.addAction(copy_action)

        img_action = QAction("粘贴图片", self)
        img_action.triggered.connect(lambda: self.paste_image_fun(row))
        menu.addAction(img_action)

        note_action = QAction("编辑说明", self)
        note_action.triggered.connect(lambda: self.edit_note_fun(row))
        menu.addAction(note_action)

        del_action = QAction("删除选中版本", self)
        del_action.triggered.connect(self.delete_versions_fun)
        menu.addAction(del_action)

        menu.popup(self.version_table.viewport().mapToGlobal(pos))

    def cell_double_fun(self, row, col):
        if col == 0:
            self.import_row_fun(row)
        elif col == 1:
            self.paste_image_fun(row)

    def import_row_fun(self, row):
        # 通过相对地址还原绝对路径后导入节点
        nk_abs = self.row_abs_path(row)
        if not nk_abs:
            return
        if os.path.exists(nk_abs):
            nuke.nodePaste(nk_abs)
        else:
            self.information(f"文件不存在:\n{nk_abs}")

    def row_abs_path(self, row):
        path_item = self.version_table.item(row, 4)
        if path_item:
            return paths.to_abs(path_item.text())
        return ""

    def copy_abs_path_fun(self, row):
        # 绝对路径写入系统剪贴板, 方便找到 nk 文件
        nk_abs = self.row_abs_path(row)
        if nk_abs:
            QApplication.clipboard().setText(nk_abs)

    def paste_image_fun(self, row):
        # 从剪贴板粘贴版本图片
        vdir = self.row_version_dir(row)
        if not vdir:
            return
        image_name = self.clipboard_write_image(vdir, TPD.PREVIEW_NAME)
        if not image_name:
            self.information("剪贴板中没有图片内容\n(可先截图, 或复制一个图片文件)")
            return
        TPD.register_version_image(vdir, image_name)
        self.refresh_version_info()
        if self.show_image_cb.isChecked():
            self.refresh_entry_info()

    def edit_note_fun(self, row):
        # 多行对话框编辑版本说明
        vdir = self.row_version_dir(row)
        if not vdir:
            return
        note_item = self.version_table.item(row, 2)
        old = note_item.text() if note_item else ""
        text, ok = QInputDialog.getMultiLineText(self, "版本说明", "说明:", old)
        if ok:
            TPD.update_version_note(vdir, text)
            self.refresh_version_info()

    def note_changed_fun(self, item):
        # 说明列就地编辑后写回 info.json
        if self._loading_table or item.column() != 2:
            return
        vdir = self.row_version_dir(item.row())
        if vdir:
            TPD.update_version_note(vdir, item.text())

    def delete_versions_fun(self):
        # 删除表格中选中的行 (支持多选)
        rows = sorted({i.row() for i in self.version_table.selectedIndexes()},
                      reverse=True)
        if not rows:
            self.information("没有选中版本")
            return
        names = [self.version_table.item(r, 0).text() for r in rows]
        if not self.question("删除选中版本？", "\n".join(names)):
            return
        fails = []
        for r in rows:
            vdir = self.row_version_dir(r)
            if vdir and not TPD.delete_path(vdir):
                fails.append(vdir)
        if fails:
            self.information("部分删除失败 (可能无权限):\n" + "\n".join(fails))
        self.refresh_version_info()
        if self.show_image_cb.isChecked():
            self.refresh_entry_info()

    # ------------------------------------------------------------------ 项目/通用
    def addpro_fun(self):
        # 添加项目
        ok, text = self.lineInput("项目名")
        if not ok:
            return
        text = text.strip()
        if not TPD.name_ok(text):
            self.information('名称无效 (不能为空或包含 \\ / : * ? " < > |)')
            return
        TPD.add_project(text)
        self.refresh_pro_info()
        self.xiangmuming.setCurrentText(text)
        self.refresh_other_info()

    def opendata_fun(self):
        # 打开数据地址
        QDesktopServices.openUrl(QUrl.fromLocalFile(paths.data_root_get()))

    def help_fun(self):
        # 说明页面: 读取工具目录下的 README.md
        md_pt = paths.local_path_get() + "README.md"
        if not os.path.exists(md_pt):
            self.information(f"说明文件不存在:\n{md_pt}")
            return
        with open(md_pt, "r", encoding="utf-8") as f:
            text = f.read()
        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        if hasattr(browser, "setMarkdown"):
            browser.setMarkdown(text)
        else:
            # Nuke13 (Qt 5.12) 不支持 markdown 渲染, 回退纯文本
            browser.setPlainText(text)
        self.help_win = QMainWindow(self)
        self.help_win.setWindowTitle("ZayTPManager 使用说明")
        self.help_win.setCentralWidget(browser)
        self.help_win.resize(1000, 800)
        self.help_win.show()

    def information(self, messagete):
        info = QMessageBox(self)
        info.setIcon(QMessageBox.Information)
        info.setWindowTitle("信息")
        info.setText(f"{messagete}")
        exec_dialog(info)

    def question(self, askinfo, curtext):
        ret = QMessageBox.question(self, f"{askinfo}", f"{curtext}")
        return ret == QMessageBox.Yes

    def lineInput(self, tile):
        text, ok = QInputDialog.getText(self, "输入", f"{tile}", QLineEdit.Normal, "")
        return ok, text


def runshow():
    # 浮动窗口方式打开
    global tpwork
    tpwork = ZayTPManagerPanel()
    tpwork.show()


nukepget = nukescripts.panels.registerWidgetAsPanel(
    "zay_tp_manager.ZayTPManagerPanel", "ZayTPManager", "ZayTPManager.MainPanel", True)


def run_show_funa():
    if nuke.getPaneFor("ZayTPManager"):
        pass
    else:
        pane = nuke.getPaneFor("Properties.1")
        nukepget.addToPane(pane)
