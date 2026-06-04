
import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'main.py',
    '--name=大创项目背景数据生成工具',
    '--onefile',
    '--windowed',
    '--noconsole',
    '--clean',
    '--add-data=config_manager.py;.',
    '--add-data=llm_client.py;.',
    '--add-data=file_parser.py;.',
    '--add-data=data_auditor.py;.',
    '--add-data=exporter.py;.',
    '--hidden-import=PyQt5',
    '--hidden-import=PyQt5.QtCore',
    '--hidden-import=PyQt5.QtGui',
    '--hidden-import=PyQt5.QtWidgets',
    '--hidden-import=requests',
    '--hidden-import=openpyxl',
    '--hidden-import=PyPDF2',
    '--hidden-import=docx',
    '--hidden-import=cryptography',
])

