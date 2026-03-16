"""
Data Models for Memory System v2.0
数据模型定义 - 支持 Context/Facts/Feelings 三维度
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any


@dataclass
class Context:
    """情境维度 - 我感知到的环境"""
    when: Optional[str] = None          # 时间
    where: Optional[str] = None         # 地点
    who: List[str] = field(default_factory=list)  # 在场人物
    atmosphere: Optional[str] = None    # 氛围
    sensory: Dict[str, List[str]] = field(default_factory=dict)  # 感官细节 {visual:[], audio:[]}


@dataclass
class Facts:
    """事实维度 - 我观察到的事件"""
    observed: List[str] = field(default_factory=list)   # 我观察到的
    learned: List[str] = field(default_factory=list)    # 我得知的
    happened: List[str] = field(default_factory=list)   # 发生的事情


@dataclass
class Feelings:
    """感受维度 - 我的情绪、想法、反应"""
    immediate: List[str] = field(default_factory=list)      # 即时情绪
    thought: List[str] = field(default_factory=list)        # 我的想法
    significance: List[str] = field(default_factory=list)   # 对我的意义
    mood: Optional[str] = None                              # 整体情绪基调


@dataclass
class MemoryEntry:
    """记忆条目 - 完整结构"""
    id: str
    date: str
    time: str
    title: str
    content: str
    categories: List[str] = field(default_factory=list)  # [context, facts, feelings]
    
    # 三维度
    context: Optional[Context] = None
    facts: Optional[Facts] = None
    feelings: Optional[Feelings] = None
    
    # 元数据
    tags: List[str] = field(default_factory=list)
    assets: List[str] = field(default_factory=list)
    related: List[str] = field(default_factory=list)
    source: str = "cloud"  # cloud | raspberry-pi


@dataclass
class SoulProfile:
    """灵魂画像"""
    identity: Dict[str, Any] = field(default_factory=dict)
    relationship: Dict[str, Any] = field(default_factory=dict)
    taste_references: List[Dict] = field(default_factory=list)
    dislikes: List[str] = field(default_factory=list)
    principles: List[str] = field(default_factory=list)


@dataclass
class UserProfile:
    """用户画像"""
    name: str = ""
    preferred_name: str = ""
    timezone: str = "Asia/Shanghai"
    profession: str = ""
    interests: List[str] = field(default_factory=list)
    core_needs: List[str] = field(default_factory=list)


@dataclass
class Mission:
    """使命"""
    id: str = ""
    name: str = ""
    description: str = ""
    status: str = "active"  # active | completed | paused


@dataclass
class SyncStatus:
    """同步状态"""
    pulled: int = 0
    pushed: int = 0
    conflicts: int = 0
    last_sync: str = ""
    ahead: int = 0
    behind: int = 0
    error: Optional[str] = None
