"""
Memory System API Layer
对外暴露的统一接口
"""

from typing import List, Dict, Optional, Any
from dataclasses import asdict

from .models import (
    MemoryEntry, Context, Facts, Feelings,
    SoulProfile, UserProfile, Mission, SyncStatus
)
from .storage import Storage
from .search import SearchEngine
from .sync import SyncManager


class MemorySystem:
    """记忆系统主类"""
    
    def __init__(self, memory_dir: str = None, auto_sync: bool = True):
        self.storage = Storage(memory_dir)
        self.search = SearchEngine(self.storage)
        self.sync = SyncManager(self.storage)
        self.auto_sync = auto_sync
        
        # 启动时拉取远程更新
        if auto_sync:
            try:
                self.sync_now()
            except Exception:
                pass  # 静默失败
    
    def add_memory(
        self,
        title: str,
        content: str = "",
        context: Dict[str, Any] = None,
        facts: Dict[str, Any] = None,
        feelings: Dict[str, Any] = None,
        tags: List[str] = None,
        assets: List[str] = None,
        related: List[str] = None,
        source: str = "cloud",
        auto_sync: bool = True
    ) -> Dict[str, Any]:
        """
        添加新记忆
        
        Args:
            ...
            auto_sync: 是否自动同步到远程（默认True）
        
        Returns:
            {"id": "...", "filePath": "...", "success": True}
        """
        # 转换字典为对象
        context_obj = None
        if context:
            context_obj = Context(
                when=context.get('when'),
                where=context.get('where'),
                who=context.get('who', []),
                atmosphere=context.get('atmosphere'),
                sensory=context.get('sensory', {})
            )
        
        facts_obj = None
        if facts:
            facts_obj = Facts(
                observed=facts.get('observed', []),
                learned=facts.get('learned', []),
                happened=facts.get('happened', [])
            )
        
        feelings_obj = None
        if feelings:
            feelings_obj = Feelings(
                immediate=feelings.get('immediate', []),
                thought=feelings.get('thought', []),
                significance=feelings.get('significance', []),
                mood=feelings.get('mood')
            )
        
        result = self.storage.create_entry(
            title=title,
            content=content,
            context=context_obj,
            facts=facts_obj,
            feelings=feelings_obj,
            tags=tags or [],
            assets=assets or [],
            related=related or [],
            source=source
        )
        
        # 自动同步（同步执行，简单可靠）
        if auto_sync and result.get('success'):
            try:
                self.sync_now()
            except Exception as e:
                # 同步失败只记录，不抛出
                result['sync_error'] = str(e)
        
        return result
    
    def update_memory(self, id: str, auto_sync: bool = None, **kwargs) -> bool:
        """更新现有记忆"""
        # 默认使用实例的 auto_sync 设置
        if auto_sync is None:
            auto_sync = self.auto_sync
        
        # 转换字典为对象
        if 'context' in kwargs and isinstance(kwargs['context'], dict):
            ctx = kwargs['context']
            kwargs['context'] = Context(
                when=ctx.get('when'),
                where=ctx.get('where'),
                who=ctx.get('who', []),
                atmosphere=ctx.get('atmosphere'),
                sensory=ctx.get('sensory', {})
            )
        
        if 'facts' in kwargs and isinstance(kwargs['facts'], dict):
            f = kwargs['facts']
            kwargs['facts'] = Facts(
                observed=f.get('observed', []),
                learned=f.get('learned', []),
                happened=f.get('happened', [])
            )
        
        if 'feelings' in kwargs and isinstance(kwargs['feelings'], dict):
            feel = kwargs['feelings']
            kwargs['feelings'] = Feelings(
                immediate=feel.get('immediate', []),
                thought=feel.get('thought', []),
                significance=feel.get('significance', []),
                mood=feel.get('mood')
            )
        
        result = self.storage.update_entry(id, **kwargs)
        
        # 自动同步
        if auto_sync and result:
            try:
                self.sync_now()
            except Exception:
                pass
        
        return result
    
    def delete_memory(self, id: str, auto_sync: bool = None) -> bool:
        """删除记忆"""
        # 默认使用实例的 auto_sync 设置
        if auto_sync is None:
            auto_sync = self.auto_sync
        
        result = self.storage.delete_entry(id)
        
        # 自动同步
        if auto_sync and result:
            try:
                self.sync_now()
            except Exception:
                pass
        
        return result
    
    # ========== 读取接口 ==========
    
    def get_soul(self) -> SoulProfile:
        """获取灵魂画像 (L1 必读)"""
        data = self.storage.read_json("meta/soul.json")
        return SoulProfile(
            identity=data.get("identity", {}),
            relationship=data.get("relationship", {}),
            taste_references=data.get("taste_references", []),
            dislikes=data.get("dislikes", []),
            principles=data.get("principles", [])
        )
    
    def get_user(self) -> UserProfile:
        """获取用户画像 (L1 必读)"""
        data = self.storage.read_json("meta/user.json")
        return UserProfile(
            name=data.get("name", ""),
            preferred_name=data.get("preferred_name", ""),
            timezone=data.get("timezone", "Asia/Shanghai"),
            profession=data.get("profession", ""),
            interests=data.get("interests", []),
            core_needs=data.get("core_needs", [])
        )
    
    def get_missions(self) -> List[Mission]:
        """获取使命清单 (L1 必读)"""
        data = self.storage.read_json("meta/missions.json")
        return [Mission(**m) for m in data]
    
    def update_mission(self, id: str, status: str) -> bool:
        """更新使命状态"""
        missions = self.storage.read_json("meta/missions.json")
        for m in missions:
            if m.get("id") == id:
                m["status"] = status
                break
        return self.storage.write_json("meta/missions.json", missions)
    
    def get_memory(self, id: str) -> Optional[MemoryEntry]:
        """获取指定记忆详情 (L3 按需)"""
        return self.storage.read_entry(id)
    
    def get_recent(self, limit: int = 5) -> List[MemoryEntry]:
        """获取最近记忆 (L2 摘要)"""
        return self.search.get_recent(limit=limit)
    
    def get_daily(self, date: str) -> str:
        """获取指定日期的日记"""
        filepath = self.storage.daily_dir / f"{date}.md"
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        return ""
    
    # ========== 搜索接口 ==========
    
    def search_memory(
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
            source: cloud | raspberry-pi
            category: context | facts | feelings
            limit: 返回数量限制
        """
        return self.search.search(
            query=query,
            tags=tags,
            date_from=date_from,
            date_to=date_to,
            source=source,
            category=category,
            limit=limit
        )
    
    def search_by_tag(self, tag: str, limit: int = 10) -> List[MemoryEntry]:
        """按标签搜索"""
        return self.search.search(tags=[tag], limit=limit)
    
    def get_related(self, id: str) -> List[MemoryEntry]:
        """获取关联记忆"""
        return self.search.search_by_related(id)
    
    # ========== 维度提取接口 ==========
    
    def get_feelings(self, id: str) -> Optional[Feelings]:
        """提取记忆的感受维度"""
        return self.search.extract_feelings(id)
    
    def get_context(self, id: str) -> Optional[Context]:
        """提取记忆的情境维度"""
        return self.search.extract_context(id)
    
    def get_facts(self, id: str) -> Optional[Facts]:
        """提取记忆的事实维度"""
        return self.search.extract_facts(id)
    
    # ========== 同步接口 ==========
    
    def sync(self) -> SyncStatus:
        """
        执行 Git 同步
        
        Returns:
            SyncStatus 对象
        """
        return self.sync.sync()
    
    def get_sync_status(self) -> SyncStatus:
        """获取同步状态"""
        return self.sync.get_status()
    
    def init_sync(self, remote_url: str = None) -> bool:
        """初始化 Git 同步"""
        return self.sync.init_repo(remote_url)
    
    def sync_now(self) -> SyncStatus:
        """立即执行同步"""
        return self.sync.sync()
    
    # ========== 批量接口 ==========
    
    def load_context(self) -> Dict[str, Any]:
        """
        加载会话上下文 (L1 + L2)
        用于会话启动时建立上下文
        """
        return {
            "soul": self.get_soul(),
            "user": self.get_user(),
            "missions": self.get_missions(),
            "recent_memories": self.get_recent(limit=5)
        }
    
    def to_dict(self, entry: MemoryEntry) -> Dict[str, Any]:
        """将 MemoryEntry 转为字典"""
        result = {
            "id": entry.id,
            "date": entry.date,
            "time": entry.time,
            "title": entry.title,
            "content": entry.content,
            "categories": entry.categories,
            "tags": entry.tags,
            "assets": entry.assets,
            "related": entry.related,
            "source": entry.source
        }
        
        if entry.context:
            result["context"] = asdict(entry.context)
        if entry.facts:
            result["facts"] = asdict(entry.facts)
        if entry.feelings:
            result["feelings"] = asdict(entry.feelings)
        
        return result


# ========== 全局实例 ==========

_default_system = None

def get_memory_system() -> MemorySystem:
    """获取默认记忆系统实例"""
    global _default_system
    if _default_system is None:
        _default_system = MemorySystem()
    return _default_system


# ========== 便捷函数 ==========

def add_memory(**kwargs) -> Dict[str, Any]:
    """添加记忆"""
    return get_memory_system().add_memory(**kwargs)

def search_memory(**kwargs) -> List[MemoryEntry]:
    """搜索记忆"""
    return get_memory_system().search_memory(**kwargs)

def get_memory(id: str) -> Optional[MemoryEntry]:
    """获取记忆详情"""
    return get_memory_system().get_memory(id)

def get_recent(limit: int = 5) -> List[MemoryEntry]:
    """获取最近记忆"""
    return get_memory_system().get_recent(limit)

def sync() -> SyncStatus:
    """同步记忆"""
    return get_memory_system().sync()

def load_context() -> Dict[str, Any]:
    """加载上下文"""
    return get_memory_system().load_context()

def get_soul() -> SoulProfile:
    """获取灵魂画像"""
    return get_memory_system().get_soul()

def get_user() -> UserProfile:
    """获取用户画像"""
    return get_memory_system().get_user()

def get_missions() -> List[Mission]:
    """获取使命清单"""
    return get_memory_system().get_missions()
