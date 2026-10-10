# Poirot — Usage Guide

> Complete guide for installing, configuring, and operating Poirot.
>
> **Languages:** [English](USAGE.md) · [简体中文](resource/USAGE.zh-CN.md) · [日本語](resource/USAGE.ja.md)

---

## Table of Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
- [Launch Modes](#launch-modes)
- [Commands](#commands)
- [Skill System](#skill-system)
- [Long-Term Memory](#long-term-memory)
- [Multi-Agent](#multi-agent)
- [Sandbox](#sandbox)
- [MCP Tools](#mcp-tools)
- [Model & Provider Switching](#model--provider-switching)
- [Docker Deployment](#docker-deployment)
- [Configuration Scenarios](#configuration-scenarios)
- [Usage Tips](#usage-tips)
- [TUI Guide](#tui-guide)
- [Troubleshooting](#troubleshooting)
- [FAQ](#faq)

---

## Requirements

| Item | Requirement |
|------|-------------|
| Python | 3.12+ |
| OS | Windows / Linux / macOS |
| LLM API Key | At least one: DeepSeek (default) / OpenAI / Qwen |
| Docker | Only for Docker sandbox mode |
| Node.js | Only for MCP stdio servers (e.g. freeweb-mcp) |

---

## Installation

### 1. Clone

```bash
git clone <repo-url>
cd Poirot
```

### 2. Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv .venv
.venv\Scripts\activate
```

**Linux / macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

> Or use conda: `conda create -n poirot python=3.12 && conda activate poirot`

### 3. Install

```bash
# Base + dev tools (pytest)
pip install -e ".[dev]"

# With Docker sandbox support
pip install -e ".[docker]"
```

### 4. Configure

```bash
cp .env.example .env
```

Edit `.env` — fill in at least one API key:

```env
DEEPSEEK_API_KEY=sk-your-key-here
```

### 5. Verify

```bash
poirot
```

You should see the Poirot ASCII logo and welcome screen.

---

## Configuration

Poirot is configured via a `.env` file in the project root. `.env.example` is the full template.

### LLM Providers

| Variable | Description | Default |
|----------|-------------|---------|
| `DEEPSEEK_API_KEY` | DeepSeek API key (default provider, chain-tail fallback) | — |
| `DEEPSEEK_BASE_URL` | DeepSeek endpoint | `https://api.deepseek.com` |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `OPENAI_BASE_URL` | OpenAI endpoint (for proxy/relay) | official default |
| `QWEN_API_KEY` | Qwen (Alibaba) API key | — |
| `QWEN_BASE_URL` | Qwen endpoint | `https://dashscope.aliyuncs.com/compatible-mode/v1` |

> At least one provider must be configured. DeepSeek is recommended as it serves as the fallback chain tail.

### Sandbox

| Variable | Description | Default |
|----------|-------------|---------|
| `POIROT_SANDBOX_USE` | Sandbox provider path (empty = disabled) | empty |
| `POIROT_SANDBOX_IMAGE` | Docker image name | `all-in-one-sandbox:latest` |
| `POIROT_SANDBOX_PORT` | Container start port (auto-increment on conflict) | `18000` |
| `POIROT_SANDBOX_EXECUTOR` | Docker exec env (`local` / `wsl`) | `local` |
| `POIROT_SANDBOX_WSL_DISTRO` | WSL distro name (when executor=wsl) | `Ubuntu` |
| `POIROT_SANDBOX_WSL_USER` | WSL user | default user |
| `POIROT_SANDBOX_CONTAINER_PREFIX` | Container name prefix | `poirot-sandbox` |
| `POIROT_SANDBOX_IDLE_TIMEOUT` | Idle destroy timeout in seconds (0 = never) | `600` |
| `POIROT_SANDBOX_REPLICAS` | Warm pool size (0 = no preheat) | `3` |

**Enable Local sandbox (host process):**
```env
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.local.local_sandbox_provider:LocalSandboxProvider
```

**Enable Docker sandbox (container isolation):**
```env
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.docker.docker_sandbox_provider:DockerSandboxProvider
```

> Docker mode: pull image first — `docker pull all-in-one-sandbox:latest`
>
> Windows + WSL2 Docker: set `POIROT_SANDBOX_EXECUTOR=wsl`

### MCP

| Variable | Description | Default |
|----------|-------------|---------|
| `POIROT_MCP_ENABLED` | MCP master switch | `false` |
| `POIROT_MCP_CONFIG_PATH` | MCP server config file path | `.poirot/mcp_servers.yaml` |
| `POIROT_MCP_CORE_TOOLS` | Core tools (comma-separated, loaded at startup) | `web_search,browse_page` |

### Skill

| Variable | Description | Default |
|----------|-------------|---------|
| `POIROT_SKILL_ENABLED` | Skill module master switch | `false` |
| `POIROT_SKILL_DB_PATH` | Skill SQLite database path | `.poirot/skills.db` |
| `POIROT_SKILL_DIRS` | Skill scan directories (comma-separated) | `skills/` |
| `POIROT_SKILL_INCLUDE_BUILTIN` | Load builtin core skills | `true` |
| `POIROT_SKILL_MAX_INJECT` | Max skills injected per turn | `3` |
| `POIROT_SKILL_QUALITY_THRESHOLD` | Quality filter threshold | `0.3` |
| `POIROT_SKILL_MIN_SELECTIONS` | Min selections before quality filter applies | `5` |

**Skill Evolution (Layer 2):**

| Variable | Description | Default |
|----------|-------------|---------|
| `POIROT_SKILL_EVOLVE_ENABLED` | Evolution switch | `false` |
| `POIROT_SKILL_EVOLVE_THRESHOLD` | Evolution trigger threshold | `0.3` |
| `POIROT_SKILL_EVOLVE_MIN_SELECTIONS` | Min selections to trigger evolution | `5` |
| `POIROT_SKILL_EVOLVE_COOLDOWN_TURNS` | Cooldown turns between evolutions | `10` |
| `POIROT_SKILL_EVOLVE_MUTATE_BUDGET` | Mutation token budget | `20` |
| `POIROT_SKILL_EVOLVE_MAX_STEPS` | Max evolution steps | `5` |

**Skill Evaluation (Layer 3):**

| Variable | Description | Default |
|----------|-------------|---------|
| `POIROT_SKILL_EVAL_ENABLED` | Evaluation switch | `false` |
| `POIROT_SKILL_EVAL_JUDGMENT_ENABLED` | Execution judgment (SkillJudgment) | `true` |
| `POIROT_SKILL_EVAL_TASK_JUDGE_ENABLED` | Task quality scoring | `true` |
| `POIROT_SKILL_EVAL_CONTRACT_CHECK` | Response contract checking | `true` |
| `POIROT_SKILL_EVAL_ASYNC` | Async eval (fire-and-forget) | `true` |
| `POIROT_SKILL_EVAL_SKIP_NO_SKILL` | Skip eval when no skill injected | `true` |
| `POIROT_SKILL_EVAL_RUNTIME_WINDOW` | RuntimeTracker window | `20` |
| `POIROT_SKILL_EVAL_DEGRADATION_DELTA` | Degradation delta threshold | `0.15` |

### Memory

| Variable | Description | Default |
|----------|-------------|---------|
| `POIROT_MEMORY_USE` | Memory provider (empty = disabled) | empty |
| `POIROT_MEMORY_STORAGE_PATH` | Markdown truth source path | `.poirot/memory` |
| `POIROT_MEMORY_ENABLE_RECALL` | before_model recall | `true` |
| `POIROT_MEMORY_TOKEN_BUDGET` | Recall token budget | `2000` |
| `POIROT_MEMORY_PHASE2_ENABLED` | L5 auto-consolidation | `false` |
| `POIROT_MEMORY_PHASE2_TURNS` | Consolidation every N turns | `10` |

### Multi-Agent

| Variable | Description | Default |
|----------|-------------|---------|
| `POIROT_MULTIAGENT_ENABLED` | Multi-agent switch | `true` |
| `POIROT_MULTIAGENT_SPECIALISTS` | Specialist list | `pi,codex,claude,subagent` |
| `POIROT_MULTIAGENT_AUTO_APPROVE` | Auto-approve calls | `true` |
| `POIROT_MULTIAGENT_PI_PROVIDER` | Pi provider (deepseek/openai/...) | empty |
| `POIROT_MULTIAGENT_PI_API_KEY` | Pi API key (empty = auto-scan env) | empty |
| `POIROT_MULTIAGENT_L2_ENABLED` | L2 evolution layer | `false` |
| `POIROT_MULTIAGENT_L3_ENABLED` | L3 eval layer | `false` |

---

## Launch Modes

### 1. TUI Full-Screen (default)

```bash
poirot
```

Textual full-screen dual-state layout — welcome view → conversation view.

| Key | Action |
|-----|--------|
| `Ctrl+P` | Command palette |
| `Ctrl+N` | MCP panel |
| `Ctrl+L` | Clear screen |
| `Ctrl+C` | Quit |
| `Enter` | Send |
| `Shift+Drag` | Select to copy |

### 2. CLI Scrolling

```bash
poirot cli
```

Traditional `prompt_toolkit` + `rich` scrolling mode. Slash-command completion + bottom toolbar.

### 3. Single Research (non-interactive)

```bash
# Basic
poirot run "Analyze AI agent framework trends in 2026"

# Specify thread and run
poirot run "question" --thread-id my-thread --run-id my-run

# Lightweight mode
poirot run "quick question" --no-expert

# No artifact saved
poirot run "question" --no-artifact
```

### Launch Arguments

| Arg | Description |
|-----|-------------|
| `--provider <name>` | Force provider (`deepseek` / `openai` / `qwen`) |
| `--model <name>` | Specify model name |
| `run <question>` | Single research subcommand |
| `--expert` / `--no-expert` | Enable/disable deep research mode |
| `--thread-id <id>` | Thread ID |
| `--run-id <id>` | Run ID |
| `--logs-root <path>` | Logs root directory |
| `--no-artifact` | Don't save artifact |

---

## Commands

Type `/` in TUI or CLI for command completion.

### Basic

| Command | Description |
|---------|-------------|
| `/help` | Show all commands |
| `/clear` | Clear screen |
| `/exit` `/quit` | Exit |
| `/expand` | Expand last round's Thought + tool results |
| `/thinking on\|off` | Toggle Thought fold display |

### Mode

| Command | Description |
|---------|-------------|
| `/expert` | Switch to expert mode (deep research), next round |
| `/default` | Switch to default mode (lightweight chat), next round |
| `/report [topic]` | Generate report from current thread |

### Model & Tools

| Command | Description |
|---------|-------------|
| `/model` | Show current model |
| `/model <provider>` | Switch provider, next round |
| `/model <provider> <model>` | Switch provider and model |
| `/tools` | List available tools |
| `/thread` | Show thread info |
| `/prompt list` | List prompt templates |
| `/prompt show <cat/name>` | Show prompt template |
| `/prompt reload` | Reload prompt templates |

### Skill

| Command | Description |
|---------|-------------|
| `/skill` `/skill list` | List active skills |
| `/skill search <query>` | Search builtin skills |
| `/skill <name>` | Force-use skill (override) |
| `/skill off` | Clear override |
| `/skill enable <name>` | Enable skill |
| `/skill disable <name>` | Disable skill |
| `/skill install <path> [name]` | Install external skill |
| `/skill evolve <name>` | Manually trigger evolution |
| `/skill capture <pattern> <name>` | Capture new skill |
| `/skill history <name>` | Skill version history |
| `/skill health [name]` | Skill health report (Layer 3) |
| `/skill eval-history <name>` | SkillJudgment history (Layer 3) |

### MCP

| Command | Description |
|---------|-------------|
| `/mcp` `/mcp list` | List loaded MCP servers and tools |
| `/mcp reload` | Reload MCP config and reconnect |

---

## Skill System

Skills are **research process knowledge bundles** — prompt-level injections, not executable functions. "How to verify a source" is a skill. "Execute a web search" is a tool.

### Three-Layer Architecture

**Layer 1 (Base):**
- `SQLiteSkillStore` — storage + version DAG + 4 counter metrics
- `SkillSelector` — quality filter + LLM hybrid selection
- `SkillInjectionMiddleware` — `before_model` injection
- `SkillMetricsMiddleware` — `wrap_tool_call` applied marking + `after_agent` attribution

**Layer 2 (Evolution):**
- `MetricMonitor` — triggers when effective_rate < threshold
- `CaptureTrigger` — manual capture trigger
- `IVEFocuser` — 5-question diagnosis + deviation evidence
- `LLMMutator` — LLM-driven skill text variation
- `ScoreDeltaGate` — pre/post mutation score gate
- `GitRatchet` — ratchet: auto-rollback on degradation

**Layer 3 (Eval):**
- `SkillJudgmentAnalyzer` — per-skill per-task LLM judgment (applied + deviation)
- `TaskQualityJudge` — 4-dimension scoring (accuracy 0.50 / completeness 0.35 / efficiency 0.05 / depth 0.10)
- `ResponseContractChecker` — contract-aware rule checking
- `RuntimeTracker` — applied-rate trend + `degraded_skills()` rollback signal
- `RegistryEvalBridge` — fail-closed bridge to L2

### Enabling Skills

```env
POIROT_SKILL_ENABLED=true
```

Builtin core skills auto-load on startup. User skills go in `skills/` (one subdirectory per skill, containing `SKILL.md`).

### Skill File Format

```markdown
---
name: source-verification
description: Verify source reliability
allowed_tools:
  - web_search
  - browse_page
---

# Source Verification Skill

## When to Use
When you need to verify source credibility...

## How
1. Check source authority
2. Cross-reference multiple sources
3. ...
```

### Selection Mechanism

Each `before_model` turn:
1. **Override** — user-specified skills (`/skill <name>`) are force-included
2. **Quality filter** — skills with `effective_rate < threshold` AND `selections >= min` are pruned
3. **LLM select** — if candidates > `max_inject`, LLM selects the most relevant ≤ max
4. **Fallback** — no LLM: rank by `effective_rate` descending

### Evolution

When enabled, skills with persistently low `effective_rate` auto-trigger:
1. `IVEFocuser` diagnoses weaknesses (5 questions)
2. `LLMMutator` rewrites skill text
3. `ScoreDeltaGate` ensures mutation scores higher than original
4. `GitRatchet` auto-rollbacks on degradation

Manual trigger: `/skill evolve <name>`

### Evaluation

When enabled, runs asynchronously after each task:
- `SkillJudgmentAnalyzer` — LLM judges if each skill was applied + records deviation
- `TaskQualityJudge` — 4-dimension weighted scoring
- `ResponseContractChecker` — scans skill text keywords to compile applicable rules, checks response compliance
- `RuntimeTracker` — tracks applied-rate trend, provides degradation signal

View results: `/skill health <name>`, `/skill eval-history <name>`

### Builtin Skills

Poirot ships with 36 builtin skills across 5 categories:

| Category | Count | Examples |
|----------|-------|----------|
| core | 12 | deep-research, source-verification, plan, spike, skill-creator, test-driven-development, systematic-debugging |
| research | 11 | arxiv, osint-investigation, systematic-literature-review, research-paper-writing, consulting-analysis |
| software-development | 7 | github-code-review, github-pr-workflow, github-repo-management, node-inspect-debugger, python-debugpy |
| creative | 3 | architecture-diagram, chart-visualization, frontend-design |
| productivity | 2 | code-documentation, ppt-generation |

> Core skills auto-load on startup. Others are discoverable via `/skill search <query>`.

---

## Long-Term Memory

Poirot implements a 5-layer long-term memory system. Memory traces are stored as Markdown (`traces.md`) — the truth source — with BM25 retrieval and Ebbinghaus decay.

### Enable

```env
POIROT_MEMORY_USE=default
```

### Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `POIROT_MEMORY_USE` | Memory provider (empty = disabled, `default` = enabled) | empty |
| `POIROT_MEMORY_STORAGE_PATH` | Markdown truth source directory | `.poirot/memory` |
| `POIROT_MEMORY_ENABLE_RECALL` | before_model recall injection | `true` |
| `POIROT_MEMORY_ENABLE_EXTRACT` | after_model real-time extraction | `false` |
| `POIROT_MEMORY_TOKEN_BUDGET` | Recall injection token budget | `2000` |
| `POIROT_MEMORY_PHASE2_ENABLED` | L5 auto-consolidation worker | `false` |
| `POIROT_MEMORY_PHASE2_TURNS` | Consolidation trigger every N turns | `10` |

### How It Works

1. **Recall (L4)** — Every `before_model`, `MemoryMiddleware` retrieves relevant memories via BM25, injects them as a per-call `HumanMessage` (protects prompt caching), and writes `recalled_memories` index to state.
2. **Consolidation (L5)** — Every N turns, `MemoryConsolidationMiddleware` non-blocking submits a task to `MemoryWorker` (daemon thread). The worker calls LLM to extract episodic memories → `encode` → if candidates ≥ N, calls LLM to merge → `consolidate`.
3. **Persistence** — All traces stored in `.poirot/memory/traces.md` (YAML frontmatter + content, `<!-- trace: {id} -->` separators).
4. **Decay** — Ebbinghaus formula computed lazily at retrieve time (no background tasks). Forgotten traces marked `metadata.forgotten=True`, filtered by retriever (not deleted).

### Observability

- `.poirot/memory/traces.md` — all memory traces (truth source)
- Journal events: `memory.encode`, `memory.consolidate`, `memory.reconsolidate`, `memory.associate`
- Worker actor in operation_log: `worker:{thread_id}:{turn_count}`

---

## Multi-Agent

Poirot can delegate sub-tasks to external coding agents (specialists) and internal self-copies (subagents).

### Enable

```env
POIROT_MULTIAGENT_ENABLED=true
POIROT_MULTIAGENT_SPECIALISTS=pi,codex,claude,subagent
```

### Configuration

| Variable | Description | Default |
|----------|-------------|---------|
| `POIROT_MULTIAGENT_ENABLED` | Multi-agent master switch | `true` |
| `POIROT_MULTIAGENT_SPECIALISTS` | Specialist list (comma-separated) | `pi,codex,claude,subagent` |
| `POIROT_MULTIAGENT_AUTO_APPROVE` | Auto-approve specialist calls | `true` |
| `POIROT_MULTIAGENT_L2_ENABLED` | L2 evolution layer | `false` |
| `POIROT_MULTIAGENT_L3_ENABLED` | L3 eval layer | `false` |

### Pi Specialist (own API key, no login)

Pi supports multiple providers — your existing DeepSeek key works directly:

```env
POIROT_MULTIAGENT_PI_PROVIDER=deepseek
POIROT_MULTIAGENT_PI_API_KEY=sk-your-deepseek-key
```

Install pi CLI: `npm install -g @earendil-works/pi-coding-agent --ignore-scripts`

Poirot auto-detects `DEEPSEEK_API_KEY` if provider/api_key not explicitly set.

### Codex / Claude Specialists

Require their respective CLI + platform credentials:
- Codex: `npm install -g @openai/codex` → `codex login` → `~/.codex/auth.json`
- Claude: `npm install -g @anthropic-ai/claude-code` → `claude` login → `~/.claude/.credentials.json`

> These CLIs are platform-bound (OpenAI / Anthropic). For own API key coding, use Pi specialist.

### Shared Sandbox

Specialists and subagents share the lead agent's Docker sandbox:
- **Subagent**: `SandboxMiddleware.abefore_model` restores ContextVar from `state["sandbox"]` — reuses parent `sandbox_id`
- **Specialist**: MCP command includes `--sandbox-url` — specialist connects to lead's Docker container via HTTP

---

## Sandbox

### Local Sandbox

Host process execution, no container isolation. For development:

```env
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.local.local_sandbox_provider:LocalSandboxProvider
```

### Docker Sandbox

Container isolation. For production:

```env
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.docker.docker_sandbox_provider:DockerSandboxProvider
POIROT_SANDBOX_IMAGE=all-in-one-sandbox:latest
```

Pull image first:
```bash
docker pull all-in-one-sandbox:latest
```

### Windows + WSL2

```env
POIROT_SANDBOX_EXECUTOR=wsl
POIROT_SANDBOX_WSL_DISTRO=Ubuntu
```

### Features

- **Warm pool** — `POIROT_SANDBOX_REPLICAS=3` pre-creates containers at startup
- **Idle destroy** — `POIROT_SANDBOX_IDLE_TIMEOUT=600` auto-destroys after 10min idle
- **Cross-process lock** — concurrent Poirot instances don't conflict
- **Path translation** — `LocalPathTranslator` auto-translates host ↔ container paths

---

## MCP Tools

MCP (Model Context Protocol) tools are configured via `.poirot/mcp_servers.yaml`.

### Enable

```env
POIROT_MCP_ENABLED=true
```

### Config Structure

```yaml
servers:
  freeweb:
    transport: stdio                    # stdio | sse | http
    command: npx
    args: ["-y", "freeweb-mcp@latest"]
    env:                                # env passed to subprocess
      # GITHUB_TOKEN: ${GITHUB_TOKEN}  # ${VAR} interpolates from host env
    enabled: true
    timeout: 300                        # per-call timeout (seconds)
    connect_timeout: 60                 # connection timeout (seconds)
    tools:
      include: []                       # whitelist (empty = all)
      exclude: ["search_and_browse"]    # blacklist

# Fallback chains: former fails → latter backs up
fallback_chains:
  web_search:
    - freeweb:web_search
    - builtin:ddg_search
  browse_page:
    - freeweb:browse_page
    - builtin:read_snapshot

# Core tools (loaded at startup)
core_tools:
  - web_search
  - browse_page

# Tool metadata (for externalization thresholds)
tool_metadata:
  web_search:
    typical_output_tokens: 800
    source: mcp
```

### Reload After Changes

```
/mcp reload
```

### Parallel Search MCP Example

For free web search and page fetching without a Parallel account or API key,
see the [runnable Parallel Search MCP example](examples/parallel-search/README.md).
It includes an opt-in HTTP configuration and a direct search/fetch command that
uses Poirot's MCP loader without an LLM.

---

## Model & Provider Switching

### Routing Chain

`FallbackChatModel` constructs role-based chains. On transient failures, auto-degrades to the next provider. DeepSeek always sits at the chain tail.

```
researcher: [openai, qwen] → deepseek (fallback tail)
reporter:   [openai, qwen] → deepseek (fallback tail)
```

### Switch at Launch

```bash
poirot --provider openai
poirot --provider qwen --model qwen-max
```

### Switch at Runtime

```
/model                    # show current
/model openai             # switch, next round
/model openai gpt-4.1     # switch + specify model
```

### Supported Providers

| Provider | Default Model | Window |
|----------|---------------|--------|
| deepseek | deepseek-v4-flash | 200K |
| openai | gpt-4.1-mini | — |
| qwen | qwen-plus | — |

---

## Docker Deployment

Poirot ships with a Dockerfile + docker-compose for one-command deployment.

### Quick Start

```bash
# 1. Copy config
cp .env.example .env
# Edit .env — fill in DEEPSEEK_API_KEY=sk-xxx

# 2. Build + run (TUI interactive)
docker compose run --rm poirot

# 3. Or single research
docker compose run --rm poirot run "Analyze AI agent trends 2026"
```

### What's Inside the Image

- Python 3.12 + all dependencies (pyyaml, langchain, etc.)
- Node.js 20 (for MCP stdio servers + pi coding agent)
- Default env: `POIROT_MEMORY_USE=default`, `POIROT_MULTIAGENT_ENABLED=true`
- Local sandbox mode (no DinD required)

### Sandbox in Docker

**Default (Local sandbox)** — agent runs commands inside the Poirot container. No Docker-in-Docker needed. Simple but no isolation.

**Docker sandbox (isolated)** — agent runs commands in a separate sandbox container. Requires Docker socket mount:

```yaml
# docker-compose.yml — uncomment:
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

```env
# .env:
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.docker.docker_sandbox_provider:DockerSandboxProvider
POIROT_SANDBOX_EXECUTOR=local
```

### Data Persistence

| Host path | Container path | Content |
|-----------|---------------|---------|
| `./.poirot/` | `/app/.poirot/` | DB, logs, artifacts, memory traces, MCP config |
| `./skills/` | `/app/skills/` | User-uploaded skills |
| `./.env` | `/app/.env` | Environment config (Ctrl+B panel can write back) |

### Common Commands

```bash
# TUI mode (default)
docker compose run --rm poirot

# CLI scrolling mode
docker compose run --rm poirot cli

# Single research
docker compose run --rm poirot run "your question"

# Expert mode
docker compose run --rm poirot --expert

# Rebuild after code changes
docker compose build
```

---

## Configuration Scenarios

### Scenario 1: Lightweight Chat (minimal)

```env
DEEPSEEK_API_KEY=sk-xxx
POIROT_SKILL_ENABLED=false
POIROT_MCP_ENABLED=false
POIROT_SANDBOX_USE=
POIROT_MEMORY_USE=
POIROT_MULTIAGENT_ENABLED=false
```

Then `/default` for lightweight mode. No sandbox, no skills, no memory — pure LLM chat.

### Scenario 2: Full Power (all features)

```env
DEEPSEEK_API_KEY=sk-xxx

# Memory (L4 recall + L5 auto-consolidation)
POIROT_MEMORY_USE=default
POIROT_MEMORY_PHASE2_ENABLED=true
POIROT_MEMORY_PHASE2_TURNS=10

# Skill (L1 base + L2 evolution + L3 eval)
POIROT_SKILL_ENABLED=true
POIROT_SKILL_EVOLVE_ENABLED=true
POIROT_SKILL_EVAL_ENABLED=true
POIROT_SKILL_MAX_INJECT=15

# Multi-Agent (specialist + L2/L3)
POIROT_MULTIAGENT_ENABLED=true
POIROT_MULTIAGENT_L2_ENABLED=true
POIROT_MULTIAGENT_L3_ENABLED=true

# Pi specialist (own DeepSeek key, no login)
POIROT_MULTIAGENT_PI_PROVIDER=deepseek
POIROT_MULTIAGENT_PI_API_KEY=sk-xxx

# Docker sandbox
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.docker.docker_sandbox_provider:DockerSandboxProvider
POIROT_SANDBOX_EXECUTOR=wsl              # Windows + WSL2

# MCP tools
POIROT_MCP_ENABLED=true
```

### Scenario 3: Development (local sandbox, no Docker)

```env
DEEPSEEK_API_KEY=sk-xxx
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.local.local_sandbox_provider:LocalSandboxProvider
POIROT_SKILL_ENABLED=true
POIROT_MEMORY_USE=default
POIROT_MULTIAGENT_ENABLED=true
```

### Scenario 4: Coding Agent (pi specialist focus)

```env
DEEPSEEK_API_KEY=sk-xxx

# Pi specialist with DeepSeek
POIROT_MULTIAGENT_ENABLED=true
POIROT_MULTIAGENT_SPECIALISTS=pi,subagent
POIROT_MULTIAGENT_PI_PROVIDER=deepseek
POIROT_MULTIAGENT_PI_API_KEY=sk-xxx

# Sandbox for code execution
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.docker.docker_sandbox_provider:DockerSandboxProvider

# Skill for coding
POIROT_SKILL_ENABLED=true
POIROT_SKILL_MAX_INJECT=15
```

---

## Usage Tips

### Memory System

**Observe memory in action:**
- `.poirot/memory/traces.md` — all memory traces (truth source, human-readable Markdown)
- Journal events in `.poirot/logs/threads/<thread_id>/runs/<run_id>/events.jsonl` — `memory.encode`, `memory.consolidate`, `memory.reconsolidate`
- Worker actor in operation_log: `worker:{thread_id}:{turn_count}`

**Tune consolidation frequency:**
```env
# More frequent (every 5 turns — faster memory building, more LLM cost)
POIROT_MEMORY_PHASE2_TURNS=5

# Less frequent (every 20 turns — slower, cheaper)
POIROT_MEMORY_PHASE2_TURNS=20
```

**Memory doesn't appear?**
1. Check `POIROT_MEMORY_USE=default` in `.env`
2. Check `.poirot/memory/traces.md` exists (auto-created on first encode)
3. First N turns: no consolidation yet (worker triggers at turn N)
4. Recall needs existing traces — empty store = no recall

### Multi-Agent

**Pi specialist not showing?**
1. `pi` CLI installed: `pi --version` (or `npm install -g @earendil-works/pi-coding-agent`)
2. API key available: `DEEPSEEK_API_KEY` in `.env` (auto-detected)
3. Check startup log for `[PiSpecialist]` messages

**Trigger specialist delegation:**
- Agent automatically calls `delegate_to_specialist(goal=..., success_criteria=...)` when it determines a sub-task needs a coding specialist
- `POIROT_MULTIAGENT_AUTO_APPROVE=true` — no human confirmation needed
- Or manually: type "use pi to write a Python script that..."

**Subagent vs Specialist:**
- **Subagent** = Poirot self-copy (same LLM, isolated context, shared sandbox) — for sub-tasks within Poirot's capability
- **Specialist** = External CLI agent (pi/codex/claude, own LLM, shared sandbox) — for coding tasks needing specialized tools

### Skill System

**Only core skills loaded?**
- By design: only `builtin_skills/core/` auto-loads at startup (12 skills)
- Other categories (research/creative/software-development/productivity) are searchable via `/skill search <query>` or `skill_search` tool
- Install externalskill install github:owner/repo`

**Skill search returns empty?**
- Skill names/descriptions are in English — search with English keywords
- `skill_search("frontend")` → finds `frontend-design` ✅
- `skill_search("前端")` → no match ❌ (substring match, no cross-language)

**Increase skill injection:**
```env
POIROT_SKILL_MAX_INJECT=15  # default 3, increase for more skills per turn
```

### Sandbox

**Windows + WSL2 Docker:**
```env
POIROT_SANDBOX_EXECUTOR=wsl
POIROT_SANDBOX_WSL_DISTRO=Ubuntu
```

**Sandbox directory is empty?**
- Agent must write to `/mnt/poirot/user-data/` (mount area) — DockerPathGuard enforces this
- Files outside mount area (e.g. `/tmp`) are lost when container is destroyed (`--rm`)
- Check `.poirot/sandbox/aio_docker/<sandbox_id>/` on Windows host for persisted files
- Check `.poirot/outputs/` for extracted artifacts (via `present_files` tool)

**Idle timeout:**
```env
POIROT_SANDBOX_IDLE_TIMEOUT=600   # 10 min (default)
POIROT_SANDBOX_IDLE_TIMEOUT=0     # never auto-destroy
```

---

## TUI Guide

### Welcome View

Centered logo + subtitle (version / mode / model) + centered input box + tip line. Switches to conversation view on first input.

### Conversation View

- **Left log:** User messages (accent left-bar cards) + assistant answers (Markdown) + tool call lines + Thought fold rows
- **Bottom input box:** Dark surface + accent left bar, with Build·model info line
- **Status bar:** Left: running spinner. Right: token usage.
- **Right panel** (wide screens ≥160 cols): Context / Compact / MCP / version info

### Thought Folding

Reasoning tokens fold into a summary line: `+ Thought: 120ms`

- `/expand` — unfold last round's full Thought + tool results
- `/thinking off` — hide Thought fold rows

### Copy

Hold `Shift` and drag to bypass Textual's mouse capture and use terminal-native selection.

---

## Troubleshooting

### `api_key is empty for provider: deepseek`

`.env` has empty `DEEPSEEK_API_KEY`. Configure at least one provider's API key.

### `no available provider for role: researcher`

No provider has a non-empty API key. Check `.env`.

### Skill module not loaded

1. `POIROT_SKILL_ENABLED=true` in `.env`
2. `skills/` directory exists with skill files (or `POIROT_SKILL_INCLUDE_BUILTIN=true`)
3. Launch from project root (`poirot`, not `cd poirot/backend && python ...`)

### MCP tools not showing

1. `POIROT_MCP_ENABLED=true`
2. Server `enabled: true` in `mcp_servers.yaml`
3. `command` is executable (e.g. `npx` requires Node.js)
4. `/mcp list` to check status, `/mcp reload` to retry

### Docker sandbox fails to start

1. Docker daemon running: `docker info`
2. Image pulled: `docker pull all-in-one-sandbox:latest`
3. Windows + WSL2: `POIROT_SANDBOX_EXECUTOR=wsl`
4. Port not occupied: adjust `POIROT_SANDBOX_PORT`

### Context overflow in long conversations

Poirot has context governance (DefaultStrategy) for auto-externalization and compaction. If issues persist:
1. `/clear` to start fresh
2. Check `current_tokens` in status bar
3. Expert mode has more aggressive governance

---

## FAQ

**Q: Do I have to use DeepSeek?**

A: No. DeepSeek is the default and serves as the fallback chain tail. You can use only OpenAI or Qwen. However, configuring DeepSeek as a fallback is recommended — it's affordable and stable.

**Q: What's the difference between Skills and MCP tools?**

A: Skills are "research process knowledge" (know how) — prompt-level injections, not executable. MCP tools are "external capabilities" (do something) — function calls, executable. "How to verify a source" is a skill. "Execute a web search" is a tool.

**Q: Will skill evolution modify my skill files?**

A: Yes. When Layer 2 is enabled, `LLMMutator` varies skill text and creates new versions (version DAG). `GitRatchet` ensures auto-rollback on degradation. All changes are recorded in SQLite — `/skill history <name>` to view.

**Q: How to disable all advanced features for simple chat?**

A:
```env
POIROT_SKILL_ENABLED=false
POIROT_MCP_ENABLED=false
POIROT_SANDBOX_USE=
```
Then `/default` for lightweight mode.

**Q: How to write my own skill?**

A: Create a subdirectory under `skills/` with a `SKILL.md` (frontmatter + body). Restart Poirot or run `/skill list`. See [Skill System](#skill-system).

**Q: How to run tests?**

A:
```bash
# All tests
python -m pytest poirot/backend/tests/ -q

# Skill module only
python -m pytest poirot/backend/tests/v1/unit/skill/ -q

# Eval layer only
python -m pytest poirot/backend/tests/v1/unit/skill/eval/ -q
```

---

<div align="center">

<sub>Questions? Open an issue.</sub>

</div>
