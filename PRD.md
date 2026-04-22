# PRD - Totvs Sync Agent

## 1. Overview
The **Totvs Sync Agent** is a specialized RPA (Robotic Process Automation) tool designed to automate the extraction of technician stock data from the Totvs Web platform. It eliminates manual overhead by navigating ERP menus and downloading reports for a predefined list of technicians.

## 2. About the Product
This RPA agent acts as a bridge between the Totvs ERP and the local data processing pipeline. It automates browser interactions, handles authentication, and ensures that stock reports are systematically collected and organized.

## 3. Purpose & Target Audience
**Context:** Lar Telecom.
**Purpose:** To streamline the stock control process by ensuring timely and accurate data availability.
**Target Audience:** Logistics team and inventory managers.

## 4. Objectives
- **Efficiency:** Reduce extraction time by 80%.
- **Accuracy:** Zero errors in matching technician codes to downloaded files.
- **Traceability:** Detailed logs for every download attempt.

## 5. Functional Requirements
- **Authentication:** Secure login via `.env` credentials.
- **Data Source:** Read technician names and codes from `technicians.json` (or .csv) in the project root.
- **Navigation:** Access the "Estoque de Técnicos" module in Totvs.
- **Extraction:** Input the technician code, generate the report, and handle the XLSX download.
- **Organization:** Save files into `./estoque_tecnico/` using the pattern `[TECH_CODE]_[DATE].xlsx`.

## 6. Non-Functional Requirements
- **Language:** English code / Portuguese (PT-BR) UI references.
- **Architecture:** Flat structure (`./agentes/` folder).
- **Concurrency:** Async Playwright for performance.
- **Reliability:** 3 retries for UI element timeouts.

## 7. Task List & Sprints (Execution Roadmap)

### Sprint 1: Foundation & Authentication (The Start)
- [x] **Setup Project**: Initialize venv, install dependencies (`playwright`, `python-dotenv`).
- [x] **Config Files**: Create `.env.example` and the initial `technicians.json` in the root.
- [x] **Login Agent**: Implement `agentes/auth_agent.py` to handle the Totvs login flow.
- [ ] **Test 1.1**: Run login script and verify successful landing page via screenshot.
- [ ] **Version Control**: Initialize Git repository, commit changes, and push to GitHub.

### Sprint 2: Navigation & Extraction Loop (The Middle)
- [ ] **Navigation**: Implement logic to reach the "Estoque de Técnicos" screen.
- [ ] **Data Reader**: Create a utility to read technician codes from the root file.
- [ ] **Core Loop**: Implement the iteration logic (Input Code -> Click 'Gerar' -> Wait for Download).
- [ ] **Download Handler**: Use `expect_download` to capture files dynamically.
- [ ] **Test 2.1**: Verify navigation to the correct module using PT-BR selectors.
- [ ] **Test 2.2**: Run the loop for a single test technician and verify if the download is triggered.
- [ ] **Version Control**: Commit sprint 2 progress and push to GitHub.

### Sprint 3: File Management & Robustness (The End)
- [ ] **File Organizer**: Implement logic to rename and move files to `./estoque_tecnico/`.
- [ ] **Error Handling**: Add try-except blocks for "Technician not found" or "Empty report" scenarios.
- [ ] **Final Orchestrator**: Create `sync_manager.py` to run the entire flow from Start to Finish.
- [ ] **Test 3.1**: Run the full list of technicians and check if the count of files in `./estoque_tecnico/` matches the source file.
- [ ] **Version Control**: Final commit and push to GitHub.

## 8. Success Metrics
- 100% of technicians from the list processed.
- Average execution time per technician < 30 seconds.
- No hardcoded credentials in the repository.

## 9. Risks & Mitigations
- **UI Changes**: If Totvs updates, update the selector mapping in a centralized config.
- **Session Timeout**: Implement a check to re-login if the session expires during the loop.
