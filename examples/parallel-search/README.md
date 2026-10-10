# Parallel Search MCP

Use [Parallel Search MCP](https://docs.parallel.ai/integrations/mcp/search-mcp)
for free web search and page fetching through Poirot's existing HTTP MCP loader.
No Parallel account or API key is needed. Anonymous search uses Fast mode and is
rate limited, so this example is suited to exploration and light use.

## Try search and fetch without an LLM

From the repository root, with Python 3.12 or later:

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -e .
```

Enable MCP in your shell (the example does not load `.env`):

```bash
export POIROT_MCP_ENABLED=true
# PowerShell: $env:POIROT_MCP_ENABLED = "true"
python examples/parallel-search/search.py "Find the Python asyncio documentation" \
  --query "Python asyncio official documentation" \
  --url https://docs.python.org/3/library/asyncio.html
```

The command loads the adjacent YAML file with `build_mcp_manager`, discovers the
tools at startup, selects them from the core registry, and prints search excerpts
and fetched page content as JSON. Omit `--url` for search only. Repeat `--query`
for related search queries or `--url` for multiple specific pages. It invokes tools
directly and does not require an LLM key.

## Enable in Poirot

After the normal [application setup](../../USAGE.md#installation), add these
settings to `.env` and launch Poirot from the repository root:

```env
POIROT_MCP_ENABLED=true
POIROT_MCP_CONFIG_PATH=examples/parallel-search/mcp_servers.yaml
```

Poirot still requires an LLM provider key for research. Its current application
bootstrap also checks for Node.js before loading any MCP servers, including HTTP
servers, so install Node.js for the application path. The direct command above
does not need Node.js.

This file selects only Parallel. To keep other MCP servers, merge the `parallel`
server into your existing YAML and add `web_search` and `web_fetch` to its
`core_tools`; avoid duplicate tool names across enabled servers. You can use
`/mcp reload` after changing configuration. The example leaves existing saved
configuration in place.
