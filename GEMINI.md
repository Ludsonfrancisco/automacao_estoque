# Gemini CLI Project Instructions - Totvs Sync Agent

This file contains foundational mandates for your operation within the **Totvs Sync Agent** project. These instructions take absolute precedence over general defaults.

## 1. Project Context
- **Product:** RPA agent for Lar Telecom to sync technician stock from Totvs Web.
- **Architecture:** Flat structure. All automation scripts MUST reside in the `./agentes/` directory.
- **Tech Stack:** Python 3.12+, Playwright (Async), MCP, `python-dotenv`, and `openpyxl`/`pandas` for data handling.

## 2. Language & Style Mandates
- **Code & Documentation:** Strictly **English**.
- **UI References:** Always use **Portuguese (PT-BR)** when referring to Totvs Web elements (e.g., 'Estoque de Técnicos', 'Gerar Relatório').
- **Python Style:** Follow **PEP 8** strictly. Use **single quotes** (`'`) for strings unless double quotes are necessary.
- **Async Pattern:** Always use `async`/`await` for browser automation.

## 3. Tooling & Security
- **Credentials:** NEVER hardcode secrets. Use `os.getenv` and ensure `.env` is loaded via `python-dotenv`.
- **Browser Automation:** Use Playwright via the MCP toolset. Prioritize `expect_download` for capturing reports.
- **Validation:** Every logic change in agents must be verified against the `PRD.md` requirements.

## 4. Development Workflow
- **Research:** Always check `docs/standards.md` before implementing new logic.
- **Implementation:** Stick to the "Sprints" defined in `PRD.md`. Do not implement features out of scope.
- **Naming:** Follow the `[purpose]_agent.py` pattern for files inside `./agentes/`.

## 5. Constraints
- Do NOT modify the `venv/` directory.
- Do NOT add external libraries without verifying they are necessary and listed in `docs/structure.md`.
- Maintain the `./estoque_tecnico/` folder as the exclusive output for downloaded reports.
