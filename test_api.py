# -*- coding: utf-8 -*-
"""
测试OpenRouter API编码是否修复
"""
import sys
import os

# 导入我们的LLM客户端
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from llm_client import LLMClient
from logger import get_logger

logger = get_logger()

print("="*70)
print("OpenRouter API编码测试")
print("="*70)

# 测试文本 - 包含中文字符
test_text = """【需要分析的论文文本】：
民族学刊 2023年第1期

摘要：本文研究缅籍华人在云南的生活现状。调研发现，当地共有约2000名缅籍居民，其中65%表示有创业意愿。市场规模约120亿元，年增长率达到28%。

关键词：民族学刊、缅籍华人、市场分析

【提取要求】：
从上面的论文文本中提取所有量化统计数据，按大创6个维度分类输出，每一条标注【来源：导入文献】
"""

print(f"\n测试文本长度: {len(test_text)} 字符")
print(f"前200字符:\n{repr(test_text[:200])}")

print("\n" + "="*70)
print("请输入OpenRouter API Key进行测试 (如果没有，直接回车跳过):")
print("="*70)
api_key = input().strip()

if api_key:
    print("\n正在测试...")
    
    try:
        llm = LLMClient("openrouter", api_key)
        result = llm.call_llm(test_text)
        
        print("\n" + "="*70)
        print("✅ API调用成功！")
        print("="*70)
        print(f"\n响应长度: {len(result)} 字符")
        print("\n响应内容:")
        print("-"*70)
        print(result[:500])
        if len(result) > 500:
            print("... (内容已截断)")
        
    except Exception as e:
        print("\n" + "="*70)
        print("❌ API调用失败")
        print("="*70)
        print(f"\n错误: {str(e)}")
        import traceback
        print("\n完整堆栈:")
        traceback.print_exc()
else:
    print("\n跳过API测试。")

print("\n" + "="*70)
print("测试完成。")
print("="*70)
