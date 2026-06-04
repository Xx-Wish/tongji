# -*- coding: utf-8 -*-
"""阿里云百炼API测试脚本"""

import requests
import json
import sys

API_KEY = "sk-18150fa7989145e39cd11467675e943c"
BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"

def test_aliyun_api():
    """测试API连接"""
    print("=" * 60)
    print("测试阿里云百炼API...")
    print("=" * 60)
    
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": "你是一个精确的数据提取器，只输出JSON，不添加任何其他文字。"},
            {"role": "user", "content": """请从以下内容中提取结构化数据：

这是一个测试文本，主要研究大数据分析在教育领域的应用。我们采用了问卷调查的方法，收集了1000份学生样本，发现65%的学生希望有更智能的数据整合工具。

请严格按照JSON格式输出：
{
    "research_goal": "研究大数据在教育领域的应用",
    "methods": ["问卷调查"],
    "key_findings": [{"finding": "65%学生需要智能工具", "evidence": "65%的学生希望有更智能的数据整合工具"}],
    "user_pain_points": ["缺乏智能数据整合工具"],
    "user_persona": "学生群体",
    "relevance_to_project": "直接相关"
}"""}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    
    try:
        print(f"\n发送请求到 {BASE_URL}...")
        response = requests.post(BASE_URL, headers=headers, json=payload, timeout=60)
        print(f"HTTP状态码: {response.status_code}")
        
        response.encoding = 'utf-8'
        
        if response.status_code != 200:
            print(f"错误响应内容: {response.text}")
            return False
        
        result = response.json()
        print("\n✅ API调用成功！")
        content = result["choices"][0]["message"]["content"]
        print(f"\n响应内容:")
        print(content)
        
        # 尝试解析JSON
        try:
            json_data = json.loads(content)
            print("\n✅ JSON解析成功！")
            print(f"\n结构化数据: {json.dumps(json_data, ensure_ascii=False, indent=2)}")
        except Exception as e:
            print(f"\n⚠️ JSON解析失败: {e}")
            # 尝试用正则提取
            import re
            match = re.search(r'(\{[\s\S]*\})', content)
            if match:
                json_str = match.group(1)
                json_data = json.loads(json_str)
                print(f"\n✅ 通过正则提取JSON成功！")
                print(f"\n结构化数据: {json.dumps(json_data, ensure_ascii=False, indent=2)}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_aliyun_api()
    print("\n" + "="*60)
    if success:
        print("✅ API测试通过！可以开始使用工具了！")
    else:
        print("❌ API测试失败，请检查网络或API密钥")
    print("="*60)
    sys.exit(0 if success else 1)
