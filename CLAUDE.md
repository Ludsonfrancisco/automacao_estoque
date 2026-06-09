# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

A one-off Python automation that processes batches of ONU serials from an Excel spreadsheet, queries the Loga dashboard (`dashboard.loga.net.br/retorno_materiais`) for each serial, and writes the response back into the same spreadsheet. Each run can have a **real side effect on the remote system**: scanning a serial with an open atendimento auto-closes it on the dashboard. Always remind the user of this before running `automatizar.py`.

## Common commands

PowerShell on Windows. Always use the venv Python explicitly (`python` from PATH is not the venv):

```powershell
# Setup (one-time)
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium

# Run batch automation (uses PLANILHA constant in automatizar.py)
.\.venv\Scripts\python.exe automatizar.py

# Run exploration with visible browser (debug / map new selectors)
.\.venv\Scripts\python.exe explorar.py SERIAL1 [SERIAL2 ...]
```

There are no tests, no linter, no build step. Verification is by running on a small set of serials and inspecting the spreadsheet + the per-run log in `logs/execucao-YYYYMMDD.log`.

## Architecture

Two-phase design, deliberately separated:

- **`loga_client.py`** — the only file that talks to the dashboard. Exposes `login`, `goto_retorno_materiais`, `is_session_alive`, `scan_serial`, and the `ScanResult` dataclass. Both scripts import from here; **no Playwright code lives in `automatizar.py` or `explorar.py`**.
- **`explorar.py`** — Phase 1. Visible browser, manual, used to discover/confirm selectors and response patterns. Writes screenshots + HTML + a captured popup sequence to `logs/exploracao-YYYYMMDD-HHMMSS/`. Run this whenever the dashboard changes or a new response shape appears.
- **`automatizar.py`** — Phase 2. Headless batch over the spreadsheet. Owns the spreadsheet I/O, the resume logic, error policy, and relogin-on-session-loss. Imports `loga_client` for everything web-related.

The split is the architectural contract: anything that interacts with the page goes in `loga_client.py`; spreadsheet bookkeeping and orchestration go in `automatizar.py`.

## Site-specific gotchas

These are not obvious from the code and burned us during development:

- **Go directly to `/login`** — `https://dashboard.loga.net.br/` is a landing page with an "Entrar" link, not the login form. Hitting `/login` directly skips it.
- **Don't use `wait_for_load_state("networkidle")`** — the dashboard has eternal polling/websocket activity and never goes idle. Use `domcontentloaded` plus `wait_for(state="visible")` on a specific element instead.
- **Initial "Aguarde... Carregando atendimentos..."** — after navigating to `/retorno_materiais`, a SweetAlert2 modal blocks interaction for ~30s. Always wait for it to hide before scanning the first serial (`aguardar_modal_inicial` in `automatizar.py`).
- **Popups auto-dismiss in ~2.5s** — SweetAlert2 toasts via `.swal2-popup`. Capture as soon as `wait_for(state="visible")` returns; don't sleep.
- **Two popups can fire per serial** — for a serial with an open atendimento, you get an `info` "Aguarde... Encerrando atendimento NUMERO... Causa: XXX" followed by a `success` "Atendimento NUMERO encerrado com sucesso!". `scan_serial` captures the *sequence* and picks the most informative one (last non-loading).

## Spreadsheet contract

`automatizar.py` hardcodes:
- `PLANILHA` — filename in project root
- `ABA` — sheet name (currently `"devolucao"`)
- Column layout: A=SN (input), B=Status, C=Detalhe (extracted atendimento number), D=Timestamp

A new batch = new `.xlsx` file in the root with the same A/`SN` shape; update the `PLANILHA` constant. Headers in B1/C1/D1 are created automatically by `ensure_headers` if absent.

**Resume behavior**: `iter_pendentes` skips any row where column B is already non-empty. To reprocess a single row, clear B/C/D for that row and rerun.

## Error policy

- Per-serial errors are caught, written as `ERRO: <type>: <message>` in column B, and execution continues. The final log line lists all failed row indices.
- A `RuntimeError` from `scan_serial` is interpreted as session loss → one relogin attempt → retry that serial once → if still failing, mark error and continue.
- Initial login failure exits with code 2 before any serial is processed.

## Credentials and secrets

Loaded from `.env` (`LOGA_USER`, `LOGA_PASS`, optional `LOGA_BASE_URL`). The `.env` is gitignored; `.env.example` is the template. Never log or commit credentials.

## Reference docs

- `README.md` — user-facing operational guide (installation, how to run a new batch, troubleshooting)
- `docs/specs/2026-05-27-automacao-retorno-loga-design.md` — original design
- `docs/plans/2026-05-27-automacao-retorno-loga-plano.md` — task-by-task implementation plan
