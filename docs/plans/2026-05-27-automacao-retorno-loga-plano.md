# Automação Retorno Loga — Plano de Implementação

**Goal:** Construir uma automação Python+Playwright que consulta seriais no dashboard Loga e grava o retorno de cada um na planilha `devolucao-27-05.xlsx`.

**Architecture:** Duas fases. Fase 1 (`explorar.py`) roda manualmente para mapear os seletores e padrões de retorno do site. Fase 2 (`automatizar.py`) roda headless processando 160 seriais em lote. Lógica compartilhada vive em `loga_client.py`.

**Tech Stack:** Python 3.11+, Playwright (Chromium), openpyxl, python-dotenv.

---

## Estrutura de arquivos

```
automacao_dashboard_loga/
├── .env                          # Criado pelo usuário, NÃO versionado
├── .env.example                  # Template versionado
├── .gitignore
├── requirements.txt
├── loga_client.py                # login, navegação, scan_serial
├── explorar.py                   # Fase 1 — descoberta manual
├── automatizar.py                # Fase 2 — execução em lote
├── devolucao-27-05.xlsx          # Já existe
├── logs/                         # Criado em runtime
└── docs/specs/2026-05-27-automacao-retorno-loga-design.md
```

---

### Task 1: Setup do projeto

**Files:**
- Create: `requirements.txt`
- Create: `.gitignore`
- Create: `.env.example`

- [ ] **Step 1: Criar `requirements.txt`**

```
playwright==1.48.0
openpyxl==3.1.5
python-dotenv==1.0.1
```

- [ ] **Step 2: Criar `.gitignore`**

```
.env
__pycache__/
*.pyc
.venv/
venv/
logs/
*.bak
```

- [ ] **Step 3: Criar `.env.example`**

```
LOGA_USER=seu_usuario_aqui
LOGA_PASS=sua_senha_aqui
LOGA_BASE_URL=https://dashboard.loga.net.br
```

