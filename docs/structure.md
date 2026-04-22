# Architecture & Structure

The project follows a **Flat Architecture** to keep the automation scripts lean and easy to navigate.

## Folder Structure
- `/`: Project root containing configuration and the main consolidation script.
- `/agentes/`: (Planned) Contains all RPA agent scripts (e.g., `auth_agent.py`).
- `/estoque_tecnico/`: Destination folder for the downloaded technician stock reports (XLSX).
- `/docs/`: Project documentation.
- `/venv/`: Python virtual environment.

## Technical Stack
- **Automation**: Playwright (Python).
- **Tooling**: Model Context Protocol (MCP) for agentic execution.
- **Configuration**: Environment variables via `.env`.
- **Data**: Excel files handled with `openpyxl` or `pandas`.
