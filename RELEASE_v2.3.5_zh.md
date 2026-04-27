# DBCheck v2.3.5 发版说明

> 📅 2026-04-27
> 🎯 本次主题：**慢查询深度分析 — 从发现问题到定位根因**

---

## 🆕 新功能

### 1. 慢查询深度分析引擎

全新 `slow_query_analyzer.py` 模块，超越传统慢查询检测，从执行延迟、I/O 模式、锁等待、临时表使用等多维度进行深度剖析，覆盖 **6 种数据库类型**。

| 数据库 | 数据来源 | 采集维度 |
|--------|----------|----------|
| MySQL | `performance_schema.events_statements_summary_by_digest` | 延迟、全表扫描、锁等待、临时表、排序操作 |
| PostgreSQL | `pg_stat_statements` | 总时间/平均时间、I/O 时间、临时块、长查询 |
| Oracle | `v$sql` | Buffer Gets、Disk Reads、Elapsed Time |
| SQL Server | `sys.dm_exec_query_stats` | CPU、逻辑读、Elapsed Time、物理读 |
| DM8 | `V$SQL` | 执行时间、磁盘读 |
| TiDB | `information_schema.cluster_slow_query` | 查询时间、内存使用量、扫描行数、Coprocessor 任务数 |

**架构亮点：**
- `SlowQueryResult` — 统一标准化结果容器
- 工厂函数 `get_slow_query_analyzer(db_type)` — 自动选择对应分析器
- `build_slow_query_ai_prompt()` — 生成专项诊断 Prompt
- 集成到 `checkdb()` AI 诊断之后执行，结果注入 `smart_analyze_*` 进行风险规则评估
- AI advisor 接收 `slow_query_top3` + `slow_query_count` 指标，提供精确到单条语句的优化建议

### 2. 增强风险规则（+28 条）

- **MySQL**：新增 17+ 条规则，包括 `performance_schema` 状态检测、全表扫描检测、锁等待比例、AI 诊断注入
- **PostgreSQL**：新增 11+ 条规则，包括 `pg_stat_statements` 扩展检测、高延迟语句、高 I/O 语句、长查询阈值检测

规则总量：**100+ → 130+ 条**，覆盖全部 6 种数据库。

### 3. `requirements.txt` — 标准化依赖管理

所有依赖统一收录到 `requirements.txt`：

```bash
pip install -r requirements.txt
```

按类别分组：核心库、Web UI、数据库驱动、SSH、批量巡检。

---

## 🐛 Bug 修复

### 1. AI 诊断章节多余空行（所有数据库脚本）

**问题**：`_render_markdown_to_doc()` 函数将 AI 生成的 Markdown 中的每个空行都渲染为一个独立的空段落，导致 `## 重点关注` 与 `## 优化建议` 等章节之间出现明显多余间距。

**修复文件**（均已修复）：
- `main_mysql.py`、`main_tidb.py`、`main_sqlserver.py` — `_render_markdown_to_doc` 空行处理
- `main_pg.py` — AI 章节渲染逻辑（2 处）
- `skill/dbcheck/scripts/main_mysql.py`、`main_sqlserver.py`、`main_pg.py` — Skill 同步版本

**修复方式**：`if not line: doc.add_paragraph()` → `if not line: continue`，跳过空行而非渲染为空段落。

### 2. `dbcheck.spec` 过期 Hidden Imports

**问题**：`dbcheck.spec` 中引用了不存在的模块（`main_oracle`、`run_inspection`），同时遗漏了新增模块（`slow_query_analyzer`、`db_history`、`desensitize`、`pyodbc`、`i18n.*`、`main_sqlserver`、`main_tidb`）。

**修复**：清理孤立引用，补充所有缺失的 `hiddenimports`。

---

## 📚 文档更新

- 中英文 README 均新增 **"慢查询深度分析"** 章节，内容包括：
  - 功能概述与架构说明
  - 各数据库采集维度表
  - 与巡检流程的集成关系
  - 增强风险规则说明
  - AI 诊断增强详情
- 中英文 README 安装依赖部分改为使用 `requirements.txt`
- Skill 文件结构补充 `slow_query_analyzer.py`

---

## 🔧 维护

- `dbcheck.spec` 与最新代码库同步（hidden imports、模块列表）
- `main.spec`（旧版 MySQL 专用 spec）保持废弃状态，`dbcheck.spec` 为当前活跃打包配置
