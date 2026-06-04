# -*- coding: utf-8 -*-
import requests
import json
import traceback
import time
import re
from logger import get_logger

logger = get_logger()


class LLMClient:
    def __init__(self, model_type, api_key):
        self.model_type = model_type
        self.api_key = api_key
        logger.info(f"LLMClient初始化，模型类型: {model_type}")

    def call_llm(self, prompt):
        logger.debug(f"调用大模型，提示词长度: {len(prompt)}")
        try:
            if self.model_type == "doubao":
                result = self._call_doubao(prompt)
            elif self.model_type == "tongyi" or self.model_type == "openrouter":
                # 统一使用阿里云百炼（兼容OpenAI格式）
                result = self._call_aliyun(prompt)
            else:
                raise ValueError(f"不支持的模型类型: {self.model_type}")
            
            logger.debug(f"大模型调用完成，响应长度: {len(result) if result else 0}")
            return result
        except Exception as e:
            logger.error(f"大模型调用异常: {str(e)}", exc_info=True)
            raise

    def _call_aliyun(self, prompt):
        """调用阿里云百炼API - 兼容OpenAI格式"""
        logger.info("开始调用阿里云百炼API...")
        url = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "qwen-plus",
            "messages": [
                {"role": "system", "content": "你是一个精确的数据提取器，只输出JSON，不添加任何其他文字。"},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 2000
        }
        
        max_retries = 3
        last_error = None
        
        for attempt in range(max_retries):
            try:
                logger.info(f"发送请求 (尝试 {attempt+1}/{max_retries})，文本长度: {len(prompt)}")
                response = requests.post(
                    url, 
                    headers=headers, 
                    json=payload, 
                    timeout=120
                )
                
                response.encoding = 'utf-8'
                logger.info(f"HTTP响应状态码: {response.status_code}")
                
                if response.status_code in [400, 500]:
                    error_info = f"{response.status_code}错误，响应内容: {response.text}"
                    logger.warning(error_info)
                    
                    if attempt < max_retries - 1:
                        wait_time = 2
                        logger.info(f"等待 {wait_time} 秒后重试...")
                        time.sleep(wait_time)
                        last_error = error_info
                        continue
                
                response.raise_for_status()
                result = response.json()
                
                logger.info("阿里云百炼API调用成功")
                if "choices" in result and len(result["choices"]) > 0:
                    return result["choices"][0]["message"]["content"]
                else:
                    error_msg = f"API响应格式异常: {result}"
                    logger.error(error_msg)
                    return error_msg
                
            except Exception as e:
                logger.error(f"阿里云百炼API调用失败 (尝试 {attempt+1}): {str(e)}", exc_info=True)
                
                if attempt < max_retries - 1:
                    wait_time = 2
                    logger.info(f"等待 {wait_time} 秒后重试...")
                    time.sleep(wait_time)
                    last_error = str(e)
                else:
                    print("="*60)
                    print("完整错误堆栈:")
                    print("="*60)
                    traceback.print_exc()
                    print("="*60)
                    return f"调用阿里云百炼API失败: {str(e)}"
        
        return f"调用阿里云百炼API失败，已重试{max_retries}次。最后错误: {last_error}"

    def _call_doubao(self, prompt):
        """调用豆包API（保留但不建议用）"""
        logger.info("调用豆包API...")
        url = "https://ark.cn-beijing.volces.com/api/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {
            "model": "ep-20241212121212-xxxxx",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            response.encoding = 'utf-8'
            response.raise_for_status()
            
            result = response.json()
            logger.info("豆包API调用成功")
            return result["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"豆包API调用失败: {str(e)}", exc_info=True)
            return f"调用豆包API失败: {str(e)}"
