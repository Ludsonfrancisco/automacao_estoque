# Automação Retorno de Materiais — Dashboard Loga

Automação Python que processa em lote os seriais de ONU da planilha de devolução, consulta o dashboard Loga, encerra atendimentos abertos automaticamente e grava o resultado de cada serial na própria planilha.

---

## O que faz

Para cada serial na coluna A da planilha:

1. Digita o serial no campo "Escaneie ou digite o Serial da ONU" do dashboard
2. Aguarda a resposta (popup)
3. Grava o resultado nas colunas B, C, D:

| Coluna | Conteúdo |
|--------|----------|
| **A** — SN | Serial da ONU (entrada) |
| **B** — Status | Ex: `[success] Atendimento 4229893 encerrado com sucesso!` ou `[warning] ONU não associada à nenhum atendimento` |
| **C** — Detalhe | Número do atendimento (quando houver) |
| **D** — Timestamp | Data/hora da consulta |

---

## Pré-requisitos

- **Python 3.11+** instalado
- Windows com PowerShell
- Credenciais do dashboard Loga

---

## Instalação (uma vez só)

```powershell
# 1. Criar ambiente virtual e instalar dependências
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt

# 2. Baixar o browser do Playwright (~150MB)
.\.venv\Scripts\python.exe -m playwright install chromium

# 3. Criar arquivo .env com suas credenciais
Copy-Item .env.example .env
notepad .env
```

No `.env`, preencher:
```
LOGA_USER=seu.usuario@dmais.com.br
LOGA_PASS=sua_senha
LOGA_BASE_URL=https://dashboard.loga.net.br
```

> ⚠️ O `.env` **nunca** é commitado (está no `.gitignore`).

---

## Como rodar

### Para cada novo lote de devolução

1. **Coloque a planilha na raiz do projeto** (qualquer nome, ex: `devolucao-15-06.xlsx`)
2. **Edite `automatizar.py`** alterando a linha:
   ```python
   PLANILHA = "devolucao-27-05.xlsx"
   ```
   para o nome da nova planilha.
3. **Faça backup** da planilha (segurança):
   ```powershell
   Copy-Item devolucao-15-06.xlsx devolucao-15-06.bak.xlsx
   ```
4. **Execute**:
   ```powershell
   .\.venv\Scripts\python.exe automatizar.py
   ```

A automação:
- Faz login automático
- Processa cada serial sequencialmente (~4-8s cada)
- Salva a planilha após cada serial (se travar, não perde nada)
- Pula linhas que já têm Status preenchido (permite **retomada**)
- Loga tudo em `logs/execucao-YYYYMMDD.log`
- Mostra no final: total / sucessos / erros

---

## Formato esperado da planilha

- Aba: `devolucao` (ajustar `ABA` em `automatizar.py` se diferente)
- Coluna **A**: header `SN` na linha 1, seriais a partir da linha 2
- Colunas B, C, D: serão criadas/preenchidas automaticamente

---

## Retomada e reprocessamento

- **Travou no meio?** Basta rodar `python automatizar.py` de novo — ele pula as linhas que já têm Status e continua de onde parou.
- **Quer reprocessar um serial específico?** Apague o conteúdo das colunas B/C/D daquela linha e rode de novo — só ela será processada.

---

## Fluxo de erro

Se um serial individual falha (timeout, popup não reconhecido, etc):
- Grava `ERRO: <motivo>` na coluna Status
- Continua processando os outros
- Resumo final mostra quantas linhas falharam

Se a sessão cair no meio (logout), tenta relogar 1× automaticamente.

---

## Exploração — para situações novas

Se o dashboard mudar, ou pra investigar um comportamento desconhecido:

```powershell
.\.venv\Scripts\python.exe explorar.py SERIAL1 SERIAL2 SERIAL3
```

Roda com browser **visível** e captura screenshot + HTML + sequência de popups em `logs/exploracao-YYYYMMDD-HHMMSS/`. Útil pra mapear novos seletores ou padrões de retorno.

---

## Estrutura do projeto

```
automacao_dashboard_loga/
├── README.md                    # este arquivo
├── requirements.txt             # dependências Python
├── .env                         # credenciais (NÃO versionar)
├── .env.example                 # template
├── .gitignore
├── loga_client.py               # cliente do dashboard (login, scan_serial)
├── explorar.py                  # Fase 1 — exploração manual
├── automatizar.py               # Fase 2 — execução em lote
├── devolucao-*.xlsx             # planilhas de devolução
├── logs/
│   ├── execucao-YYYYMMDD.log    # log de cada rodada
│   └── exploracao-*/            # capturas das explorações
└── docs/
    ├── specs/                   # documento de design
    └── plans/                   # plano de implementação task-a-task
```

---

## Troubleshooting

| Problema | Causa provável | Solução |
|----------|----------------|---------|
| `ERRO: defina LOGA_USER e LOGA_PASS no .env` | `.env` não existe ou está vazio | Criar `.env` (ver Instalação) |
| `Login falhou — verifique LOGA_USER e LOGA_PASS` | Credenciais erradas | Conferir usuário/senha no `.env` |
| Browser não abre / `playwright._impl._errors.Error: Executable doesn't exist` | Chromium não baixado | Rodar `playwright install chromium` |
| `Planilha não encontrada` | Nome do arquivo incorreto em `automatizar.py` | Conferir `PLANILHA = "..."` |
| Muitos `ERRO: TimeoutError` em sequência | Site fora do ar ou sessão caiu sem detectar | Conferir manualmente no browser; depois rodar de novo (pula os já feitos) |

---

## Histórico

- **2026-05-27** — Primeira execução completa: 160 seriais, 107 atendimentos encerrados, 53 já não associados, 0 erros (~21 min).
