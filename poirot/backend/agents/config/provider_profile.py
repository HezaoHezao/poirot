"""Provider profiles — declarative provider definitions.

每个 provider 声明一次：API 类型、env 变量名、默认端点/模型/窗口、优先级。
provider_config.py 在调用时读 env 解析为 ProviderConfig，不在模块加载时读 env
（利于测试 monkeypatch）。

设计借鉴 hermes-agent ProviderProfile，但遵循 Poirot 规范：
- frozen dataclass（声明层不可变）
- 接口小：只声明，不构造 client（构造在 build_chat_model）
- kind 枚举决定 LangChain class，避免 if-else 散落
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# provider → LangChain class 映射类型
ProviderKind = Literal["deepseek", "openai_compat", "anthropic", "gemini", "ollama", "fake"]


@dataclass(frozen=True)
class ProviderProfile:
    """声明式 provider 配置模板。env 变量名在此声明，值在 provider_config 解析时读。"""

    name: str                          # "deepseek", "openai", "anthropic"...
    kind: ProviderKind                 # 决定 build_chat_model 用哪个 LangChain class
    env_key: str                       # API key 的 env 变量名（如 "DEEPSEEK_API_KEY"）
    env_base_url: str                  # base_url 的 env 变量名
    env_model: str                     # model 的 env 变量名
    default_base_url: str | None       # env 未设时的默认端点
    default_model: str                 # env 未设时的默认模型
    default_window: int                # 默认上下文窗口（token 数）
    priority: int                      # 降级链优先级（小=优先）
    is_default: bool                   # 是否为默认 provider
    no_key_required: bool = False      # fake/ollama 等无需 API key


# ── 注册表：所有内置 provider ──────────────────────────────────────────────
# 新增 provider 只需在此列表追加一项 + .env.example 补对应 env 变量。
PROVIDER_PROFILES: list[ProviderProfile] = [
    # DeepSeek — 默认 provider，降级链尾兜底
    ProviderProfile(
        name="deepseek", kind="deepseek",
        env_key="DEEPSEEK_API_KEY", env_base_url="DEEPSEEK_BASE_URL", env_model="DEEPSEEK_MODEL",
        default_base_url="https://api.deepseek.com",
        default_model="deepseek-v4-flash", default_window=200_000,
        priority=10, is_default=True,
    ),
    # OpenAI — 官方 API
    ProviderProfile(
        name="openai", kind="openai_compat",
        env_key="OPENAI_API_KEY", env_base_url="OPENAI_BASE_URL", env_model="OPENAI_MODEL",
        default_base_url=None,
        default_model="gpt-4.1-mini", default_window=128_000,
        priority=20, is_default=False,
    ),
    # Qwen — 阿里通义，OpenAI 兼容
    ProviderProfile(
        name="qwen", kind="openai_compat",
        env_key="QWEN_API_KEY", env_base_url="QWEN_BASE_URL", env_model="QWEN_MODEL",
        default_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        default_model="qwen-plus", default_window=131_072,
        priority=30, is_default=False,
    ),
    # Anthropic Claude — 原生 API（x-api-key header）
    ProviderProfile(
        name="anthropic", kind="anthropic",
        env_key="ANTHROPIC_API_KEY", env_base_url="ANTHROPIC_BASE_URL", env_model="ANTHROPIC_MODEL",
        default_base_url="https://api.anthropic.com",
        default_model="claude-sonnet-4-20250514", default_window=200_000,
        priority=40, is_default=False,
    ),
    # Google Gemini — 原生 API
    ProviderProfile(
        name="gemini", kind="gemini",
        env_key="GEMINI_API_KEY", env_base_url="GEMINI_BASE_URL", env_model="GEMINI_MODEL",
        default_base_url="https://generativelanguage.googleapis.com/v1beta",
        default_model="gemini-2.0-flash", default_window=1_000_000,
        priority=50, is_default=False,
    ),
    # Moonshot / Kimi — OpenAI 兼容
    ProviderProfile(
        name="moonshot", kind="openai_compat",
        env_key="MOONSHOT_API_KEY", env_base_url="MOONSHOT_BASE_URL", env_model="MOONSHOT_MODEL",
        default_base_url="https://api.moonshot.cn/v1",
        default_model="moonshot-v1-128k", default_window=131_072,
        priority=60, is_default=False,
    ),
    # OpenRouter — 聚合平台，OpenAI 兼容
    ProviderProfile(
        name="openrouter", kind="openai_compat",
        env_key="OPENROUTER_API_KEY", env_base_url="OPENROUTER_BASE_URL", env_model="OPENROUTER_MODEL",
        default_base_url="https://openrouter.ai/api/v1",
        default_model="anthropic/claude-sonnet-4", default_window=200_000,
        priority=70, is_default=False,
    ),
    # xAI Grok — OpenAI 兼容
    ProviderProfile(
        name="xai", kind="openai_compat",
        env_key="XAI_API_KEY", env_base_url="XAI_BASE_URL", env_model="XAI_MODEL",
        default_base_url="https://api.x.ai/v1",
        default_model="grok-3", default_window=131_072,
        priority=80, is_default=False,
    ),
    # Zhipu GLM — OpenAI 兼容
    ProviderProfile(
        name="zhipu", kind="openai_compat",
        env_key="ZHIPU_API_KEY", env_base_url="ZHIPU_BASE_URL", env_model="ZHIPU_MODEL",
        default_base_url="https://open.bigmodel.cn/api/paas/v4",
        default_model="glm-4-plus", default_window=131_072,
        priority=90, is_default=False,
    ),
    # NVIDIA NIM — OpenAI 兼容
    ProviderProfile(
        name="nvidia", kind="openai_compat",
        env_key="NVIDIA_API_KEY", env_base_url="NVIDIA_BASE_URL", env_model="NVIDIA_MODEL",
        default_base_url="https://integrate.api.nvidia.com/v1",
        default_model="nvidia/llama-3.1-nemotron-70b-instruct", default_window=128_000,
        priority=100, is_default=False,
    ),
    # Novita — 聚合平台，OpenAI 兼容
    ProviderProfile(
        name="novita", kind="openai_compat",
        env_key="NOVITA_API_KEY", env_base_url="NOVITA_BASE_URL", env_model="NOVITA_MODEL",
        default_base_url="https://api.novita.ai/openai/v1",
        default_model="deepseek/deepseek-v3.2", default_window=163_840,
        priority=105, is_default=False,
    ),
    # Ollama — 本地，无需 API key
    ProviderProfile(
        name="ollama", kind="ollama",
        env_key="OLLAMA_API_KEY", env_base_url="OLLAMA_BASE_URL", env_model="OLLAMA_MODEL",
        default_base_url="http://localhost:11434",
        default_model="llama3.1", default_window=32_768,
        priority=110, is_default=False, no_key_required=True,
    ),
    # Fake — 测试用
    ProviderProfile(
        name="fake", kind="fake",
        env_key="FAKE_API_KEY", env_base_url="FAKE_BASE_URL", env_model="FAKE_MODEL",
        default_base_url=None,
        default_model="fake-chat", default_window=4_096,
        priority=999, is_default=False, no_key_required=True,
    ),
]

_PROFILE_MAP: dict[str, ProviderProfile] = {p.name: p for p in PROVIDER_PROFILES}


def get_provider_profile(name: str) -> ProviderProfile | None:
    """按 name 查 provider profile，不存在返 None。"""
    return _PROFILE_MAP.get(name)


def list_provider_profiles() -> list[ProviderProfile]:
    """返回全部 provider profiles。"""
    return list(PROVIDER_PROFILES)
