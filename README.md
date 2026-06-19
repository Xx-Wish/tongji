# 大创项目背景数据生成工具

<p align="center">
  <b>🚀 基于大模型 API 的大学生创新创业项目背景数据一键生成工具</b>
</p>

---

## 📖 项目简介

本项目是一个基于 **PyQt5** 开发的 Windows 桌面应用程序，旨在帮助大学生创新创业团队快速、高效地生成标准化的项目背景数据。通过接入豆包、通义千问等主流大语言模型 API，结合项目申报书、参考文献等资料，自动生成高质量、可直接用于项目申报的数据分析报告。

**适用场景**：大学生创新创业训练计划项目（大创项目）的数据调研、文献分析、背景数据生成等环节。

---

## ✨ 功能特性

| 模块 | 功能说明 |
|------|---------|
| 🔑 **API 配置** | 支持豆包（Doubao）、通义千问（Tongyi）、百度 OCR 等主流大模型 API |
| 🔒 **安全存储** | API Key 采用 Fernet 加密算法本地存储，保障密钥安全 |
| 📄 **文件导入** | 支持导入项目申报书（Word/PDF）和参考文献（PDF） |
| 🤖 **智能解析** | 自动识别文档类型，提取结构化量化数据 |
| 🔍 **数据审核** | 内置数据质量审核机制，确保生成数据准确可靠 |
| 📊 **一键导出** | 支持导出 Excel（.xlsx）和 Word（.docx）格式报告 |
| 🌐 **网络检索** | 支持从知网等学术平台抓取补充数据 |
| 📦 **单文件 EXE** | 支持 PyInstaller 打包为单文件，免安装运行 |

---

## 🏗️ 项目架构

```
tongji/
├── main.py              # 主程序入口（PyQt5 GUI）
├── config_manager.py    # 配置文件管理与加密存储
├── llm_client.py        # 大模型 API 客户端（豆包/通义千问）
├── file_parser.py       # PDF/Word 文件解析模块
├── data_auditor.py      # 数据质量审核模块
├── exporter.py          # 数据导出（Excel/Word）
├── web_scraper.py       # 网络数据抓取模块
├── logger.py            # 日志系统
├── build.py             # PyInstaller 打包脚本
├── batch_config.yaml    # 批量配置模板
├── requirements.txt     # 项目依赖清单
├── PDF_OCR_使用说明.md  # PDF OCR 使用说明
├── 日志使用说明.md      # 日志系统使用说明
├── README.md            # 本文件
├── test_api.py          # API 测试脚本
├── test_aliyun_api.py   # 阿里云 API 测试脚本
├── test_encoding.py     # 编码测试脚本
└── data/                # 协作数据模块
    ├── progress.py      # 成员进度追踪
    └── changelog.py     # 更新日志记录
```

---

## 🚀 快速开始

### 环境要求

| 依赖 | 最低版本 | 说明 |
|------|---------|------|
| Python | 3.8+ | 推荐 Python 3.10 |
| 操作系统 | Windows 10/11 | 64 位系统 |
| 内存 | 4GB+ | 处理大文件建议 8GB |
| 磁盘 | 500MB | 含依赖安装空间 |

### 安装步骤

```bash
# 1. 克隆仓库
git clone https://github.com/Xx-Wish/tongji.git
cd tongji

# 2. 创建虚拟环境（推荐）
python -m venv venv
venv\Scripts\activate  # Windows

# 3. 安装依赖
pip install -r requirements.txt

# 4. 运行程序
python main.py
```

### 打包为 EXE

```bash
python build.py
```

生成的 EXE 文件位于 `dist/` 目录下，可直接分发给未安装 Python 的用户使用。

---

## 📘 使用教程

### 第一步：配置 API Key

1. 启动程序后，切换到 **"API 配置"** 标签页
2. 选择大模型类型（豆包 / 通义千问）
3. 输入对应的 API Key
4. 点击 **"保存配置"**，API Key 将加密存储在本地

> 💡 **提示**：API Key 只需配置一次，下次启动程序会自动加载。

### 第二步：生成数据

1. 切换到 **"生成数据"** 标签页
2. 在输入框中填写项目关键词（如"智慧校园"、"碳中和"等）
3. 可选：点击 **"导入文件"** 上传项目申报书或参考文献（PDF/Word）
4. 点击 **"生成数据"** 按钮
5. 等待进度条完成

