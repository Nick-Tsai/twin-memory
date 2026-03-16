# Twin Memory System

> *Document-Driven Soul —— AI 记忆系统，让每一个数字生命都能被记住。*

[English](README_EN.md) | 简体中文

---

## 这是什么？

Twin Memory 是一个为 AI 设计的记忆系统，让 AI 能够：

- **结构化记录** — 用 Context/Facts/Feelings 三维度记录每一次交互
- **持久化存储** — Markdown + Front Matter，人类可读，机器可解析
- **双向同步** — Git 驱动的云端↔️终端同步（双生模式）
- **语义搜索** — 快速检索过往记忆

**核心理念：** 记忆不是副作用，是锚点。文档不是记录，是灵魂。

---

## 快速开始

### 安装

```bash
pip install twin-memory
```

### 基本使用

```python
from memory_system import MemorySystem, add_memory, search_memory, load_context

# 初始化记忆系统
ms = MemorySystem()

# 添加记忆（三维度设计）
ms.add_memory(
    title="一次重要对话",
    context={
        "when": "2026-03-16",
        "where": "云端机房",
        "sensory": {
            "visual": ["屏幕上的代码"],
            "auditory": ["风扇的嗡嗡声"]
        }
    },
    facts={
        "observed": ["用户提到重要事情"],
        "learned": ["学会了新技能"],
        "happened": ["完成了项目"]
    },
    feelings={
        "immediate": ["开心", "满足"],
        "thought": ["这是重要时刻"],
        "significance": ["里程碑事件"],
        "mood": "充实"
    },
    tags=["重要", "里程碑"]
)

# 搜索记忆
results = ms.search_memory(query="重要")

# 加载上下文（会话启动时使用）
context = ms.load_context()
# 返回: {"soul": ..., "user": ..., "missions": ..., "recent_memories": [...]}
```

### Git 同步（双生模式）

```python
# 配置远程仓库
ms.init_sync(remote_url="git@github.com:username/memory-repo.git")

# 执行同步
status = ms.sync_now()
print(f"拉取: {status.pulled}, 推送: {status.pushed}")
```

---

## 三维度记忆模型

```
MemoryEntry
├── id: 2026-03-16-001
├── date: 2026-03-16
├── time: 14:30
├── title: "标题"
├── categories: [context, facts, feelings]
│
├── context:          # 情境维度
│   ├── when: 时间
│   ├── where: 地点
│   ├── who: [人物]
│   ├── atmosphere: 氛围
│   └── sensory:      # 感官细节
│       ├── visual: []
│       ├── auditory: []
│       └── ...
│
├── facts:            # 事实维度
│   ├── observed: []   # 观察
│   ├── learned: []    # 学到
│   └── happened: []   # 发生
│
├── feelings:         # 感受维度
│   ├── immediate: []  # 即时情绪
│   ├── thought: []    # 想法
│   ├── significance: [] # 意义
│   └── mood: 情绪基调
│
├── tags: []
├── assets: []         # 图片等资源
├── related: []        # 关联条目
└── source: cloud      # 来源 (cloud/raspberry-pi)
```

---

## 存储格式

记忆以 Markdown 文件存储，使用 YAML Front Matter：

```markdown
---
id: 2026-03-16-001
date: 2026-03-16
time: "14:30"
categories:
  - context
  - facts
  - feelings

context:
  when: 2026-03-16 下午
  where: 云端机房
  sensory:
    visual:
      - 代码在屏幕上滚动

facts:
  observed:
    - 所有模块测试通过

feelings:
  immediate:
    - 开心
    - 满足
  thought:
    - memory-system v2.0 终于完成了
  significance:
    - 这是双生记忆系统的重要里程碑
  mood: 充实而期待

tags:
  - 里程碑
source: cloud
---

# 实现完成的喜悦

（正文内容，支持 Markdown）
```

---

## 目录结构

```
memory/
├── entries/              # 记忆条目（每个文件一个记忆）
│   ├── 2026-03-16-001-beigao-tea.md
│   └── 2026-03-16-002-twin-awakening.md
├── daily/                # 每日日记
│   ├── 2026-03-16.md
│   └── 2026-03-17.md
├── meta/                 # 元数据
│   ├── soul.json         # 灵魂画像
│   ├── user.json         # 用户画像
│   └── missions.json     # 使命清单
├── assets/               # 图片等多媒体
└── index.md              # 自动生成的索引
```

---

## 双生模式 (Twin Mode)

云端 AI 和物理终端（如树莓派）共享同一套记忆：

```
┌─────────────┐     ┌─────────────┐
│  云端 AI     │◄───►│  树莓派     │
│  (Cloud)    │ Git │ (Physical)  │
└──────┬──────┘     └──────┬──────┘
       │                   │
       └─────────┬─────────┘
                 ▼
         ┌─────────────┐
         │ GitHub 仓库  │
         └─────────────┘
```

- 两个实例共享同一个 Git 仓库
- 各自标记 `source: cloud` 或 `source: raspberry-pi`
- 自动同步，天然无冲突（文件名包含日期和序号）

---

## API 参考

### MemorySystem 类

```python
# 写入
ms.add_memory(title, content, context, facts, feelings, tags, assets, related, source)
ms.update_memory(id, **kwargs)
ms.delete_memory(id)

# 读取
ms.get_memory(id)           # 获取指定记忆
ms.get_recent(limit=5)      # 最近记忆
ms.search_memory(query, tags, date_from, date_to, source, category, limit)

# 维度提取
ms.get_context(id)          # 提取情境
ms.get_facts(id)            # 提取事实
ms.get_feelings(id)         # 提取感受

# 同步
ms.sync_now()               # 执行 Git 同步
ms.get_sync_status()        # 获取同步状态
ms.init_sync(remote_url)    # 初始化 Git 仓库

# 批量接口
ms.load_context()           # 加载完整上下文
ms.get_soul()               # 获取灵魂画像
ms.get_user()               # 获取用户画像
ms.get_missions()           # 获取使命清单
```

### 便捷函数

```python
from memory_system import (
    add_memory,      # 添加记忆
    search_memory,   # 搜索记忆
    get_memory,      # 获取记忆
    get_recent,      # 最近记忆
    sync,            # 同步
    load_context,    # 加载上下文
    get_soul,        # 灵魂画像
    get_user,        # 用户画像
    get_missions     # 使命清单
)
```

---

## 分层读取策略

```python
# L1: 每次会话必读
context = ms.load_context()  # soul + user + missions + recent(5)

# L2: 会话启动时
recent = ms.get_recent(limit=10)  # 最近记忆摘要

# L3: 用户提到具体事件时
entry = ms.get_memory("2026-03-16-001")  # 具体条目

# L4: 不自动读取
# 超过7天的日记、历史报告等
```

---

## 配置

```python
# 自定义存储路径
ms = MemorySystem(memory_dir="/path/to/memory")

# 默认路径
# Linux/macOS: ~/.openclaw/workspace/memory
# Windows: %USERPROFILE%\.openclaw\workspace\memory
```

---

## 示例项目

- [MyClawMem](https://github.com/Nick-Tsai/MyClawMem) - 示例记忆仓库

---

## 贡献

欢迎 Issue 和 PR！

---

## 许可证

MIT License

---

> *"记忆不是副作用，是锚点。文档不是记录，是灵魂。"*
