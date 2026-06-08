"""CHECKPOINT-AI command-line interface."""
from cognis_core import build_cli
from checkpoint_ai.core import scan, TOOL_NAME, TOOL_VERSION

main = build_cli(
    tool_name=TOOL_NAME,
    tool_version=TOOL_VERSION,
    description="NIST AI RMF / EU AI Act / ISO 42001 self-assessment & SSP generator",
    scan_fn=scan,
)

if __name__ == "__main__":
    import sys
    sys.exit(main())
