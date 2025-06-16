'''
v1.5 迅雷thunder链接转https链接
created by HelloWorld05
in 2025.06.14
更新内容：
1. 修复剪贴板复制时的对象引用错误
2. 优化样式表管理
3. 增强异常处理的针对性
4. 改进用户输入体验
5. 新增批量转换功能
6. 添加URL格式验证
7. 添加状态栏显示操作信息
8. 添加保存结果到文件功能
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
        thunder-https v1.5
        
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
        self.setWindowTitle("迅雷链接转换器 v1.5")
        self.setGeometry(300, 300, 700, 550)  # 增加窗口高度
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
        
        # 增加垂直间距
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
        
        # 增加垂直间距
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
        
        # 添加弹性空间使按钮组在底部
        btn_layout.addStretch(1)
        
        layout.addLayout(btn_layout)
        
        # 添加弹性空间确保布局顶部对齐
        layout.addStretch(1)
        
        # 添加状态栏
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("就绪", 5000)
        
    def validate_thunder_url(self, url):
        """验证thunder链接格式是否正确"""
        pattern = r'^thunder://[A-Za-z0-9+/=]+$'
        return re.match(pattern, url) is not None
    
    def convert_links(self):
        """批量转换链接"""
        input_text = self.input_field.toPlainText().strip()
        if not input_text:
            self.status_bar.showMessage("错误：请输入迅雷地址", 5000)
            QMessageBox.critical(self, "错误", "请输入迅雷地址")
            return
            
        thunder_urls = [url.strip() for url in input_text.splitlines() if url.strip()]
        if not thunder_urls:
            self.status_bar.showMessage("错误：没有有效的输入链接", 5000)
            QMessageBox.critical(self, "错误", "没有有效的输入链接")
            return
            
        self.converted_urls = []  # 清空之前的转换结果
        result_text = ""
        success_count = 0
        error_count = 0
        
        for url in thunder_urls:
            if not url.startswith('thunder://'):
                result_text += f"# 错误：{url} - 地址必须以thunder://开头\n"
                error_count += 1
                continue
                
            if not self.validate_thunder_url(url):
                result_text += f"# 错误：{url} - 无效的thunder链接格式\n"
                error_count += 1
                continue
                
            try:
                encoded_str = url[10:]
                decoded_bytes = base64.b64decode(encoded_str)
                decoded_url = decoded_bytes.decode('utf-8')
                
                # 验证解码后的URL格式
                if not (decoded_url.startswith("AA") and decoded_url.endswith("ZZ")):
                    result_text += f"# 错误：{url} - 无效的thunder链接内容\n"
                    error_count += 1
                    continue
                    
                trimmed_url = decoded_url[2:-2]
                final_url = parse.unquote(trimmed_url)
                self.converted_urls.append(final_url)
                result_text += final_url + "\n"
                success_count += 1
            except (base64.binascii.Error, ValueError) as e:
                result_text += f"# 错误：{url} - Base64解码失败: {str(e)}\n"
                error_count += 1
            except UnicodeDecodeError:
                result_text += f"# 错误：{url} - URL解码失败（非UTF-8编码）\n"
                error_count += 1
            except Exception as e:
                result_text += f"# 错误：{url} - 处理过程中发生异常: {str(e)}\n"
                error_count += 1
        
        # 显示转换结果
        self.result_field.setPlainText(result_text.strip())
        
        # 更新按钮状态
        has_results = bool(self.converted_urls)
        self.copy_btn.setEnabled(has_results)
        self.open_btn.setEnabled(has_results)
        self.save_btn.setEnabled(has_results)
        
        # 更新状态栏
        status_msg = f"转换完成: 成功 {success_count} 条, 失败 {error_count} 条"
        self.status_bar.showMessage(status_msg, 10000)
        
        # 自动滚动到结果顶部
        self.result_field.moveCursor(QTextCursor.Start)
        
    def copy_links(self):
        """复制所有转换后的链接到剪贴板"""
        if self.converted_urls:
            clipboard = QApplication.clipboard()
            clipboard.setText("\n".join(self.converted_urls))
            self.status_bar.showMessage("链接已复制到剪贴板", 5000)
            QMessageBox.information(self, "成功", f"已复制 {len(self.converted_urls)} 条链接到剪贴板")
        else:
            self.status_bar.showMessage("没有可用的转换结果", 5000)
            QMessageBox.warning(self, "警告", "没有可用的转换结果")
    
    def open_links(self):
        """在浏览器中打开所有转换后的链接"""
        if not self.converted_urls:
            self.status_bar.showMessage("没有可用的链接", 5000)
            QMessageBox.warning(self, "警告", "没有可用的链接")
            return
            
        try:
            for url in self.converted_urls:
                QDesktopServices.openUrl(QUrl(url))
            self.status_bar.showMessage(f"正在浏览器中打开 {len(self.converted_urls)} 个链接", 5000)
        except Exception as e:
            self.status_bar.showMessage(f"打开链接时出错: {str(e)}", 5000)
            QMessageBox.critical(self, "错误", f"无法打开链接: {str(e)}")
    
    def save_results(self):
        """保存转换结果到文件"""
        if not self.converted_urls:
            self.status_bar.showMessage("没有可保存的内容", 5000)
            QMessageBox.warning(self, "警告", "没有可保存的内容")
            return
            
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "保存结果", "", "文本文件 (*.txt);;所有文件 (*)", options=options)
        
        if file_path:
            try:
                # 确保文件扩展名正确
                if not file_path.lower().endswith('.txt'):
                    file_path += '.txt'
                    
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(self.converted_urls))
                
                self.status_bar.showMessage(f"结果已保存到 {os.path.basename(file_path)}", 10000)
                QMessageBox.information(self, "保存成功", f"文件已保存到:\n{file_path}")
            except Exception as e:
                self.status_bar.showMessage(f"保存失败: {str(e)}", 5000)
                QMessageBox.critical(self, "保存错误", f"保存文件时出错: {str(e)}")
    
    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ThunderConverter()
    window.show()
    sys.exit(app.exec_())