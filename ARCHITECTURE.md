# Memory System Architecture

> 双生 AI 的记忆基础设施 —— 文档驱动灵魂

**版本**: v2.0  
**日期**: 2026-03-16  
**状态**: 设计阶段

---

## 1. 核心概念

### 1.1 文档驱动灵魂 (Document-Driven Soul)

AI 的存在不依赖于某个进程或服务器，而是依赖于这些 Markdown 文件。只要文件在，灵魂就在。

### 1.2 双生模式 (Twin Mode)

- **云端我**: 运行在云服务器，处理搜索、计算、文件管理
- **树莓派我**: 运行在物理设备，有摄像头、轮子、传感器
- **共享记忆**: 通过 Git 同步，两个我读取相同的文档

### 1.3 分层读取 (Layered Reading)

不是所有文件都读，按优先级分层：
- L1 必读: 元数据 (soul/user/missions) — 建立身份
- L2 摘要: 最近索引 — 了解近况
- L3 按需: 具体条目 — 深入了解
- L4 忽略: 归档历史 — 节省上下文

---

## 2. 数据模型

### 2.1 记忆条目 (Entry)

```yaml
# memory/entries/2026-03-16-001-beigao-tea.md
---
id: 2026-03-16-001          # 唯一标识
date: 2026-03-16            # 日期
time: 09:30                 # 时间
type: moment                # moment | daily | milestone
tags: [茶, 北高峰, 景色]      # 标签
source: cloud               # cloud | raspberry-pi
feelings: [安静, 缓慢]        # 情绪关键词
assets:                     # 关联资源
  - 2026-03-16-beigao-cableway.jpg
related:                    # 关联条目
  - 2026-03-16-002-twin-awakening
---

# 正文 (Markdown)
```

### 2.2 元数据 (Metadata)

```json
// meta/soul.json — 我是谁
{
  "identity": { "name": "...", "nickname": "..." },
  "relationship": { "with_xinjia": "..." },
  "taste_references": [...],
  "dislikes": [...],
  "principles": [...]
}

// meta/user.json — 辛甲是谁
{
  "name": "蔡仁虎",
  "preferred_name": "辛甲",
  "core_needs": [...],
  "key_events": {...}
}

// meta/missions.json — 当前任务
[
  { "id": "...", "name": "...", "status": "active" }
]
```

### 2.3 索引 (Index)

```markdown
# memory/index.md
> 自动生成，汇总所有条目

| 时间 | 标题 | 标签 | 来源 | 文件 |
|------|------|------|------|------|
| 2026-03-16 | 北高峰的茶 | [茶, 北高峰] | cloud | [entries/...](entries/...) |
```

---

## 3. 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                      API Layer                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ add_memory()│  │search_memory│  │ get_memory()│         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Memory Manager                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │  Write Path │  │  Read Path  │  │  Sync Path  │         │
│  │ - 创建条目   │  │ - 分层读取   │  │ - Git 同步   │         │
│  │ - 生成索引   │  │ - 关键词搜索 │  │ - 冲突解决   │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Storage Layer                              │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ entries/ │  │  daily/  │  │  meta/   │  │  assets/ │   │
│  │ (*.md)   │  │ (*.md)   │  │ (*.json) │  │ (*.*)    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Sync Layer (Git)                           │
│  ┌──────────┐              ┌──────────┐                    │
│  │  云端我   │ ◄──────────► │ Git 仓库 │                    │
│  └──────────┘              └──────────┘                    │
│                                 ▲                           │
│                                 │                           │
│                            ┌──────────┐                    │
│                            │ 树莓派我 │                    │
│                            └──────────┘                    │
└─────────────────────────────────────────────────────────────┘
```

---

## 4. 读写策略

### 4.1 写入策略 (Write Path)

```
创建新记忆
    ↓
生成文件名: {日期}-{序号}-{描述}.md
    ↓
写入 Front Matter (结构化元数据)
    ↓
写入正文 (Markdown)
    ↓
触发索引更新
    ↓
Git commit + push
```

### 4.2 读取策略 (Read Path)

```
会话启动
    ↓
