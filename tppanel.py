# -*- coding: utf-8 -*-
#Make : Mr-Cheese
#QQ : 971346144
import nuke
import nukescripts
import sys
import os
import json
import shutil
import os
from pathlib import Path

from datetime import datetime




import T2_RWJson as RWJ # 读写json
import T2_PTSet as PTS # 路径文件设定


if nuke.NUKE_VERSION_MAJOR < 11:
    from PySide.QtGui import *
    from PySide.QtCore import *
else:
    try:
        from PySide6.QtGui import *
        from PySide6.QtCore import *
        from PySide6.QtWidgets import *
    except:
        from PySide2.QtGui import *
        from PySide2.QtCore import *
        from PySide2.QtWidgets import *

if nuke.NUKE_VERSION_MAJOR < 13:
    stdi,stdo,stde=sys.stdin,sys.stdout,sys.stderr 
    reload(sys)    
    sys.stdin,sys.stdout,sys.stderr=stdi,stdo,stde 
    sys.setdefaultencoding('utf-8')
    
### ========================================================================================



class templateWork(QMainWindow):  # QDialog   QWidget

    def __init__(self, parent=None):
        super(templateWork, self).__init__(parent)
        # self.setWindowFlags(Qt.Tool|Qt.WindowStaysOnTopHint)
        
        self.wdsize = 1000
        self.hdsize = 800

        self.setUI_fun()
        self.resize(self.wdsize,self.hdsize)
        
        self.setWindowTitle("模版管理工具 Made: Mr.Cheese QQ: 971346144")
    
    
    def setUI_fun(self):
    
        self.search_lined = QLineEdit("") # 搜索项，搜索类别下的内容 # 多加一个在全部类别下的文件夹搜索all
        self.search_lined.setPlaceholderText("搜索:")
        self.search_lined.textChanged.connect(self.refresh_other_info)
    
        self.xiangmuming = QComboBox()
        self.xiangmuming.currentIndexChanged.connect(self.refresh_other_info)
        self.bianhao_list = QListWidget()
        self.bianhao_list.itemClicked.connect(self.refresh_version_info)
        self.banben_list = QListWidget()
        self.banben_list.itemClicked.connect(self.refresh_version_notename_info)
        self.banben_list.currentItemChanged.connect(self.refresh_version_notename_info)
        # 为QListWidget绑定右键菜单
        self.banben_list.setContextMenuPolicy(Qt.CustomContextMenu)
        self.banben_list.customContextMenuRequested.connect(self.show_right_click_menu)
        
        
        self.nodename_list = QListWidget()
        
        self.refall = QPushButton("刷新界面")
        self.refall.clicked.connect(self.refresh_info)
        self.addpro = QPushButton("添加项目")
        self.addpro.clicked.connect(self.addpro_fun)

        self.delpro = QPushButton("打开数据地址")
        self.delpro.clicked.connect(self.delpro_fun)
        
        self.addtiaomu = QPushButton("添加条目")
        self.addtiaomu.clicked.connect(self.addtiaomu_fun)
        self.deltiaomu = QPushButton("删除条目")
        self.deltiaomu.clicked.connect(self.deltiaomu_fun)
        self.deltiaomu.clicked.connect(self.refresh_version_info)
        self.deltiaomu.clicked.connect(self.refresh_version_notename_info)

        
        self.addnk = QPushButton("添加nuke节点")
        self.addnk.clicked.connect(self.addnk_fun)
        self.addnk.clicked.connect(self.refresh_version_info)
        self.addnk.clicked.connect(self.refresh_version_notename_info)
        self.miaoshu = QTextEdit()
        self.miaoshu.setReadOnly(True)

        
        self.layouta = QVBoxLayout()
        self.layoutb = QVBoxLayout()
        self.layoutc = QVBoxLayout()
        self.layoutd = QHBoxLayout()
        self.layoute = QHBoxLayout()
        self.layoutf = QHBoxLayout()
        
        self.layoutd.addWidget(self.addpro)
        self.layoutd.addWidget(self.delpro)
        self.layoutd.addWidget(self.refall)
        
        self.layoute.addWidget(self.addtiaomu)
        self.layoute.addWidget(self.deltiaomu)

        # self.layoutf.addWidget(self.addnk)

        self.layouta.addWidget(self.xiangmuming)
        self.layouta.addLayout(self.layoutd)
        self.layouta.addWidget(self.search_lined)
        self.layouta.addWidget(self.bianhao_list)
        self.layouta.addLayout(self.layoute)
        
        
        
        self.layoutc.addWidget(self.miaoshu)
        
        self.layoutc.addWidget(self.nodename_list)
        
        self.layoutb.addWidget(self.banben_list)
        self.layoutb.addWidget(self.addnk)
        # self.layoutb.addLayout(self.layoutf)
        self.layoutf.addLayout(self.layoutb)
        self.layoutf.addLayout(self.layoutc)
        
        
        # -----------------------------------------------------------
        self.MasterLayout = QVBoxLayout()
        self.MasterLayout.setContentsMargins(0,0,0,0)
        self.MasterLayout.addLayout(self.layouta)
        self.MasterLayout.addLayout(self.layoutb)
        self.MasterLayout.addLayout(self.layoutf)
        
        self.central_widget = QWidget()
        self.central_widget.setLayout(self.MasterLayout)
        self.setCentralWidget(self.central_widget)
        
        
        # ----------------------
        self.refresh_info()
        # 
        self.setStyleSheet("""
            QWidget{
                font-size: 25px;
            }
        """)
        
    
    ##------------------------------------------------------------------------------------
    # --- 右键菜单连接
    def show_right_click_menu(self, pos):
        """ 显示右键菜单 """
        
        # 获取发出信号的对象
        kb = self.sender()
        
        item = kb.itemAt(pos)  # 获取鼠标右键点击处的item

        if item:       
            # 创建菜单
            menu = QMenu(self)
            
            # 运行功能但不关闭面板
            run_action = QAction("导入nuke节点", self)
            run_action.triggered.connect(lambda: self.importnk_fun(item))
            menu.addAction(run_action)

            # 添加操作
            add_action = QAction("设置描述", self)
            add_action.triggered.connect(lambda: self.savemiaoshu_fun(item))
            menu.addAction(add_action)
            
            # 添加操作
            name_action = QAction("设置命名", self)
            name_action.triggered.connect(lambda: self.namechange_fun(item))
            menu.addAction(name_action)
            
            # 添加操作
            del_action = QAction("删除这个版本", self)
            del_action.triggered.connect(lambda: self.delcurnkvers_fun(item))
            menu.addAction(del_action)
            

            
            menu.popup(kb.viewport().mapToGlobal(pos))  # 显示菜单，并保持item引用
    
    def delcurnkvers_fun(self,item):
        figv = item.toolTip()
        pt = os.path.dirname(figv)
        textv = pt.split("/")[-1]
        ask = self.question("删除这个版本？",f"{textv}")
        if ask:
            dect = self.delete_directory(pt)
            if dect:
                self.information("删除成功")
            else:
                self.information("删除失败")
            self.refresh_version_info()
            self.refresh_version_notename_info()
    
    def safe_rename_directory(self,old_path, new_path):
        """
        安全地重命名文件夹，包含基本的验证和错误处理
        
        参数:
            old_path (str): 原文件夹路径
            new_path (str): 新文件夹路径
        
        返回:
            bool: 重命名是否成功
        """
        # 转换为Path对象
        old_dir = Path(old_path)
        new_dir = Path(new_path)
        
        # 检查原文件夹是否存在
        if not old_dir.exists() or not old_dir.is_dir():
            print(f"错误: 原文件夹 '{old_path}' 不存在或不是一个目录")
            return False
        
        # 检查新路径是否已存在
        if new_dir.exists():
            print(f"错误: 目标路径 '{new_path}' 已存在")
            return False
        
        # 检查权限
        try:
            # 尝试创建一个临时文件测试写入权限
            test_file = old_dir / ".rename_test"
            with open(test_file, "w") as f:
                f.write("test")
            test_file.unlink()  # 删除测试文件
        except PermissionError:
            print(f"错误: 没有权限修改文件夹 '{old_path}'")
            return False
        
        # 执行重命名
        try:
            old_dir.rename(new_dir)
            print(f"文件夹重命名成功: '{old_path}' -> '{new_path}'")
            return True
        except Exception as e:
            print(f"错误: 重命名失败: {str(e)}")
            return False
    
    def namechange_fun(self,item):
        # 修改命名
        figv = item.toolTip()
        pt = os.path.dirname(figv)
        namev = pt.split("/")[-1]
        notefilept = f"{pt}/note.json"
        dt = RWJ.ReadJson(notefilept)
        try:
            tipv = dt["tip"]
        except:
            tipv = ""

        
        text, ok = QInputDialog.getText(
            self,                  # 父窗口
            "输入",          # 对话框标题
            "简短一些备注:",      # 提示文本
            text=f"{tipv}"        # 默认值
        )
        
        # 处理用户输入
        if ok and text:
            dt["tip"] = text
            RWJ.WriteJson(notefilept,dt)
            item.setText(f"{text}   {namev}")


    def savemiaoshu_fun(self,item):
        # 保存描述
        figv = item.toolTip()
        pt = os.path.dirname(figv)
        notefilept = f"{pt}/note.json"
        dt = RWJ.ReadJson(notefilept)
        notev = dt["note"]
        
        tp,text = self.input_dialog_fun("note","备注信息",notev)
        if tp:
            dt["note"] = text
            RWJ.WriteJson(notefilept,dt)
            self.miaoshu.setPlainText(f"{text}")

        
    def input_dialog_fun(self,tile,label,text):
        # 多行输入
        text, ok = QInputDialog.getMultiLineText(self, f"{tile}", f"{label}", f"{text}")
        if ok:
            return True, text
        else:
            return False, text
        
    def importnk_fun(self,item):
        # 导入节点
        figv = item.toolTip()
        nuke.nodePaste(figv)
    
    def addnk_fun(self):
        # 添加节点
        pt = self.CurrentFilePath()
        curpro = self.xiangmuming.currentText()
        if curpro != "":
            item = self.bianhao_list.currentItem()
            if item:
                textv = item.text()
                # 调用now()函数获取当前的日期和时间
                current_datetime = datetime.now()
                # 打印原始的datetime对象
                # print("Current datetime:", current_datetime)
                # 如果你想要格式化输出，可以使用strftime()函数
                # formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
                formatted_datetime = current_datetime.strftime("%Y_%m_%d")
                # print("Formatted datetime:", formatted_datetime)
                
                fd = pt + f"/{curpro}/{textv}/"
                try:
                    bh = max([int(i.split("_")[0]) for i in os.listdir(fd)])
                except ValueError:
                    bh = 0
                bh = "%04d"%(bh+1)
                srcfile = f"{pt}tlenuke.nk"
                dstfile = f"{fd}{bh}_{formatted_datetime}/tlenuke.nk"
                notefilept = f"{fd}{bh}_{formatted_datetime}/note.json"
                notenamelistpt = f"{fd}{bh}_{formatted_datetime}/nodenamelist.json"
                
                try:
                    nuke.nodeCopy(srcfile)
                    # 检测路径是否存在，不存在则创建
                    if not os.path.exists(os.path.dirname(dstfile)):
                        os.makedirs(os.path.dirname(dstfile))
                    
                    # 使用shutil.move()进行剪切（移动）操作
                    shutil.move(srcfile, dstfile)
                    
                    ntdt = {} # 备注字典
                    ntdt["note"] = ""
                    ntdt["tip"] = ""
                    nadt = {} # 节点名字字典
                    nds = nuke.selectedNodes()
                    ndsv = [i.name() for i in nds]
                    nadt["nodenamelist"] = ndsv
                    RWJ.WriteJson(notenamelistpt,nadt)
                    RWJ.WriteJson(notefilept,ntdt)
                    # self.refresh_version_info()
                    
                except RuntimeError:
                    self.information("没有选中节点")

            else:
                self.information("没有选中模版名")
        
        else:
            self.information("没有项目")
        

          
    def addtiaomu_fun(self):
        # 添加条目
        pt = self.CurrentFilePath()
        curpro = self.xiangmuming.currentText()
        if curpro != "":
            tp , text = self.lineInput("这是什么？")
            if tp:
                fd = pt + f"/{curpro}/" + text
                if not os.path.exists(fd):
                    os.makedirs(fd)
                    self.refresh_tiaomu_info()
        
    def deltiaomu_fun(self):
        # 删除条目
        item = self.bianhao_list.currentItem()
        if item:
            textv = item.text()
            pt = self.CurrentFilePath()
            curpro = self.xiangmuming.currentText()
            if curpro != "":
                fd = pt + f"/{curpro}/" + textv
                ask = self.question("删除这个条目？",f"{textv}")
                if ask:
                    dect = self.delete_directory(fd)
                    if dect:
                        self.information("删除成功")
                    else:
                        self.information("删除失败")
                    self.refresh_tiaomu_info()
            
        else:
            print("没有选中任何模版名称")
            
    
    def information(self,messagete):
        # 信息提示窗口
        info = QMessageBox()
        info.setIcon(QMessageBox.Information)
        info.setWindowTitle('信息')
        info.setText(f"{messagete}")
        # info.addButton("确认", QMessageBox.AcceptRole)
        # info.addButton("取消", QMessageBox.RejectRole)
        # info.addButton("忽略", QMessageBox.DestructiveRole)
        api = info.exec_()
        # if api == QMessageBox.AcceptRole:
            # print("您选择了确认")
        # elif api == QMessageBox.RejectRole:
            # print("您选择了取消")
        # else:
            # print("您选择了忽略")
    
    def question(self,askinfo,curtext):
        # 询问窗口
        question = QMessageBox.question(self,
                                        f'{askinfo}',
                                        f'{curtext}',
                                        )
        if question == QMessageBox.Yes:
            return True
        else:
            return False
            
    def delete_directory(self,path):
        try:
            shutil.rmtree(path)
        except OSError as e:
            print(f"Error: {e.strerror}")
            return False
        else:
            # 检查文件夹是否还存在
            if os.path.exists(path):
                print(f"Directory {path} still exists after attempted deletion.")
                return False
            else:
                print(f"Directory {path} has been successfully deleted.")
                return True


        
    def delpro_fun(self):
        # 打开数据地址
        pt = self.CurrentFilePath()
        url = QUrl.fromLocalFile(pt)
        QDesktopServices.openUrl(url)
        
        
    def addpro_fun(self):
        # 添加项目
        pt = self.CurrentFilePath()
        tp , text = self.lineInput("项目名")
        if tp:
            fd = pt + text
            if not os.path.exists(fd):
                os.makedirs(fd)
                self.refresh_info()
                
    
    
    def refresh_version_notename_info(self,item=None):
        # 刷新当前版本的备注和节点列表
        self.nodename_list.clear()
        self.miaoshu.setPlainText("")
        if item:
            figv = item.toolTip()
            pt = os.path.dirname(figv)

            notefilept = f"{pt}/note.json"
            notenamelistpt = f"{pt}/nodenamelist.json"

            dt = RWJ.ReadJson(notefilept)
            notev = dt["note"]
            dt2 = RWJ.ReadJson(notenamelistpt)
            namelist = dt2["nodenamelist"]
            self.miaoshu.setPlainText(f"{notev}")
            self.nodename_list.addItems(namelist)
        
        
    
    def sort_files_by_prefix_split(self,folder_path):
        # 获取文件夹中的所有文件
        files = os.listdir(folder_path)
        
        # 排序函数：通过下划线分割提取第一个部分并转为整数
        def get_prefix_number(filename):
            parts = filename.split('_')
            if parts and parts[0].isdigit():
                return int(parts[0])
            return 0
        
        # 按提取的数字倒序排序
        sorted_files = sorted(files, key=get_prefix_number, reverse=True)
        
        return sorted_files
    
        
    def refresh_version_info(self):
        # 刷新节点版本
        self.banben_list.clear()
        pt = self.CurrentFilePath()
        curpro = self.xiangmuming.currentText()
        if curpro != "":
            item = self.bianhao_list.currentItem()
            if item:
                textv = item.text()            
                fd = pt + f"/{curpro}/{textv}/"
                # vers = os.listdir(fd) 
                vers = self.sort_files_by_prefix_split(fd) 
                # self.banben_list.addItems(vers)
                for i in vers:
                    notefilept = f"{fd}{i}/note.json"
                    dt = RWJ.ReadJson(notefilept)
                    try:
                        tipv = dt["tip"]
                    except:
                        tipv = ""
                    toname = f"{tipv}   {i}"
                    iv = QListWidgetItem(toname)
                    tpset = f"{fd}{i}/tlenuke.nk"
                    iv.setToolTip(tpset)
                    self.banben_list.addItem(iv)
                
        
    def refresh_tiaomu_info(self):
        # 刷新条目
        self.bianhao_list.clear()
        pt = self.CurrentFilePath()
        curpro = self.xiangmuming.currentText()
        if curpro != "":
            ptp = pt + f"/{curpro}/"
            tiaomulist = os.listdir(ptp)
            
            # 查找关键字
            gvtext = self.search_lined.text()
            gvtext = gvtext.lower() # 关键字
            if gvtext.replace(" ","") != "":
                tiaomulist = [i for i in tiaomulist if gvtext in i]
                
            self.bianhao_list.addItems(tiaomulist)
            
        
    def refresh_pro_info(self):
        # 刷新项目
        self.xiangmuming.clear()
        pt = self.CurrentFilePath()
        prolist = os.listdir(pt)
        self.xiangmuming.addItems(prolist)
        
    
    def refresh_other_info(self):
        # 刷新界面2
        self.refresh_tiaomu_info()
        self.refresh_version_info()
        self.refresh_version_notename_info()
    
    def refresh_info(self):
        # 刷新界面
        self.refresh_pro_info()
        self.refresh_other_info()

    
    
    def lineInput(self,tile):
        text, ok = QInputDialog.getText(self, "输入", f"{tile}",QLineEdit.Normal,"")
        if ok:
            return True, text
        else:
            return False, text
    
    #### 获取程序所在路径位置
    def CurrentFilePath(self):
        # return 一个当前程序所在路径的位置
        # cc = os.path.dirname(os.path.abspath(__file__)) + "/"
        # cc = cc.replace(os.sep, "/")
        cc = PTS.local_path_get()
        cfp = cc + "templateWork/"

        if not os.path.exists(cfp):
            os.makedirs(cfp)
        return cfp
    

def runshow():
    global tpwork
    tpwork = templateWork()
    tpwork.show()


nukepget = nukescripts.panels.registerWidgetAsPanel("tppanel.templateWork","nk模版管理","QZDFlixuaiobo.templateWork_ver30",True)

def run_show_funa():
    if nuke.getPaneFor("nk模版管理"):
        pass
    else:
        pane = nuke.getPaneFor("Properties.1")
        nukepget.addToPane(pane)


if __name__ == '__main__':
    #app = QApplication(sys.argv)
    # widget = listbuttonpanel()
    # widget.show()
    # runshow()
    run_show_funa()