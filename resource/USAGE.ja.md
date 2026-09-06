# Poirot 使用ガイド

> Poirotのインストール、設定、操作の完全ガイド。
>
> **言語：** [English](../USAGE.md) · [简体中文](USAGE.zh-CN.md) · [日本語](USAGE.ja.md)

---

## 目次

- [要件](#要件)
- [インストール](#インストール)
- [設定](#設定)
- [起動モード](#起動モード)
- [コマンド](#コマンド)
- [Skillシステム](#skillシステム)
- [長期記憶](#長期記憶)
- [マルチエージェント](#マルチエージェント)
- [Sandbox](#sandbox)
- [MCPツール](#mcpツール)
- [モデル・プロバイダー切替](#モデルプロバイダー切替)
- [Docker デプロイ](#docker-デプロイ)
- [設定シナリオ](#設定シナリオ)
- [使用ヒント](#使用ヒント)
- [TUIガイド](#tuiガイド)
- [トラブルシューティング](#トラブルシューティング)
- [FAQ](#faq)

---

## 要件

| 項目 | 要件 |
|------|------|
| Python | 3.12+ |
| OS | Windows / Linux / macOS |
| LLM API Key | DeepSeek（デフォルト）/ OpenAI / Qwen のいずれか一つ |
| Docker | Docker Sandboxモードのみ |
| Node.js | MCP stdioサーバー（freeweb-mcp等）のみ |

---

## インストール

### 1. クローン

```bash
git clone <repo-url>
cd Poirot
```

### 2. 仮想環境

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

> condaも可：`conda create -n poirot python=3.12 && conda activate poirot`

### 3. インストール

```bash
# 基本 + 開発ツール（pytest）
pip install -e ".[dev]"

# Docker Sandbox対応
pip install -e ".[docker]"
```

### 4. 設定

```bash
cp .env.example .env
```

`.env`を編集 — 少なくとも一つのAPI Keyを入力：

```env
DEEPSEEK_API_KEY=sk-your-key-here
```

### 5. 確認

```bash
poirot
```

PoirotのASCIIロゴとウェルカム画面が表示されれば成功。

---

## 設定

プロジェクトルートの`.env`ファイルで設定します。`.env.example`が完全なテンプレートです。

### LLMプロバイダー

| 変数 | 説明 | デフォルト |
|------|------|-----------|
| `DEEPSEEK_API_KEY` | DeepSeek APIキー（デフォルト、フォールバック尾部） | — |
| `DEEPSEEK_BASE_URL` | DeepSeekエンドポイント | `https://api.deepseek.com` |
| `OPENAI_API_KEY` | OpenAI APIキー | — |
| `OPENAI_BASE_URL` | OpenAIエンドポイント（プロキシ用） | 公式デフォルト |
| `QWEN_API_KEY` | Qwen APIキー | — |
| `QWEN_BASE_URL` | Qwenエンドポイント | `https://dashscope.aliyuncs.com/compatible-mode/v1` |

> 少なくとも一つのプロバイダーを設定してください。DeepSeekをフォールバックとして設定を推奨します。

### Sandbox

| 変数 | 説明 | デフォルト |
|------|------|-----------|
| `POIROT_SANDBOX_USE` | Sandboxプロバイダーパス（空=無効） | 空 |
| `POIROT_SANDBOX_IMAGE` | Dockerイメージ名 | `all-in-one-sandbox:latest` |
| `POIROT_SANDBOX_PORT` | コンテナ開始ポート | `18000` |
| `POIROT_SANDBOX_EXECUTOR` | Docker実行環境（`local` / `wsl`） | `local` |
| `POIROT_SANDBOX_WSL_DISTRO` | WSLディストロ名 | `Ubuntu` |
| `POIROT_SANDBOX_WSL_USER` | WSLユーザー | デフォルトユーザー |
| `POIROT_SANDBOX_CONTAINER_PREFIX` | コンテナ名プレフィックス | `poirot-sandbox` |
| `POIROT_SANDBOX_IDLE_TIMEOUT` | アイドル破棄タイムアウト秒（0=破棄しない） | `600` |
| `POIROT_SANDBOX_REPLICAS` | ウォームプールサイズ（0=事前作成しない） | `3` |

**Local Sandbox（ホストプロセス）:**
```env
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.local.local_sandbox_provider:LocalSandboxProvider
```

**Docker Sandbox（コンテナ分離）:**
```env
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.docker.docker_sandbox_provider:DockerSandboxProvider
```

> Dockerモード：最初にイメージをプル — `docker pull all-in-one-sandbox:latest`
>
> Windows + WSL2：`POIROT_SANDBOX_EXECUTOR=wsl`を設定

### MCP

| 変数 | 説明 | デフォルト |
|------|------|-----------|
| `POIROT_MCP_ENABLED` | MCPマスタースイッチ | `false` |
| `POIROT_MCP_CONFIG_PATH` | MCP設定ファイルパス | `.poirot/mcp_servers.yaml` |
| `POIROT_MCP_CORE_TOOLS` | コアツール（カンマ区切り、起動時にロード） | `web_search,browse_page` |

### Skill

| 変数 | 説明 | デフォルト |
|------|------|-----------|
| `POIROT_SKILL_ENABLED` | Skillモジュールマスタースイッチ | `false` |
| `POIROT_SKILL_DB_PATH` | Skill SQLiteパス | `.poirot/skills.db` |
| `POIROT_SKILL_DIRS` | Skillスキャンディレクトリ | `skills/` |
| `POIROT_SKILL_INCLUDE_BUILTIN` | builtinコアSkillをロード | `true` |
| `POIROT_SKILL_MAX_INJECT` | 1ターンの最大注入Skill数 | `3` |
| `POIROT_SKILL_QUALITY_THRESHOLD` | 品質フィルター閾値 | `0.3` |
| `POIROT_SKILL_MIN_SELECTIONS` | 品質フィルター適用最小選択回数 | `5` |

**Skill進化（Layer 2）:**

| 変数 | 説明 | デフォルト |
|------|------|-----------|
| `POIROT_SKILL_EVOLVE_ENABLED` | 進化スイッチ | `false` |
| `POIROT_SKILL_EVOLVE_THRESHOLD` | 進化トリガー閾値 | `0.3` |
| `POIROT_SKILL_EVOLVE_MIN_SELECTIONS` | 進化最小選択回数 | `5` |
| `POIROT_SKILL_EVOLVE_COOLDOWN_TURNS` | 進化クールダウンターン数 | `10` |
| `POIROT_SKILL_EVOLVE_MUTATE_BUDGET` | 変異トークン予算 | `20` |
| `POIROT_SKILL_EVOLVE_MAX_STEPS` | 最大進化ステップ数 | `5` |

**Skill評価（Layer 3）:**

| 変数 | 説明 | デフォルト |
|------|------|-----------|
| `POIROT_SKILL_EVAL_ENABLED` | 評価スイッチ | `false` |
| `POIROT_SKILL_EVAL_JUDGMENT_ENABLED` | 実行判定 | `true` |
| `POIROT_SKILL_EVAL_TASK_JUDGE_ENABLED` | タスク品質スコアリング | `true` |
| `POIROT_SKILL_EVAL_CONTRACT_CHECK` | レスポンス契約チェック | `true` |
| `POIROT_SKILL_EVAL_ASYNC` | 非同期eval | `true` |
| `POIROT_SKILL_EVAL_SKIP_NO_SKILL` | Skill未注入時にevalスキップ | `true` |
| `POIROT_SKILL_EVAL_RUNTIME_WINDOW` | RuntimeTrackerウィンドウ | `20` |
| `POIROT_SKILL_EVAL_DEGRADATION_DELTA` | 劣化判定delta | `0.15` |

---

## 起動モード

### 1. TUIフルスクリーン（デフォルト）

```bash
poirot
```

| キー | アクション |
|------|-----------|
| `Ctrl+P` | コマンドパレット |
| `Ctrl+N` | MCPパネル |
| `Ctrl+L` | 画面クリア |
| `Ctrl+C` | 終了 |
| `Enter` | 送信 |
| `Shift+ドラッグ` | コピー選択 |

### 2. CLIスクロール

```bash
poirot cli
```

### 3. 単発リサーチ（非対話）

```bash
poirot run "2026年のAIエージェントフレームワーク動向を分析"
poirot run "質問" --thread-id my-thread --run-id my-run
poirot run "簡単な質問" --no-expert
poirot run "質問" --no-artifact
```

---

## コマンド

### 基本

| コマンド | 説明 |
|---------|------|
| `/help` | 全コマンド表示 |
| `/clear` | 画面クリア |
| `/exit` `/quit` | 終了 |
| `/expand` | 前ラウンドのThought + ツール結果を展開 |
| `/thinking on\|off` | Thought折りたたみ表示切替 |

### モード

| コマンド | 説明 |
|---------|------|
| `/expert` | expertモード（ディープリサーチ）に切替 |
| `/default` | defaultモード（ライト会話）に切替 |
| `/report [topic]` | 現在のスレッドからレポート生成 |

### モデル・ツール

| コマンド | 説明 |
|---------|------|
| `/model` | 現在のモデル表示 |
| `/model <provider>` | プロバイダー切替 |
| `/model <provider> <model>` | プロバイダー + モデル指定切替 |
| `/tools` | 利用可能ツール一覧 |
| `/thread` | スレッド情報表示 |

### Skill

| コマンド | 説明 |
|---------|------|
| `/skill` `/skill list` | アクティブSkill一覧 |
| `/skill search <query>` | builtin Skill検索 |
| `/skill <name>` | Skill強制使用（override） |
| `/skill off` | overrideクリア |
| `/skill enable/disable <name>` | Skill有効化/無効化 |
| `/skill install <path> [name]` | 外部Skillインストール |
| `/skill evolve <name>` | 手動進化トリガー |
| `/skill capture <pattern> <name>` | 新規Skillキャプチャ |
| `/skill history <name>` | Skillバージョン履歴 |
| `/skill health [name]` | Skillヘルスレポート（Layer 3） |
| `/skill eval-history <name>` | SkillJudgment履歴（Layer 3） |

### MCP

| コマンド | 説明 |
|---------|------|
| `/mcp` `/mcp list` | MCPサーバー・ツール一覧 |
| `/mcp reload` | MCP設定リロード |

---

## Skillシステム

Skillは**リサーチプロセス知識バンドル**です — promptレベル注入であり、実行可能な関数ではありません。「情報源の検証方法」はSkill、「Web検索の実行」はツールです。

### 三層アーキテクチャ

**Layer 1（ベース）:**
- `SQLiteSkillStore` — ストレージ + バージョンDAG + 4カウンター
- `SkillSelector` — 品質フィルター + LLMハイブリッド選択
- `SkillInjectionMiddleware` — `before_model`注入
- `SkillMetricsMiddleware` — `wrap_tool_call`適用マーキング + `after_agent`アトリビューション

**Layer 2（進化）:**
- `MetricMonitor` — effective_rateが閾値未満でトリガー
- `IVEFocuser` — 5問診断 + 偏差エビデンス
- `LLMMutator` — LLMによるSkillテキスト変異
- `ScoreDeltaGate` — 変異前後スコアゲート
- `GitRatchet` — ラチェット：劣化時にロールバック

**Layer 3（評価）:**
- `SkillJudgmentAnalyzer` — per-skill per-task LLM判定
- `TaskQualityJudge` — 4次元スコアリング（accuracy 0.50 / completeness 0.35 / efficiency 0.05 / depth 0.10）
- `ResponseContractChecker` — 契約対応ルールチェック
- `RuntimeTracker` — applied_rateトレンド + `degraded_skills()`ロールバックシグナル

### Skill有効化

```env
POIROT_SKILL_ENABLED=true
```

BuiltinコアSkillは起動時に自動ロード。ユーザーSkillは`skills/`ディレクトリに配置。

### Skillファイル形式

```markdown
---
name: source-verification
description: 情報源の信頼性を検証
allowed_tools:
  - web_search
  - browse_page
---

# Source Verification Skill

## 使用タイミング
情報源の信頼性を検証する必要がある時...

## 方法
1. ソースの権威性を確認
2. 複数ソースで交差検証
3. ...
```

### Builtin Skills

Poirotは5カテゴリ36個のbuiltin Skillを同梱：

| カテゴリ | 数 | 例 |
|---------|-----|-----|
| core | 12 | deep-research, source-verification, plan, spike, skill-creator, test-driven-development |
| research | 11 | arxiv, osint-investigation, systematic-literature-review, research-paper-writing |
| software-development | 7 | github-code-review, github-pr-workflow, node-inspect-debugger, python-debugpy |
| creative | 3 | architecture-diagram, chart-visualization, frontend-design |
| productivity | 2 | code-documentation, ppt-generation |

> Coreカテゴリは自動ロード。その他は`/skill search <query>`で発見。

---

## 長期記憶

Poirotは5層の長期記憶システムを実装しています。記憶トレースはMarkdown（`traces.md`）に保存 — truth source — BM25検索とエビングハウス忘却曲線を組み合わせています。

### 有効化

```env
POIROT_MEMORY_USE=default
```

### 設定

| 変数 | 説明 | デフォルト |
|------|------|-----------|
| `POIROT_MEMORY_USE` | 記憶プロバイダー（空=無効、`default`=有効） | 空 |
| `POIROT_MEMORY_STORAGE_PATH` | Markdown truth source ディレクトリ | `.poirot/memory` |
| `POIROT_MEMORY_ENABLE_RECALL` | before_model リコール注入 | `true` |
| `POIROT_MEMORY_TOKEN_BUDGET` | リコール注入トークン予算 | `2000` |
| `POIROT_MEMORY_PHASE2_ENABLED` | L5 自動統合ワーカー | `false` |
| `POIROT_MEMORY_PHASE2_TURNS` | Nターンごとに統合トリガー | `10` |

### 仕組み

1. **リコール（L4）** — 各 `before_model` で、MemoryMiddleware が BM25 で関連記憶を検索し、per-call HumanMessage として注入（プロンプトキャッシュを保護）。
2. **統合（L5）** — Nターンごとに、MemoryConsolidationMiddleware が非ブロッキングでタスクを MemoryWorker（デーモンスレッド）に送信。ワーカーが LLM でエピソード記憶を抽出 → encode → 候補 ≥ N → LLM で統合 → consolidate。
3. **永続化** — 全トレースは `.poirot/memory/traces.md` に保存。
4. **忘却** — エビングハウス式を取得時に遅延計算（バックグラウンドタスクなし）。忘却トレースは `metadata.forgotten=True` でマーク、retriever がフィルタ（削除なし）。

---

## マルチエージェント

Poirotはサブタスクを外部コーディングエージェント（specialist）と内部自己コピー（subagent）に委譲できます。

### 有効化

```env
POIROT_MULTIAGENT_ENABLED=true
POIROT_MULTIAGENT_SPECIALISTS=pi,codex,claude,subagent
```

### 設定

| 変数 | 説明 | デフォルト |
|------|------|-----------|
| `POIROT_MULTIAGENT_ENABLED` | マルチエージェントマスタースイッチ | `true` |
| `POIROT_MULTIAGENT_SPECIALISTS` | specialistリスト（カンマ区切り） | `pi,codex,claude,subagent` |
| `POIROT_MULTIAGENT_AUTO_APPROVE` | specialist呼び出し自動承認 | `true` |
| `POIROT_MULTIAGENT_L2_ENABLED` | L2 進化レイヤー | `false` |
| `POIROT_MULTIAGENT_L3_ENABLED` | L3 評価レイヤー | `false` |

### Pi Specialist（独自APIキー、ログイン不要）

Pi は複数プロバイダーをサポート — 既存の DeepSeek キーがそのまま使えます：

```env
POIROT_MULTIAGENT_PI_PROVIDER=deepseek
POIROT_MULTIAGENT_PI_API_KEY=sk-your-deepseek-key
```

Pi CLI インストール: `npm install -g @earendil-works/pi-coding-agent --ignore-scripts`

### 共有サンドボックス

- **Subagent**: SandboxMiddleware.abefore_model が state["sandbox"] から ContextVar を復元 — 親の sandbox_id を再利用
- **Specialist**: MCP コマンドに `--sandbox-url` を含む — specialist が HTTP でリードの Docker コンテナに接続

---

## Sandbox

### Local Sandbox

```env
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.local.local_sandbox_provider:LocalSandboxProvider
```

### Docker Sandbox

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

## MCPツール

```env
POIROT_MCP_ENABLED=true
```

設定ファイル`.poirot/mcp_servers.yaml`：

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

変更後`/mcp reload`でリロード。

### リモートMCPサーバー（http）

`transport: http` はローカルプロセス不要でリモートMCPサーバーに直接接続します。
`headers` は `${VAR}` のホスト環境からの補間に対応しており、API key を
設定ファイルに書く必要はありません。

例：[You.com](https://you.com/docs) のリモートMCPサーバー（web search。
key は [you.com/platform/api-keys](https://you.com/platform/api-keys) で取得）：

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

キーレス設定（基本の `you-search` のみ）：
`url: https://api.you.com/mcp?profile=free` を使い、`headers` を外します。

---

## モデル・プロバイダー切替

### ルーティングチェーン

```
researcher: [openai, qwen] → deepseek（フォールバック尾部）
reporter:   [openai, qwen] → deepseek（フォールバック尾部）
```

### 起動時指定

```bash
poirot --provider openai
poirot --provider qwen --model qwen-max
```

### 実行時切替

```
/model                    # 現在のモデル表示
/model openai             # 切替
/model openai gpt-4.1     # 切替 + モデル指定
```

### 対応プロバイダー

| プロバイダー | デフォルトモデル | ウィンドウ |
|------------|----------------|-----------|
| deepseek | deepseek-v4-flash | 200K |
| openai | gpt-4.1-mini | — |
| qwen | qwen-plus | — |

---

## Docker デプロイ

Poirot は Dockerfile + docker-compose でワンコマンドデプロイに対応しています。

### クイックスタート

```bash
# 1. 設定コピー
cp .env.example .env
# .env 編集 — DEEPSEEK_API_KEY=sk-xxx を入力

# 2. ビルド + 実行（TUI 対話）
docker compose run --rm poirot

# 3. または単発リサーチ
docker compose run --rm poirot run "AIエージェントトレンド 2026"
```

### イメージ内容

- Python 3.12 + 全依存関係（pyyaml、langchain 等）
- Node.js 20（MCP stdio server + pi coding agent）
- デフォルト有効：`POIROT_MEMORY_USE=default`、`POIROT_MULTIAGENT_ENABLED=true`
- デフォルト Local sandbox（DinD 不要）

### コンテナ内 Sandbox

**デフォルト（Local sandbox）** — agent は Poirot コンテナ内でコマンド実行。DinD 不要。

**Docker 隔離 sandbox** — agent は独立 sandbox コンテナで実行。docker.sock マウントが必要：

```yaml
# docker-compose.yml — コメント解除：
volumes:
  - /var/run/docker.sock:/var/run/docker.sock
```

```env
# .env：
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.docker.docker_sandbox_provider:DockerSandboxProvider
POIROT_SANDBOX_EXECUTOR=local
```

### データ永続化

| ホストパス | コンテナパス | 内容 |
|-----------|-------------|------|
| `./.poirot/` | `/app/.poirot/` | DB、ログ、artifact、memory、MCP 設定 |
| `./skills/` | `/app/skills/` | ユーザー skill |
| `./.env` | `/app/.env` | 環境設定（Ctrl+B パネルで書き戻し可能） |

---

## 設定シナリオ

### シナリオ 1：ライトweight チャット（最小構成）

```env
DEEPSEEK_API_KEY=sk-xxx
POIROT_SKILL_ENABLED=false
POIROT_MCP_ENABLED=false
POIROT_SANDBOX_USE=
POIROT_MEMORY_USE=
POIROT_MULTIAGENT_ENABLED=false
```

`/default` でライトモードへ。sandbox / skill / memory なし — 純粋な LLM チャット。

### シナリオ 2：フル機能（全フィーチャー有効）

```env
DEEPSEEK_API_KEY=sk-xxx

# 記憶（L4 リコール + L5 自動統合）
POIROT_MEMORY_USE=default
POIROT_MEMORY_PHASE2_ENABLED=true
POIROT_MEMORY_PHASE2_TURNS=10

# Skill（L1 + L2 進化 + L3 評価）
POIROT_SKILL_ENABLED=true
POIROT_SKILL_EVOLVE_ENABLED=true
POIROT_SKILL_EVAL_ENABLED=true
POIROT_SKILL_MAX_INJECT=15

# マルチエージェント（specialist + L2/L3）
POIROT_MULTIAGENT_ENABLED=true
POIROT_MULTIAGENT_L2_ENABLED=true
POIROT_MULTIAGENT_L3_ENABLED=true

# Pi specialist（DeepSeek キー使用、ログイン不要）
POIROT_MULTIAGENT_PI_PROVIDER=deepseek
POIROT_MULTIAGENT_PI_API_KEY=sk-xxx

# Docker sandbox
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.docker.docker_sandbox_provider:DockerSandboxProvider
POIROT_SANDBOX_EXECUTOR=wsl

# MCP ツール
POIROT_MCP_ENABLED=true
```

### シナリオ 3：開発モード（Local sandbox、Docker なし）

```env
DEEPSEEK_API_KEY=sk-xxx
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.local.local_sandbox_provider:LocalSandboxProvider
POIROT_SKILL_ENABLED=true
POIROT_MEMORY_USE=default
POIROT_MULTIAGENT_ENABLED=true
```

### シナリオ 4：コーディング Agent（pi specialist 重視）

```env
DEEPSEEK_API_KEY=sk-xxx

# Pi specialist + DeepSeek
POIROT_MULTIAGENT_ENABLED=true
POIROT_MULTIAGENT_SPECIALISTS=pi,subagent
POIROT_MULTIAGENT_PI_PROVIDER=deepseek
POIROT_MULTIAGENT_PI_API_KEY=sk-xxx

# コード実行 sandbox
POIROT_SANDBOX_USE=poirot.backend.agents.sandbox.docker.docker_sandbox_provider:DockerSandboxProvider

# コーディング skill
POIROT_SKILL_ENABLED=true
POIROT_SKILL_MAX_INJECT=15
```

---

## 使用ヒント

### 記憶システム

**記憶の動作確認：**
- `.poirot/memory/traces.md` — 全記憶トレース（truth source、人間可読 Markdown）
- Journal イベント：`.poirot/logs/threads/<thread_id>/runs/<run_id>/events.jsonl` — `memory.encode`、`memory.consolidate`
- Worker actor：`worker:{thread_id}:{turn_count}`

**統合頻度の調整：**
```env
POIROT_MEMORY_PHASE2_TURNS=5   # より頻繁（LLM コスト増）
POIROT_MEMORY_PHASE2_TURNS=20  # より省コスト
```

### マルチエージェント

**Pi specialist が表示されない？**
1. `pi` CLI インストール確認：`pi --version`
2. API key 確認：`.env` に `DEEPSEEK_API_KEY`
3. 起動ログの `[PiSpecialist]` メッセージを確認

### Skill システム

**core skill しかロードされない？**
- 設計通り：起動時に `builtin_skills/core/` のみロード（12 個）
- その他は `/skill search <query>` で検索
- `skill_search` は英語キーワードで検索してください

### Sandbox

**Windows + WSL2 Docker：**
```env
POIROT_SANDBOX_EXECUTOR=wsl
POIROT_SANDBOX_WSL_DISTRO=Ubuntu
```

**Sandbox ディレクトリが空？**
- Agent は `/mnt/poirot/user-data/` に書き込む必要あり（DockerPathGuard が強制）
- マウントエリア外のファイルは `--rm` で消失

---

## TUIガイド

- **ウェルカム画面**：中央ロゴ + 入力ボックス、最初の入力で会話画面に切替
- **会話画面**：左側会話エリア + 下部入力ボックス + ステータスバー、ワイド画面では右側情報パネル
- **Thought折りたたみ**：`+ Thought: 120ms`、`/expand`で全文展開、`/thinking off`で非表示
- **コピー**：`Shift`を押しながらドラッグで選択

---

## トラブルシューティング

### `api_key is empty for provider: deepseek`

`.env`のAPI Keyが空です。少なくとも一つのプロバイダーを設定してください。

### Skillモジュールがロードされない

1. `POIROT_SKILL_ENABLED=true`
2. `skills/`ディレクトリが存在
3. プロジェクトルートから起動

### MCPツールが表示されない

1. `POIROT_MCP_ENABLED=true`
2. server `enabled: true`
3. `command`が実行可能
4. `/mcp list`で状態確認、`/mcp reload`で再試行

### Docker Sandbox起動失敗

1. Dockerデーモンが実行中
2. イメージがプル済み
3. Windows + WSL2：`POIROT_SANDBOX_EXECUTOR=wsl`

---

## FAQ

**Q: DeepSeekを使わなければなりませんか？**

A: いいえ。DeepSeekはデフォルトかつフォールバック尾部です。OpenAIやQwenのみでも使用可能ですが、DeepSeekをフォールバックとして設定を推奨します。

**Q: SkillとMCPツールの違いは？**

A: Skillは「リサーチプロセス知識」（know how）— prompt注入、実行不可。MCPツールは「外部能力」（do something）— function call、実行可能。

**Q: Skill進化はSkillファイルを変更しますか？**

A: はい。Layer 2有効時、`LLMMutator`がSkillテキストを変異し新バージョンを作成します。`GitRatchet`が劣化時にロールバックします。`/skill history <name>`で履歴確認。

**Q: 高度な機能を全て無効にしてシンプルな会話をするには？**

A:
```env
POIROT_SKILL_ENABLED=false
POIROT_MCP_ENABLED=false
POIROT_SANDBOX_USE=
```
その後`/default`でライトモードに。

**Q: 独自Skillの書き方は？**

A: `skills/`下にサブディレクトリを作成し、`SKILL.md`（frontmatter + 本文）を配置。再起動または`/skill list`で確認。

**Q: テストの実行方法は？**

A:
```bash
python -m pytest poirot/backend/tests/ -q
python -m pytest poirot/backend/tests/v1/unit/skill/ -q
```

---

<div align="center">

<sub>質問はIssueへ。</sub>

</div>
