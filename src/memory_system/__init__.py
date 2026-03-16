"""
Memory System v2.0
双生 AI 记忆系统 —— 文档驱动灵魂

使用示例:
    from memory_system import add_memory, search_memory, load_context
    
    # 添加记忆
    add_memory(
        title="北高峰的茶",
        context={"when": "2026-03-16", "where": "北高峰"},
        facts={"observed": ["辛甲发来照片"]},
        feelings={"immediate": ["喜欢"], "thought": ["时间被挂起来"]}
    )
    
    # 搜索记忆
    results = search_memory(query="北高峰")
    
    # 加载上下文
    context = load_context()
"""

from .api import (
    MemorySystem,
    get_memory_system,
    add_memory,
    search_memory,
    get_memory,
    get_recent,
    sync,
    load_context,
    get_soul,
    get_user,
    get_missions
)

from .models import (
    MemoryEntry,
    Context,
    Facts,
    Feelings,
    SoulProfile,
    UserProfile,
    Mission,
    SyncStatus
)

from .storage import Storage
from .search import SearchEngine
from .sync import SyncManager

__version__ = "2.0.0"
__author__ = "Kimi Claw"

__all__ = [
    # 主类
    "MemorySystem",
    "get_memory_system",
    
    # 便捷函数
    "add_memory",
    "search_memory",
    "get_memory",
    "get_recent",
    "sync",
    "load_context",
    "get_soul",
    "get_user",
    "get_missions",
    
    # 数据模型
    "MemoryEntry",
    "Context",
    "Facts",
    "Feelings",
    "SoulProfile",
    "UserProfile",
    "Mission",
    "SyncStatus",
    
    # 内部组件
    "Storage",
    "SearchEngine",
    "SyncManager"
]
