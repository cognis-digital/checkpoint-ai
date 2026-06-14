"""CHECKPOINT-AI MCP server — exposes assess as an MCP tool for Cognis.Studio.

Requires the optional 'mcp' extra: pip install cognis-checkpoint-ai[mcp]
"""
from __future__ import annotations

import sys


def _require_mcp():
    """Import and return (build_mcp_server, TOOL_NAME, assess), raising ImportError with a
    clear message when the optional 'cognis_core' dependency is not installed."""
    try:
        from cognis_core.mcp import build_mcp_server  # type: ignore[import]
    except ImportError as exc:
        raise ImportError(
            "The MCP server requires the 'cognis_core' package. "
            "Install it with: pip install cognis-checkpoint-ai[mcp]"
        ) from exc
    from checkpoint_ai.core import assess, TOOL_NAME  # noqa: PLC0415

    return build_mcp_server, TOOL_NAME, assess


def run_mcp_server() -> None:
    """Entry point: build and start the MCP server."""
    build_mcp_server, TOOL_NAME, assess_fn = _require_mcp()
    server = build_mcp_server(
        tool_name=TOOL_NAME,
        description="NIST AI RMF / EU AI Act / ISO 42001 self-assessment & SSP generator",
        scan_fn=assess_fn,
    )
    server()


if __name__ == "__main__":
    try:
        run_mcp_server()
    except ImportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
