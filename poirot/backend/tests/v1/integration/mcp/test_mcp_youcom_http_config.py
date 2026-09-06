"""远程 MCP server（http transport）配置加载单测 — USAGE.md「Remote MCP Server (http)」示例。

以 You.com 远程 MCP server 为例，验证 http transport + headers ${VAR} 插值 +
fallback_chains / core_tools / tool_metadata 解析链路（不发起真实网络连接）。
"""
import os
import tempfile
from pathlib import Path

from poirot.backend.agents.mcp import build_mcp_manager, McpManager


_YOUCOM_YAML = """
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

core_tools:
  - web_search

tool_metadata:
  web_search:
    typical_output_tokens: 800
    source: mcp
"""


def test_http_server_config_loads():
    """http transport server → McpServerConfig 字段正确（url/headers/超时）。"""
    from poirot.backend.agents.mcp.config import load_mcp_config

    with tempfile.TemporaryDirectory() as tmp:
        yaml_path = Path(tmp) / "mcp_servers.yaml"
        yaml_path.write_text(_YOUCOM_YAML, encoding="utf-8")
        config = load_mcp_config(str(yaml_path))

    assert "youcom" in config.servers, "youcom server should load"
    server = config.servers["youcom"]
    assert server.transport == "http"
    assert server.url == "https://api.you.com/mcp"
    assert server.enabled is True
    assert server.timeout == 300
    assert server.connect_timeout == 60
    print("PASS: http server config fields")


def test_http_server_header_env_interpolation():
    """headers 内 ${YDC_API_KEY} → 从宿主 env 插值；未设置时原样保留。"""
    from poirot.backend.agents.mcp.config import load_mcp_config

    with tempfile.TemporaryDirectory() as tmp:
        yaml_path = Path(tmp) / "mcp_servers.yaml"
        yaml_path.write_text(_YOUCOM_YAML, encoding="utf-8")

        os.environ["YDC_API_KEY"] = "test-key-123"
        try:
            config = load_mcp_config(str(yaml_path))
            server = config.servers["youcom"]
            assert server.headers["Authorization"] == "Bearer test-key-123"
            print("PASS: ${YDC_API_KEY} interpolated from host env")
        finally:
            del os.environ["YDC_API_KEY"]

        # 未设置 → 占位符原样保留（load_mcp_config 不抛）
        config = load_mcp_config(str(yaml_path))
        server = config.servers["youcom"]
        assert server.headers["Authorization"] == "Bearer ${YDC_API_KEY}"
        print("PASS: unset env keeps ${VAR} placeholder, no raise")


def test_build_mcp_manager_with_http_server():
    """enabled=true + http server 配置 → 构造 McpManager，registry 含 fallback chain。"""
    with tempfile.TemporaryDirectory() as tmp:
        yaml_path = Path(tmp) / "mcp_servers.yaml"
        yaml_path.write_text(_YOUCOM_YAML, encoding="utf-8")
        os.environ["POIROT_MCP_ENABLED"] = "true"
        manager = build_mcp_manager(str(yaml_path))
    try:
        assert manager is not None, "enabled + http config → should construct manager"
        assert isinstance(manager, McpManager)
        assert manager.registry._fallback_chains.get("web_search") == [
            "youcom:you-search",
            "builtin:ddg_search",
        ]
        assert "web_search" in manager.registry._core_tools
        print("PASS: http server → McpManager with fallback chain registered")
    finally:
        os.environ["POIROT_MCP_ENABLED"] = "false"
