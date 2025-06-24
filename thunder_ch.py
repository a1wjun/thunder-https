'''
v1.6 迅雷thunder链接转https链接
created by HelloWorld05
in 2025.06.23
更新内容：
1. 使用 bool() 函数直接返回验证结果。
2. 将错误信息显示和警告信息显示封装成单独的函数，以减少代码重复。
3. 使用列表 result_text 来存储结果，最后统一使用 "\n".join(result_text) 来生成最终结果显示字符串，减少每次字符串拼接的开销。
4. 移除了不必要的 continue 语句，保持代码简洁。
5. 在 open_links 函数中移除了不必要的异常处理，因为 QDesktopServices.openUrl 不会抛出需要捕获的异常。
'''
import sys
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                            QHBoxLayout, QLineEdit, QPushButton, QLabel,
                            QMessageBox, QMenuBar, QAction, QStatusBar, 
                            QFileDialog, QPlainTextEdit, QSizePolicy, QSpacerItem)
from PyQt5.QtGui import QIcon, QDesktopServices, QTextCursor, QFont
from PyQt5.QtCore import Qt, QUrl
from urllib import parse
import base64
import os
import re

# 样式常量
INPUT_STYLE = """
    QPlainTextEdit {
        border: 2px solid #3498db;
        border-radius: 10px;
        padding: 8px;
        font-size: 14px;
        background: #ffffff;
    }
    QPlainTextEdit:focus {
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
    QPushButton:disabled {{
        background-color: #95a5a6;
        color: #7f8c8d;
    }}
"""

