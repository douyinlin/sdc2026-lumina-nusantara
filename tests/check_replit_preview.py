"""Acceptance against an already-running proxied Preview; synthetic CVs only."""
import argparse
import json
from pathlib import Path
import shutil
import sys

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.i18n import T


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--browser", default=shutil.which("chromium"))
    parser.add_argument("--output", type=Path, default=ROOT / "generated-artifacts/replit-acceptance")
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    expect.set_options(timeout=30000)
    report = {"url": args.url, "checks": [], "page_errors": [], "websocket_frames": 0}

    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=args.browser, args=["--no-sandbox"])

        def opened(socket):
            if "/_stcore/stream" in socket.url:
                socket.on("framereceived", lambda _: report.update(
                    websocket_frames=report["websocket_frames"] + 1))

        def healthy(page):
            expect(page.locator('[data-testid="stException"]')).to_have_count(0)
            expect(page.locator('[data-testid="stApp"]')).to_have_attribute(
                "data-test-script-state", "notRunning", timeout=45000)

        def capture(page, name):
            healthy(page)
            page.wait_for_timeout(600)
            page.screenshot(path=str(args.output / f"{name}.png"), full_page=True)

        def landing(lang):
            page = browser.new_page(viewport={"width": 1440, "height": 1100},
                                    reduced_motion="reduce")
            page.on("pageerror", lambda error: report["page_errors"].append(str(error)))
            page.on("websocket", opened)
            response = page.goto(args.url, wait_until="domcontentloaded")
            assert response.status == 200, response.status
            page.locator(".sr-scene-cta").click()
            selector = page.get_by_role("combobox", name="Language / Bahasa / 语言", exact=True)
            expect(selector).to_be_visible(timeout=45000)
            selector.click()
            page.get_by_role("option", name={
                "en": "English", "ms": "Bahasa Malaysia", "zh": "中文"
            }[lang], exact=True).click()
            expect(page.get_by_role("button", name=T(lang)["p1_btn"], exact=True)).to_be_visible()
            return page

        try:
            for lang in ("en", "ms", "zh"):
                t = T(lang)
                page = landing(lang)
                capture(page, f"landing-{lang}")
                report["checks"].append(f"landing-{lang}")
                page.get_by_role("button", name=t["p1_btn"], exact=True).click()
                expect(page.get_by_role("button", name=t["continue"], exact=True)).to_be_disabled()
                page.locator('input[type="file"]').set_input_files({
                    "name": "fictional-profile.txt", "mimeType": "text/plain",
                    "buffer": b"Fictional profile for software testing: SQL Python Excel communication",
                })
                proceed = page.get_by_role("button", name=t["continue"], exact=True)
                expect(proceed).to_be_enabled()
                capture(page, f"intake-{lang}")
                proceed.click()
                expect(page.get_by_role("heading", name=t["p3"], exact=True)).to_be_visible()
                expect(page.locator(".srui-score").first).to_be_visible()
                expect(page.locator(".srui-path").first).to_be_visible()
                expect(page.locator('[data-testid="stImage"] img').first).to_be_visible()
                capture(page, f"results-{lang}")
                page.get_by_role("button", name="▸ " + t["sdg_open_btn"], exact=True).click()
                expect(page.get_by_role("button", name="▾ " + t["sdg_open_btn"], exact=True)).to_be_visible()
                expect(page.get_by_text(t["sdg_wheel_caption"], exact=True)).to_be_visible()
                capture(page, f"sdg-{lang}")
                page.get_by_role("button", name="▾ " + t["sdg_open_btn"], exact=True).click()
                expect(page.get_by_role("button", name="▸ " + t["sdg_open_btn"], exact=True)).to_be_visible()
                report["checks"].append(f"synthetic-CV-results-learning-DOSM-SDG-{lang}")
                page.close()
            for persona, action in (("p2_btn", "analyse"), ("p3_btn", "cc_run")):
                t = T("en")
                page = landing("en")
                page.get_by_role("button", name=t[persona], exact=True).click()
                page.get_by_role("button", name=t[action], exact=True).click()
                expect(page.locator('[data-testid="stMetric"]').first).to_be_visible()
                capture(page, persona)
                report["checks"].append(persona + "-intake-results")
                page.close()
            assert report["websocket_frames"] > 0, "No Streamlit WebSocket frames received"
            assert not report["page_errors"], report["page_errors"]
            report["passed"] = True
        finally:
            browser.close()
            (args.output / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2))
            print(json.dumps(report, ensure_ascii=False))


if __name__ == "__main__":
    main()
