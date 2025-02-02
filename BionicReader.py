import json
import os
import sys
import re
import fitz
from PySide6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QTextEdit,
    QFileDialog, QSlider, QLabel, QSpinBox, QFontComboBox, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QFontDatabase
from weasyprint import HTML
import platform

PLATFORM:str = platform.system()

def resource_path(relative_path: str) -> str:
    """
    获取资源的绝对路径。用于访问打包后的资源文件。

    :param relative_path: 相对路径

    :return: 绝对路径
    """
    base_path: str = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

def get_bionic_reader_folder_path(folder_name: str) -> str:
    """
    获取 BionicReader 相关资源文件夹的路径。

    :param folder_name: 文件夹名称
    :return: 文件夹路径
    """
    if PLATFORM == 'Windows':
        return os.path.join(os.environ.get('APPDATA', ''), 'BionicReader', folder_name)
    else:  # macOS and Linux
        return os.path.join(os.path.expanduser('~'), 'Library', 'Application Support', 'BionicReader', folder_name)

# 配置文件夹路径
CONFIG_FOLDER_PATH: str = get_bionic_reader_folder_path('config')

if not os.path.exists(CONFIG_FOLDER_PATH):
    os.makedirs(CONFIG_FOLDER_PATH)

# 配置文件路径
CONFIG_FILE_PATH: str = os.path.join(CONFIG_FOLDER_PATH, 'config.json')

def bionic_reading(text, bold_ratio=0.4):
    """
    使用正则表达式把文本分割成【单词】与【符号/标点】。
    对单词应用 Bionic Reading，其余符号原样保留。
    """
    tokens = re.findall(r"[A-Za-z0-9]+|[^A-Za-z0-9]+", text)
    result = []
    for token in tokens:
        if re.match(r"[A-Za-z0-9]+", token):
            bold_len = max(1, int(len(token) * bold_ratio))
            result.append(f"<b>{token[:bold_len]}</b>{token[bold_len:]}")
        else:
            result.append(token)
    return "".join(result)

def extract_text_from_pdf(pdf_path):
    """
    使用 PyMuPDF 读取 PDF 并转换为字符串。
    """
    doc = fitz.open(pdf_path)
    text = "\n".join(page.get_text("text") for page in doc)
    return text

