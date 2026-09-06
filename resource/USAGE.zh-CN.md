# Poirot 使用说明书

> Poirot 的完整安装、配置与操作指南。
>
> **语言：** [English](../USAGE.md) · [简体中文](USAGE.zh-CN.md) · [日本語](USAGE.ja.md)

---

## 目录

- [环境要求](#环境要求)
- [安装](#安装)
- [配置详解](#配置详解)
- [启动方式](#启动方式)
- [命令参考](#命令参考)
- [Skill 系统](#skill-系统)
- [长期记忆](#长期记忆)
- [多 Agent](#多-agent)
- [Sandbox 沙箱](#sandbox-沙箱)
- [MCP 工具配置](#mcp-工具配置)
- [模型与 Provider 切换](#模型与-provider-切换)
- [Docker 部署](#docker-部署)
- [配置场景](#配置场景)
- [使用技巧](#使用技巧)
- [TUI 操作指南](#tui-操作指南)
- [故障排查](#故障排查)
- [FAQ](#faq)

---

## 环境要求

| 项目 | 要求 |
|------|------|
| Python | 3.12+ |
| 操作系统 | Windows / Linux / macOS |
| LLM API Key | DeepSeek（默认）/ OpenAI / Qwen 至少一个 |
| Docker | 仅 Sandbox Docker 模式需要 |
| Node.js | 仅 MCP stdio server（如 freeweb-mcp）需要 |

---

## 安装

### 1. 克隆仓库

```bash
git clone <repo-url>
cd Poirot
```

### 2. 创建虚拟环境

**Windows（PowerShell）：**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS：**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

> 也可使用 conda：`conda create -n poirot python=3.12 && conda activate poirot`

### 3. 安装依赖

```bash
# 基础安装 + 开发工具（pytest）
pip install -e ".[dev]"

# 如需 Docker 沙箱
pip install -e ".[docker]"
```

### 4. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env`，至少填入一个 API Key：

```env
DEEPSEEK_API_KEY=sk-your-key-here
```

### 5. 验证安装

```bash
poirot
```

看到 Poirot ASCII Logo + 欢迎页即安装成功。

---

## 配置详解

Poirot 通过项目根目录的 `.env` 文件配置。`.env.example` 是完整模板。

### LLM Provider

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `DEEPSEEK_API_KEY` | DeepSeek API 密钥（默认 provider，链尾兜底） | — |
| `DEEPSEEK_BASE_URL` | DeepSeek 端点 | `https://api.deepseek.com` |
| `OPENAI_API_KEY` | OpenAI API 密钥 | — |
| `OPENAI_BASE_URL` | OpenAI 端点（代理/中转时填写） | 官方默认 |
| `QWEN_API_KEY` | 通义千问 API 密钥 | — |
| `QWEN_BASE_URL` | Qwen 端点 | `https://dashscope.aliyuncs.com/compatible-mode/v1` |

> 至少配置一个 provider。推荐至少配置 DeepSeek 作为降级兜底。

### Sandbox 沙箱

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `POIROT_SANDBOX_USE` | 沙箱 provider 路径（留空=禁用） | 留空 |
| `POIROT_SANDBOX_IMAGE` | Docker 镜像名 | `all-in-one-sandbox:latest` |
| `POIROT_SANDBOX_PORT` | 容器起始端口（占用时自动递增） | `18000` |
| `POIROT_SANDBOX_EXECUTOR` | Docker 执行环境（`local` / `wsl`） | `local` |
| `POIROT_SANDBOX_WSL_DISTRO` | WSL 发行版名 | `Ubuntu` |
| `POIROT_SANDBOX_WSL_USER` | WSL 内执行用户 | 默认用户 |
| `POIROT_SANDBOX_CONTAINER_PREFIX` | 容器名前缀 | `poirot-sandbox` |
| `POIROT_SANDBOX_IDLE_TIMEOUT` | 空闲销毁超时秒（0=永不） | `600` |
| `POIROT_SANDBOX_REPLICAS` | 预热池大小（0=不预热） | `3` |

**启用 Local 沙箱：**
```env
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.local.local_sandbox_provider:LocalSandboxProvider
```

**启用 Docker 沙箱：**
```env
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.docker.docker_sandbox_provider:DockerSandboxProvider
```

> Docker 模式首次需拉取镜像：`docker pull all-in-one-sandbox:latest`
>
> Windows + WSL2：设 `POIROT_SANDBOX_EXECUTOR=wsl`

### MCP

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `POIROT_MCP_ENABLED` | MCP 总开关 | `false` |
| `POIROT_MCP_CONFIG_PATH` | MCP 配置文件路径 | `.poirot/mcp_servers.yaml` |
| `POIROT_MCP_CORE_TOOLS` | 核心工具（逗号分隔，启动必加载） | `web_search,browse_page` |

### Skill

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `POIROT_SKILL_ENABLED` | Skill 模块总开关 | `false` |
| `POIROT_SKILL_DB_PATH` | Skill SQLite 路径 | `.poirot/skills.db` |
| `POIROT_SKILL_DIRS` | Skill 扫描目录（逗号分隔） | `skills/` |
| `POIROT_SKILL_INCLUDE_BUILTIN` | 是否加载 builtin 核心 skill | `true` |
| `POIROT_SKILL_MAX_INJECT` | 单轮最多注入 skill 数 | `3` |
| `POIROT_SKILL_QUALITY_THRESHOLD` | quality filter 淘汰阈值 | `0.3` |
| `POIROT_SKILL_MIN_SELECTIONS` | 淘汰判定最少 selections | `5` |

**Skill 自进化（Layer 2）：**

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `POIROT_SKILL_EVOLVE_ENABLED` | 自进化开关 | `false` |
| `POIROT_SKILL_EVOLVE_THRESHOLD` | 进化触发阈值 | `0.3` |
| `POIROT_SKILL_EVOLVE_MIN_SELECTIONS` | 进化最少 selections | `5` |
| `POIROT_SKILL_EVOLVE_COOLDOWN_TURNS` | 进化冷却轮数 | `10` |
| `POIROT_SKILL_EVOLVE_MUTATE_BUDGET` | 变异 token 预算 | `20` |
| `POIROT_SKILL_EVOLVE_MAX_STEPS` | 最大进化步数 | `5` |

**Skill 评估（Layer 3）：**

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `POIROT_SKILL_EVAL_ENABLED` | 评估层开关 | `false` |
| `POIROT_SKILL_EVAL_JUDGMENT_ENABLED` | 执行判断 | `true` |
| `POIROT_SKILL_EVAL_TASK_JUDGE_ENABLED` | 任务质量评分 | `true` |
| `POIROT_SKILL_EVAL_CONTRACT_CHECK` | 响应契约检查 | `true` |
| `POIROT_SKILL_EVAL_ASYNC` | 异步 eval | `true` |
| `POIROT_SKILL_EVAL_SKIP_NO_SKILL` | 无 skill 时跳过 eval | `true` |
| `POIROT_SKILL_EVAL_RUNTIME_WINDOW` | RuntimeTracker 窗口 | `20` |
| `POIROT_SKILL_EVAL_DEGRADATION_DELTA` | 退化判定 delta | `0.15` |

---

## 启动方式

### 1. TUI 全屏应用（默认）

```bash
poirot
```

| 快捷键 | 功能 |
|--------|------|
| `Ctrl+P` | 命令面板 |
| `Ctrl+N` | MCP 管理面板 |
| `Ctrl+L` | 清屏 |
| `Ctrl+C` | 退出 |
| `Enter` | 发送 |
| `Shift+拖动` | 选取复制 |

### 2. 传统滚动 CLI

```bash
poirot cli
```

### 3. 单次研究（非交互）

```bash
poirot run "分析 2026 年 AI Agent 框架发展趋势"
poirot run "问题" --thread-id my-thread --run-id my-run
poirot run "快速问答" --no-expert
poirot run "问题" --no-artifact
```

---

## 命令参考

### 基础命令

| 命令 | 说明 |
|------|------|
| `/help` | 显示所有命令 |
| `/clear` | 清屏 |
| `/exit` `/quit` | 退出 |
| `/expand` | 展开上一轮 Thought + 工具结果 |
| `/thinking on\|off` | 切换 Thought 折叠显示 |

### 模式切换

| 命令 | 说明 |
|------|------|
| `/expert` | 切换到 expert 模式（深度研究） |
| `/default` | 切换到 default 模式（轻量对话） |
| `/report [topic]` | 从当前 thread 生成报告 |

### 模型与工具

| 命令 | 说明 |
|------|------|
| `/model` | 显示当前模型 |
| `/model <provider>` | 切换 provider |
| `/model <provider> <model>` | 切换 provider 并指定模型 |
| `/tools` | 列出可用工具 |
| `/thread` | 显示 thread 信息 |

### Skill 命令

| 命令 | 说明 |
|------|------|
| `/skill` `/skill list` | 列出 active skills |
| `/skill search <query>` | 搜索 builtin skills |
| `/skill <name>` | 强制使用 skill（override） |
| `/skill off` | 清除 override |
| `/skill enable/disable <name>` | 启用/禁用 skill |
| `/skill install <path> [name]` | 安装外部 skill |
| `/skill evolve <name>` | 手动触发进化 |
| `/skill capture <pattern> <name>` | 沉淀新 skill |
| `/skill history <name>` | skill 版本历史 |
| `/skill health [name]` | skill 健康报告（Layer 3） |
| `/skill eval-history <name>` | SkillJudgment 历史（Layer 3） |

### MCP 命令

| 命令 | 说明 |
|------|------|
| `/mcp` `/mcp list` | 列出 MCP server 和工具 |
| `/mcp reload` | 重新加载 MCP 配置 |

---

## Skill 系统

Skill 是**研究过程知识 bundle**——prompt-level 注入，不是可执行函数。"如何验证信源"是 skill，"执行一次搜索"是工具。

### 三层架构

**Layer 1（基础层）：**
- `SQLiteSkillStore` — 存储 + 版本 DAG + 4 计数器
- `SkillSelector` — quality filter + LLM 混合选择
- `SkillInjectionMiddleware` — `before_model` 注入
- `SkillMetricsMiddleware` — `wrap_tool_call` applied 标记 + `after_agent` 归因

**Layer 2（进化层）：**
- `MetricMonitor` — effective_rate 低于阈值时触发
- `CaptureTrigger` — 手动 capture
- `IVEFocuser` — 5 问题诊断 + 偏差证据
- `LLMMutator` — LLM 变异 skill 文本
- `ScoreDeltaGate` — 变异前后评分门控
- `GitRatchet` — 棘轮：退化时回滚

**Layer 3（评估层）：**
- `SkillJudgmentAnalyzer` — per-skill per-task LLM 判断
- `TaskQualityJudge` — 4 维评分（accuracy 0.50 / completeness 0.35 / efficiency 0.05 / depth 0.10）
- `ResponseContractChecker` — contract-aware 规则检查
- `RuntimeTracker` — applied_rate 趋势 + `degraded_skills()` 回滚信号

### 启用 Skill

```env
POIROT_SKILL_ENABLED=true
```

Builtin 核心 skill 自动加载。用户 skill 放在 `skills/` 目录。

### Skill 文件格式

```markdown
---
name: source-verification
description: 验证信源可靠性
allowed_tools:
  - web_search
  - browse_page
---

# Source Verification Skill

## 何时使用
需要验证信源可信度时...

## 如何做
1. 检查来源权威性
2. 交叉验证
3. ...
```

### 内置 Skills

Poirot 内置 36 个 skill，分 5 类：

| 类别 | 数量 | 示例 |
|------|------|------|
| core | 12 | deep-research, source-verification, plan, spike, skill-creator, test-driven-development |
| research | 11 | arxiv, osint-investigation, systematic-literature-review, research-paper-writing |
| software-development | 7 | github-code-review, github-pr-workflow, node-inspect-debugger, python-debugpy |
| creative | 3 | architecture-diagram, chart-visualization, frontend-design |
| productivity | 2 | code-documentation, ppt-generation |

> Core 类自动加载，其余通过 `/skill search <query>` 发现。

---

## 长期记忆

Poirot 实现了 5 层长期记忆系统。记忆 trace 以 Markdown（`traces.md`）存储 — truth source — 配合 BM25 检索和艾宾浩斯衰减。

### 启用

```env
POIROT_MEMORY_USE=default
```

### 配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `POIROT_MEMORY_USE` | 记忆 provider（空=禁用，`default`=启用） | 空 |
| `POIROT_MEMORY_STORAGE_PATH` | Markdown truth source 目录 | `.poirot/memory` |
| `POIROT_MEMORY_ENABLE_RECALL` | before_model 召回注入 | `true` |
| `POIROT_MEMORY_TOKEN_BUDGET` | 召回注入 token 预算 | `2000` |
| `POIROT_MEMORY_PHASE2_ENABLED` | L5 自动沉淀 worker | `false` |
| `POIROT_MEMORY_PHASE2_TURNS` | 每 N 轮触发沉淀 | `10` |

### 工作原理

1. **召回（L4）** — 每次 `before_model`，MemoryMiddleware 通过 BM25 检索相关记忆，注入为 per-call HumanMessage（保护 prompt caching）。
2. **沉淀（L5）** — 每 N 轮，MemoryConsolidationMiddleware 非阻塞提交任务到 MemoryWorker（daemon 线程）。worker 调 LLM 抽取 episodic 记忆 → encode → 候选 ≥ N → LLM 合并 → consolidate。
3. **持久化** — 所有 trace 存储在 `.poirot/memory/traces.md`（YAML frontmatter + 正文）。
4. **衰减** — 艾宾浩斯公式在检索时懒计算（无后台任务）。遗忘的 trace 标记 `metadata.forgotten=True`，retriever 过滤（不删除）。

---

## 多 Agent

Poirot 可以将子任务委派给外部 coding agent（specialist）和内部自身副本（subagent）。

### 启用

```env
POIROT_MULTIAGENT_ENABLED=true
POIROT_MULTIAGENT_SPECIALISTS=pi,codex,claude,subagent
```

### 配置

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `POIROT_MULTIAGENT_ENABLED` | 多 Agent 总开关 | `true` |
| `POIROT_MULTIAGENT_SPECIALISTS` | specialist 列表（逗号分隔） | `pi,codex,claude,subagent` |
| `POIROT_MULTIAGENT_AUTO_APPROVE` | 自动批准 specialist 调用 | `true` |
| `POIROT_MULTIAGENT_L2_ENABLED` | L2 演化层 | `false` |
| `POIROT_MULTIAGENT_L3_ENABLED` | L3 评估层 | `false` |

### Pi Specialist（自带 API key，无需登录）

Pi 支持多 provider — 你现有的 DeepSeek key 直接可用：

```env
POIROT_MULTIAGENT_PI_PROVIDER=deepseek
POIROT_MULTIAGENT_PI_API_KEYMiddleware.abefore_model 从 state["sandbox"] 恢复 ContextVar — 复用父 sandbox_id
- **Specialist**：MCP 命令包含 `--sandbox-url` — specialist 通过 HTTP 连接 lead 的 Docker 容器

---

## Sandbox 沙箱

### Local 沙箱

```env
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.local.local_sandbox_provider:LocalSandboxProvider
```

### Docker 沙箱

```env
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.docker.docker_sandbox_provider:DockerSandboxProvider
POIROT_SANDBOX_IMAGE=all-in-one-sandbox:latest
```

```bash
docker pull all-in-one-sandbox:latest
```

### Windows + WSL2

```env
POIROT_SANDBOX_EXECUTOR=wsl
POIROT_SANDBOX_WSL_DISTRO=Ubuntu
```

---

## MCP 工具配置

```env
POIROT_MCP_ENABLED=true
```

配置文件 `.poirot/mcp_servers.yaml`：

```yaml
servers:
  freeweb:
    transport: stdio
    command: npx
    args: ["-y", "freeweb-mcp@latest"]
    enabled: true
    timeout: 300
    tools:
      include: []
      exclude: ["search_and_browse"]

fallback_chains:
  web_search:
    - freeweb:web_search
    - builtin:ddg_search

core_tools:
  - web_search
  - browse_page
```

修改后执行 `/mcp reload` 重新加载。

### 远程 MCP Server（http）

`transport: http` 直连远程 MCP server，无需本地进程。`headers` 支持 `${VAR}`
从宿主环境插值，API key 不落盘。

示例：[You.com](https://you.com/docs) 的远程 MCP server（web search，
key 在 [you.com/platform/api-keys](https://you.com/platform/api-keys) 获取）：

```yaml
servers:
  youcom:
    transport: http
    url: https://api.you.com/mcp
    headers:
      Authorization: "Bearer ${YDC_API_KEY}"
    enabled: true
    timeout: 300
    connect_timeout: 60

fallback_chains:
  web_search:
    - youcom:you-search
    - builtin:ddg_search
```

免 key 方式（仅基础 `you-search`）：`url: https://api.you.com/mcp?profile=free`，
去掉 `headers` 即可。

---

## 模型与 Provider 切换

### 路由链

```
researcher: [openai, qwen] → deepseek（兜尾）
reporter:   [openai, qwen] → deepseek（兜尾）
```

### 启动时指定

```bash
poirot --provider openai
poirot --provider qwen --model qwen-max
```

### 运行时切换

```
/model                    # 查看当前
/model openai             # 切换
/model openai gpt-4.1     # 切换 + 指定模型
```

### 支持的 Provider

| Provider | 默认模型 | 窗口 |
|----------|----------|------|
| deepseek | deepseek-v4-flash | 200K |
| openai | gpt-4.1-mini | — |
| qwen | qwen-plus | — |

---

## Docker 部署

Poirot 提供 Dockerfile + docker-compose，一键部署。

### 快速启动

```bash
# 1. 复制配置
cp .env.example .env
# 编辑 .env — 填入 DEEPSEEK_API_KEY=sk-xxx

# 2. 构建并运行（TUI 交互）
docker compose run --rm poirot

# 3. 或单次研究
docker compose run --rm poirot run "分析 2026 年 AI agent 趋势"
```

### 镜像内容

- Python 3.12 + 全部依赖（pyyaml、langchain 等）
- Node.js 20（MCP stdio server + pi coding agent）
- 默认开启：`POIROT_MEMORY_USE=default`、`POIROT_MULTIAGENT_ENABLED=true`
- 默认 Local sandbox（无需 DinD）

### 容器内 Sandbox

**默认（Local sandbox）** — agent 在 Poirot 容器内执行命令，无需 DinD。

**Docker 隔离 sandbox** — agent 在独立沙箱容器中执行，需挂载 docker.sock：

```yaml
# docker-compose.yml — 取消注释：
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

```env
# .env：
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.docker.docker_sandbox_provider:DockerSandboxProvider
POIROT_SANDBOX_EXECUTOR=local
```

### 数据持久化

| 宿主机路径 | 容器路径 | 内容 |
|-----------|---------|------|
| `./.poirot/` | `/app/.poirot/` | DB、日志、artifact、memory traces、MCP 配置 |
| `./skills/` | `/app/skills/` | 用户上传的 skill |
| `./.env` | `/app/.env` | 环境配置（Ctrl+B 面板可写回） |

---

## 配置场景

### 场景 1：轻量聊天（最小配置）

```env
DEEPSEEK_API_KEY=sk-xxx
POIROT_SKILL_ENABLED=false
POIROT_MCP_ENABLED=false
POIROT_SANDBOX_USE=
POIROT_MEMORY_USE=
POIROT_MULTIAGENT_ENABLED=false
```

然后 `/default` 进入轻量模式。无 sandbox、无 skill、无记忆 — 纯 LLM 对话。

### 场景 2：全功能（所有特性开启）

```env
DEEPSEEK_API_KEY=sk-xxx

# 记忆（L4 召回 + L5 自动沉淀）
POIROT_MEMORY_USE=default
POIROT_MEMORY_PHASE2_ENABLED=true
POIROT_MEMORY_PHASE2_TURNS=10

# Skill（L1 基础 + L2 演化 + L3 评估）
POIROT_SKILL_ENABLED=true
POIROT_SKILL_EVOLVE_ENABLED=true
POIROT_SKILL_EVAL_ENABLED=true
POIROT_SKILL_MAX_INJECT=15

# 多 Agent（specialist + L2/L3）
POIROT_MULTIAGENT_ENABLED=true
POIROT_MULTIAGENT_L2_ENABLED=true
POIROT_MULTIAGENT_L3_ENABLED=true

# Pi specialist（自带 DeepSeek key，无需登录）
POIROT_MULTIAGENT_PI_PROVIDER=deepseek
POIROT_MULTIAGENT_PI_API_KEY=sk-xxx

# Docker sandbox
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.docker.docker_sandbox_provider:DockerSandboxProvider
POIROT_SANDBOX_EXECUTOR=wsl              # Windows + WSL2

# MCP 工具
POIROT_MCP_ENABLED=true
```

### 场景 3：开发模式（Local sandbox，无 Docker）

```env
DEEPSEEK_API_KEY=sk-xxx
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.local.local_sandbox_provider:LocalSandboxProvider
POIROT_SKILL_ENABLED=true
POIROT_MEMORY_USE=default
POIROT_MULTIAGENT_ENABLED=true
```

### 场景 4：编码 Agent（pi specialist 为主）

```env
DEEPSEEK_API_KEY=sk-xxx

# Pi specialist + DeepSeek
POIROT_MULTIAGENT_ENABLED=true
POIROT_MULTIAGENT_SPECIALISTS=pi,subagent
POIROT_MULTIAGENT_PI_PROVIDER=deepseek
POIROT_MULTIAGENT_PI_API_KEY=sk-xxx

# 代码执行 sandbox
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.docker.docker_sandbox_provider:DockerSandboxProvider

# 编码 skill
POIROT_SKILL_ENABLED=true
POIROT_SKILL_MAX_INJECT=15
```

---

## 使用技巧

### 记忆系统

**观察记忆运行：**
- `.poirot/memory/traces.md` — 所有记忆 trace（truth source，人类可读 Markdown）
- Journal 事件在 `.poirot/logs/threads/<thread_id>/runs/<run_id>/events.jsonl` — `memory.encode`、`memory.consolidate`
- Worker actor 在 operation_log 中：`worker:{thread_id}:{turn_count}`

**调整沉淀频率：**
```env
# 更频繁（每 5 轮 — 记忆建立更快，LLM 开销更大）
POIROT_MEMORY_PHASE2_TURNS=5

# 更省（每 20 轮 — 更慢，更便宜）
POIROT_MEMORY_PHASE2_TURNS=20
```

**记忆没生效？**
1. 检查 `.env` 有 `POIROT_MEMORY_USE=default`
2. 检查 `.poirot/memory/traces.md` 是否存在（首次 encode 时自动创建）
3. 前 N 轮无沉淀（worker 在第 N 轮才触发）
4. 召回需要已有 trace — 空库 = 无召回

### 多 Agent

**Pi specialist 没出现？**
1. `pi` CLI 已安装：`pi --version`（或 `npm install -g @earendil-works/pi-coding-agent`）
2. API key 可用：`.env` 里有 `DEEPSEEK_API_KEY`（自动检测）
3. 查看启动日志中 `[PiSpecialist]` 消息

**触发 specialist 委派：**
- Agent 自动调 `delegate_to_specialist(goal=..., success_criteria=...)` 处理子任务
- `POIROT_MULTIAGENT_AUTO_APPROVE=true` — 无需人工确认
- 或手动：输入"用 pi 写一个 Python 脚本..."

**Subagent vs Specialist：**
- **Subagent** = Poirot 自身副本（同 LLM，隔离 context，共享 sandbox）— 适合 Poirot 能力范围内的子任务
- **Specialist** = 外部 CLI agent（pi/codex/claude，各自 LLM，共享 sandbox）— 适合需要专业工具的编码任务

### Skill 系统

**只加载了 core skill？**
- 设计如此：启动时只加载 `builtin_skills/core/`（12 个）
- 其他类别通过 `/skill search <关键词>` 或 `skill_search` 工具搜索
- 安装外部 skill：`/skill install github:owner/repo`

**skill_search 返回空？**
- Skill name/description 是英文 — 用英文关键词搜索
- `skill_search("frontend")` → 找到 `frontend-design` ✅
- `skill_search("前端")` → 无匹配 ❌（子串匹配，无跨语言）

### Sandbox

**Windows + WSL2 Docker：**
```env
POIROT_SANDBOX_EXECUTOR=wsl
POIROT_SANDBOX_WSL_DISTRO=Ubuntu
```

**Sandbox 目录是空的？**
- Agent 必须写到 `/mnt/poirot/user-data/`（挂载区）— DockerPathGuard 强制
- 挂载区外的文件（如 `/tmp`）在容器销毁时丢失（`--rm`）
- 查看 Windows host 上 `.poirot/sandbox/aio_docker/<sandbox_id>/` 的持久化文件
- 查看 `.poirot/outputs/` 的提取产物（通过 `present_files` 工具）

---

## TUI 操作指南

- **欢迎页**：居中 Logo + 输入框，首次输入后切换到对话页
- **对话页**：左侧对话区 + 底部输入框 + 状态行，宽屏显示右侧信息面板
- **Thought 折叠**：`+ Thought: 120ms`，`/expand` 展开全文，`/thinking off` 关闭
- **复制**：按住 `Shift` 拖动选取

---

## 故障排查

### `api_key is empty for provider: deepseek`

`.env` 中 API Key 为空，至少配置一个 provider。

### Skill 模块未加载

1. `POIROT_SKILL_ENABLED=true`
2. `skills/` 目录存在
3. 从项目根目录启动

### MCP 工具不显示

1. `POIROT_MCP_ENABLED=true`
2. server `enabled: true`
3. `command` 可执行
4. `/mcp list` 查看状态，`/mcp reload` 重试

### Docker 沙箱启动失败

1. Docker daemon 运行中
2. 镜像已拉取
3. Windows + WSL2：`POIROT_SANDBOX_EXECUTOR=wsl`

---

## FAQ

**Q: 必须用 DeepSeek 吗？**

A: 不是。DeepSeek 是默认且作为降级兜底。可只用 OpenAI 或 Qwen，但推荐配置 DeepSeek 作为兜底。

**Q: Skill 和 MCP 工具有什么区别？**

A: Skill 是"研究过程知识"（know how），prompt 注入，不可执行。MCP 工具是"外部能力"（do something），function call，可执行。

**Q: Skill 自进化会修改我的 skill 文件吗？**

A: 会。Layer 2 启用后 `LLMMutator` 变异 skill 文本并创建新版本。`GitRatchet` 确保退化时回滚。`/skill history <name>` 查看历史。

**Q: 如何禁用高级功能做简单对话？**

A:
```env
POIROT_SKILL_ENABLED=false
POIROT_MCP_ENABLED=false
POIROT_SANDBOX_USE=
```
然后 `/default` 轻量模式。

**Q: 如何写自己的 Skill？**

A: 在 `skills/` 下创建子目录，含 `SKILL.md`（frontmatter + 正文）。重启或 `/skill list`。

**Q: 如何跑测试？**

A:
```bash
python -m pytest poirot/backend/tests/ -q
python -m pytest poirot/backend/tests/v1/unit/skill/ -q
```

---

<div align="center">

<sub>有问题？提 Issue。</sub>

</div>
