import sys
import os
from PySide6.QtWidgets import QApplication, QWidget, QLabel, QSystemTrayIcon, QMenu
from PySide6.QtGui import QPixmap, QAction
from PySide6.QtCore import Qt, QPoint, QTimer

# 资源路径兼容函数：打包exe和直接pyw运行都能用
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class DesktopPet(QWidget):
    def __init__(self):
        super().__init__()

        # 窗口设置：无边框、置顶、透明背景
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.SubWindow
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.resize(200, 200)

        # 加载两张状态图，使用resource_path兼容打包
        self.label = QLabel(self)
        self.label.resize(200, 200)

        self.normal_pix = QPixmap(resource_path("shiro_idle.png"))
        self.pet_pix = QPixmap(resource_path("shiro_pet.png"))

        # 默认显示正常状态
        self.label.setPixmap(self.normal_pix)

        # 3秒恢复定时器
        self.recover_timer = QTimer(self)
        self.recover_timer.setSingleShot(True)
        self.recover_timer.timeout.connect(self.show_normal)

        # 拖拽变量
        self.drag = False
        self.drag_pos = QPoint()
        self.click_start_pos = QPoint()
        self.drag_threshold = 8
        self.is_petting = False # 是否处于抚摸动画状态

        # 托盘菜单
        self.tray = QSystemTrayIcon(self)
        menu = QMenu()

        act_show = QAction("显示", self)
        act_hide = QAction("隐藏", self)
        act_quit = QAction("退出", self)

        act_show.triggered.connect(self.show)
        act_hide.triggered.connect(self.hide)
        act_quit.triggered.connect(app.quit)

        menu.addAction(act_show)
        menu.addAction(act_hide)
        menu.addSeparator()
        menu.addAction(act_quit)

        self.tray.setContextMenu(menu)
        self.tray.show()

    def show_normal(self):
        """恢复待机图片，解除抚摸锁定"""
        self.label.setPixmap(self.normal_pix)
        self.is_petting = False

    def show_pet(self):
        """切换抚摸状态，锁定，启动计时器"""
        self.label.setPixmap(self.pet_pix)
        self.is_petting = True
        self.recover_timer.start(3000)

    # 鼠标事件
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag = True
            global_pos = event.globalPosition().toPoint()
            self.drag_pos = global_pos - self.frameGeometry().topLeft()
            self.click_start_pos = global_pos

        if event.button() == Qt.RightButton:
            self.tray.contextMenu().exec(event.globalPosition().toPoint())

    def mouseMoveEvent(self, event):
        if self.drag:
            global_pos = event.globalPosition().toPoint()
            self.move(global_pos - self.drag_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag = False
            global_pos = event.globalPosition().toPoint()
            dist = (global_pos - self.click_start_pos).manhattanLength()
            # 只有不在抚摸状态，且是点击，才触发抚摸
            if dist < self.drag_threshold and not self.is_petting:
                self.show_pet()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    pet = DesktopPet()
    pet.show()
    sys.exit(app.exec())
