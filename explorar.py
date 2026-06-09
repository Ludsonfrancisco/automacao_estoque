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

        # Aguarda o modal "Aguarde... Carregando atendimentos" sumir, se houver
        try:
            page.locator(".swal2-popup, [role='dialog']").first.wait_for(
                state="hidden", timeout=30000
            )
        except Exception:
            pass

        page.screenshot(path=str(out_dir / "00-inicial.png"), full_page=False)
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
                page.screenshot(path=str(out_dir / f"{i:02d}-{serial}-erro.png"), full_page=False)
                continue

            # Captura SEQUÊNCIA de alertas durante 20s (loading -> resultado final)
            import time
            captures: list[dict] = []
            seen_texts: set[str] = set()
            t_end = time.time() + 20
            while time.time() < t_end:
                try:
                    popup = page.locator(".swal2-popup").first
                    if popup.is_visible(timeout=500):
                        text = popup.inner_text()
                        if text and text not in seen_texts:
                            seen_texts.add(text)
                            icon_classes = popup.evaluate(
                                "el => Array.from(el.querySelectorAll('.swal2-icon')).map(i => i.className).join('|')"
                            )
                            html = popup.evaluate("el => el.outerHTML")
                            captures.append({"text": text, "icon": icon_classes, "html": html})
                            print(f"[explorar] popup #{len(captures)}: icone={icon_classes!r} texto={text[:120]!r}")
                except Exception:
                    pass
                page.wait_for_timeout(300)

            page.screenshot(path=str(out_dir / f"{i:02d}-{serial}.png"), full_page=False)
            (out_dir / f"{i:02d}-{serial}.html").write_text(page.content(), encoding="utf-8")

            # Salva todas as capturas
            with (out_dir / f"{i:02d}-{serial}-RETORNOS.txt").open("w", encoding="utf-8") as f:
                for j, c in enumerate(captures, 1):
                    f.write(f"=== popup {j} ===\n")
                    f.write(f"icon: {c['icon']}\n")
                    f.write(f"text:\n{c['text']}\n\n")
                    f.write(f"html:\n{c['html']}\n\n{'-'*60}\n")

        input("\n[explorar] Pressione Enter para fechar o browser...")
        browser.close()

    print(f"\n[explorar] DONE. Verifique {out_dir}")
    return 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python explorar.py SERIAL1 [SERIAL2 ...]", file=sys.stderr)
        sys.exit(2)
    sys.exit(main(sys.argv[1:]))
