"""
Search Engine
搜索实现
"""

import re
from typing import List, Optional
from pathlib import Path

from .models import MemoryEntry, Context, Facts, Feelings


class SearchEngine:
    """搜索引擎"""
    
    def __init__(self, storage):
        self.storage = storage
    
    def search(
        self,
        query: str = None,
        tags: List[str] = None,
        date_from: str = None,
        date_to: str = None,
        source: str = None,
        category: str = None,
        limit: int = 5
    ) -> List[MemoryEntry]:
        """
        搜索记忆
        
        Args:
            query: 关键词（搜索标题、内容、感受想法）
            tags: 标签过滤
            date_from: 开始日期 (YYYY-MM-DD)
            date_to: 结束日期
            source: 来源过滤 (cloud/raspberry-pi)
            category: 维度过滤 (context/facts/feelings)
            limit: 返回数量限制
        """
        entries = []
        for filepath in self.storage.list_entries():
            entry = self.storage._parse_entry_file(filepath)
            
            # 过滤: 关键词
            if query:
                if not self._match_query(entry, query):
                    continue
            
            # 过滤: 标签
            if tags:
                if not any(tag in entry.tags for tag in tags):
                    continue
            
            # 过滤: 日期范围
            if date_from and entry.date < date_from:
                continue
            if date_to and entry.date > date_to:
                continue
            
            # 过滤: 来源
            if source and entry.source != source:
                continue
            
            # 过滤: 维度
            if category and category not in entry.categories:
                continue
            
            entries.append(entry)
        
        # 按日期倒序排序
        def sort_key(e):
            time_val = e.time if e.time else "00:00"
            return (e.date, str(time_val))
        
        entries.sort(key=sort_key, reverse=True)
        
        return entries[:limit]
    
    def _match_query(self, entry: MemoryEntry, query: str) -> bool:
        """检查条目是否匹配查询"""
        query_lower = query.lower()
        
        # 检查标题
        if query_lower in entry.title.lower():
            return True
        
        # 检查内容
        if query_lower in entry.content.lower():
            return True
        
        # 检查标签
        for tag in entry.tags:
            if query_lower in tag.lower():
                return True
        
        # 检查感受（重点）
        if entry.feelings:
            # 检查即时情绪
            for feeling in entry.feelings.immediate:
                if query_lower in feeling.lower():
                    return True
            # 检查想法
            for thought in entry.feelings.thought:
                if query_lower in thought.lower():
                    return True
            # 检查意义
            for sig in entry.feelings.significance:
                if query_lower in sig.lower():
                    return True
            # 检查情绪基调
            if entry.feelings.mood and query_lower in entry.feelings.mood.lower():
                return True
        
        # 检查情境
        if entry.context:
            if entry.context.where and query_lower in entry.context.where.lower():
                return True
            if entry.context.atmosphere and query_lower in entry.context.atmosphere.lower():
                return True
            # 检查感官细节
            for key, values in entry.context.sensory.items():
                for value in values:
                    if query_lower in value.lower():
                        return True
        
        # 检查事实
        if entry.facts:
            for observed in entry.facts.observed:
                if query_lower in observed.lower():
                    return True
            for learned in entry.facts.learned:
                if query_lower in learned.lower():
                    return True
            for happened in entry.facts.happened:
                if query_lower in happened.lower():
                    return True
        
        return False
    
    def get_recent(self, limit: int = 5) -> List[MemoryEntry]:
        """获取最近记忆"""
        entries = []
        for filepath in self.storage.list_entries():
            entry = self.storage._parse_entry_file(filepath)
            entries.append(entry)
        
        # 按日期倒序排序（先按日期，再按时间）
        def sort_key(e):
            # 确保 time 是字符串
            time_val = e.time if e.time else "00:00"
            return (e.date, str(time_val))
        
        entries.sort(key=sort_key, reverse=True)
        
        return entries[:limit]
    
    def get_by_date(self, date: str) -> List[MemoryEntry]:
        """获取指定日期的所有记忆"""
        entries = []
        for filepath in self.storage.list_entries():
            entry = self.storage._parse_entry_file(filepath)
            if entry.date == date:
                entries.append(entry)
        
        entries.sort(key=lambda e: e.time, reverse=True)
        return entries
    
    def search_by_related(self, entry_id: str) -> List[MemoryEntry]:
        """搜索关联条目"""
        entry = self.storage.read_entry(entry_id)
        if not entry or not entry.related:
            return []
        
        results = []
        for related_id in entry.related:
            related_entry = self.storage.read_entry(related_id)
            if related_entry:
                results.append(related_entry)
        
        return results
    
    def extract_feelings(self, entry_id: str) -> Optional[Feelings]:
        """提取记忆的感受维度"""
        entry = self.storage.read_entry(entry_id)
        if entry:
            return entry.feelings
        return None
    
    def extract_context(self, entry_id: str) -> Optional[Context]:
        """提取记忆的情境维度"""
        entry = self.storage.read_entry(entry_id)
        if entry:
            return entry.context
        return None
    
    def extract_facts(self, entry_id: str) -> Optional[Facts]:
        """提取记忆的事实维度"""
        entry = self.storage.read_entry(entry_id)
        if entry:
            return entry.facts
        return None
