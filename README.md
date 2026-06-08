# CHECKPOINT-AI — NIST AI RMF / EU AI Act / ISO 42001 self-assessment & SSP generator

> Part of the **[Cognis Neural Suite](https://github.com/cognis-digital)** by [Cognis Digital](https://cognis.digital)
> MIT License · domain: `federal`

[![PyPI](https://img.shields.io/pypi/v/cognis-checkpoint-ai.svg)](https://pypi.org/project/cognis-checkpoint-ai/)
[![CI](https://github.com/cognis-digital/checkpoint-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/cognis-digital/checkpoint-ai/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

NIST AI RMF / EU AI Act / ISO 42001 self-assessment & SSP generator.

## Install

```bash
pip install cognis-checkpoint-ai
```

For local development from this repo:

```bash
pip install -e .
```

## Quick start

```bash
checkpoint-ai --version
checkpoint-ai scan demos/                          # run against bundled demo
checkpoint-ai scan demos/ --format sarif --out r.sarif --fail-on high
checkpoint-ai mcp                                   # start as MCP server (Cognis.Studio / Claude Desktop / Cursor)
```

## Built-in demo scenarios

Every scenario folder includes a `SCENARIO.md` describing what it represents and what findings to expect.

- `demos/01-pre-launch-gap-analysis/` — see [`SCENARIO.md`](demos/01-pre-launch-gap-analysis/SCENARIO.md)
- `demos/02-iso-42001-readiness/` — see [`SCENARIO.md`](demos/02-iso-42001-readiness/SCENARIO.md)
- `demos/03-eu-ai-act-high-risk/` — see [`SCENARIO.md`](demos/03-eu-ai-act-high-risk/SCENARIO.md)

## How it fits the Cognis Neural Suite

This tool is one of 52 in the [Cognis Neural Suite](https://github.com/cognis-digital). The full suite + launcher lives at:

- Suite landing: https://cognis.digital
- All 52 repos: https://github.com/cognis-digital
- Cognis.Studio (Enterprise AI Workforce, MCP host): https://cognis.studio

Every Suite tool ships an MCP server, so Cognis.Studio agents can call them as scoped capabilities.

## License

MIT. See [LICENSE](LICENSE).

## About

**[Cognis Digital](https://cognis.digital)** — Wyoming, USA · *Making Tomorrow Better Today: Advanced Cybersecurity, AI Innovation, and Blockchain Expertise.*
