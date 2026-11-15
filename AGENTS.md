# AGENTS.md

Project guide for AI agents working in this repository.

## Project

NASA Space Apps 2026 — **Synthetic Data: STARDUST CRUSADERS / Outer Space Monitoring**.
Generate realistic synthetic patient datasets by fusing four real data domains
(vital signs, retinal/ophthalmology, fitness, sleep) through a causal cascade.

## Layout

```
agents/                      Original role prompts (Spanish source of truth)
  agente_sintetizador_de_datos.md
  skills/agente_de_configuracion.md
  skills/agente_validador_medico_y_estadistico.md
.opencode/                   opencode config consumed by VS Code / CLI
  agent/                     Registered agents (primary + subagents)
  skill/                     Registered skills (SKILL.md knowledge packs)
app/                         Python terminal interface + future modules
  main.py                    CLI entry point
  core/                      registry, paths, context
  modules/                   Future modular scripts (generate/configure/validate/preview)
config/                      JSON causal parameters (owned by data-configurator)
dataSources/                 Raw input CSVs (read-only)
output/                      Generated datasets + reports
```

## Agents

- **data-synthesizer** (primary) — writes `app/modules/generate.py` and the causal logic.
- **data-configurator** (subagent) — owns `config/*.json` weights, distributions, bounds.
- **data-validator** (subagent) — audits outputs, writes `output/validation_report.md`.

Invoke subagents with `@data-configurator` / `@data-validator`, or let the primary delegate.

## Skills

- `synthetic-data-generation` — data dictionary, causal cascade, hard rules.
- `synthetic-data-validation` — sanity checks, correlation checks, report format.

## Conventions

- Python 3.10+ (dev machine: 3.13). Standard library only for the CLI; generation
  modules may use `pandas`/`numpy`.
- No ML/GAN generation — pure arithmetic + statistical distributions.
- No magic numbers in code: every weight/mean/std/bound comes from `config/*.json`.
- Every `app/modules/<name>.py` must expose `run(context) -> int` (exit code).
  `context` is defined in `app/core/registry.py`.

## Commands

```powershell
python app/main.py            # interactive menu
python app/main.py info       # list data sources and module status
python app/main.py generate --records 1000 --output output/dataset.csv
python app/main.py configure  # (future) write config JSON
python app/main.py validate --input output/dataset.csv
python app/main.py preview --input output/dataset.csv --rows 10
```

## Notes

- After editing anything under `.opencode/` or `opencode.json`, **restart opencode**
  (config is loaded once at startup).
- The `agents/` folder holds the original Spanish prompts; the English translations
  live in `.opencode/agent/`.
