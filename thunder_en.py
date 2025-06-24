'''
v1.6 Convert Thunder thunder links to https links
created by HelloWorld05
in 2025.06.23
Updates:
1. Use the bool() function to directly return validation results.
2. Encapsulate error message display and warning message display into separate functions to reduce code duplication.
3. Use the list result_text to store results, and finally use "\n".join(result_text) to generate the final result display string, reducing the overhead of each string concatenation.
4. Removed unnecessary continue statements to keep the code concise.
5. Removed unnecessary exception handling in the open_links function because QDesktopServices.openUrl will not throw exceptions that need to be caught.
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

# Style constants
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
        self.setWindowTitle("About")
        content = """
        thunder-https v1.6
        
        Features:
        - Convert Thunder exclusive links to normal URLs
        - Support single and batch conversion
        - Support link copying
        - Support direct opening in browser
        - Support saving conversion results to file
        
        Updates:
        - Added batch conversion function
        - Added URL format validation
        - Added status bar for operation information
        - Added save results to file function
        - Optimized UI experience
        
        Developer: HelloWorld05
        Developer Homepage: https://github.com/helloworldpxy
        Project Homepage: https://github.com/helloworldpxy/thunder-https
        © 2025 All rights reserved
        """
        self.setText(content)
        self.setIcon(QMessageBox.Information)

class ThunderConverter(QMainWindow):
    def __init__(self):
        super().__init__()
        self.converted_urls = []  # Store all converted URLs
        self.initUI()
        
    def initUI(self):
        self.setWindowTitle("Thunder Link Converter v1.6")
        self.setGeometry(300, 300, 700, 550)
        self.setMinimumSize(650, 450)
        
        # Create menu bar
        menubar = self.menuBar()
        help_menu = menubar.addMenu('Help')
        about_action = QAction('About', self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        # Main interface layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Input section
        input_label = QLabel("Input Thunder links (one per line, supports batch conversion):")
        input_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(input_label)
        
        self.input_field = QPlainTextEdit()
        self.input_field.setPlaceholderText("Please enter Thunder links starting with thunder:// (one per line, supports pasting from clipboard)...")
        self.input_field.setStyleSheet(INPUT_STYLE)
        self.input_field.setMinimumHeight(100)
        layout.addWidget(self.input_field)
        
        # Convert button
        self.convert_btn = QPushButton("Convert Links")
        self.convert_btn.setStyleSheet(BUTTON_STYLE.format("#3498db", "#2980b9", "#1c6da8"))
        self.convert_btn.clicked.connect(self.convert_links)
        layout.addWidget(self.convert_btn, 0, Qt.AlignHCenter)
        
        layout.addSpacing(15)
        
        # Result display
        result_label = QLabel("Conversion Results:")
        result_label.setFont(QFont("Arial", 10, QFont.Bold))
        layout.addWidget(result_label)
        
        self.result_field = QPlainTextEdit()
        self.result_field.setReadOnly(True)
        self.result_field.setStyleSheet(RESULT_STYLE)
        self.result_field.setMinimumHeight(150)
        layout.addWidget(self.result_field)
        
        layout.addSpacing(15)
        
        # Action buttons
        btn_layout = QHBoxLayout()
        self.copy_btn = QPushButton("Copy Links")
        self.copy_btn.setStyleSheet(BUTTON_STYLE.format("#2ecc71", "#27ae60", "#219a52"))
        self.copy_btn.clicked.connect(self.copy_links)
        self.copy_btn.setEnabled(False)
        
        self.open_btn = QPushButton("Open Links")
        self.open_btn.setStyleSheet(BUTTON_STYLE.format("#9b59b6", "#8e44ad", "#7d3c98"))
        self.open_btn.clicked.connect(self.open_links)
        self.open_btn.setEnabled(False)
        
        self.save_btn = QPushButton("Save Results")
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
        
        # Add status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready", 5000)
        
    def validate_thunder_url(self, url):
        """Validate Thunder link format"""
        pattern = r'^thunder://[A-Za-z0-9+/=]+$'
        return bool(re.match(pattern, url))
    
    def convert_links(self):
        """Batch convert links"""
        input_text = self.input_field.toPlainText().strip()
        if not input_text:
            self.show_error("Please enter Thunder links")
            return
            
        thunder_urls = [url.strip() for url in input_text.splitlines() if url.strip()]
        if not thunder_urls:
            self.show_error("No valid input links")
            return
            
        self.converted_urls = []
        result_text = []
        success_count = 0
        error_count = 0
        
        for url in thunder_urls:
            if not url.startswith('thunder://'):
                result_text.append(f"# Error: {url} - Address must start with thunder://")
                error_count += 1
            elif not self.validate_thunder_url(url):
                result_text.append(f"# Error: {url} - Invalid Thunder link format")
                error_count += 1
            else:
                try:
                    encoded_str = url[10:]
                    decoded_bytes = base64.b64decode(encoded_str)
                    decoded_url = decoded_bytes.decode('utf-8')
                    
                    if not (decoded_url.startswith("AA") and decoded_url.endswith("ZZ")):
                        result_text.append(f"# Error: {url} - Invalid Thunder link content")
                        error_count += 1
                    else:
                        final_url = parse.unquote(decoded_url[2:-2])
                        self.converted_urls.append(final_url)
                        result_text.append(final_url)
                        success_count += 1
                except (base64.binascii.Error, ValueError, UnicodeDecodeError) as e:
                    result_text.append(f"# Error: {url} - Exception occurred during processing: {str(e)}")
                    error_count += 1
        
        self.result_field.setPlainText("\n".join(result_text))
        
        # Update button states
        self.update_buttons()
        
        # Update status bar
        self.status_bar.showMessage(f"Conversion complete: {success_count} successful, {error_count} failed", 10000)
        
        # Auto-scroll to top of results
        self.result_field.moveCursor(QTextCursor.Start)
        
    def update_buttons(self):
        """Update action button states"""
        has_results = bool(self.converted_urls)
        self.copy_btn.setEnabled(has_results)
        self.open_btn.setEnabled(has_results)
        self.save_btn.setEnabled(has_results)
        
    def show_error(self, message):
        """Display error message"""
        self.status_bar.showMessage(f"Error: {message}", 5000)
        QMessageBox.critical(self, "Error", message)
        
    def copy_links(self):
        """Copy all converted links to clipboard"""
        if self.converted_urls:
            clipboard = QApplication.clipboard()
            clipboard.setText("\n".join(self.converted_urls))
            self.status_bar.showMessage("Links copied to clipboard", 5000)
            QMessageBox.information(self, "Success", f"Copied {len(self.converted_urls)} links to clipboard")
        else:
            self.show_warning("No conversion results available")
    
    def show_warning(self, message):
        """Display warning message"""
        self.status_bar.showMessage(f"Warning: {message}", 5000)
        QMessageBox.warning(self, "Warning", message)
    
    def open_links(self):
        """Open all converted links in browser"""
        if not self.converted_urls:
            self.show_warning("No links available")
            return
            
        for url in self.converted_urls:
            QDesktopServices.openUrl(QUrl(url))
        self.status_bar.showMessage(f"Opening {len(self.converted_urls)} links in browser", 5000)
        
    def save_results(self):
        """Save conversion results to file"""
        if not self.converted_urls:
            self.show_warning("No content to save")
            return
            
        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save Results", "", "Text Files (*.txt);;All Files (*)", options=options)
        
        if file_path:
            try:
                if not file_path.lower().endswith('.txt'):
                    file_path += '.txt'
                    
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("\n".join(self.converted_urls))
                
                self.status_bar.showMessage(f"Results saved to {os.path.basename(file_path)}", 10000)
                QMessageBox.information(self, "Save Successful", f"File saved to:\n{file_path}")
            except Exception as e:
                self.show_error(f"Error saving file: {str(e)}")
    
    def show_about(self):
        dialog = AboutDialog(self)
        dialog.exec_()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    window = ThunderConverter()
    window.show()
    sys.exit(app.exec_())