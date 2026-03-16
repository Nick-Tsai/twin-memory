"""
Memory System Tests
测试用例
"""

import pytest
import tempfile
import shutil
from pathlib import Path

from memory_system import (
    MemorySystem,
    MemoryEntry,
    add_memory,
    search_memory,
    get_memory,
    sync
)


class TestMemorySystem:
    """记忆系统测试"""
    
    @pytest.fixture
    def temp_memory(self):
        """创建临时记忆目录"""
        temp_dir = tempfile.mkdtemp()
        memory_dir = Path(temp_dir) / "memory"
        
        # 初始化元数据
        (memory_dir / "meta").mkdir(parents=True)
        
        import json
        (memory_dir / "meta" / "soul.json").write_text(json.dumps({
            "identity": {"name": "Test"}
        }))
        (memory_dir / "meta" / "user.json").write_text(json.dumps({
            "name": "Test User"
        }))
        (memory_dir / "meta" / "missions.json").write_text(json.dumps([
            {"id": "m1", "name": "Test Mission", "status": "active"}
        ]))
        
        yield memory_dir
        
        # 清理
        shutil.rmtree(temp_dir)
    
    def test_add_memory(self, temp_memory):
        """测试添加记忆"""
        system = MemorySystem(str(temp_memory))
        
        result = system.add_memory(
            title="测试记忆",
            content="这是一个测试",
            tags=["测试", "例子"],
            feelings=["开心"]
        )
        
        assert result["success"] is True
        assert "id" in result
        assert "filePath" in result
    
    def test_get_memory(self, temp_memory):
        """测试获取记忆"""
        system = MemorySystem(str(temp_memory))
        
        # 先添加
        result = system.add_memory(
            title="可查询的记忆",
            content="内容在这里"
        )
        
        # 再查询
        entry = system.get_memory(result["id"])
        
        assert entry is not None
        assert entry.title == "可查询的记忆"
    
    def test_search_memory(self, temp_memory):
        """测试搜索记忆"""
        system = MemorySystem(str(temp_memory))
        
        # 添加多条记忆
        system.add_memory(title="北高峰的茶", content="很好喝", tags=["茶"])
        system.add_memory(title="西湖的景", content="很美", tags=["景色"])
        system.add_memory(title="灵隐的禅", content="很安静", tags=["禅"])
        
        # 搜索
        results = system.search_memory(query="北高峰")
        
        assert len(results) >= 1
        assert any("北高峰" in r.title for r in results)
    
    def test_search_by_tag(self, temp_memory):
        """测试按标签搜索"""
        system = MemorySystem(str(temp_memory))
        
        system.add_memory(title="记忆1", content="", tags=["工作"])
        system.add_memory(title="记忆2", content="", tags=["生活"])
        system.add_memory(title="记忆3", content="", tags=["工作"])
        
        results = system.search_memory(tags=["工作"])
        
        assert len(results) == 2
        assert all("工作" in r.tags for r in results)
    
    def test_get_recent(self, temp_memory):
        """测试获取最近记忆"""
        system = MemorySystem(str(temp_memory))
        
        # 添加多条
        for i in range(10):
            system.add_memory(title=f"记忆{i}", content="")
        
        # 获取最近 5 条
        results = system.get_recent(limit=5)
        
        assert len(results) == 5
    
    def test_update_memory(self, temp_memory):
        """测试更新记忆"""
        system = MemorySystem(str(temp_memory))
        
        # 添加
        result = system.add_memory(title="旧标题", content="旧内容")
        
        # 更新
        success = system.update_memory(result["id"], title="新标题")
        
        assert success is True
        
        # 验证
        entry = system.get_memory(result["id"])
        assert entry.title == "新标题"
    
    def test_delete_memory(self, temp_memory):
        """测试删除记忆"""
        system = MemorySystem(str(temp_memory))
        
        # 添加
        result = system.add_memory(title="将被删除", content="")
        
        # 删除
        success = system.delete_memory(result["id"])
        
        assert success is True
        
        # 验证
        entry = system.get_memory(result["id"])
        assert entry is None
    
    def test_load_context(self, temp_memory):
        """测试加载上下文"""
        system = MemorySystem(str(temp_memory))
        
        context = system.load_context()
        
        assert "soul" in context
        assert "user" in context
        assert "missions" in context
        assert "recent_memories" in context


class TestStorage:
    """存储层测试"""
    
    # ... storage specific tests


class TestSearch:
    """搜索层测试"""
    
    # ... search specific tests


class TestSync:
    """同步层测试"""
    
    # ... sync specific tests
    pass
