"""Cliente para o dashboard Loga — login, navegação e scan de seriais."""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError


BASE_URL = os.getenv("LOGA_BASE_URL", "https://dashboard.loga.net.br")
LOGIN_PATH = "/login"
RETORNO_PATH = "/retorno_materiais"


@dataclass
class ScanResult:
    status: str
    detalhe: Optional[str]
    raw_html: str


def login(page: Page, user: str, password: str) -> None:
    """Faz login no dashboard. Lança RuntimeError se credenciais inválidas."""
    # Vai direto pra /login (evita a landing page com link "Entrar")
    page.goto(f"{BASE_URL}{LOGIN_PATH}", wait_until="domcontentloaded")

    # Aguarda o campo de email ficar disponível (página pode demorar)
    email_locator = page.locator(
        'input[name="email"], input[name="usuario"], input[type="email"]'
    ).first
    email_locator.wait_for(state="visible", timeout=30000)
    email_locator.fill(user)

    page.fill('input[name="password"], input[name="senha"], input[type="password"]', password)
    page.click('button[type="submit"]')

    # aguarda sair de /login
    page.wait_for_url(lambda url: "/login" not in url.lower(), timeout=20000)

    if "/login" in page.url.lower():
        raise RuntimeError("Login falhou — verifique LOGA_USER e LOGA_PASS no .env")


def goto_retorno_materiais(page: Page) -> None:
    """Navega para a página de retorno de materiais."""
    page.goto(f"{BASE_URL}{RETORNO_PATH}", wait_until="domcontentloaded")
    # aguarda o input de scan aparecer — sinaliza que a página está pronta
    page.get_by_placeholder("Escaneie ou digite o Serial da ONU").wait_for(
        state="visible", timeout=15000
    )


def is_session_alive(page: Page) -> bool:
    """Verifica se ainda está logado (não foi redirecionado para /login)."""
    return "/login" not in page.url.lower()


import re
import time


def _icon_type(class_attr: str) -> str:
    """Extrai o tipo do ícone (warning/success/error/info/question) da classe."""
    for t in ("warning", "success", "error", "info", "question"):
        if f"swal2-{t}" in class_attr:
            return t
    return "unknown"


def scan_serial(page: Page, serial: str, timeout_ms: int = 20000) -> ScanResult:
    """Digita o serial no campo de scan e captura o(s) retorno(s).

    Captura uma SEQUÊNCIA de popups (pode ter "Aguarde..." seguido do resultado).
    Retorna o popup mais informativo (último não-loading, ou o único).

    Levanta:
        TimeoutError — se nenhum retorno aparecer
        RuntimeError — se a sessão tiver expirado
    """
    if not is_session_alive(page):
        raise RuntimeError("Sessão expirada — necessário relogar")

    input_locator = page.get_by_placeholder("Escaneie ou digite o Serial da ONU")
    input_locator.click()
    input_locator.fill("")
    input_locator.fill(serial)
    input_locator.press("Enter")

    # Aguarda o primeiro popup aparecer
    popup_selector = ".swal2-popup"
    try:
        page.wait_for_selector(popup_selector, timeout=timeout_ms, state="visible")
    except PlaywrightTimeoutError:
        raise TimeoutError(f"Nenhum retorno apareceu para serial {serial} em {timeout_ms}ms")

    # Captura sequência de popups (texto único + ícone) durante até timeout_ms
    captures: list[tuple[str, str, str]] = []  # (text, icon_type, html)
    seen_texts: set[str] = set()
    t_end = time.time() + (timeout_ms / 1000.0)

    while time.time() < t_end:
        try:
            popup = page.locator(popup_selector).first
            if popup.is_visible(timeout=300):
                text = popup.inner_text().strip()
                if text and text not in seen_texts:
                    seen_texts.add(text)
                    icon_class = popup.evaluate(
                        "el => { const i = el.querySelector('.swal2-icon'); return i ? i.className : ''; }"
                    )
                    html = popup.evaluate("el => el.outerHTML")
                    captures.append((text, _icon_type(icon_class), html))
            else:
                # popup sumiu — se já capturou algo, podemos sair cedo
                if captures:
                    break
        except Exception:
            pass
        page.wait_for_timeout(300)

    if not captures:
        raise TimeoutError(f"Popup apareceu mas texto não foi capturado para serial {serial}")

    # Escolhe o popup mais informativo: o último que NÃO é só "Aguarde..."
    chosen_idx = len(captures) - 1
    for idx in range(len(captures) - 1, -1, -1):
        text_lower = captures[idx][0].lower()
        if "aguarde" not in text_lower or "encerrando" in text_lower or "atendimento" in text_lower:
            chosen_idx = idx
            break

    final_text, final_icon, final_html = captures[chosen_idx]
    # Limpa o texto: remove "!" / "i" inicial (ícone), normaliza quebras
    cleaned = re.sub(r"^[!i\?\s]+\n", "", final_text).strip()

    # Tenta extrair número de atendimento (4+ dígitos)
    match = re.search(r"atendimento\s+(\d{4,})", cleaned, re.IGNORECASE)
    if not match:
        match = re.search(r"\b(\d{6,})\b", cleaned)
    detalhe = match.group(1) if match else None

    # Aguarda popup sumir antes de retornar (evita interferência no próximo scan)
    try:
        page.wait_for_selector(popup_selector, state="hidden", timeout=10000)
    except Exception:
        pass

    return ScanResult(
        status=f"[{final_icon}] {cleaned}",
        detalhe=detalhe,
        raw_html=final_html,
    )