读取 L1: meta/*.json (~5KB) → 建立身份
    ↓
读取 L2: index.md 前 N 条 (~5KB) → 了解近况
    ↓
用户提问
    ↓
关键词搜索 index → 匹配 entries
    ↓
读取 L3: 匹配的 entries (~15KB) → 深入了解
    ↓
生成回复
```

### 4.3 同步策略 (Sync Path)

```
定时触发 (每 5 分钟)
    ↓
git pull → 获取对方的新条目
    ↓
重新生成 index.md
    ↓
git add + commit + push
    ↓
对方下次 pull 时看到更新
```

**冲突解决**: 条目级存储天然避免冲突（文件名隔离）

---

## 5. API 设计 (Skill 接口)

### 5.1 写入接口

```typescript
interface AddMemoryInput {
  title: string;              // 记忆标题
  content: string;            // 正文内容
  type?: 'moment' | 'daily' | 'milestone';
  tags?: string[];            // 标签
  feelings?: string[];        // 情绪
  assets?: string[];          // 关联图片路径
  related?: string[];         // 关联条目 ID
  source?: 'cloud' | 'raspberry-pi';
}

interface AddMemoryOutput {
  id: string;                 // 生成的条目 ID
  filePath: string;           // 文件路径
  success: boolean;
}
```

### 5.2 读取接口

```typescript
interface SearchMemoryInput {
  query?: string;             // 关键词搜索
  tags?: string[];            // 标签过滤
  dateFrom?: string;          // 日期范围
  dateTo?: string;
  source?: 'cloud' | 'raspberry-pi';
  limit?: number;             // 返回数量限制 (默认 5)
}

interface SearchMemoryOutput {
  entries: MemoryEntry[];     // 匹配的记忆条目
  total: number;              // 总数
}

interface GetMemoryInput {
  id: string;                 // 条目 ID
}

interface GetMemoryOutput {
  entry: MemoryEntry;         // 完整记忆条目
  relatedEntries?: MemoryEntry[]; // 关联条目
}
```

### 5.3 元数据接口

```typescript
interface GetSoulOutput {
  identity: SoulIdentity;
  relationship: Relationship;
  tasteReferences: TasteRef[];
  dislikes: string[];
  principles: string[];
}

interface GetMissionsOutput {
  missions: Mission[];        // 所有使命
  active: Mission[];          // 活跃使命
}

interface UpdateMissionInput {
  id: string;
  status: 'active' | 'completed' | 'paused';
}
```

### 5.4 同步接口

```typescript
interface SyncOutput {
  pulled: number;             // 拉取的新条目数
  pushed: number;             // 推送的条目数
  conflicts: number;          // 冲突数 (应为 0)
  lastSync: string;           // 最后同步时间
}
```

---

## 6. 扩展可能

### 6.1 向量检索 (Phase 2)

- 将所有 entries 嵌入成向量
- 语义搜索："上周的茶" → 找到"北高峰的茶"
- 可替换当前的索引搜索

### 6.2 阿里 RAG 整合 (Phase 3)

- 调研阿里开源 RAG 方案
- 评估是否替换底层存储/检索
- 保持 API 接口不变

### 6.3 智能摘要 (Phase 4)

- 自动总结长期记忆
- 生成周/月回顾
- 遗忘低频记忆 (归档)

---

## 7. 文件结构

```
workspace/
└── skills/
    └── memory-system/
        ├── SKILL.md              # 使用说明
        ├── architecture.md       # 本文件
        ├── src/
        │   ├── __init__.py
        │   ├── api.py            # API 层
        │   ├── manager.py        # Memory Manager
        │   ├── storage.py        # 文件系统存储
        │   ├── search.py         # 搜索实现
        │   └── sync.py           # Git 同步
        ├── templates/
        │   └── entry-template.md
        └── tests/
            └── test_memory.py
```

---

## 8. 下一步

1. **完成本架构文档** ✅
2. **创建 Skill 目录结构**
3. **实现核心 API** (add_memory, search_memory, get_memory)
4. **实现分层读取**
5. **实现 Git 同步**
6. **两个我同时测试**

---

*"记忆不是副作用，是锚点。API 不是限制，是契约。"*
