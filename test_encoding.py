# -*- coding: utf-8 -*-
"""
编码测试脚本 - 验证中文文本在发送到API前是否正常
"""

import sys
import json

print("=" * 60)
print("Python编码环境测试")
print("=" * 60)

# 检查默认编码
print(f"1. sys.getdefaultencoding(): {sys.getdefaultencoding()}")
print(f"2. sys.stdout.encoding: {sys.stdout.encoding}")
print(f"3. sys.stdin.encoding: {sys.stdin.encoding}")

# 测试中文文本
test_text = """
【需要分析的论文文本】：
民族學刊 2023年第1期

摘要：本文研究缅籍华人在云南的生活现状。调研发现，当地共有约2000名缅籍居民，其中65%表示有创业意愿。市场规模约120亿元，年增长率达到28%。

关键词：民族學刊、缅籍华人、市场分析

【提取要求】：
从上面的论文文本中提取所有量化统计数据，按大创6个维度分类输出，每一条标注【来源：导入文献】
"""

print("\n" + "=" * 60)
print("4. 测试中文文本编码")
print("=" * 60)
print(f"文本长度: {len(test_text)} 字符")
print(f"前200字符预览:")
print(repr(test_text[:200]))

# 测试json编码
print("\n" + "=" * 60)
print("5. 测试JSON编码")
print("=" * 60)
test_payload = {
    "role": "user",
    "content": test_text
}

try:
    json_str = json.dumps(test_payload, ensure_ascii=False)
    print("✅ JSON编码成功")
    print(f"JSON长度: {len(json_str)}")
    
    # 测试UTF-8编码
    utf8_bytes = json_str.encode('utf-8')
    print(f"✅ UTF-8编码成功，字节数: {len(utf8_bytes)}")
    
    # 解码回来
    decoded = utf8_bytes.decode('utf-8')
    print("✅ UTF-8解码成功")
    
except Exception as e:
    print(f"❌ 编码错误: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("编码环境测试完成！")
print("如果上面没有错误，说明编码环境正常。")
print("=" * 60)