class BionicReadingApp(QWidget):
    def __init__(self):
        super().__init__()
        self.config_file = CONFIG_FILE_PATH
        self.config = {}
        self.load_fonts()
        self.load_config()
        self.init_ui()

        if self.config.get("dark_mode", False):
            self.apply_dark_theme()
        else:
            self.apply_light_theme()

    def init_ui(self):
        """
        初始化用户界面。
        :return:
        """
        self.setWindowTitle("Bionic Reading 1.0.0")
        self.setGeometry(100, 100, 1000, 600)

        self.text_edit = QTextEdit()

        self.load_button = QPushButton("加载 PDF / TXT")
        self.load_button.clicked.connect(self.load_file)

        bold_ratio = self.config.get("bold_ratio", 40)
        self.bold_ratio_label = QLabel(f"加粗比例 ({bold_ratio}%)")
        self.bold_ratio_slider = QSlider(Qt.Horizontal)
        self.bold_ratio_slider.setRange(10, 90)
        self.bold_ratio_slider.setValue(self.config.get("bold_ratio", 40))
        self.bold_ratio_slider.valueChanged.connect(self.update_bold_ratio)

        self.font_size_label = QLabel("字号：")
        self.font_size_spinbox = QSpinBox()
        self.font_size_spinbox.setRange(8, 48)
        self.font_size_spinbox.setValue(self.config.get("font_size", 16))
        self.font_size_spinbox.valueChanged.connect(self.update_font_size)

        self.letter_spacing_label = QLabel("字距：")
        self.letter_spacing_spinbox = QSpinBox()
        self.letter_spacing_spinbox.setRange(0, 20)
        self.letter_spacing_spinbox.setValue(self.config.get("letter_spacing", 5))
        self.letter_spacing_spinbox.valueChanged.connect(self.update_spacing)

        self.line_spacing_label = QLabel("行距：")
        self.line_spacing_spinbox = QSpinBox()
        self.line_spacing_spinbox.setRange(10, 50)
        self.line_spacing_spinbox.setValue(self.config.get("line_spacing", 20))
        self.line_spacing_spinbox.valueChanged.connect(self.update_spacing)

        self.font_selector = QFontComboBox()
        self.font_selector.currentFontChanged.connect(self.update_font)
        self.font_selector.setCurrentFont(QFont(self.config.get("font_family", "Arial")))

        self.theme_switch = QCheckBox("深色模式")
        self.theme_switch.setChecked(self.config.get("dark_mode", False))
        self.theme_switch.stateChanged.connect(self.toggle_theme)

        self.refresh_button = QPushButton("刷新格式")
        self.refresh_button.clicked.connect(self.refresh_text)

        self.export_button = QPushButton("导出为 HTML 或 PDF")
        self.export_button.clicked.connect(self.export_file)

        main_layout = QHBoxLayout()
        main_layout.addWidget(self.text_edit, 3)

        control_layout = QVBoxLayout()
        control_layout.addWidget(self.load_button)
        control_layout.addWidget(self.bold_ratio_label)
        control_layout.addWidget(self.bold_ratio_slider)
        control_layout.addWidget(self.font_size_label)
        control_layout.addWidget(self.font_size_spinbox)

        self.select_font_label = QLabel("字体：")
        control_layout.addWidget(self.select_font_label)
        control_layout.addWidget(self.font_selector)

        control_layout.addWidget(self.letter_spacing_label)
        control_layout.addWidget(self.letter_spacing_spinbox)
        control_layout.addWidget(self.line_spacing_label)
        control_layout.addWidget(self.line_spacing_spinbox)
        control_layout.addWidget(self.theme_switch)
        control_layout.addWidget(self.refresh_button)
        control_layout.addWidget(self.export_button)
        control_layout.addStretch()
        control_layout.addWidget(QLabel("Ma Chenxing © 2025 BionicReader"))

        widgets = [
            self.load_button, self.bold_ratio_label, self.bold_ratio_slider,
            self.font_size_label, self.font_size_spinbox, self.font_selector,
            self.letter_spacing_label, self.letter_spacing_spinbox, self.select_font_label,
            self.line_spacing_label, self.line_spacing_spinbox, self.refresh_button,
            self.theme_switch, self.export_button
        ]
        for widget in widgets:
            widget.setFont(self.default_font)

        main_layout.addLayout(control_layout, 1)
        self.setLayout(main_layout)

    def load_config(self):
        """
        从 JSON 文件读取配置。
        如果文件不存在或出错，则使用默认值。
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Error loading config.json: {e}")
                self.config = {}
        else:
            self.config = {}

    def save_config(self):
        """
        将当前控件值写入 JSON 文件。
        """
        self.config["bold_ratio"] = self.bold_ratio_slider.value()
        self.config["font_size"] = self.font_size_spinbox.value()
        self.config["letter_spacing"] = self.letter_spacing_spinbox.value()
        self.config["line_spacing"] = self.line_spacing_spinbox.value()
        self.config["font_family"] = self.font_selector.currentFont().family()
        self.config["dark_mode"] = self.theme_switch.isChecked()

        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Error saving config.json: {e}")

    def load_fonts(self):
        """
        加载字体，如果加载失败则使用默认字体。
        :return:
        """
        font_mi_path = resource_path("MiSans-Regular.otf")
        font_mi = QFontDatabase.addApplicationFont(font_mi_path)
        if font_mi != -1:
            family_mi = QFontDatabase.applicationFontFamilies(font_mi)[0]
            self.default_font = QFont(family_mi, 10)
        else:
            print(f"Failed to load MiSans-Regular.otf from {font_mi_path}")
            self.default_font = QFont("Arial", 10)
        self.setFont(self.default_font)

    def load_file(self):
        """
        加载 PDF 或 TXT 文件。
        :return:
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "选择文件", "", "Text Files (*.txt);;PDF Files (*.pdf)"
        )
        if file_path:
            if file_path.endswith(".pdf"):
                text = extract_text_from_pdf(file_path)
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            self.display_bionic_text(text)

    def display_bionic_text(self, text):
        """
        显示 Bionic Reading 格式的文本。
        :param text:
        :return:
        """
        bold_ratio = self.bold_ratio_slider.value() / 100
        font_size = self.font_size_spinbox.value()
        font_family = self.font_selector.currentFont().family()
        letter_spacing = self.letter_spacing_spinbox.value()
        line_spacing = self.line_spacing_spinbox.value()

        processed_text = bionic_reading(text, bold_ratio)
        self.text_edit.setHtml(
            f"<div style='font-size:{font_size}pt; font-family:{font_family}; "
            f"letter-spacing:{letter_spacing}px; line-height:{line_spacing}px;'>{processed_text}</div>"
        )

    def update_bold_ratio(self):
        """
        更新加粗比例。
        :return:
        """
        ratio = self.bold_ratio_slider.value()
        self.bold_ratio_label.setText(f"加粗比例 ({ratio}%)")
        self.display_bionic_text(self.text_edit.toPlainText())
        self.save_config()

    def update_font_size(self):
        """
        更新字号。
        :return:
        """
        self.display_bionic_text(self.text_edit.toPlainText())
        self.save_config()

    def update_font(self):
        """
        更新字体。
        :return:
        """
        self.display_bionic_text(self.text_edit.toPlainText())
        self.save_config()

    def update_spacing(self):
        """
        更新字距或行距。
        :return:
        """
        self.display_bionic_text(self.text_edit.toPlainText())
        self.save_config()

    def refresh_text(self):
        """
        刷新文本格式。
        :return:
        """
        self.display_bionic_text(self.text_edit.toPlainText())

    def export_file(self):
        """
        导出为 HTML 或 PDF 文件。
        :return:
        """
        export_path, _ = QFileDialog.getSaveFileName(
            self, "导出文件", "", "HTML Files (*.html);;PDF Files (*.pdf)"
        )
        if export_path:
            content = self.text_edit.toHtml()
            if export_path.endswith(".html"):
                with open(export_path, "w", encoding="utf-8") as f:
                    f.write(content)
            elif export_path.endswith(".pdf"):
                HTML(string=content).write_pdf(export_path)

    def toggle_theme(self):
        """
        主题切换：用户勾选/取消“深色模式”时调用
        """
        if self.theme_switch.isChecked():
            self.apply_dark_theme()
        else:
            self.apply_light_theme()
        self.save_config()

    def apply_light_theme(self):
        """
        应用浅色主题。
        :return:
        """
        style_sheet = """
           QWidget {
               background-color: #f0f0f0;
           }   
           QPushButton {
               border: 2px solid #D5D5D5;  /* Dark gray border */
               border-radius: 14px;  /* Rounded corners */
               background-color: transparent;
               color: #4F4F4F;  /* Text color same as border */
               padding: 8px;
               margin: 8px;
           }

           QPushButton:hover {
               background-color: #E0E0E0;  /* Light gray on hover */
               border: 2px solid #2689FF;  /* Blue border on hover */
           }

           QPushButton:pressed {
               background-color: #A0A0A0;  /* Darker gray on press */
           }
           QComboBox {
                border: 2px solid #E6E6E6;
                border-radius: 10px;       /* 圆角 */
                background-color: transparent;
                padding: 5px;
                margin: 5px;
                color: #4F4F4F;
            }
            
            /* 鼠标悬停样式 */
            QComboBox:hover {
                border: 2px solid #2689FF;  /* 浅蓝色边框 */
                background-color: #F9F9F9;  /* 浅灰色背景 */
            }
            
            /* 下拉按钮 */
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 2px solid #E6E6E6; /* 分隔线 */
                background-color: transparent;
                border-top-right-radius: 10px;  /* 圆角 */
                border-bottom-right-radius: 10px;
            }
            
            /* 下拉箭头 */
            QComboBox::down-arrow {
                image: url(down-arrow-light.png);  /* 替换为你的箭头图标路径 */
                width: 10px;
                height: 10px;
            }
            
            /* 下拉列表样式 */
            QComboBox QAbstractItemView {
                border: 2px solid #E6E6E6;
                border-radius: 10px;
                background-color: #FFFFFF;
                selection-background-color: #2689FF;  /* 选中项背景色 */
                selection-color: #FFFFFF;             /* 选中项文字颜色 */
            }

           QLineEdit{
               border: 2px solid #E6E6E6;
               border-radius: 10px;
               background-color: transparent;
               padding: 5px;
               margin: 5px;
           }
           QLineEdit:focus {
               border: 2px solid #0265DC;
           }
           QLineEdit:focus:hover {
               border: 2px solid #0053B7;
           }
           QLineEdit:hover {
               border: 2px solid #B0B0B0;
           }

           QTextEdit {
               border: 2px solid #E6E6E6;
               border-radius: 10px;
               padding: 5px;
               margin: 5px;
               background-color: transparent;
           }
           QTextEdit:focus {
               border: 2px solid #0265DC;
           }
           QTextEdit:focus:hover {
               border: 2px solid #0053B7;
           }
           QTextEdit:hover {
               border: 2px solid #B0B0B0;
           }
           /* 垂直滚动条样式 */
               QScrollBar:vertical {
                   background: transparent;
                   width: 10px;
                   margin: 0px;
               }
               QScrollBar::handle:vertical {
                   background: #cccccc;
                   border-radius: 5px;
                   min-height: 20px;
               }
               QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                   border: none;
                   background: none;
                   height: 0px;
               }
               QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                   border: none;
                   background: none;
               }
               QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                   background: none;
               }
               /* 水平滚动条样式 */
               QScrollBar:horizontal {
                   background: transparent;
                   height: 10px;
                   margin: 0px;
               }
               QScrollBar::handle:horizontal {
                   background: #cccccc;
                   border-radius: 5px;
                   min-width: 20px;
               }
               QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                   border: none;
                   background: none;
                   width: 0px;
               }
               QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
                   border: none;
                   background: none;
               }
               QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                   background: none;
               }

           QLabel {
               color: #4F4F4F;
           }
           QCheckBox {
               color: #4F4F4F;
           }
           QCheckBox::hover {
               color: #0053B7;
           }
           QCheckBox::indicator {
               width: 10px;
               height: 10px;
               border: 2px solid #4F4F4F;
               border-radius: 3px;
               color: #4F4F4F;
           }
           QCheckBox::indicator:checked {
               background-color: #2689FF;
           }
           QCheckBox::indicator:checked:hover {
               background-color: #0053B7;
           }


           QGraphicsView {
               border: 2px solid #E6E6E6;
               border-radius: 10px;
               background-color: #a6a6a6;
               padding: 5px;
           }

           QMenuBar {
               background-color: #fefefe;
               color: #4F4F4F;

           }

           QMenuBar::item {
               background-color: transparent;
               padding: 5px 10px;
               border-radius: 5px;
           }

           QMenuBar:hover {
               color: #dadada;
           }

           QMenuBar::item:selected {
               background-color: #dadada;
           }

           QMenu {
               background-color: #fefefe;
               color: #4F4F4F;
           }

           QMenu::item {
               padding: 5px 20px;
               border-radius: 5px;
           }

           QMenu::item:selected {
               background-color: #dadada;
           }
           QPushButton[text="Cancel"] {
               border-radius: 14px;  /* Rounded corners */
               width: 50px;  /* Fixed width */
               height: 20px;  /* Fixed height */
           }
           QPushButton[text="OK"] {
                   border: 2px solid #2689FF;  /* Blue border */
                   background-color: #2689FF;  /* Blue */
                   border-radius: 14px;  /* Rounded corners */
                   width: 50px;  /* Fixed width */
                   height: 20px;  /* Fixed height */
                   color: #fefefe;  /* White text */
               }
               QPushButton[text="OK"]:hover {
                   border: 2px solid #0053B7;  /* Darker blue on hover */
                   background-color: #0053B7;  /* Darker blue on hover */
               }
               QPushButton[text="OK"]:pressed {
                   border: 2px solid #004299;  /* Dark blue on press */
                   background-color: #004299;  /* Dark blue on press */
           }

           QSpinBox {
               color: #4F4F4F; /* 深色文本 */
               border: 2px solid #E6E6E6; /* 边框颜色 */
               border-radius: 5px; /* 圆角 */
               padding: 2px; /* 内边距 */
               background-color: transparent; /* 背景色 */
           }

           QSpinBox:hover {
               border: 2px solid #2689FF; /* 悬停时边框颜色 */
           }

           QSpinBox:focus {
               border: 2px solid #0053B7; /* 聚焦时边框颜色 */
               background-color: #efefef; /* 聚焦时背景色 */
           }

           /* 上按钮样式 */
           QSpinBox::up-button {
               background-color: #E0E0E0; /* 按钮背景色 */
               border: none; /* 无边框 */
               border-top-right-radius: 4px; /* 上按钮圆角 */
               width: 15px; /* 按钮宽度 */
           }

           QSpinBox::up-button:hover {
               background-color: #D0D0D0; /* 悬停时按钮背景色 */
           }

           QSpinBox::up-button:pressed {
               background-color: #C0C0C0; /* 按下时按钮背景色 */
           }

           /* 下按钮样式 */
           QSpinBox::down-button {
               background-color: #E0E0E0; /* 按钮背景色 */
               border: none; /* 无边框 */
               border-bottom-right-radius: 4px; /* 下按钮圆角 */
               width: 15px; /* 按钮宽度 */
           }

           QSpinBox::down-button:hover {
               background-color: #D0D0D0; /* 悬停时按钮背景色 */
           }

           QSpinBox::down-button:pressed {
               background-color: #C0C0C0; /* 按下时按钮背景色 */
           }

           /* 箭头样式 */
           QSpinBox::up-arrow {
               width: 8px; /* 箭头宽度 */
               height: 8px; /* 箭头高度 */
               image: url(up-arrow-light.png); /* 自定义上箭头图片 */
           }

           QSpinBox::up-arrow:hover {
               width: 9px; /* 悬停时箭头大小 */
               height: 9px;
           }

           QSpinBox::down-arrow {
               width: 8px; /* 箭头宽度 */
               height: 8px; /* 箭头高度 */
               image: url(down-arrow-light.png); /* 自定义下箭头图片 */
           }

           QSpinBox::down-arrow:hover {
               width: 9px; /* 悬停时箭头大小 */
               height: 9px;
           }

           /* 禁用状态 */
           QSpinBox:disabled {
               background-color: #F0F0F0; /* 禁用时背景色 */
               color: #A0A0A0; /* 禁用时文本颜色 */
               border: 2px solid #D0D0D0; /* 禁用时边框颜色 */
           }

           QSpinBox::up-button:disabled, QSpinBox::down-button:disabled {
               background-color: #E0E0E0; /* 禁用时按钮背景色 */
           }

           QSpinBox::up-arrow:disabled, QSpinBox::down-arrow:disabled {
               image: url(disabled-arrow-light.png); /* 禁用时箭头图片 */
           }

           """
        self.setStyleSheet(style_sheet)
        self.setFont(self.default_font)

    def apply_dark_theme(self):
        """
        应用深色主题。
        :return:
        """
        style_sheet = """
           QWidget {
               background-color: #1E1E1E;  /* Dark background color */

           }

           QPushButton {
               border: 2px solid #4A4A4A;  /* Border with dark gray color */
               border-radius: 14px;  /* Rounded corners */
               background-color: #2E2E2E;  /* Dark background color */
               color: #D9D9D9;  /* Light gray text color */
               padding: 8px;
               margin: 8px;
           }

           QPushButton:hover {
               background-color: #3A3A3A;  /* Slightly lighter on hover */
               border: 2px solid #2689ff;  /* Slightly darker border on hover */
           }

           QPushButton:pressed {
               background-color: #5A5A5A;  /* Slightly darker on press */
           }
          

           QLineEdit{
               border: 2px solid #4A4A4A; /* Dark gray border */
               border-radius: 10px; /* Rounded corners */
               background-color: #2E2E2E; /* Dark background */
               padding: 5px; /* Padding */
               margin: 5px; /* Margin */
               color: #E6E6E6; /* Light gray text color */
           }
           QLineEdit:focus {
               border: 2px solid #2689FF; /* Blue border on focus */
           }
           QLineEdit:focus:hover {
               border: 2px solid #0053B7; /* Darker blue border on hover */
           }
           QLineEdit:hover {
               border: 2px solid #6A6A6A; /* Darker gray border on hover */
           }
            QComboBox {
                border: 2px solid #4A4A4A;
                border-radius: 10px;
                background-color: #2E2E2E;
                padding: 5px;
                margin: 5px;
                color: #E6E6E6;
            }
    }
    QComboBox:hover {
        border: 2px solid #2689FF;
        background-color: #3A3A3A;
    }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right;
        width: 20px;
        border-left: 2px solid #4A4A4A;
        background-color: transparent;
        border-top-right-radius: 10px;
        border-bottom-right-radius: 10px;
    }
    QComboBox::down-arrow {
        image: url(down-arrow-light.png);
        width: 10px;
        height: 10px;
    }
    QComboBox QAbstractItemView {
        border: 2px solid #4A4A4A;
        border-radius: 10px;
        background-color: #2E2E2E;
        selection-background-color: #2689FF;
        selection-color: #FFFFFF;
        color: #E6E6E6;
    }
           QTextEdit {
               border: 2px solid #4A4A4A;
               border-radius: 10px;
               padding: 5px;
               margin: 5px;
               background-color: #2E2E2E;
               color: #E6E6E6;
           }
           QTextEdit:focus {
               border: 2px solid #2689FF;
           }
           QTextEdit:focus:hover {
               border: 2px solid #0053B7;
           }
           QTextEdit:hover {
               border: 2px solid #6A6A6A;
           }

           QLabel {
               color: #D9D9D9;  /* Light gray text color */

           }
           /* 垂直滚动条样式 */
               QScrollBar:vertical {
                   background: #2E2E2E;
                   width: 10px;
                   margin: 0px;

               }
               QScrollBar::handle:vertical {
                   background: #aaa;
                   border-radius: 5px;
                   min-height: 20px;
               }
               QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                   border: none;
                   background: none;
                   height: 0px;
               }
               QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                   border: none;
                   background: none;
               }
               QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                   background: none;
               }
               /* 水平滚动条样式 */
               QScrollBar:horizontal {
                   background: #2E2E2E;
                   height: 10px;
                   margin: 0px;

               }
               QScrollBar::handle:horizontal {
                   background: #cccccc;
                   border-radius: 5px;
                   min-width: 20px;
               }
               QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                   border: none;
                   background: none;
                   width: 0px;
               }
               QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {
                   border: none;
                   background: none;
               }
               QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                   background: none;
               }

           QCheckBox {
               color: #D9D9D9;
           }
           QCheckBox:hover {
               color: #2689FF;  /* Slightly blue hover color */
           }
           QCheckBox::indicator {
               width: 10px;
               height: 10px;
               border: 2px solid #D9D9D9;
               border-radius: 3px;
               background-color: #2E2E2E;
           }
           QCheckBox::indicator:checked {
               background-color: #2689FF;
           }
           QCheckBox::indicator:checked:hover {
               background-color: #0053B7;
           }

           QGraphicsView {
               border: 2px solid #4A4A4A;
               border-radius: 10px;
               background-color: #2E2E2E;
               padding: 5px;
           }

           QMenuBar {
               background-color: #1F1F1F;  /* Dark background */
               color: #D9D9D9;  /* Light text color */
           }

           QMenuBar::item {
               background-color: transparent;
               padding: 5px 10px;
               border-radius: 5px;
           }

           QMenuBar::item:selected {
               background-color: #3A3A3A;  /* Slight highlight */
           }

           QMenu {
               background-color: #1F1F1F;  /* Menu dark background */
               color: #D9D9D9;  /* Light text color */
           }
           QMenu:hover {
               color: #D9D9D9;  /* Light text color */
           }

           QMenu::item {
               padding: 5px 20px;
               border-radius: 5px;
           }

           QMenu::item:selected {
               background-color: #3A3A3A;  /* Slight highlight on selection */
           }
           QPushButton[text="OK"] {
               background-color: #2689FF; /* 按钮背景色 */
               color: #FFFFFF; /* 按钮文本颜色 */
               border: 2px solid #0053B7; /* 边框颜色 */
               border-radius: 6px; /* 圆角 */
               padding: 5px 10px; /* 内边距 */
           }
           QPushButton[text="Cancel"] {
               border-radius: 14px;  /* Rounded corners */
               width: 50px;  /* Fixed width */
               height: 20px;  /* Fixed height */
           }
           QPushButton[text="OK"] {
                   border: 2px solid #2689FF;  /* Blue border */
                   background-color: #2689FF;  /* Blue */
                   border-radius: 14px;  /* Rounded corners */
                   width: 50px;  /* Fixed width */
                   height: 25px;  /* Fixed height */
                   color: #fefefe;  /* White text */
               }
               QPushButton[text="OK"]:hover {
                   border: 2px solid #0053B7;  /* Darker blue on hover */
                   background-color: #0053B7;  /* Darker blue on hover */
               }
               QPushButton[text="OK"]:pressed {
                   border: 2px solid #004299;  /* Dark blue on press */
                   background-color: #004299;  /* Dark blue on press */
           }
           QSpinBox {
               background-color: #2E2E2E; /* 深色背景 */
               color: #D9D9D9; /* 文本颜色 */
               border: 2px solid #4A4A4A; /* 边框颜色 */
               border-radius: 5px; /* 圆角 */
               padding: 2px; /* 内边距 */
           }

           QSpinBox:hover {
               border: 2px solid #2689FF; /* 悬停时边框颜色 */
           }

           QSpinBox:focus {
               border: 2px solid #0053B7; /* 聚焦时边框颜色 */
           }

           /* 上按钮样式 */
           QSpinBox::up-button {
               background-color: #4A4A4A; /* 按钮背景色 */
               border: none; /* 无边框 */
               border-top-right-radius: 4px; /* 上按钮圆角 */
               width: 15px; /* 按钮宽度 */
           }

           QSpinBox::up-button:hover {
               background-color: #5A5A5A; /* 悬停时按钮背景色 */
           }

           QSpinBox::up-button:pressed {
               background-color: #3A3A3A; /* 按下时按钮背景色 */
           }

           /* 下按钮样式 */
           QSpinBox::down-button {
               background-color: #4A4A4A; /* 按钮背景色 */
               border: none; /* 无边框 */
               border-bottom-right-radius: 4px; /* 下按钮圆角 */
               width: 15px; /* 按钮宽度 */
           }

           QSpinBox::down-button:hover {
               background-color: #5A5A5A; /* 悬停时按钮背景色 */
           }

           QSpinBox::down-button:pressed {
               background-color: #3A3A3A; /* 按下时按钮背景色 */
           }

           """
        self.setStyleSheet(style_sheet)
        self.setFont(self.default_font)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BionicReadingApp()
    window.show()
    sys.exit(app.exec())