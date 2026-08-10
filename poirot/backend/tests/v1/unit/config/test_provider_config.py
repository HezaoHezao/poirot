import pytest

from poirot.backend.agents.config.provider_config import (
    ProviderConfig,
    ProviderConfigError,
    get_provider_config,
    select_provider_config,
)


def test_selects_explicit_provider_before_default() -> None:
    config = select_provider_config(provider="openai")

    assert config.provider == "openai"
    assert config.model == "gpt-4.1-mini"


def test_selects_default_provider_when_not_explicit() -> None:
    config = select_provider_config(provider=None)

    assert config.provider == "deepseek"
    assert config.default is True


def test_selects_novita_provider() -> None:
    config = select_provider_config(provider="novita")

    assert config.provider == "novita"
    assert config.model == "moonshotai/kimi-k3"
    assert config.base_url == "https://api.novita.ai/openai/v1"


def test_model_override_keeps_provider_settings() -> None:
    config = select_provider_config(provider="qwen", model="qwen-max")

    assert config.provider == "qwen"
    assert config.model == "qwen-max"
    assert config.base_url == "https://dashscope.aliyuncs.com/compatible-mode/v1"


def test_missing_api_key_is_clear() -> None:
    config = ProviderConfig(
        provider="deepseek",
        model="deepseek-chat",
        api_key="",
        base_url=None,
        priority=10,
        default=True,
        enabled=True,
    )

    with pytest.raises(ProviderConfigError, match="api_key is empty for provider: deepseek"):
        config.require_api_key()