RESULT_STYLE = """
    QPlainTextEdit {
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
        thunder-https v1.6
        
        功能：
        - 转换迅雷专用链为普通URL
        - 支持单条和批量转换
        - 支持链接复制
        - 支持浏览器直接打开
        - 支持保存转换结果到文件
        
        更新内容：
        - 新增批量转换功能
        - 添加URL格式验证
        - 添加状态栏显示操作信息
        - 添加保存结果到文件功能
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
        self.converted_urls = []  # 存储所有转换后的URL
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("迅雷链接转换器 v1.6")
        self.setGeometry(300, 300, 700, 550)
        self.setMinimumSize(650, 450)
        
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
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # 输入部分
        input_label = QLabel("输入迅雷链接（每行一个，支持批量转换）:")
        input_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(input_label)
        
        self.input_field = QPlainTextEdit()
        self.input_field.setPlaceholderText("请输入thunder://开头的迅雷链接（每行一个，支持从剪贴板粘贴）...")
        self.input_field.setStyleSheet(INPUT_STYLE)
        self.input_field.setMinimumHeight(100)
        layout.addWidget(self.input_field)
        
        # 转换按钮
        self.convert_btn = QPushButton("转换链接")
        self.convert_btn.setStyleSheet(BUTTON_STYLE.format("#3498db", "#2980b9", "#1c6da8"))
        self.convert_btn.clicked.connect(self.convert_links)
        layout.addWidget(self.convert_btn, 0, Qt.AlignHCenter)
        
        layout.addSpacing(15)
        
        # 结果显示
        result_label = QLabel("转换结果:")
        result_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(result_label)
        
        self.result_field = QPlainTextEdit()
        self.result_field.setReadOnly(True)
        self.result_field.setStyleSheet(RESULT_STYLE)
        self.result_field.setMinimumHeight(150)
        layout.addWidget(self.result_field)
        
        layout.addSpacing(15)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        self.copy_btn = QPushButton("复制链接")
        self.copy_btn.setStyleSheet(BUTTON_STYLE.format("#2ecc71", "#27ae60", "#219a52"))
        self.copy_btn.clicked.connect(self.copy_links)
        self.copy_btn.setEnabled(False)
        
        self.open_btn = QPushButton("打开链接")
        self.open_btn.setStyleSheet(BUTTON_STYLE.format("#9b59b6", "#8e44ad", "#7d3c98"))
        self.open_btn.clicked.connect(self.open_links)
        self.open_btn.setEnabled(False)
        
        self.save_btn = QPushButton("保存结果")
        self.save_btn.setStyleSheet(BUTTON_STYLE.format("#f39c12", "#e67e22", "#d35400"))
        self.save_btn.clicked.connect(self.save_results)
        self.save_btn.setEnabled(False)
        
        btn_layout.addWidget(self.copy_btn)
        btn_layout.addWidget(self.open_btn)
        btn_layout.addWidget(self.save_btn)
        btn_layout.setSpacing(15)
        
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)
        
        layout.addStretch(1)
        
        # 添加状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪", 5000)
        
    def validate_thunder_url(self, url):
        """验证thunder链接格式是否正确"""
        pattern = r'^thunder://[A-Za-z0-9+/=]+$'
        return bool(re.match(pattern, url))
    
    def convert_links(self):
        """批量转换链接"""
        input_text = self.input_field.toPlainText().strip()
        if not input_text:
            self.show_error("请输入迅雷地址")
            return
            
        thunder_urls = [url.strip() for url in input_text.splitlines() if url.strip()]
        if not thunder_urls:
            self.show_error("没有有效的输入链接")
            return
            
        self.converted_urls = []
        result_text = []
        success_count = 0
        error_count = 0
        
        for url in thunder_urls:
            if not url.startswith('thunder://'):
                result_text.append(f"# 错误：{url} - 地址必须以thunder://开头")
                error_count += 1
            elif not self.validate_thunder_url(url):
                result_text.append(f"# 错误：{url} - 无效的thunder链接格式")
                error_count += 1
            else:
                try:
                    encoded_str = url[10:]
                    decoded_bytes = base64.b64decode(encoded_str)
                    decoded_url = decoded_bytes.decode('utf-8')
                    
                    if not (decoded_url.startswith("AA") and decoded_url.endswith("ZZ")):
                        result_text.append(f"# 错误：{url} - 无效的thunder链接内容")
                        error_count += 1
                    else:
                        final_url = parse.unquote(decoded_url[2:-2])
                        self.converted_urls.append(final_url)
                        result_text.append(final_url)
                        success_count += 1
                except (base64.binascii.Error, ValueError, UnicodeDecodeError) as e:
                    result_text.append(f"# 错误：{url} - 处理过程中发生异常: {str(e)}")
                    error_count += 1
        
        self.result_field.setPlainText("\n".join(result_text))
        
        # 更新按钮状态
        self.update_buttons()
        
        # 更新状态栏
        self.status_bar.showMessage(f"转换完成: 成功 {success_count} 条, 失败 {error_count} 条", 10000)
        
        # 自动滚动到结果顶部
        self.result_field.moveCursor(QTextCursor.Start)
        
    def update_buttons(self):
        """更新操作按钮状态"""
        has_results = bool(self.converted_urls)
        self.copy_btn.setEnabled(has_results)
        self.open_btn.setEnabled(has_results)
        self.save_btn.setEnabled(has_results)
        
    def show_error(self, message):
        """显示错误信息"""
        self.status_bar.showMessage(f"错误：{message}", 5000)
        QMessageBox.critical(self, "错误", message)
        
    def copy_links(self):
        """复制所有转换后的链接到剪贴板"""
        if self.converted_urls:
            clipboard = QApplication.clipboard()
            clipboard.setText("\n".join(self.converted_urls))
            self.status_bar.showMessage("链接已复制到剪贴板", 5000)
            QMessageBox.information(self, "成功", f"已复制 {len(self.converted_urls)} 条链接到剪贴板")
        else:
            self.show_warning("没有可用的转换结果")
    
    def show_warning(self, message):
        """显示警告信息"""
        self.status_bar.showMessage(f"警告：{message}", 5000)
        QMessageBox.warning(self, "警告", message)
    
    def open_links(self):
        """在浏览器中打开所有转换后的链接"""
        if not self.converted_urls:
            self.show_warning("没有可用的链接")
            return
            
        for url in self.converted_urls:
            QDesktopServices.openUrl(QUrl(url))
        self.status_bar.showMessage(f"正在浏览器中打开 {len(self.converted_urls)} 个链接", 5000)
        
    def save_results(self):
        """保存转换结果到文件"""
        if not self.converted_urls:
            self.show_warning("没有可保存的内容")
            return
            
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存结果", "", "文本文件 (*.txt);;所有文件 (*)", options=options)
        
        if file_path:
            try:
                if not file_path.lower().endswith('.txt'):
                    file_path += '.txt'
                    
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(self.converted_urls))
                
                self.status_bar.showMessage(f"结果已保存到 {os.path.basename(file_path)}", 10000)
                QMessageBox.information(self, "保存成功", f"文件已保存到:\n{file_path}")
            except Exception as e:
                self.show_error(f"保存文件时出错: {str(e)}")
    
    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ThunderConverter()
    window.show()
    sys.exit(app.exec_())
