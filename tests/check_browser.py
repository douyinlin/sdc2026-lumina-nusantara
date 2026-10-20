"""Run against a temporary local server using an installed Chrome."""
import json
import argparse
from pathlib import Path
from playwright.sync_api import sync_playwright, expect

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--url", default="http://127.0.0.1:8501")
parser.add_argument("--output", type=Path, default=Path("test-results/browser"))
args = parser.parse_args()
OUT = args.output
OUT.mkdir(parents=True, exist_ok=True)
with sync_playwright() as p:
    browser = p.chromium.launch(channel="chrome", headless=True)
    page = browser.new_page(viewport={"width": 1440, "height": 1800})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(args.url, wait_until="networkidle")
    expect(page.get_by_role("heading", name="SkillRadar MY · 第一版")).to_be_visible(timeout=30000)
    metrics = page.locator('[data-testid="stMetricValue"]')
    expect(metrics).to_have_text(["25.0%", "66.7%", "0.0%"])
    page.screenshot(path=str(OUT / "default.png"), full_page=True)
    combo = page.get_by_role("combobox").last
    combo.click()
    page.get_by_role("option", name="SQL", exact=True).click()
    page.keyboard.press("Escape")
    expect(metrics).to_have_text(["50.0%", "66.7%", "33.3%"])
    page.screenshot(path=str(OUT / "sql-added.png"), full_page=True)
    # Clear through the actual widget, without changing server session state.
    page.get_by_role("button", name="Clear all", exact=True).click()
    expect(metrics).to_have_text(["0.0%", "0.0%", "0.0%"])
    expect(page.get_by_text("尚未选择技能：三个岗位的技能覆盖率均为 0%。", exact=True)).to_be_visible()
    page.screenshot(path=str(OUT / "empty.png"), full_page=True)
    # Smoke check the retained experiment in all languages and both scenarios.
    page.get_by_text("显示旧版实验功能 / Show experimental features", exact=True).click()
    expect(page.get_by_role("heading", name="📡 SkillRadar MY", exact=True)).to_be_visible()
    expect(page.locator('[data-testid="stException"]')).to_have_count(0)
    lang = page.get_by_role("combobox", name="Language / Bahasa / 语言", exact=True)
    lang.click()
    page.get_by_role("option", name="中文", exact=True).click()
    expect(page.get_by_text("未来岗位排名", exact=True)).to_be_visible()
    page.get_by_text("快速冲击", exact=True).click()
    expect(page.locator('[data-testid="stException"]')).to_have_count(0)
    lang.click()
    page.get_by_role("option", name="Bahasa Malaysia", exact=True).click()
    expect(page.locator('[data-testid="stException"]')).to_have_count(0)
    browser.close()
    assert not errors, errors
print(json.dumps({"browser": "Chrome headless", "default": [25, 66.7, 0], "sql_added": [50, 66.7, 33.3], "empty": [0, 0, 0], "page_errors": errors, "screenshots": str(OUT)}))
