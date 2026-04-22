## 7. Task List & Sprints (Execution Roadmap)

### Sprint 1: Foundation & Authentication (The Start) [DONE]
- [x] **Setup Project**: Initialize venv, install dependencies (`playwright`, `python-dotenv`).
- [x] **Config Files**: Create `.env.example` and the initial `technicians.json` in the root.
- [x] **Login Agent**: Implement `agentes/auth_agent.py` to handle the Totvs login flow.
- [x] **Test 1.1**: Run login script and verify successful landing page via screenshot.
- [x] **Version Control**: Initialize Git repository, commit changes, and push to GitHub.

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
