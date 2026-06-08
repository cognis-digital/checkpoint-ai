# CHECKPOINT-AI — NIST AI RMF / EU AI Act / ISO 42001 self-assessment & SSP generator

> Part of the **[Cognis Neural Suite](https://github.com/cognis-digital)** by [Cognis Digital](https://cognis.digital)
> Cognis Open Collaboration License (COCL) v1.0 · domain: `federal`

[![PyPI](https://img.shields.io/pypi/v/cognis-checkpoint-ai.svg)](https://pypi.org/project/cognis-checkpoint-ai/)
[![CI](https://github.com/cognis-digital/checkpoint-ai/actions/workflows/ci.yml/badge.svg)](https://github.com/cognis-digital/checkpoint-ai/actions)
[![License: COCL 1.0](https://img.shields.io/badge/License-COCL%201.0-2b6cb0.svg)](LICENSE)
[![Suite](https://img.shields.io/badge/Cognis-Neural%20Suite-6b46c1.svg)](https://github.com/cognis-digital)

**NIST AI RMF / EU AI Act / ISO 42001 self-assessment & SSP generator.**

*Federal / Compliance — NIST, CMMC, FedRAMP, and SBIR/GSA workflows.*

## Why

Security and intelligence teams need NIST AI RMF / EU AI Act / ISO 42001 self-assessment & SSP generator without standing up heavyweight infrastructure. `checkpoint-ai` is single-purpose, scriptable, CI-friendly, and self-hostable: point it at a target, get prioritized findings in the format your workflow already speaks (table, JSON, SARIF, HTML), and wire it into agents over MCP when you want it autonomous.

## Install

```bash
pip install cognis-checkpoint-ai
# or, from this repo:
pip install -e ".[dev]"
```

## Quick start

```bash
checkpoint-ai --version
checkpoint-ai scan demos/                      # run against the bundled demo
checkpoint-ai scan demos/ --format sarif --out r.sarif --fail-on high
checkpoint-ai scan demos/ --format html --out report.html
checkpoint-ai mcp                              # expose as an MCP server (Cognis.Studio / Claude Desktop / Cursor)
```

## Built-in demo scenarios

Each scenario folder includes a `SCENARIO.md` describing the situation and the findings to expect.

- [`demos/01-pre-launch-gap-analysis/`](demos/01-pre-launch-gap-analysis/SCENARIO.md)
- [`demos/02-iso-42001-readiness/`](demos/02-iso-42001-readiness/SCENARIO.md)
- [`demos/03-eu-ai-act-high-risk/`](demos/03-eu-ai-act-high-risk/SCENARIO.md)

## Output formats

- **Table** (default) — human-readable terminal summary
- **JSON** — machine-readable findings for pipelines
- **SARIF** — drops into GitHub code-scanning / IDE problem panes
- **HTML** — shareable report with severity rollups

## Credits / Built on

Cognis composes and credits the best of open source. This tool builds on / interoperates with:

- [`usnistgov/OSCAL`](https://github.com/usnistgov/OSCAL) — control catalog format

Missing a credit? Open a PR — see [CONTRIBUTING.md](CONTRIBUTING.md).

## How it fits the Cognis Neural Suite

`checkpoint-ai` is one of **52 tools** in the [Cognis Neural Suite](https://github.com/cognis-digital). Every tool ships an MCP server, so [Cognis.Studio](https://cognis.studio) agents can call them as scoped capabilities.

**Sibling tools in `federal`:** [`cmmcmap`](https://github.com/cognis-digital/cmmcmap), [`fedramplens`](https://github.com/cognis-digital/fedramplens), [`sbirscout`](https://github.com/cognis-digital/sbirscout), [`gsafinder`](https://github.com/cognis-digital/gsafinder), [`clearancepath`](https://github.com/cognis-digital/clearancepath)

## Architecture & roadmap

- Design notes: [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)
- Planned work: [`ROADMAP.md`](ROADMAP.md)

## Contributing

PRs, new detections, and demo scenarios are welcome under the collaboration-pull model. See [CONTRIBUTING.md](CONTRIBUTING.md) and [SECURITY.md](SECURITY.md).

## License

Source-available under the **Cognis Open Collaboration License (COCL) v1.0** — free for personal, internal-evaluation, research, and educational use; **commercial / production use requires a license** (licensing@cognis.digital). See [LICENSE](LICENSE).

## Responsible use

This is dual-use security software. Use it only against systems, data, and identities you own or are explicitly authorized in writing to test, and in compliance with applicable law.

## About

**[Cognis Digital](https://cognis.digital)** — Wyoming, USA · *Making Tomorrow Better Today: Advanced Cybersecurity, AI Innovation, and Blockchain Expertise.*
