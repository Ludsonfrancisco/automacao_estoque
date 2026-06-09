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

## 8. Success Metrics
- 100% of technicians from the list processed.
- Average execution time per technician < 30 seconds.
- No hardcoded credentials in the repository.

## 9. Risks & Mitigations
- **UI Changes**: If Totvs updates, update the selector mapping in a centralized config.
- **Session Timeout**: Implement a check to re-login if the session expires during the loop.
