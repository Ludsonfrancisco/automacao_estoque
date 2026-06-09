# Automação de Retorno de Materiais — Dashboard Loga

**Data:** 2026-05-27
**Status:** Aprovado (aguardando revisão final)

## Objetivo

Automatizar a consulta de seriais de ONU no dashboard https://dashboard.loga.net.br/retorno_materiais, capturando a mensagem de retorno de cada serial e gravando-a de volta na planilha de entrada.

## Entrada

Arquivo `devolucao-27-05.xlsx` na raiz do projeto:
- Aba: `devolucao`
- Coluna A: `SN` (cabeçalho na linha 1, 160 seriais nas linhas 2–161)
- Colunas B, C, D, E: vazias (E1 contém o número 160, contagem)

## Saída

Mesmo arquivo, com colunas adicionais preenchidas:
- **Coluna B — Status:** texto do retorno (ex: `ONU não associada à nenhum atendimento`, `Baixado`, `Aceito a ser baixado`)
- **Coluna C — Detalhe:** número ou código adicional, quando o site retornar (campo opcional)
- **Coluna D — Timestamp:** data/hora da consulta (formato `YYYY-MM-DD HH:MM:SS`)

Headers nas células B1, C1, D1.

## Arquitetura

### Duas fases

**Fase 1 — Exploração interativa** (`explorar.py`):
- Roda **uma vez**, com browser visível, manualmente, com você do lado
- Faz login, navega para `/retorno_materiais`
- Recebe 2–3 seriais de teste via input/argumento (idealmente: 1 já baixado, 1 não vinculado, 1 com outro status)
- Para cada um: digita, captura HTML do retorno, screenshot, e texto literal
- Objetivo: descobrir seletor exato do retorno, formato, e o trigger (Enter vs botão)
- Resultado salvo em `logs/exploracao-YYYYMMDD.txt`

**Fase 2 — Automação em lote** (`automatizar.py`):
- Roda **headless**, processa os 160 seriais
- Usa os seletores/padrões descobertos na Fase 1
- Salva a planilha após cada serial (retomada segura)

### Stack

- **Python 3.11+**
- **Playwright** (browser automation, modo Chromium headless)
- **openpyxl** (leitura/escrita do .xlsx)
- **python-dotenv** (credenciais via `.env`)

### Estrutura de arquivos

```
automacao_dashboard_loga/
├── devolucao-27-05.xlsx
├── .env                          # LOGA_USER, LOGA_PASS (gitignored)
├── .env.example                  # template sem valores
├── .gitignore
├── requirements.txt
├── explorar.py                   # Fase 1
├── automatizar.py                # Fase 2
├── loga_client.py                # módulo compartilhado: login, navegação, scan
├── logs/
│   ├── exploracao-YYYYMMDD.txt
│   └── execucao-YYYYMMDD.log
└── docs/
    └── specs/2026-05-27-automacao-retorno-loga-design.md
```

### Módulo `loga_client.py`

Encapsula a interação com o site para ser reutilizado entre Fase 1 e Fase 2.

Funções:
- `login(page, user, password)` — faz login
- `goto_retorno_materiais(page)` — navega para a página alvo
- `scan_serial(page, serial) -> dict` — digita o serial, aguarda retorno, devolve `{status: str, detalhe: str|None, raw_html: str}`
- `is_session_alive(page) -> bool` — verifica se ainda está logado

### Fluxo do `automatizar.py`

1. Carrega `.env` — falha com mensagem clara se `LOGA_USER`/`LOGA_PASS` ausentes
2. Carrega `devolucao-27-05.xlsx` (modo write-back)
3. Garante headers em B1=`Status`, C1=`Detalhe`, D1=`Timestamp`
4. Abre Playwright (Chromium headless), faz login, navega para `/retorno_materiais`
5. Para cada linha de 2 a 161:
   - Se coluna B já preenchida e não-vazia → **pula** (suporta retomada)
   - Pega serial da coluna A
   - Chama `scan_serial(page, serial)`
   - Grava resultado em B/C/D
   - `wb.save()` — persiste imediatamente
   - Limpa input para próximo scan
6. Após cada 10 seriais: verifica sessão; se caiu, tenta relogar 1×
7. Imprime resumo final: total / sucessos / erros / linhas com erro

### Tratamento de erros

- **Erro num serial individual** (timeout, retorno não reconhecido, campo sumiu):
  - Grava `ERRO: <motivo curto>` na coluna B
  - Loga stack trace completo em `logs/execucao-YYYYMMDD.log`
  - Segue para próximo serial
- **Sessão expirada / redirect para login**:
  - Tenta `login()` 1×
  - Se falhar, encerra com código de saída ≠ 0 e mensagem clara
- **Credenciais inválidas (login inicial)**:
  - Encerra antes de processar qualquer serial, mensagem clara

### Retomada

- Reexecutar `automatizar.py` é seguro: ele pula linhas que já têm coluna B preenchida
- Para reprocessar um serial específico, basta limpar manualmente B/C/D daquela linha

### Segurança

- `.env` listado em `.gitignore` — credenciais nunca em código nem em commits
- `.env.example` versionado com placeholders (sem valores reais)
- Logs não imprimem senha
- Sem hardcode de URL secreta — `dashboard.loga.net.br` é o único endpoint público usado

## Padrões de retorno conhecidos

Da conversa inicial:
- `ONU não associada à nenhum atendimento` (esperado nos primeiros ~50 seriais, que já foram processados manualmente pelo usuário)
- Mensagens equivalentes a "baixado" e "aceito a ser baixado" — texto exato a confirmar na Fase 1
- Possível número de retorno em alguns casos — armazenar na coluna C

## Critério de aceitação

- Rodar `python automatizar.py` processa todos os 160 seriais sem intervenção manual
- Cada linha da planilha tem B/C/D preenchidos ao final
- Se a execução for interrompida, rodar de novo continua de onde parou
- Erros individuais não derrubam a execução inteira
- Credenciais nunca aparecem em logs nem em arquivos versionados

## Fora de escopo

- Interface gráfica
- Notificação por e-mail/Slack ao terminar
- Processamento em paralelo (sequencial é suficiente para 160 seriais)
- Backup automático da planilha (usuário faz manual se quiser; o arquivo é salvo em cada iteração mas não é versionado)
