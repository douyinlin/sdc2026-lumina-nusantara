"""Test an existing web app, without building or starting a local app server.

Defaults to the public Streamlit site. Supply --url for an existing Replit
Preview or branch preview. The public site changes only after its branch is
deployed; testing it is not proof that an unmerged PR is deployed.
"""
import argparse
import json
from pathlib import Path
import shutil
import sys

from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.i18n import T

parser = argparse.ArgumentParser()
parser.add_argument("--url", default="https://sdc2026-lumina-nusantara-65cnugvuxdle5dgp9ky3fs.streamlit.app")
parser.add_argument("--browser", default=shutil.which("chromium"))
parser.add_argument("--output", type=Path, default=Path("/tmp/skillradar-web-check"))
args = parser.parse_args()
args.output.mkdir(parents=True, exist_ok=True)
expect.set_options(timeout=20000)


def settle(app):
    app.wait_for_timeout(200)
    expect(app.locator('[data-testid="stApp"]')).to_have_attribute(
        "data-test-script-state", "notRunning", timeout=45000
    )


def healthy(app, text):
    expect(app.locator('[data-testid="stException"]')).to_have_count(0)
    expect(app.get_by_text(text["error"], exact=True)).not_to_be_visible()


with sync_playwright() as playwright:
    browser = playwright.chromium.launch(
        executable_path=args.browser, args=["--no-sandbox"], headless=True
    )
    page = browser.new_page(viewport={"width": 1440, "height": 1000})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(args.url, wait_until="domcontentloaded", timeout=30000)
    # Community Cloud hosts the actual Streamlit application inside this iframe.
    if ".streamlit.app" in args.url:
        host = page.wait_for_selector('iframe[src*="/~/"]', timeout=20000)
        app = host.content_frame()
    else:
        app = page
    t = T("en")
    app.get_by_role("button", name=t["p1_btn"], exact=True).click(timeout=30000)
    settle(app)
    healthy(app, t)
    expect(app.get_by_role("button", name=t["continue"], exact=True)).to_be_disabled()
    page.screenshot(path=str(args.output / "intake.png"), full_page=True)
    app.locator('input[type="file"]').set_input_files(ROOT / "data/sample_cv.txt")
    expect(app.get_by_role("button", name=t["continue"], exact=True)).to_be_enabled()
    settle(app)
    app.get_by_role("button", name=t["continue"], exact=True).click()
    expect(app.get_by_role("heading", name=t["p3"], exact=True)).to_be_visible(timeout=45000)
    settle(app)
    healthy(app, t)
    page.screenshot(path=str(args.output / "results.png"), full_page=True)
    app.get_by_text(t["fast"], exact=True).click()
    settle(app)
    healthy(app, t)
    app.get_by_role("button", name="▸ " + t["sdg_open_btn"], exact=True).click()
    settle(app)
    expect(app.get_by_text(t["sdg_wheel_caption"], exact=True)).to_be_visible()
    page.set_viewport_size({"width": 390, "height": 844})
    page.emulate_media(reduced_motion="reduce")
    page.screenshot(path=str(args.output / "mobile.png"), full_page=True)
    browser.close()
    assert not errors, errors
    print(json.dumps({"tested_url": args.url, "flow": "worker",
                      "checks": ["empty profile", "synthetic CV", "results",
                                 "scenario switch", "SDG toggle", "mobile capture"],
                      "page_errors": errors, "output": str(args.output)}))
