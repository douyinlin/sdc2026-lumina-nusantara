"""Test an existing web app, without building or starting a local app server.

Defaults to the public Streamlit site. Supply --url for an existing Replit
Preview or branch preview. The public site changes only after its branch is
deployed; testing it is not proof that an unmerged PR is deployed.
"""
import argparse
import json
import re
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
    # The migrated iframe still executes the repository's static particle script.
    expect(app.frame_locator('iframe[title="st.iframe"]').locator("canvas")).to_have_count(1)
    app.get_by_role("button", name=t["p1_btn"], exact=True).click(timeout=30000)
    settle(app)
    healthy(app, t)
    expect(app.get_by_role("button", name=t["continue"], exact=True)).to_be_disabled()
    # Exercise the new field control and weekly-hours input in a real browser.
    app.get_by_role("combobox", name=t["target_field"], exact=True).click()
    app.get_by_role("option", name="Computer Science", exact=True).click()
    settle(app)
    app.get_by_role("spinbutton", name=t["q_hours"], exact=True).fill("16")
    app.get_by_role("spinbutton", name=t["q_hours"], exact=True).press("Enter")
    settle(app)
    page.screenshot(path=str(args.output / "intake.png"), full_page=True)
    app.locator('input[type="file"]').set_input_files(ROOT / "data/sample_cv.txt")
    expect(app.get_by_role("button", name=t["continue"], exact=True)).to_be_enabled()
    settle(app)
    def synthetic_upload(contents):
        app.locator('input[type="file"]').set_input_files({"name": "same-name.txt", "mimeType": "text/plain", "buffer": contents})
        settle(app)

    def choose_excel():
        app.get_by_role("textbox", name=t["skill_search"], exact=True).fill("Excel")
        app.get_by_role("textbox", name=t["skill_search"], exact=True).press("Enter")
        settle(app)
        app.get_by_role("combobox", name=t["skill_search_results"], exact=True).click()
        app.get_by_role("combobox", name=t["skill_search_results"], exact=True).press("ArrowDown")
        app.get_by_role("listbox").get_by_text("Excel / spreadsheets", exact=True).click()
        app.get_by_text(t["draft_note"], exact=True).click()
        settle(app)
        app.get_by_role("button", name=t["use_skills"], exact=True).click()
        settle(app)
        expect(app.locator(".srui-chips").first.locator(".srui-chip")).to_have_text([re.compile("excel", re.I)])

    synthetic_upload(b"Fictional profile: SQL")
    choose_excel()
    app.get_by_role("spinbutton", name=t["q_hours"], exact=True).fill("12")
    app.get_by_role("spinbutton", name=t["q_hours"], exact=True).press("Enter")
    settle(app)
    expect(app.locator(".srui-chips").first.locator(".srui-chip")).to_have_text([re.compile("excel", re.I)])
    app.get_by_role("button", name=t["clear_skills"], exact=True).click()
    settle(app)
    expect(app.get_by_role("button", name=t["continue"], exact=True)).to_be_disabled()
    app.get_by_role("spinbutton", name=t["q_hours"], exact=True).fill("10")
    app.get_by_role("spinbutton", name=t["q_hours"], exact=True).press("Enter")
    settle(app)
    expect(app.get_by_role("button", name=t["continue"], exact=True)).to_be_disabled()
    synthetic_upload(b"Fictional profile: Python")
    expect(app.locator(".srui-chips").first.locator(".srui-chip")).to_have_text([re.compile("python", re.I)])
    synthetic_upload(b"Fictional profile: SQL")
    choose_excel()
    app.get_by_role("button", name=t["continue"], exact=True).click()
    expect(app.get_by_role("heading", name=t["p3"], exact=True)).to_be_visible(timeout=45000)
    settle(app)
    healthy(app, t)
    expect(app.locator(".srui-chips").first.locator(".srui-chip")).to_have_text([re.compile("excel", re.I)])
    # A missing matplotlib dependency previously hid this chart silently.
    expect(app.locator('[data-testid="stImage"] img').first).to_be_visible()
    page.screenshot(path=str(args.output / "results.png"), full_page=True)
    app.get_by_text(t["src_jobstreet"], exact=True).first.click()
    settle(app)
    healthy(app, t)
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
                                 "target field", "weekly hours", "edited synthetic skills", "manual override after upload", "clear with upload retained", "same filename new content", "source switch", "scenario switch", "SDG toggle", "particle iframe", "DOSM chart", "mobile capture"],
                      "page_errors": errors, "output": str(args.output)}))
