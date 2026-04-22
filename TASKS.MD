## 6. Passo a Passo do Robô (Workflow)

1.  **Início e Autenticação**:
    *   Carregar credenciais do arquivo `.env`.
    *   Realizar login no portal Totvs Web através do `auth_agent.py`.
2.  **Navegação**:
    *   Navegar pelos menus do ERP até alcançar a tela de **"Estoque de Técnicos"**.
3.  **Preparação de Dados**:
    *   Ler a lista de técnicos (nomes e códigos) do arquivo `technicians.json` na raiz do projeto.
4.  **Loop de Extração (Core Loop)**:
    *   Para cada técnico na lista:
        *   Limpar o campo de código anterior (se necessário).
        *   Inserir o código do técnico atual.
        *   Clicar no botão **'Gerar'**.
        *   Aguardar o processamento do relatório.
        *   Capturar o download do arquivo XLSX de forma dinâmica.
        *   **Mover o arquivo baixado imediatamente para a pasta `./estoque_tecnico/`.**
        *   Renomear o arquivo seguindo o padrão `[CODIGO]_[DATA].xlsx` para evitar sobreposição.
5.  **Finalização e Logs**:
    *   Registrar o status da operação (Sucesso/Erro) para cada técnico.
    *   Fechar a sessão e encerrar o navegador de forma segura.

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
- [ ] **Download & Move**: Implement logic to capture the download and save it directly in `./estoque_tecnico/`.
- [ ] **Test 2.1**: Verify navigation to the correct module using PT-BR selectors.
- [ ] **Test 2.2**: Run the loop for a single test technician and verify if the file is moved to the correct folder.
- [ ] **Version Control**: Commit sprint 2 progress and push to GitHub.

### Sprint 3: File Management & Robustness (The End)
- [ ] **Renaming Logic**: Implement standardized renaming (`[TECH_CODE]_[DATE].xlsx`).
- [ ] **Error Handling**: Add try-except blocks for "Technician not found", "Empty report" or "Timeout".
- [ ] **Final Orchestrator**: Create `sync_manager.py` to run the entire flow from Start to Finish.
- [ ] **Test 3.1**: Run the full list of technicians and check if the count of files in `./estoque_tecnico/` matches the source list.
- [ ] **Version Control**: Final commit and push to GitHub.
