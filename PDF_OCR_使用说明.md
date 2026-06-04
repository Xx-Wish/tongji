# 百度OCR PDF解析功能 - 使用说明
============================================

## 📋 功能概述

本工具已完全升级PDF解析方案，采用**PyMuPDF + 百度高精度OCR**双剑合璧方案，彻底解决PDF乱码问题。

## 🔧 系统要求

### 必需依赖包

请确保安装以下Python库：

```bash
pip install pymupdf requests
```

或者使用提供的 requirements.txt：

```bash
pip install -r requirements.txt
```

## 🚀 快速开始

### 第一步：配置百度OCR密钥

1. 前往[百度智能云](https://cloud.baidu.com/)
2. 登录/注册账号
3. 开通**文字识别OCR**服务（免费额度充足）
4. 创建应用，获取：
   - API Key
   - Secret Key

### 第二步：在工具中配置

1. 打开工具
2. 切换到「API配置&规则」标签页
3. 在「百度OCR配置」区域：
   - 输入API Key（密码显示，自动加密存储
   - 输入Secret Key（密码显示，自动加密存储
4. 点击「保存OCR配置」

### 第三步：导入PDF文件

1. 点击「导入项目申报书」或「导入参考文献」
2. 选择PDF文件
3. 工具会自动：
   - 使用PyMuPDF将PDF转300DPI高清图片
   - 调用百度高精度OCR识别文字
   - 显示解析进度（正在解析第X页/共Y页
4. 解析完成后自动提示🎉

## ✨ 核心特性

### 1. 完美支持各种PDF

✅ **LaTeX自定义字体**：OCR直接识别，不依赖字体
✅ **分栏论文**：完美支持两栏/三栏
✅ **扫描版PDF**：像扫描仪一样识别图片
✅ **加密PDF**：支持标准PDF
✅ **图片版PDF**：完美识别

### 2. 完整错误处理

| 错误类型 | 提示信息 |
|---------|---------|
| 未安装PyMuPDF | 提示运行 pip install pymupdf |
| 未配置OCR密钥 | 详细配置引导步骤 |
| 密钥错误 | 检查密钥配置 |
| 网络错误 | 提示检查网络 |
| 无法打开PDF | 检查文件是否损坏 |
| 识别失败 | 显示具体错误原因 |

### 3. 进度显示

- 解析前：正在打开文件...
- 解析中：正在解析第X页/共Y页
- 完成后：🎉 PDF解析完成！已识别文字：XXXX字

## 🔒 安全保障

- API Key和Secret Key本地加密存储
- 使用cryptography库加密
- 下次打开自动读取，无需重复输入
- 百度OCR的access_token缓存30天

## 🔄 完整流程

```
导入PDF文件
    ↓
FileParser._parse_pdf()
    ↓
使用PyMuPDF打开PDF
    ↓
每一页转300DPI图片
    ↓
百度高精度OCR识别
    ↓
合并为纯净文本
    ↓
送入数据审核、整合模块
    ↓
项目-文献相关性分析
    ↓
输出结果
```

## 📦 打包说明

### 使用PyInstaller打包

确保包含所有依赖：

```bash
pyinstaller --onefile --windowed --name "大创项目文献政策统计分析工具" --add-data "requirements.txt;." main.py
```

打包时会自动包含：
- PyQt5
- PyMuPDF
- requests
- python-docx
- openpyxl
- cryptography
- 等等...

## ⚠️ 常见问题

### Q: OCR识别速度慢怎么办？

A: 百度OCR需要网络请求，每页约1-3秒/页，多页PDF需要耐心等待。进度条会实时显示。

### Q: 识别准确率不高？

A: 请确保PDF清晰，300DPI已经是最佳识别精度。

### Q: 免费额度够吗？

A: 百度OCR免费版每天有充足的调用次数，个人使用完全足够。

### Q: Word文件需要OCR吗？

A: 不需要！Word文件继续使用原来的python-docx解析，速度快且准确。

### Q: 必须配置了OCR密钥，但还是报错？

A: 请检查：
1. 网络连接
2. API Key和Secret Key是否正确
3. 百度OCR服务是否已开通

## 📞 技术细节

### 百度OCR API

- 接口：`accurate_basic`（高精度版
- 语言：`CHN_ENG`（中英混合
- 图片：300DPI PNG
- 超时：单页60秒

### PyMuPDF配置

```python
zoom = 300 / 72  # DPI转换
mat = fitz.Matrix(zoom, zoom)
pix = page.get_pixmap(matrix=mat, alpha=False)
```

## 📝 更新日志

### v2.0 (当前版本
- ✅ 完全重构PDF解析方案
- ✅ 集成百度高精度OCR
- ✅ 300DPI高清渲染
- ✅ 完整错误处理
- ✅ 实时进度显示
- ✅ 密钥加密本地存储
