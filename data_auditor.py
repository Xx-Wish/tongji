# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from collections import defaultdict
import re


class DataAuditor:
    def __init__(self, project_info=None):
        self.source_counts = defaultdict(int)
        self.project_info = project_info
        self.keywords_set = set()
        self.theme_words = set()
        
        if project_info:
            if project_info.get('keywords'):
                for kw in project_info['keywords']:
                    if isinstance(kw, str):
                        self.keywords_set.update([kw.lower()])
            if project_info.get('theme'):
                if isinstance(project_info['theme'], str):
                    self.theme_words.update(re.findall(r'[\w]+', project_info['theme'].lower()))
            if project_info.get('research_content'):
                rc = project_info['research_content']
                if isinstance(rc, list):
                    for item in rc:
                        if isinstance(item, str):
                            self.keywords_set.update(re.findall(r'[\w]{2,}', item.lower()))
                elif isinstance(rc, str):
                    self.keywords_set.update(re.findall(r'[\w]{2,}', rc.lower()))
            if project_info.get('target_users'):
                if isinstance(project_info['target_users'], str):
                    self.keywords_set.update(re.findall(r'[\w]{2,}', project_info['target_users'].lower()))
        
        self.source_type_priority = {
            'government': 20,
            'academic': 18,
            'official': 16,
            'reputable_media': 14,
            'user_document': 20,
            'web_search': 10,
            'web_scrape': 8,
            'user_upload': 15,
            'default': 5
        }
    
    def set_project_info(self, project_info):
        self.project_info = project_info
        if project_info:
            if project_info.get('keywords'):
                for kw in project_info['keywords']:
                    if isinstance(kw, str):
                        self.keywords_set.update([kw.lower()])
            if project_info.get('theme'):
                if isinstance(project_info['theme'], str):
                    self.theme_words.update(re.findall(r'[\w]+', project_info['theme'].lower()))

    def audit_data(self, data_list):
        """审核所有数据 - 只评分排序，不丢弃"""
        if not data_list:
            return []
        
        self._count_sources(data_list)
        
        audited_data = []
        for idx, data in enumerate(data_list):
            if data.get('skip_audit') or data.get('source_type') == 'user_document':
                data['audit_score'] = 100
                data['score_breakdown'] = {'skip_audit': '用户导入文档，免审核'}
                data['weight'] = data.get('weight', 10)
                data['audit_passed'] = True
                data['source_verified'] = True
                audited_data.append(data)
                continue
            
            score_details = self._calculate_score(data)
            total_score = sum(score_details.values())
            
            has_valid_source = self._verify_source(data)
            
            data['audit_score'] = total_score
            data['score_breakdown'] = score_details
            data['weight'] = self._calculate_weight(total_score)
            data['audit_passed'] = True  # 全部保留，只评分
            data['source_verified'] = has_valid_source
            data['audit_timestamp'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            audited_data.append(data)
        
        # 按相关性分数从高到低排序！
        audited_data.sort(
            key=lambda x: (
                x['score_breakdown'].get('relevance', 0),
                x.get('weight', 0),
                x.get('audit_score', 0)
            ),
            reverse=True
        )
        
        return audited_data
    
    def _count_sources(self, data_list):
        for data in data_list:
            source = data.get('source', 'unknown')
            self.source_counts[source] += 1
    
    def _calculate_score(self, data):
        """计算四维度分数（降低相关性权重，增强其他维度）"""
        score_details = {}
        
        score_details['timeliness'] = self._calculate_timeliness(data)
        score_details['cross_validation'] = self._calculate_cross_validation(data)
        score_details['relevance'] = self._calculate_relevance(data)
        score_details['content_value'] = self._calculate_content_value(data)
        
        return score_details
    
    def _calculate_timeliness(self, data):
        """时效性：30分（提高！）"""
        try:
            publish_date = None
            
            if 'publish_date' in data:
                try:
                    publish_date = datetime.strptime(str(data['publish_date']), '%Y-%m-%d')
                except:
                    pass
            
            if not publish_date and 'content' in data:
                publish_date = self._extract_date_from_content(data['content'])
            
            if publish_date:
                days_diff = (datetime.now() - publish_date).days
                if days_diff <= 90:
                    return 30
                elif days_diff <= 180:
                    return 26
                elif days_diff <= 365:
                    return 22
                elif days_diff <= 730:
                    return 18
                elif days_diff <= 1095:
                    return 14
                elif days_diff <= 1825:
                    return 10
                else:
                    return 6
            else:
                return 12
        except Exception as e:
            return 10
    
    def _extract_date_from_content(self, content):
        date_patterns = [
            r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})',
            r'(\d{4})年(\d{1,2})月',
            r'(\d{4})-(\d{1,2})'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, content)
            if match:
                try:
                    year = int(match.group(1))
                    month = int(match.group(2))
                    day = int(match.group(3)) if len(match.groups()) > 2 else 1
                    if 2000 <= year <= 2030 and 1 <= month <= 12:
                        return datetime(year, month, day)
                except:
                    continue
        return None
    
    def _calculate_cross_validation(self, data):
        """交叉印证：25分（提高！）"""
        source = data.get('source', 'unknown')
        
        if source == 'unknown':
            return 5
        
        count = self.source_counts.get(source, 1)
        
        if count >= 10:
            return 25
        elif count >= 7:
            return 20
        elif count >= 5:
            return 16
        elif count >= 4:
            return 12
        elif count >= 3:
            return 9
        elif count >= 2:
            return 6
        else:
            return 5
    
    def _calculate_relevance(self, data):
        """项目相关性：25分（降低！不再是最重要的）"""
        if not self.project_info and not self.keywords_set:
            return 5
        
        content = str(data.get('data', '') + ' ' + data.get('content', '') + ' ' + data.get('title', '')).lower()
        
        if not content:
            return 0
        
        matches = set()
        
        for keyword in self.keywords_set:
            if keyword and keyword in content:
                matches.add(keyword)
        
        for theme_word in self.theme_words:
            if theme_word and theme_word in content:
                matches.add(theme_word)
        
        match_count = len(matches)
        if match_count >= 8:
            score = 25
        elif match_count >= 6:
            score = 20
        elif match_count >= 4:
            score = 15
        elif match_count >= 3:
            score = 10
        elif match_count >= 2:
            score = 6
        elif match_count >= 1:
            score = 3
        else:
            score = 0
        
        if self.project_info and self.project_info.get('theme'):
            theme = self.project_info['theme'].lower()
            if any(word in content for word in theme.split()):
                score += 4
                score = min(score, 25)
        
        return score
    
    def _calculate_content_value(self, data):
        """内容价值：20分（提高！）"""
        source_type = data.get('source_type', 'default')
        content = data.get('content', '')
        
        type_scores = {
            'government': 16,
            'academic': 18,
            'official': 14,
            'reputable_media': 12,
            'user_document': 20,
            'web_search': 10,
            'web_scrape': 8,
            'user_upload': 14,
            'default': 6
        }
        
        base_score = type_scores.get(source_type, 6)
        
        content_length = len(str(content))
        if content_length > 1000:
            base_score += 2
        elif content_length > 500:
            base_score += 1
        
        if self._has_quantitative_data(content):
            base_score += 2
        
        if 'source' in data and data['source']:
            base_score += 1
        
        return min(int(base_score), 20)
    
    def _has_quantitative_data(self, content):
        patterns = [
            r'\d+%',
            r'\d+[万亿千百十]+',
            r'增长\d+',
            r'减少\d+',
            r'上升\d+',
            r'下降\d+'
        ]
        
        for pattern in patterns:
            if re.search(pattern, content):
                return True
        return False
    
    def _verify_source(self, data):
        source = data.get('source', '')
        source_type = data.get('source_type', '')
        
        if not source or source == 'unknown':
            return False
        
        if 'user' in source_type.lower() or '用户' in source:
            return True
        
        if source_type in ['government', 'academic', 'official', 'reputable_media']:
            return True
        
        if data.get('url'):
            return True
        
        return False
    
    def _calculate_weight(self, total_score):
        if total_score >= 90:
            return 10
        elif total_score >= 80:
            return 9
        elif total_score >= 70:
            return 8
        elif total_score >= 60:
            return 7
        elif total_score >= 50:
            return 5
        else:
            return 3
    
    def get_audit_statistics(self, audited_data):
        if not audited_data:
            return {}
        
        stats = {
            'total_count': len(audited_data),
            'source_distribution': defaultdict(int),
            'source_type_distribution': defaultdict(int),
            'avg_score': 0,
            'score_ranges': {
                '90-100': 0,
                '80-89': 0,
                '70-79': 0,
                '60-69': 0,
                '<60': 0
            }
        }
        
        total_score = 0
        
        for data in audited_data:
            score = data.get('audit_score', 0)
            total_score += score
            
            if score >= 90:
                stats['score_ranges']['90-100'] += 1
            elif score >= 80:
                stats['score_ranges']['80-89'] += 1
            elif score >= 70:
                stats['score_ranges']['70-79'] += 1
            elif score >= 60:
                stats['score_ranges']['60-69'] += 1
            else:
                stats['score_ranges']['<60'] += 1
            
            stats['source_distribution'][data.get('source', 'unknown')] += 1
            stats['source_type_distribution'][data.get('source_type', 'default')] += 1
        
        stats['avg_score'] = total_score / len(audited_data) if audited_data else 0
        
        return stats