### 第三步：查看与导出

1. 切换到 **"结果展示"** 标签页查看生成的数据
2. 点击 **"导出 Excel"** 或 **"导出 Word"** 保存结果

---

## 🔧 配置说明

### API 支持列表

| 模型 | 获取方式 | 状态 |
|------|---------|------|
| 豆包（Doubao） | 火山引擎控制台 | ✅ 支持 |
| 通义千问（Tongyi） | 阿里云控制台 | ✅ 支持 |
| 百度 OCR | 百度智能云 | ✅ 支持 |

### 配置文件位置

- 加密配置文件：`<程序目录>/.dachuang_tool/config.json`
- 加密密钥文件：`<程序目录>/.dachuang_tool/key.key`

> ⚠️ **安全提示**：请勿将 `key.key` 文件分享给他人，该文件用于解密你的 API Key。

---

## 🛠️ 技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| PyQt5 | ≥5.15.0 | GUI 界面框架 |
| requests | ≥2.28.0 | HTTP 请求 / API 调用 |
| python-docx | ≥0.8.11 | Word 文档读写 |
| PyMuPDF | ≥1.23.0 | PDF 文档解析 |
| openpyxl | ≥3.1.0 | Excel 文件读写 |
| cryptography | ≥41.0.0 | API Key 加密存储 |

---

## 👥 团队成员

| 角色 | GitHub | 任务分工 |
|------|--------|---------|
| 组长 | [Xx-Wish](https://github.com/Xx-Wish) | 创建仓库、搭建框架、管理 Issue 与 PR |
| 组员 A | [yxy-code-ux](https://github.com/yxy-code-ux) | 完善 README 文档与项目介绍 |
| 组员 B | [lighter888](https://github.com/lighter888) | 制作日志系统 |
| 组员 C | [Firefly0688](https://github.com/Firefly0688) | 制作 API 本地存储功能 |
| 组员 D | [xuanxuanxuan777](https://github.com/xuanxuanxuan777) | 制作历史记录功能 |

---

## ❓ 常见问题（FAQ）

<details>
<summary><b>Q1：为什么点击"生成数据"后没有反应？</b></summary>
<p>请检查：</p>
<ul>
  <li>是否已在"API 配置"页面正确配置并保存了 API Key</li>
  <li>API Key 是否有效（未过期、有额度）</li>
  <li>网络连接是否正常</li>
  <li>查看日志文件 <code>dachuang_tool.log</code> 了解详细错误信息</li>
</ul>
</details>

<details>
<summary><b>Q2：PDF 文件导入后解析失败？</b></summary>
<p>请确认：</p>
<ul>
  <li>PDF 文件未被加密或损坏</li>
  <li>PDF 内容是文本格式而非扫描图片（扫描版 PDF 需要配置百度 OCR）</li>
  <li>文件大小不超过 50MB</li>
</ul>
</details>

<details>
<summary><b>Q3：如何查看程序运行日志？</b></summary>
<p>程序运行时会在目录下生成 <code>dachuang_tool.log</code> 文件，记录了所有操作的详细信息，包括 API 请求、文件解析、错误追踪等。可以使用记事本或 VS Code 打开查看。</p>
</details>

<details>
<summary><b>Q4：生成的数据不准确怎么办？</b></summary>
<p>建议：</p>
<ul>
  <li>提供更具体、更专业的关键词</li>
  <li>导入相关的参考文献和申报书作为上下文</li>
  <li>尝试切换不同的大模型获取更好的结果</li>
</ul>
</details>

---

## 📄 开源协议

本项目仅用于学习和教育目的。请遵守各 API 提供商的使用条款。

---

## 📝 更新日志

| 版本 | 日期 | 内容 |
|------|------|------|
| v0.1 | 2026-06 | 组长创建初始项目，搭建 PyQt5 基础框架 |
| v0.2 | 2026-06 | 组员 A 完善 README 文档，补充详细说明 |
| v0.3 | 2026-06 | 组员 D 完善成员合作信息，补充全部成员 GitHub 账户，创建 data/progress.py 与 data/changelog.py |
