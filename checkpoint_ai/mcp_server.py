"""CHECKPOINT-AI MCP server — exposes scan as an MCP tool for Cognis.Studio."""
from cognis_core.mcp import build_mcp_server
from checkpoint_ai.core import scan, TOOL_NAME

run_mcp_server = build_mcp_server(
    tool_name=TOOL_NAME,
    description="NIST AI RMF / EU AI Act / ISO 42001 self-assessment & SSP generator",
    scan_fn=scan,
)

if __name__ == "__main__":
    run_mcp_server()
