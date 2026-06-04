# -*- coding: utf-8 -*-
from docx import Document
import os
import re
import requests
import base64
import io
import json
from pathlib import Path
import tempfile

# 尝试导入PyMuPDF
try:
    import fitz
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False


class FileParser:
    # 百度OCR Access Token缓存
    _baidu_access_token = None
    _token_expire_time = 0
    
    # 进度回调
    progress_callback = None
    
    @staticmethod
    def set_progress_callback(callback):
        FileParser.progress_callback = callback
    
    @staticmethod
    def parse_file(file_path, config_manager=None):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".docx" or ext == ".doc":
            return FileParser._parse_docx(file_path)
        elif ext == ".pdf":
            return FileParser._parse_pdf(file_path, config_manager)
        elif ext == ".txt":
            return FileParser._parse_txt(file_path)
        else:
            raise ValueError(f"不支持的文件格式: {ext}")

    @staticmethod
    def _parse_docx(file_path):
        doc = Document(file_path)
        text = []
        for para in doc.paragraphs:
            text.append(para.text)
        return "\n".join(text)

    @staticmethod
    def _parse_pdf(file_path, config_manager=None):
        if not PYMUPDF_AVAILABLE:
            raise ImportError("需要安装PyMuPDF库：\n请运行命令 pip install pymupdf")
        
        if not config_manager:
            raise ValueError("需要配置管理器来获取百度OCR密钥")
        
        # 获取百度OCR密钥
        api_key, secret_key = config_manager.get_baidu_keys()
        if not api_key or not secret_key:
            raise ValueError("请先在设置中配置百度OCR的API Key和Secret Key！\n\n操作步骤：\n1. 前往百度智能云 https://cloud.baidu.com/\n2. 开通文字识别OCR服务\n3. 创建应用获取API Key和Secret Key\n4. 在工具的「API配置&规则」页面配置并保存")
        
        try:
            # 获取Access Token
            access_token = FileParser._get_baidu_access_token(api_key, secret_key)
        except Exception as e:
            error_str = str(e)
            if "network" in error_str.lower() or "request" in error_str.lower():
                raise Exception(f"网络连接失败，请检查网络连接后重试：\n{error_str}")
            elif "invalid" in error_str.lower() or "error" in error_str.lower():
                raise Exception(f"百度OCR密钥错误，请检查配置：\n{error_str}")
            else:
                raise Exception(f"获取百度OCR授权失败：\n{error_str}")
        
        try:
            # 使用PyMuPDF打开PDF
            doc = fitz.open(file_path)
        except Exception as e:
            raise Exception(f"无法打开PDF文件：\n{str(e)}\n请检查文件是否损坏或格式正确。")
        
        total_pages = doc.page_count
        all_text = []
        
        try:
            for page_num in range(total_pages):
                if FileParser.progress_callback:
                    FileParser.progress_callback(page_num + 1, total_pages)
                
                page = doc[page_num]
                
                # 渲染为300DPI的图片
                zoom = 300 / 72
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat, alpha=False)
                
                # 转换为PNG
                img_data = pix.tobytes("png")
                
                # 使用百度OCR识别
                ocr_result = FileParser._baidu_ocr_recognize(img_data, access_token)
                all_text.append(ocr_result)
        except Exception as e:
            raise Exception(f"PDF解析过程中出错（第{page_num+1}页）：\n{str(e)}")
        finally:
            doc.close()
        
        final_text = "\n".join(all_text)
        if not final_text.strip():
            raise Warning("PDF解析完成，但未识别到任何文字内容。\n请检查PDF是否为扫描版或图片版。")
        
        return final_text
    
    @staticmethod
    def _get_baidu_access_token(api_key, secret_key):
        # 检查缓存的token是否有效
        import time
        current_time = time.time()
        if FileParser._baidu_access_token and current_time < FileParser._token_expire_time:
            return FileParser._baidu_access_token
        
        url = "https://aip.baidubce.com/oauth/2.0/token"
        params = {
            "grant_type": "client_credentials",
            "client_id": api_key,
            "client_secret": secret_key
        }
        
        try:
            response = requests.get(url, params=params, timeout=30)
            result = response.json()
            
            if "access_token" in result:
                FileParser._baidu_access_token = result["access_token"]
                # token有效期约30天，提前2小时过期
                FileParser._token_expire_time = current_time + (30 * 24 * 60 * 60 - 2 * 60 * 60)
                return FileParser._baidu_access_token
            else:
                error_msg = result.get("error_description", "未知错误")
                raise Exception(f"获取百度Access Token失败：{error_msg}")
        
        except requests.RequestException as e:
            raise Exception(f"网络请求失败：{str(e)}")
    
    @staticmethod
    def _baidu_ocr_recognize(img_data, access_token):
        # 图片base64编码
        img_base64 = base64.b64encode(img_data).decode('utf-8')
        
        url = f"https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic?access_token={access_token}"
        
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        
        data = {
            'image': img_base64,
            'language_type': 'CHN_ENG'
        }
        
        try:
            response = requests.post(url, headers=headers, data=data, timeout=60)
            result = response.json()
            
            if "error_code" in result:
                error_msg = result.get("error_msg", "未知错误")
                raise Exception(f"百度OCR识别失败：{error_msg}")
            
            # 提取识别结果
            words_result = result.get("words_result", [])
            texts = [item.get("words", "") for item in words_result]
            
            return "\n".join(texts)
        
        except requests.RequestException as e:
            raise Exception(f"OCR网络请求失败：{str(e)}")

    @staticmethod
    def _parse_txt(file_path):
        # 尝试多种编码格式
        encodings = ['utf-8', 'gbk', 'gb18030', 'utf-16', 'utf-16-le', 'utf-16-be']
        for encoding in encodings:
            try:
                with open(file_path, "r", encoding=encoding, errors="strict") as f:
                    return f.read()
            except (UnicodeDecodeError, UnicodeError):
                continue
        # 如果所有编码都失败，最后尝试用utf-8并替换
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
        except Exception:
            return ""
