'''
v1.4 迅雷thunder链接转https链接
created by HelloWorld05
in 2025.05.22
更新内容：
1. 修复剪贴板复制时的对象引用错误
2. 优化样式表管理
3. 增强异常处理的针对性
4. 改进用户输入体验
'''
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLineEdit, QPushButton, QLabel,
                            QMessageBox, QMenuBar, QAction)
from PyQt5.QtGui import QIcon, QDesktopServices
from PyQt5.QtCore import Qt, QUrl
from urllib import parse
import base64

# 样式常量
INPUT_STYLE = """
    QLineEdit {
        border: 2px solid #3498db;
        border-radius: 10px;
        padding: 8px;
        font-size: 14px;
    }
    QLineEdit:focus {
        border-color: #2980b9;
    }
"""

BUTTON_STYLE = """
    QPushButton {{
        background-color: {};
        color: white;
        border: none;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 14px;
        min-width: 100px;
    }}
    QPushButton:hover {{
        background-color: {};
    }}
    QPushButton:pressed {{
        background-color: {};
    }}
"""

RESULT_STYLE = """
    QLineEdit {
        border: 2px solid #2ecc71;
        border-radius: 10px;
        padding: 8px;
        font-size: 14px;
        background: #f8f9fa;
    }
"""

class AboutDialog(QMessageBox):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("关于")
        content = """
        thunder-https v1.4
        
        功能：
        - 转换迅雷专用链为普通URL
        - 支持链接复制
        - 支持浏览器直接打开
        
        更新内容：
        - 修复已知问题
        - 优化界面体验
        
        开发者: HelloWorld05
        开发者主页：https://github.com/helloworldpxy
        项目主页：https://github.com/helloworldpxy/thunder-https
        © 2025 All rights reserved
        """
        self.setText(content)
        self.setIcon(QMessageBox.Information)

class ThunderConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.converted_url = ""
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("迅雷链接转换器")
        self.setGeometry(300, 300, 600, 300)
        self.setMinimumSize(500, 250)
        
        # 创建菜单栏
        menubar = self.menuBar()
        about_menu = menubar.addMenu('帮助')
        about_action = QAction('关于', self)
        about_action.triggered.connect(self.show_about)
        about_menu.addAction(about_action)
        
        # 主界面布局
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(25, 25, 25, 25)
        
        # 输入部分
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("请输入thunder://开头的迅雷链接（支持从剪贴板粘贴）...")
        self.input_field.setStyleSheet(INPUT_STYLE)
        self.input_field.returnPressed.connect(self.convert_link)  # 回车触发转换
        input_layout.addWidget(self.input_field)
        
        # 转换按钮
        self.convert_btn = QPushButton("转换链接")
        self.convert_btn.setStyleSheet(BUTTON_STYLE.format("#3498db", "#2980b9", "#1c6da8"))
        self.convert_btn.clicked.connect(self.convert_link)
        
        # 结果显示
        result_layout = QHBoxLayout()
        self.result_field = QLineEdit()
        self.result_field.setReadOnly(True)
        self.result_field.setStyleSheet(RESULT_STYLE)
        result_layout.addWidget(self.result_field)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.copy_btn = QPushButton("复制链接")
        self.copy_btn.setStyleSheet(BUTTON_STYLE.format("#2ecc71", "#27ae60", "#219a52"))
        self.copy_btn.clicked.connect(self.copy_link)
        
        self.open_btn = QPushButton("打开链接")
        self.open_btn.setStyleSheet(BUTTON_STYLE.format("#27ae60", "#219a52", "#1b7d3d"))
        self.open_btn.clicked.connect(self.open_link)
        
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addWidget(self.open_btn)
        btn_layout.setSpacing(15)
        
        # 组合布局
        layout.addLayout(input_layout)
        layout.addWidget(self.convert_btn, 0, Qt.AlignHCenter)
        layout.addSpacing(20)
        layout.addLayout(result_layout)
        layout.addSpacing(15)
        layout.addLayout(btn_layout)
        
    def convert_link(self):
        thunder_url = self.input_field.text().strip()
        if not thunder_url:
            QMessageBox.critical(self, "错误", "请输入迅雷地址")
            return
        if not thunder_url.startswith('thunder://'):
            QMessageBox.critical(self, "错误", "地址必须以 thunder:// 开头")
            return
        
        try:
            encoded_str = thunder_url[10:]
            decoded_bytes = base64.b64decode(encoded_str)
        except (base64.binascii.Error, ValueError) as e:
            QMessageBox.critical(self, "解码错误", f"Base64解码失败: {str(e)}")
            return
        except Exception as e:
            QMessageBox.critical(self, "错误", f"处理过程中发生异常: {str(e)}")
            return
            
        try:
            decoded_url = decoded_bytes.decode('utf-8')
            trimmed_url = decoded_url[2:-2]
            final_url = parse.unquote(trimmed_url)
            self.converted_url = final_url
            self.result_field.setText(final_url)
        except UnicodeDecodeError:
            QMessageBox.critical(self, "解码错误", "URL解码失败（非UTF-8编码）")
        except Exception as e:
            QMessageBox.critical(self, "解析错误", f"URL处理失败: {str(e)}")
    
    def copy_link(self):
        if self.converted_url:
            clipboard = QApplication.clipboard()
            clipboard.setText(self.converted_url)
            QMessageBox.information(self, "成功", "链接已复制到剪贴板")
        else:
            QMessageBox.warning(self, "警告", "没有可用的转换结果")
    
    def open_link(self):
        if self.converted_url:
            try:
                QDesktopServices.openUrl(QUrl(self.converted_url))
            except Exception as e:
                QMessageBox.critical(self, "错误", f"无法打开链接: {str(e)}")
        else:
            QMessageBox.warning(self, "警告", "没有可用的链接")
    
    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ThunderConverter()
    window.show()
    sys.exit(app.exec_())