
# 大创项目背景数据生成工具

## 项目简介
这是一个基于PyQt5开发的Windows桌面工具，用于帮助大学生创新创业项目快速生成标准化的背景数据。

## 功能特性
- 支持豆包、通义千问等主流大模型API
- API Key加密存储，安全可靠
- 支持导入项目申报书和参考文献（PDF/Word）
- 内置数据审核机制，确保数据质量
- 一键导出Excel和Word格式报告
- 单文件EXE，免安装运行

## 安装依赖
```bash
pip install -r requirements.txt
```

## 运行程序
```bash
python main.py
```

## 打包为EXE
```bash
python build.py
```

## 使用说明
1. 在"API配置"标签页配置大模型API Key
2. 在"生成数据"标签页输入项目关键词
3. 可选：导入项目申报书和参考文献
4. 点击"生成数据"按钮
5. 在"结果展示"标签页查看结果并导出

## 技术栈
- PyQt5: 界面开发
- requests: API请求
- python-docx: Word文件处理
- PyPDF2: PDF文件处理
- openpyxl: Excel文件处理
- cryptography: 加密模块
- PyInstaller: 打包工具

