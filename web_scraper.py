# -*- coding: utf-8 -*-
import re
import json
import time
from typing import List, Dict, Any
from logger import get_logger

logger = get_logger()


class DeclarationDataExtractor:
    """项目申报书专用数据提取器 - 针对申报书特点优化"""
    
    @staticmethod
    def build_system_prompt() -> str:
        """申报书专用System Prompt"""
        return """你是一个专业的项目申报书分析专家。你的任务是从给定的项目申报书文本中提取结构化信息，并严格按照指定的JSON格式输出。不要添加任何解释或额外文字。如果某字段在文本中找不到明确信息，请设为null或空数组。

[提取要求]
1. 准确识别申报书的各个组成部分（背景、现状、目标、创新点、技术路线、预期成果等）。
2. 对于现状和问题，尽量提取出量化数据（如百分比、增长率、具体指标）。
3. 创新点要提炼成简明的列表，每项不超过30字。
4. 技术路线请按“阶段-动作-产出”的逻辑链进行总结。
5. 用户痛点和画像如果文本中没有明说，请根据行业问题和受益对象合理推断，并在字段中用"推断："开头注明。
6. 所有字段输出严格遵循JSON Schema。
"""
    
    @staticmethod
    def build_prompt_for_declaration(text: str, chunk_idx: int = 1, total_chunks: int = 1) -> str:
        """为申报书构建完整提示词"""
        
        chunk_info = f" (第{chunk_idx}/{total_chunks}段)" if total_chunks > 1 else ""
        
        prompt = f"""[输出格式]
{{
  "project_title": "项目名称",
  "background_and_significance": "立项背景与意义（国家战略、行业痛点）",
  "current_status_and_problems": {{
    "industry_status": "领域现状",
    "existing_problems": ["问题1", "问题2"],
    "quantitative_data": ["数据1", "数据2"]
  }},
  "project_objectives": {{
    "overall_goal": "总目标",
    "sub_goals": ["子目标1", "子目标2"]
  }},
  "innovation_points": ["创新点1", "创新点2"],
  "technical_route": [
    {{
      "phase": "阶段名称",
      "actions": ["动作1", "动作2"],
      "outputs": ["产出1"]
    }}
  ],
  "expected_outcomes": {{
    "economic_benefits": "经济效益",
    "social_benefits": "社会效益",
    "key_indicators": ["指标1", "指标2"]
  }},
  "user_pain_points": ["痛点1", "痛点2"],
  "user_persona": "推断的用户画像描述",
  "relevance_analysis": "与本数据整合统计工具的相关性分析"
}}

现在，从以下申报书文本中提取信息：

{text}

请严格按照上述JSON格式输出，不要包含任何Markdown标记或其他解释文字。
"""
        
        return prompt
    
    @staticmethod
    def prepare_declaration_tasks(text: str) -> List[Dict[str, Any]]:
        """准备申报书提取任务 - 支持分段"""
        
        # 申报书通常更长，用5000字分段
        chunk_size = 5000
        tasks = []
        
        if len(text) > chunk_size:
            logger.info(f"申报书较长 ({len(text)}字)，将分段提取")
            chunks = []
            for i in range(0, len(text), chunk_size):
                # 重叠200字避免信息截断
                start_idx = max(0, i - 200) if i > 0 else 0
                chunk = text[start_idx:i+chunk_size]
                chunks.append(chunk)
            
            for idx, chunk in enumerate(chunks):
                prompt = DeclarationDataExtractor.build_prompt_for_declaration(
                    chunk, idx+1, len(chunks)
                )
                tasks.append({
                    'prompt': prompt,
                    'chunk_idx': idx+1,
                    'total_chunks': len(chunks),
                    'doc_type': 'declaration'
                })
        else:
            prompt = DeclarationDataExtractor.build_prompt_for_declaration(text, 1, 1)
            tasks.append({
                'prompt': prompt,
                'chunk_idx': 1,
                'total_chunks': 1,
                'doc_type': 'declaration'
            })
        
        return tasks
    
    @staticmethod
    def merge_declaration_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """合并多个分段的提取结果"""
        
        merged = {
            "project_title": None,
            "background_and_significance": "",
            "current_status_and_problems": {
                "industry_status": "",
                "existing_problems": [],
                "quantitative_data": []
            },
            "project_objectives": {
                "overall_goal": "",
                "sub_goals": []
            },
            "innovation_points": [],
            "technical_route": [],
            "expected_outcomes": {
                "economic_benefits": "",
                "social_benefits": "",
                "key_indicators": []
            },
            "user_pain_points": [],
            "user_persona": None,
            "relevance_analysis": ""
        }
        
        for result in results:
            if not result:
                continue
            
            # 项目名称取第一个非空的
            if not merged["project_title"] and result.get("project_title"):
                merged["project_title"] = result["project_title"]
            
            # 合并背景
            if result.get("background_and_significance"):
                if merged["background_and_significance"]:
                    merged["background_and_significance"] += "\n"
                merged["background_and_significance"] += result["background_and_significance"]
            
            # 合并现状与问题
            status = result.get("current_status_and_problems", {})
            if status.get("industry_status"):
                if merged["current_status_and_problems"]["industry_status"]:
                    merged["current_status_and_problems"]["industry_status"] += "\n"
                merged["current_status_and_problems"]["industry_status"] += status["industry_status"]
            
            merged["current_status_and_problems"]["existing_problems"].extend(status.get("existing_problems", []))
            merged["current_status_and_problems"]["quantitative_data"].extend(status.get("quantitative_data", []))
            
            # 合并目标
            objectives = result.get("project_objectives", {})
            if objectives.get("overall_goal"):
                if not merged["project_objectives"]["overall_goal"]:
                    merged["project_objectives"]["overall_goal"] = objectives["overall_goal"]
            merged["project_objectives"]["sub_goals"].extend(objectives.get("sub_goals", []))
            
            # 合并创新点
            merged["innovation_points"].extend(result.get("innovation_points", []))
            
            # 合并技术路线
            merged["technical_route"].extend(result.get("technical_route", []))
            
            # 合并预期成果
            outcomes = result.get("expected_outcomes", {})
            if outcomes.get("economic_benefits"):
                if merged["expected_outcomes"]["economic_benefits"]:
                    merged["expected_outcomes"]["economic_benefits"] += "\n"
                merged["expected_outcomes"]["economic_benefits"] += outcomes["economic_benefits"]
            
            if outcomes.get("social_benefits"):
                if merged["expected_outcomes"]["social_benefits"]:
                    merged["expected_outcomes"]["social_benefits"] += "\n"
                merged["expected_outcomes"]["social_benefits"] += outcomes["social_benefits"]
            
            merged["expected_outcomes"]["key_indicators"].extend(outcomes.get("key_indicators", []))
            
            # 合并用户痛点
            merged["user_pain_points"].extend(result.get("user_pain_points", []))
            
            # 用户画像取第一个非空的
            if not merged["user_persona"] and result.get("user_persona"):
                merged["user_persona"] = result["user_persona"]
            
            # 相关性分析
            if result.get("relevance_analysis"):
                if merged["relevance_analysis"]:
                    merged["relevance_analysis"] += "\n"
                merged["relevance_analysis"] += result["relevance_analysis"]
        
        # 去重
        merged["current_status_and_problems"]["existing_problems"] = list(set(merged["current_status_and_problems"]["existing_problems"]))
        merged["current_status_and_problems"]["quantitative_data"] = list(set(merged["current_status_and_problems"]["quantitative_data"]))
        merged["project_objectives"]["sub_goals"] = list(set(merged["project_objectives"]["sub_goals"]))
        merged["innovation_points"] = list(set(merged["innovation_points"]))
        merged["expected_outcomes"]["key_indicators"] = list(set(merged["expected_outcomes"]["key_indicators"]))
        merged["user_pain_points"] = list(set(merged["user_pain_points"]))
        
        return merged
    
    @staticmethod
    def convert_to_tool_format(declaration_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """将申报书数据转换为工具能识别的格式"""
        
        tool_data = []
        
        # 背景与意义 -> 领域现状
        if declaration_data.get("background_and_significance"):
            tool_data.append({
                'content': declaration_data["background_and_significance"],
                'category': '领域现状',
                'source': '项目申报书'
            })
        
        # 行业现状 -> 领域现状
        industry_status = declaration_data.get("current_status_and_problems", {}).get("industry_status", "")
        if industry_status:
            tool_data.append({
                'content': industry_status,
                'category': '领域现状',
                'source': '项目申报书'
            })
        
        # 量化数据 -> 领域现状
        for data in declaration_data.get("current_status_and_problems", {}).get("quantitative_data", []):
            if data:
                tool_data.append({
                    'content': data,
                    'category': '领域现状',
                    'source': '项目申报书'
                })
        
        # 现存问题 -> 痛点问题
        for problem in declaration_data.get("current_status_and_problems", {}).get("existing_problems", []):
            if problem:
                tool_data.append({
                    'content': problem,
                    'category': '痛点问题',
                    'source': '项目申报书'
                })
        
        # 目标 -> 政策支撑
        if declaration_data.get("project_objectives", {}).get("overall_goal"):
            tool_data.append({
                'content': declaration_data["project_objectives"]["overall_goal"],
                'category': '政策支撑',
                'source': '项目申报书'
            })
        
        # 创新点 -> 创新点支撑
        for ip in declaration_data.get("innovation_points", []):
            if ip:
                tool_data.append({
                    'content': ip,
                    'category': '创新点支撑',
                    'source': '项目申报书'
                })
        
        # 技术路线 -> 创新点支撑
        for tr in declaration_data.get("technical_route", []):
            phase = tr.get("phase", "")
            if phase:
                tool_data.append({
                    'content': phase,
                    'category': '创新点支撑',
                    'source': '项目申报书'
                })
        
        # 用户痛点 -> 痛点问题
        for pain in declaration_data.get("user_pain_points", []):
            if pain:
                tool_data.append({
                    'content': pain,
                    'category': '痛点问题',
                    'source': '项目申报书'
                })
        
        # 用户画像 -> 用户画像
        if declaration_data.get("user_persona"):
            tool_data.append({
                'content': declaration_data["user_persona"],
                'category': '用户画像',
                'source': '项目申报书'
            })
        
        # 预期成果 -> 政策支撑
        eco_benefits = declaration_data.get("expected_outcomes", {}).get("economic_benefits", "")
        if eco_benefits:
            tool_data.append({
                'content': eco_benefits,
                'category': '政策支撑',
                'source': '项目申报书'
            })
        
        social_benefits = declaration_data.get("expected_outcomes", {}).get("social_benefits", "")
        if social_benefits:
            tool_data.append({
                'content': social_benefits,
                'category': '政策支撑',
                'source': '项目申报书'
            })
        
        for indicator in declaration_data.get("expected_outcomes", {}).get("key_indicators", []):
            if indicator:
                tool_data.append({
                    'content': indicator,
                    'category': '领域现状',
                    'source': '项目申报书'
                })
        
        # 相关性分析 -> 政策支撑
        if declaration_data.get("relevance_analysis"):
            tool_data.append({
                'content': declaration_data["relevance_analysis"],
                'category': '政策支撑',
                'source': '项目申报书'
            })
        
        return tool_data


class PaperDataExtractor:
    """论文数据提取器 - 保持原有功能"""
    
    @staticmethod
    def prepare_extraction_tasks(text: str) -> List[Dict[str, Any]]:
        """准备提取任务 - 支持长文本分段处理"""
        
        # 超过6000字的论文分段提取
        chunk_size = 6000
        tasks = []
        
        if len(text) > chunk_size:
            logger.info(f"论文较长 ({len(text)}字)，将分段提取")
            chunks = []
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i+chunk_size]
                chunks.append(chunk)
            
            for idx, chunk in enumerate(chunks):
                prompt = PaperDataExtractor.build_prompt_for_chunk(chunk, idx+1, len(chunks))
                tasks.append({
                    'prompt': prompt,
                    'chunk_idx': idx+1,
                    'total_chunks': len(chunks),
                    'doc_type': 'paper'
                })
        else:
            prompt = PaperDataExtractor.build_prompt_for_chunk(text, 1, 1)
            tasks.append({
                'prompt': prompt,
                'chunk_idx': 1,
                'total_chunks': 1,
                'doc_type': 'paper'
            })
        
        return tasks
    
    @staticmethod
    def build_prompt_for_chunk(text: str, chunk_idx: int, total_chunks: int) -> str:
        """为单个文本段构建提示词"""
        
        chunk_info = f" (第{chunk_idx}/{total_chunks}段)" if total_chunks > 1 else ""
        
        prompt = f"""请从以下论文内容中提取结构化数据。

论文内容：
{text}

请严格按照以下JSON格式输出，不要包含任何Markdown标记或其他文字：
{{
    "research_goal": "研究目标（字符串）",
    "methods": ["方法1", "方法2"],
    "key_findings": [
        {{"finding": "发现内容", "evidence": "原文证据"}}
    ],
    "user_pain_points": ["痛点1", "痛点2"],
    "user_persona": "用户画像描述（字符串）",
    "relevance_to_project": "与数据整合统计工具的相关性（字符串）"
}}

只输出JSON对象，不要其他内容。
"""
        
        return prompt
    
    @staticmethod
    def process_extraction_responses(responses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """处理多个响应，合并去重并转换为现有格式"""
        
        all_data = []
        
        for resp in responses:
            response_text = resp.get('response', '')
            parsed_data = PaperDataExtractor.extract_json_from_response(response_text)
            
            if parsed_data:
                all_data.append(parsed_data)
        
        return PaperDataExtractor.convert_to_tool_format(all_data)
    
    @staticmethod
    def extract_json_from_response(response_text: str) -> Dict[str, Any]:
        """从响应中提取JSON对象，使用正则处理各种情况"""
        
        if not response_text:
            return None
        
        try:
            return json.loads(response_text)
        except Exception:
            # 尝试用正则提取JSON
            match = re.search(r'(\{[\s\S]*\})', response_text)
            if match:
                try:
                    json_str = match.group(1)
                    return json.loads(json_str)
                except Exception as e:
                    logger.warning(f"正则提取JSON失败: {e}")
        
        return None
    
    @staticmethod
    def convert_to_tool_format(all_parsed_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """将提取的JSON格式转换为工具能识别的格式"""
        
        tool_data = []
        
        for data in all_parsed_data:
            # research_goal -> 领域现状
            if data.get('research_goal'):
                tool_data.append({
                    'content': data['research_goal'],
                    'category': '领域现状',
                    'source': '参考文献'
                })
            
            # methods -> 创新点支撑
            for method in data.get('methods', []):
                if method:
                    tool_data.append({
                        'content': method,
                        'category': '创新点支撑',
                        'source': '参考文献'
                    })
            
            # key_findings -> 领域现状
            for finding in data.get('key_findings', []):
                finding_text = finding.get('finding', '')
                if finding_text:
                    tool_data.append({
                        'content': finding_text,
                        'category': '领域现状',
                        'source': '参考文献'
                    })
            
            # user_pain_points -> 痛点问题
            for pain in data.get('user_pain_points', []):
                if pain:
                    tool_data.append({
                        'content': pain,
                        'category': '痛点问题',
                        'source': '参考文献'
                    })
            
            # user_persona -> 用户画像
            if data.get('user_persona'):
                tool_data.append({
                    'content': data['user_persona'],
                    'category': '用户画像',
                    'source': '参考文献'
                })
            
            # relevance_to_project -> 政策支撑
            if data.get('relevance_to_project'):
                tool_data.append({
                    'content': data['relevance_to_project'],
                    'category': '政策支撑',
                    'source': '参考文献'
                })
        
        # 去重
        seen = set()
        unique_data = []
        for item in tool_data:
            key = item['content']
            if key not in seen:
                seen.add(key)
                unique_data.append(item)
        
        return unique_data


class SmartDataExtractor:
    """智能提取器 - 根据文件类型自动选择策略"""
    
    @staticmethod
    def detect_document_type(text: str, file_name: str = "") -> str:
        """智能检测文档类型"""
        
        # 1. 优先看文件名
        if "立项" in file_name or "申报" in file_name or "申请书" in file_name:
            logger.info(f"通过文件名识别为申报书: {file_name}")
            return "declaration"
        
        # 2. 检测关键词
        declaration_keywords = [
            "立项背景", "研究意义", "研究目标", "预期成果", "技术路线",
            "创新点", "可行性分析", "项目名称", "申报书", "申请书"
        ]
        
        paper_keywords = [
            "摘要", "关键词", "引言", "方法", "结果", "讨论", "结论",
            "参考文献", "Abstract", "Introduction", "Method"
        ]
        
        declaration_score = 0
        paper_score = 0
        
        for keyword in declaration_keywords:
            if keyword in text:
                declaration_score += 1
        
        for keyword in paper_keywords:
            if keyword in text:
                paper_score += 1
        
        if declaration_score > paper_score:
            logger.info(f"通过内容识别为申报书 (得分: {declaration_score}/{paper_score})")
            return "declaration"
        else:
            logger.info(f"通过内容识别为论文 (得分: {paper_score}/{declaration_score})")
            return "paper"
    
    @staticmethod
    def prepare_tasks(text: str, file_name: str = "", force_type: str = None) -> List[Dict[str, Any]]:
        """根据文档类型准备提取任务"""
        
        if force_type:
            doc_type = force_type
        else:
            doc_type = SmartDataExtractor.detect_document_type(text, file_name)
        
        if doc_type == "declaration":
            return DeclarationDataExtractor.prepare_declaration_tasks(text)
        else:
            return PaperDataExtractor.prepare_extraction_tasks(text)
    
    @staticmethod
    def process_responses(responses: List[Dict[str, Any]], doc_type: str) -> List[Dict[str, Any]]:
        """根据文档类型处理响应"""
        
        if doc_type == "declaration":
            # 申报书需要先合并JSON再转换
            parsed_list = []
            for resp in responses:
                parsed = PaperDataExtractor.extract_json_from_response(resp.get('response', ''))
                if parsed:
                    parsed_list.append(parsed)
            
            merged = DeclarationDataExtractor.merge_declaration_results(parsed_list)
            return DeclarationDataExtractor.convert_to_tool_format(merged)
        else:
            # 论文使用原有处理方式
            return PaperDataExtractor.process_extraction_responses(responses)


class WebScraper:
    """原有的WebScraper类保持不变，用于其他功能"""
    
    def __init__(self):
        pass
    
    def extract_project_info(self, text: str) -> Dict:
        """提取项目信息 - 简化版"""
        return {
            'theme': text[:200] if len(text) > 0 else '',
            'direction': '',
            'keywords': []
        }
    
    def analyze_document(self, text: str, doc_type: str) -> Dict:
        """分析文档 - 简化版"""
        return {
            'summary': text[:500] if len(text) > 0 else '',
            'keywords': [],
            'timestamp': time.strftime('%Y-%m-%d')
        }
    
    def search_web(self, query: str) -> List[Dict]:
        """搜索网络 - 空实现"""
        return []
