"""
Storage Layer
文件系统存储实现
"""

import os
import json
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

from .models import MemoryEntry, Context, Facts, Feelings


class Storage:
    """文件系统存储"""
    
    def __init__(self, memory_dir: str = None):
        if memory_dir is None:
            # 默认路径
            home = Path.home()
            memory_dir = home / ".openclaw" / "workspace" / "memory"
        self.memory_dir = Path(memory_dir)
        self.entries_dir = self.memory_dir / "entries"
        self.meta_dir = self.memory_dir / "meta"
        self.assets_dir = self.memory_dir / "assets"
        self.daily_dir = self.memory_dir / "daily"
        
        # 确保目录存在
        for d in [self.entries_dir, self.meta_dir, self.assets_dir, self.daily_dir]:
            d.mkdir(parents=True, exist_ok=True)
    
    def _generate_front_matter(self, data: Dict[str, Any]) -> str:
        """生成 YAML Front Matter"""
        lines = ["---"]
        
        def format_value(v, indent=0):
            prefix = "  " * indent
            if isinstance(v, dict):
                result = []
                for key, val in v.items():
                    if isinstance(val, (dict, list)):
                        result.append(f"{prefix}{key}:")
                        result.append(format_value(val, indent + 1))
                    else:
                        result.append(f"{prefix}{key}: {val}")
                return "\n".join(result)
            elif isinstance(v, list):
                if not v:
                    return f"{prefix}[]"
                result = []
                for item in v:
                    if isinstance(item, str):
                        # 检查是否需要引号
                        if any(c in item for c in [':', '#', '[', ']', '{', '}', ',', '&', '*', '?', '|', '-', '<', '>', '=', '!', '%', '@', '`', '"', "'"]):
                            item = f'"{item}"'
                        result.append(f"{prefix}- {item}")
                    else:
                        result.append(f"{prefix}- {item}")
                return "\n".join(result)
            else:
                return f"{prefix}{v}"
        
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                lines.append(f"{key}:")
                lines.append(format_value(value, 1))
            else:
                lines.append(f"{key}: {value}")
        
        lines.append("---")
        return "\n".join(lines)
    
    def _parse_front_matter(self, content: str) -> tuple:
        """解析 YAML Front Matter，返回 (front_matter_dict, body)"""
        if not content.startswith('---'):
            return {}, content
        
        parts = content.split('---', 2)
        if len(parts) < 3:
            return {}, content
        
        fm_text = parts[1].strip()
        body = parts[2].strip()
        
        # 使用 PyYAML 解析
        try:
            result = yaml.safe_load(fm_text)
            if not isinstance(result, dict):
                result = {}
        except Exception as e:
            print(f"YAML parse error: {e}")
            result = {}
        
        return result, body
    
    def _dict_to_context(self, data: Dict) -> Context:
        """字典转 Context 对象"""
        if not data or not isinstance(data, dict):
            return Context()
        return Context(
            when=data.get('when'),
            where=data.get('where'),
            who=data.get('who', []),
            atmosphere=data.get('atmosphere'),
            sensory=data.get('sensory', {})
        )
    
    def _dict_to_facts(self, data: Dict) -> Facts:
        """字典转 Facts 对象"""
        if not data or not isinstance(data, dict):
            return Facts()
        return Facts(
            observed=data.get('observed', []),
            learned=data.get('learned', []),
            happened=data.get('happened', [])
        )
    
    def _dict_to_feelings(self, data: Dict) -> Feelings:
        """字典转 Feelings 对象"""
        if not data or not isinstance(data, dict):
            return Feelings()
        return Feelings(
            immediate=data.get('immediate', []),
            thought=data.get('thought', []),
            significance=data.get('significance', []),
            mood=data.get('mood')
        )
    
    def _context_to_dict(self, ctx: Context) -> Dict:
        """Context 对象转字典"""
        if not ctx:
            return {}
        result = {}
        if ctx.when:
            result['when'] = ctx.when
        if ctx.where:
            result['where'] = ctx.where
        if ctx.who:
            result['who'] = ctx.who
        if ctx.atmosphere:
            result['atmosphere'] = ctx.atmosphere
        if ctx.sensory:
            result['sensory'] = ctx.sensory
        return result
    
    def _facts_to_dict(self, facts: Facts) -> Dict:
        """Facts 对象转字典"""
        if not facts:
            return {}
        result = {}
        if facts.observed:
            result['observed'] = facts.observed
        if facts.learned:
            result['learned'] = facts.learned
        if facts.happened:
            result['happened'] = facts.happened
        return result
    
    def _feelings_to_dict(self, feelings: Feelings) -> Dict:
        """Feelings 对象转字典"""
        if not feelings:
            return {}
        result = {}
        if feelings.immediate:
            result['immediate'] = feelings.immediate
        if feelings.thought:
            result['thought'] = feelings.thought
        if feelings.significance:
            result['significance'] = feelings.significance
        if feelings.mood:
            result['mood'] = feelings.mood
        return result
    
    def create_entry(
        self,
        title: str,
        content: str = "",
        context: Context = None,
        facts: Facts = None,
        feelings: Feelings = None,
        tags: List[str] = None,
        assets: List[str] = None,
        related: List[str] = None,
        source: str = "cloud"
    ) -> Dict[str, Any]:
        """创建新记忆条目"""
        
        # 生成 ID
        date_str = datetime.now().strftime("%Y-%m-%d")
        existing = list(self.entries_dir.glob(f"{date_str}-*.md"))
        seq = len(existing) + 1
        seq_str = f"{seq:03d}"
        
        # 生成文件名
        slug = re.sub(r'[^\w\s-]', '', title).strip().lower()
        slug = re.sub(r'[-\s]+', '-', slug)[:30]
        filename = f"{date_str}-{seq_str}-{slug}.md"
        filepath = self.entries_dir / filename
        
        # 生成 ID
        entry_id = f"{date_str}-{seq_str}"
        
        # 确定 categories
        categories = []
        if context:
            categories.append("context")
        if facts:
            categories.append("facts")
        if feelings:
            categories.append("feelings")
        if not categories:
            categories = ["moment"]
        
        # 构建 Front Matter
        fm_data = {
            "id": entry_id,
            "date": date_str,
            "time": datetime.now().strftime("%H:%M"),
            "categories": categories
        }
        
        if context:
            fm_data["context"] = self._context_to_dict(context)
        if facts:
            fm_data["facts"] = self._facts_to_dict(facts)
        if feelings:
            fm_data["feelings"] = self._feelings_to_dict(feelings)
        
        fm_data["tags"] = tags or []
        fm_data["source"] = source
        fm_data["assets"] = assets or []
        fm_data["related"] = related or []
        
        # 写入文件
        front_matter = self._generate_front_matter(fm_data)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(front_matter)
            f.write("\n\n")
            f.write(f"# {title}\n\n")
            f.write(content)
        
        return {
            "id": entry_id,
            "filePath": str(filepath),
            "success": True
        }
    
    def read_entry(self, entry_id: str) -> Optional[MemoryEntry]:
        """读取指定条目"""
        # 查找文件
        pattern = f"*{entry_id}*.md"
        files = list(self.entries_dir.glob(pattern))
        
        if not files:
            return None
        
        filepath = files[0]
        return self._parse_entry_file(filepath)
    
    def _parse_entry_file(self, filepath: Path) -> MemoryEntry:
        """解析条目文件"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析 Front Matter
        fm, body = self._parse_front_matter(content)
        
        # 提取标题
        title = ""
        for line in body.split('\n'):
            if line.startswith('# '):
                title = line[2:].strip()
                break
        
        # 构建对象
        context = self._dict_to_context(fm.get('context', {}))
        facts = self._dict_to_facts(fm.get('facts', {}))
        feelings = self._dict_to_feelings(fm.get('feelings', {}))
        
        return MemoryEntry(
            id=fm.get('id', ''),
            date=fm.get('date', ''),
            time=fm.get('time', ''),
            title=title,
            content=body,
            categories=fm.get('categories', []),
            context=context,
            facts=facts,
            feelings=feelings,
            tags=fm.get('tags', []),
            assets=fm.get('assets', []),
            related=fm.get('related', []),
            source=fm.get('source', 'cloud')
        )
    
    def update_entry(self, entry_id: str, **kwargs) -> bool:
        """更新条目"""
        entry = self.read_entry(entry_id)
        if not entry:
            return False
        
        # 查找文件
        pattern = f"*{entry_id}*.md"
        files = list(self.entries_dir.glob(pattern))
        if not files:
            return False
        
        filepath = files[0]
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 解析 Front Matter
        fm, body = self._parse_front_matter(content)
        
        # 更新字段
        for key, value in kwargs.items():
            if key == 'content':
                body = value
            elif key == 'title':
                # 更新标题行
                lines = body.split('\n')
                for i, line in enumerate(lines):
                    if line.startswith('# '):
                        lines[i] = f"# {value}"
                        break
                body = '\n'.join(lines)
            elif key == 'context' and isinstance(value, Context):
                fm['context'] = self._context_to_dict(value)
            elif key == 'facts' and isinstance(value, Facts):
                fm['facts'] = self._facts_to_dict(value)
            elif key == 'feelings' and isinstance(value, Feelings):
                fm['feelings'] = self._feelings_to_dict(value)
            else:
                fm[key] = value
        
        # 写回文件
        front_matter = self._generate_front_matter(fm)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(front_matter)
            f.write("\n\n")
            f.write(body)
        
        return True
    
    def delete_entry(self, entry_id: str) -> bool:
        """删除条目"""
        pattern = f"*{entry_id}*.md"
        files = list(self.entries_dir.glob(pattern))
        
        if not files:
            return False
        
        files[0].unlink()
        return True
    
    def list_entries(self) -> List[Path]:
        """列出所有条目文件"""
        return sorted(self.entries_dir.glob("*.md"))
    
    def read_json(self, relative_path: str) -> Any:
        """读取 JSON 文件"""
        filepath = self.memory_dir / relative_path
        if not filepath.exists():
            return {}
        
        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def write_json(self, relative_path: str, data: Any) -> bool:
        """写入 JSON 文件"""
        filepath = self.memory_dir / relative_path
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return True