- [ ] **Step 4: Instalar dependências (rodar no PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
playwright install chromium
```

Expected: instala sem erros; `playwright install chromium` baixa o browser (~150MB).

- [ ] **Step 5: Pedir ao usuário criar `.env` real**

Avisar o usuário: "Copie `.env.example` para `.env` e preencha com seu usuário e senha do dashboard Loga. Este arquivo NÃO será versionado."

---

### Task 2: Esqueleto do `loga_client.py` — login

**Files:**
- Create: `loga_client.py`

Este módulo NÃO terá testes unitários automatizados (depende de browser + site externo). Validação é manual via `explorar.py` na Task 3.

- [ ] **Step 1: Criar `loga_client.py` com login**

```python
"""Cliente para o dashboard Loga — login, navegação e scan de seriais."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError


BASE_URL = os.getenv("LOGA_BASE_URL", "https://dashboard.loga.net.br")
RETORNO_PATH = "/retorno_materiais"


@dataclass
class ScanResult:
    status: str
    detalhe: Optional[str]
    raw_html: str


def login(page: Page, user: str, password: str) -> None:
    """Faz login no dashboard. Lança RuntimeError se credenciais inválidas."""
    page.goto(BASE_URL)
    # Seletores reais a confirmar na Fase 1 — abaixo são chutes baseados em padrão comum
    page.fill('input[name="email"], input[name="usuario"], input[type="email"]', user)
    page.fill('input[name="password"], input[name="senha"], input[type="password"]', password)
    page.click('button[type="submit"]')
    page.wait_for_load_state("networkidle", timeout=15000)

    if "/login" in page.url or "login" in page.url.lower():
        raise RuntimeError("Login falhou — verifique LOGA_USER e LOGA_PASS no .env")


def goto_retorno_materiais(page: Page) -> None:
    """Navega para a página de retorno de materiais."""
    page.goto(f"{BASE_URL}{RETORNO_PATH}")
    page.wait_for_load_state("networkidle", timeout=15000)


def is_session_alive(page: Page) -> bool:
    """Verifica se ainda está logado (não foi redirecionado para /login)."""
    return "/login" not in page.url.lower()


def scan_serial(page: Page, serial: str) -> ScanResult:
    """STUB — implementação real na Task 4, depois de explorar o site."""
    raise NotImplementedError("scan_serial será implementado após Fase 1 (explorar.py)")
```

- [ ] **Step 2: Commit**

```powershell
git init
git add requirements.txt .gitignore .env.example loga_client.py
git commit -m "feat: setup projeto e esqueleto do loga_client"
```

---

### Task 3: `explorar.py` — Fase 1 (descoberta manual)

**Files:**
- Create: `explorar.py`

Este script roda **com browser visível** e captura HTML/screenshot/texto de cada serial testado, para mapearmos os seletores reais.

- [ ] **Step 1: Criar `explorar.py`**

```python
"""Fase 1 — Exploração manual do site para mapear seletores e retornos.

Uso:
    python explorar.py SERIAL1 SERIAL2 SERIAL3

Roda com browser VISÍVEL. Para cada serial:
  - digita no campo de scan
  - aguarda 5s
  - captura screenshot, HTML do retorno, e texto
  - salva tudo em logs/exploracao-YYYYMMDD-HHMMSS/
"""
from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from playwright.sync_api import sync_playwright

import loga_client


def main(seriais: list[str]) -> int:
    load_dotenv()
    user = os.getenv("LOGA_USER")
    password = os.getenv("LOGA_PASS")
    if not user or not password:
        print("ERRO: defina LOGA_USER e LOGA_PASS no .env", file=sys.stderr)
        return 1

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    out_dir = Path("logs") / f"exploracao-{stamp}"
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[explorar] salvando capturas em {out_dir}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=300)
        context = browser.new_context()
        page = context.new_page()

        print("[explorar] fazendo login...")
        loga_client.login(page, user, password)
        print("[explorar] login OK; navegando para retorno_materiais...")
        loga_client.goto_retorno_materiais(page)

        # Captura inicial — estado da página antes de qualquer scan
        page.screenshot(path=out_dir / "00-inicial.png", full_page=True)
        (out_dir / "00-inicial.html").write_text(page.content(), encoding="utf-8")

        for i, serial in enumerate(seriais, 1):
            print(f"\n[explorar] === serial {i}: {serial} ===")
            try:
                input_locator = page.get_by_placeholder("Escaneie ou digite o Serial da ONU")
                input_locator.click()
                input_locator.fill(serial)
                input_locator.press("Enter")
            except Exception as e:
                print(f"[explorar] ERRO ao digitar serial: {e}")
                page.screenshot(path=out_dir / f"{i:02d}-{serial}-erro.png", full_page=True)
                continue

            # aguarda algo aparecer — 5s é generoso para inspeção visual
            page.wait_for_timeout(5000)

            page.screenshot(path=out_dir / f"{i:02d}-{serial}.png", full_page=True)
            (out_dir / f"{i:02d}-{serial}.html").write_text(page.content(), encoding="utf-8")
            print(f"[explorar] capturado screenshot + HTML")

        input("\n[explorar] Pressione Enter para fechar o browser...")
        browser.close()

    print(f"\n[explorar] DONE. Verifique {out_dir}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python explorar.py SERIAL1 [SERIAL2 ...]", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
```

- [ ] **Step 2: Rodar com 2-3 seriais de teste (com usuário do lado)**

Avisar o usuário:
> "Rode `python explorar.py <serial_baixado> <serial_nao_vinculado> <serial_aceito>` com 2-3 seriais reais que você já saiba os retornos esperados. O browser vai abrir visível — acompanhe e me mande a pasta `logs/exploracao-YYYYMMDD-HHMMSS/` quando terminar."

- [ ] **Step 3: Confirmar com o usuário os seletores reais**

Após rodar, ANTES de continuar para Task 4:
1. Abrir os HTMLs capturados e identificar:
   - Seletor exato do campo de input (confirmar que `placeholder="Escaneie ou digite o Serial da ONU"` funciona)
   - Seletor do elemento que mostra o retorno (provável: toast, alert, ou card)
   - Texto exato das mensagens (`"ONU não associada à nenhum atendimento"`, "Baixado", etc.)
   - Se há um número/código adicional retornado
   - Se o trigger é Enter (já assumido) ou se precisa clicar em botão
2. Atualizar a Task 4 abaixo com os seletores REAIS antes de implementar.

- [ ] **Step 4: Commit**

```powershell
git add explorar.py
git commit -m "feat: script de exploração manual (Fase 1)"
```

---

### Task 4: Implementar `scan_serial` com base na Fase 1

**Files:**
- Modify: `loga_client.py` (substituir o stub `scan_serial`)

> **PRÉ-REQUISITO:** Task 3 concluída e seletores confirmados. Os trechos abaixo usam seletores genéricos baseados em padrões comuns — **substituir pelos reais** descobertos na Fase 1.

- [ ] **Step 1: Substituir o stub `scan_serial` em `loga_client.py`**

Substituir a função `scan_serial` (atualmente um stub) por:

```python
def scan_serial(page: Page, serial: str, timeout_ms: int = 10000) -> ScanResult:
    """Digita o serial no campo de scan e captura o retorno.

    Levanta:
        TimeoutError — se nenhum retorno aparecer em timeout_ms
        RuntimeError — se a sessão tiver expirado (redirect para login)
    """
    if not is_session_alive(page):
        raise RuntimeError("Sessão expirada — necessário relogar")

    # 1) Localizar o input pelo placeholder
    input_locator = page.get_by_placeholder("Escaneie ou digite o Serial da ONU")
    input_locator.click()
    input_locator.fill("")  # limpa qualquer resíduo
    input_locator.fill(serial)
    input_locator.press("Enter")

    # 2) Aguardar o elemento de retorno aparecer
    #    SELETOR A CONFIRMAR NA FASE 1 — abaixo é um chute baseado em toast comum
    retorno_selector = ".toast, .alert, [role='alert'], .swal2-container, .notyf__toast"
    try:
        page.wait_for_selector(retorno_selector, timeout=timeout_ms, state="visible")
    except PlaywrightTimeoutError:
        raise TimeoutError(f"Nenhum retorno apareceu para serial {serial} em {timeout_ms}ms")

    # 3) Extrair texto do retorno
    retorno_el = page.locator(retorno_selector).first
    raw_html = retorno_el.evaluate("el => el.outerHTML")
    status_text = retorno_el.inner_text().strip()

    # 4) Tentar extrair um número/código adicional, se houver
    #    Regex genérica — ajustar com base no que aparece de fato
    import re
    match = re.search(r"\b(\d{4,})\b", status_text)
    detalhe = match.group(1) if match else None

    # 5) Limpar o estado para o próximo scan
    #    Fechar toast/alert se necessário — depende do componente real
    try:
        close_btn = page.locator(".toast .close, .alert .close, .swal2-close").first
        if close_btn.is_visible(timeout=500):
            close_btn.click()
    except Exception:
        pass  # não-fatal

    return ScanResult(status=status_text, detalhe=detalhe, raw_html=raw_html)
```

- [ ] **Step 2: Testar manualmente com 1 serial**

Adicionar temporariamente ao final de `explorar.py` (ou criar `test_scan_manual.py`):

```python
# Adicionar após o loop em explorar.py, OU rodar em REPL
result = loga_client.scan_serial(page, "48575443DE5892A3")
print(f"Status: {result.status}")
print(f"Detalhe: {result.detalhe}")
print(f"HTML: {result.raw_html[:200]}...")
```

Rodar: `python explorar.py 48575443DE5892A3`
Expected: imprime status (provavelmente "ONU não associada à nenhum atendimento") sem exceção.

- [ ] **Step 3: Commit**

```powershell
git add loga_client.py
git commit -m "feat: implementa scan_serial com seletores confirmados"
```

---

### Task 5: `automatizar.py` — leitura/escrita da planilha

**Files:**
- Create: `automatizar.py`

- [ ] **Step 1: Criar `automatizar.py` com a lógica de planilha (sem browser ainda)**

```python
"""Fase 2 — Automação em lote dos 160 seriais.

Uso:
    python automatizar.py

Lê devolucao-27-05.xlsx, processa cada serial da coluna A,
grava Status/Detalhe/Timestamp nas colunas B/C/D.
Salva após cada serial. Pula linhas já preenchidas (retomada).
"""
from __future__ import annotations

import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from openpyxl import load_workbook
from playwright.sync_api import sync_playwright

import loga_client


PLANILHA = "devolucao-27-05.xlsx"
ABA = "devolucao"
COL_SERIAL = 1   # A
COL_STATUS = 2   # B
COL_DETALHE = 3  # C
COL_TIMESTAMP = 4  # D
HEADER_ROW = 1
FIRST_DATA_ROW = 2


def setup_logging() -> Path:
    Path("logs").mkdir(exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d")
    log_path = Path("logs") / f"execucao-{stamp}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(log_path, encoding="utf-8"), logging.StreamHandler()],
    )
    return log_path


def ensure_headers(ws) -> None:
    """Garante que B1=Status, C1=Detalhe, D1=Timestamp."""
    if ws.cell(HEADER_ROW, COL_STATUS).value != "Status":
        ws.cell(HEADER_ROW, COL_STATUS).value = "Status"
    if ws.cell(HEADER_ROW, COL_DETALHE).value != "Detalhe":
        ws.cell(HEADER_ROW, COL_DETALHE).value = "Detalhe"
    if ws.cell(HEADER_ROW, COL_TIMESTAMP).value != "Timestamp":
        ws.cell(HEADER_ROW, COL_TIMESTAMP).value = "Timestamp"


def iter_pendentes(ws):
    """Gera (row_idx, serial) para linhas com serial e SEM status preenchido."""
    for row_idx in range(FIRST_DATA_ROW, ws.max_row + 1):
        serial = ws.cell(row_idx, COL_SERIAL).value
        status = ws.cell(row_idx, COL_STATUS).value
        if serial and not status:
            yield row_idx, str(serial).strip()


def grava_resultado(ws, row_idx: int, status: str, detalhe: str | None) -> None:
    ws.cell(row_idx, COL_STATUS).value = status
    ws.cell(row_idx, COL_DETALHE).value = detalhe or ""
    ws.cell(row_idx, COL_TIMESTAMP).value = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
```

- [ ] **Step 2: Commit parcial**

```powershell
git add automatizar.py
git commit -m "feat: estrutura inicial automatizar.py (planilha apenas)"
```

---

### Task 6: `automatizar.py` — integração com browser + loop principal

**Files:**
- Modify: `automatizar.py` (adicionar `main()` ao final)

- [ ] **Step 1: Adicionar `main()` ao final de `automatizar.py`**

```python
def relogar(page, user: str, password: str) -> bool:
    try:
        loga_client.login(page, user, password)
        loga_client.goto_retorno_materiais(page)
        return True
    except Exception as e:
        logging.error(f"Falha ao relogar: {e}")
        return False


def main() -> int:
    log_path = setup_logging()
    logging.info(f"Log em {log_path}")

    load_dotenv()
    user = os.getenv("LOGA_USER")
    password = os.getenv("LOGA_PASS")
    if not user or not password:
        logging.error("Defina LOGA_USER e LOGA_PASS no .env")
        return 1

    if not Path(PLANILHA).exists():
        logging.error(f"Planilha não encontrada: {PLANILHA}")
        return 1

    wb = load_workbook(PLANILHA)
    ws = wb[ABA]
    ensure_headers(ws)
    wb.save(PLANILHA)

    pendentes = list(iter_pendentes(ws))
    total = len(pendentes)
    logging.info(f"{total} seriais pendentes")
    if total == 0:
        logging.info("Nada a fazer.")
        return 0

    sucessos = 0
    erros = 0
    linhas_com_erro: list[int] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        logging.info("Fazendo login...")
        try:
            loga_client.login(page, user, password)
            loga_client.goto_retorno_materiais(page)
        except Exception as e:
            logging.error(f"Login inicial falhou: {e}")
            browser.close()
            return 2

        for i, (row_idx, serial) in enumerate(pendentes, 1):
            logging.info(f"[{i}/{total}] linha {row_idx} — serial {serial}")
            try:
                result = loga_client.scan_serial(page, serial)
                grava_resultado(ws, row_idx, result.status, result.detalhe)
                sucessos += 1
                logging.info(f"  -> {result.status}")
            except RuntimeError as e:
                # provavelmente sessão expirada
                logging.warning(f"  sessão pode ter caído: {e} — tentando relogar")
                if relogar(page, user, password):
                    try:
                        result = loga_client.scan_serial(page, serial)
                        grava_resultado(ws, row_idx, result.status, result.detalhe)
                        sucessos += 1
                        logging.info(f"  -> {result.status} (após relogin)")
                    except Exception as e2:
                        msg = f"ERRO: {type(e2).__name__}: {str(e2)[:120]}"
                        grava_resultado(ws, row_idx, msg, None)
                        erros += 1
                        linhas_com_erro.append(row_idx)
                        logging.exception(f"  falhou após relogin")
                else:
                    msg = f"ERRO: relogin falhou"
                    grava_resultado(ws, row_idx, msg, None)
                    erros += 1
                    linhas_com_erro.append(row_idx)
            except Exception as e:
                msg = f"ERRO: {type(e).__name__}: {str(e)[:120]}"
                grava_resultado(ws, row_idx, msg, None)
                erros += 1
                linhas_com_erro.append(row_idx)
                logging.exception(f"  erro processando serial {serial}")

            wb.save(PLANILHA)  # salva a cada serial

        browser.close()

    logging.info("=" * 60)
    logging.info(f"FIM. Total: {total} | Sucessos: {sucessos} | Erros: {erros}")
    if linhas_com_erro:
        logging.info(f"Linhas com erro: {linhas_com_erro}")
    return 0 if erros == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Smoke test — rodar com a planilha completa**

Avisar usuário antes:
> "Vou rodar `python automatizar.py` agora. Vai processar os 160 seriais headless. Recomendo fazer um backup da planilha (`Copy-Item devolucao-27-05.xlsx devolucao-27-05.bak.xlsx`) antes."

Rodar: `python automatizar.py`

Expected:
- Cria `logs/execucao-YYYYMMDD.log`
- Imprime progresso `[N/160] linha X — serial Y -> <status>`
- Salva a planilha após cada serial
- No final: resumo com sucessos/erros

- [ ] **Step 3: Validar resultado na planilha**

Abrir `devolucao-27-05.xlsx` e conferir:
- B1=Status, C1=Detalhe, D1=Timestamp
- Linhas 2-51 (primeiros ~50): provavelmente "ONU não associada à nenhum atendimento"
- Linhas 52+: outros status
- Coluna D com timestamp recente em todas

- [ ] **Step 4: Commit**

```powershell
git add automatizar.py
git commit -m "feat: loop principal de automação com retomada e relogin"
```

---

### Task 7: Polimento e documentação mínima

**Files:**
- Create: `README.md` (apenas se o usuário pedir — pular por padrão)

- [ ] **Step 1: Confirmar com usuário se quer README**

Por padrão, NÃO criar README a menos que o usuário peça explicitamente. Se pedir, criar README curto com:
- Pré-requisitos (Python, criar .env)
- Como rodar (`python automatizar.py`)
- Como retomar (basta rodar de novo)
- Como reprocessar uma linha (limpar B/C/D)

- [ ] **Step 2: Verificar `.gitignore` cobre tudo**

Confirmar que `.env`, `logs/`, `__pycache__/`, `*.bak`, `.venv/` estão todos listados.

- [ ] **Step 3: Commit final**

```powershell
git status   # garantir que .env NÃO aparece
git add -A
git commit -m "chore: polimento final"
```

---

## Self-Review (checklist do plano)

- [x] Cobre todos os requisitos do spec? Login ✓, leitura planilha ✓, scan loop ✓, escrita ✓, save-per-serial ✓, retomada ✓, erro individual ✓, relogin ✓, .env ✓, gitignore ✓
- [x] Sem placeholders "TBD"? Há um ponto explícito de "seletores a confirmar na Fase 1" — é intencional, faz parte do design de duas fases
- [x] Tipos/nomes consistentes? `ScanResult.status/detalhe/raw_html` usados em loga_client e automatizar — confere
- [x] Cada task produz artefato testável independentemente
