# DBCheck v2.3.5 Release Notes

> 📅 2026-04-27
> 🎯 Theme: **Slow Query Deep Analysis — from detection to root cause**

---

## 🆕 New Features

### 1. Slow Query Deep Analysis Engine

A brand-new `slow_query_analyzer.py` module that goes beyond basic slow query detection — correlating execution latency, I/O patterns, lock waits, and temporary table usage across **6 database types**.

| Database | Data Source | Key Dimensions |
|----------|-------------|----------------|
| MySQL | `performance_schema.events_statements_summary_by_digest` | Latency, full table scans, lock waits, temp tables, sort ops |
| PostgreSQL | `pg_stat_statements` | Total/avg time, I/O time, temp blocks, long queries |
| Oracle | `v$sql` | Buffer Gets, Disk Reads, Elapsed Time |
| SQL Server | `sys.dm_exec_query_stats` | CPU, logical reads, elapsed time, physical reads |
| DM8 | `V$SQL` | Execution time, disk reads |
| TiDB | `information_schema.cluster_slow_query` | Query time, memory, scanned rows, Coprocessor tasks |

**Architecture highlights:**
- `SlowQueryResult` — standardized result container across all databases
- Factory function `get_slow_query_analyzer(db_type)` — auto-selects the right analyzer
- `build_slow_query_ai_prompt()` — generates targeted diagnostic prompts
- Integrates into `checkdb()` after AI diagnosis, results fed into `smart_analyze_*` for risk evaluation
- AI advisor receives `slow_query_top3` + `slow_query_count` metrics for precise per-query recommendations

### 2. Enhanced Risk Rules (+28 rules)

**MySQL**: +17 new rules including `performance_schema` status check, full table scan detection, lock wait ratio, AI diagnosis injection
**PostgreSQL**: +11 new rules including `pg_stat_statements` extension check, high-latency query, high I/O query, long-running query detection

Overall rule coverage: **100+ → 130+ rules** across all 6 database types.

### 3. `requirements.txt` — Standardized Dependency Management

All dependencies are now listed in `requirements.txt`:

```
pip install -r requirements.txt
```

Drivers are organized by category: Core, Web UI, Database Drivers, SSH, Batch Inspection.

---

## 🐛 Bug Fixes

### 1. AI Diagnosis Chapter Empty Lines (All Database Scripts)

**Problem**: The `_render_markdown_to_doc()` function was generating extra blank paragraphs for every empty line in AI-generated Markdown content, causing visible gaps between sections like `## 重点关注` and `## 优化建议`.

**Affected files** (all fixed):
- `main_mysql.py`, `main_tidb.py`, `main_sqlserver.py` — `_render_markdown_to_doc` empty line handler
- `main_pg.py` — AI chapter inline renderer (2 locations)
- `skill/dbcheck/scripts/main_mysql.py`, `main_sqlserver.py`, `main_pg.py` — skill mirrors

**Fix**: Changed `if not line: doc.add_paragraph()` → `if not line: continue` — skip empty lines instead of rendering them as blank paragraphs.

### 2. `dbcheck.spec` Stale Hidden Imports

**Problem**: `dbcheck.spec` referenced non-existent modules (`main_oracle`, `run_inspection`) and was missing newly added modules (`slow_query_analyzer`, `db_history`, `desensitize`, `pyodbc`, `i18n.*`, `main_sqlserver`, `main_tidb`).

**Fix**: Cleaned up orphaned references and added all missing `hiddenimports`.

---

## 📚 Documentation

- Added **"Slow Query Deep Analysis"** section to both `README.md` and `README_zh.md` with:
  - Feature overview and architecture diagram
  - Per-database collection dimensions table
  - Integration flow with `checkdb()`
  - Enhanced risk rules documentation
  - AI diagnosis enhancement details
- Updated `README.md` / `README_zh.md` dependency installation section to use `requirements.txt`
- Updated Skill file structure to include `slow_query_analyzer.py`

---

## 🔧 Maintenance

- `dbcheck.spec` synchronized with latest codebase (hidden imports, module list)
- `main.spec` (legacy MySQL-only spec) remains deprecated — `dbcheck.spec` is the active spec
