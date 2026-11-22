"""Run after npm run build. Uses a fresh test database and browser profile."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import urlopen
from urllib.error import HTTPError
from urllib.request import Request
from playwright.sync_api import sync_playwright, expect

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from test_materials import pdf
import json

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / "docs" / "evidence"


def start(db):
    p = subprocess.Popen(
        [sys.executable, "-u", str(ROOT / "server.py"), "--port", "0"],
        cwd=ROOT,
        env={**os.environ, "ZHIXU_DB": str(db), "PYTHONIOENCODING": "utf-8"},
        stdout=subprocess.PIPE,
        encoding="utf-8",
    )
    url = p.stdout.readline().strip().split()[-1]
    with urlopen(url + "/api/state") as resp:
        assert resp.status == 200
    return p, url


def run():
    with tempfile.TemporaryDirectory() as folder, sync_playwright() as driver:
        work = Path(folder)
        (work / "Original-Taylor.pdf").write_bytes(pdf())
        p, url = start(work / "store.db")
        chromium = shutil.which("chromium") or shutil.which("google-chrome")
        try:
            browser = driver.chromium.launch(
                executable_path=chromium, args=["--disable-dev-shm-usage"]
            )
            page = browser.new_page(
                viewport={"width": 1440, "height": 960}, device_scale_factor=1
            )
            errors = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(url)
            expect(page.get_by_role("heading", name="学习总览")).to_be_visible()
            page.evaluate("document.fonts.ready")
            page.screenshot(path=EVIDENCE / "dashboard.png", full_page=True)
            page.get_by_role("link", name="资料库", exact=True).click()
            page.locator("#upload input").set_input_files(work / "Original-Taylor.pdf")
            page.get_by_role("button", name="导入资料").click()
            expect(
                page.get_by_text("Taylor polynomial near zero", exact=True).first
            ).to_be_visible()
            expect(page.get_by_text("原文命中「Taylor」", exact=False)).to_be_visible()
            print(
                "PASS PDF import, visible excerpt, page anchor and course association"
            )
            page.get_by_role("link", name="按此资料优先诊断").click()
            expect(
                page.get_by_text("写出零点处三阶泰勒多项式", exact=False)
            ).to_be_visible()
            expect(
                page.get_by_role("link", name="Original-Taylor.pdf · 第 1 页")
            ).to_be_visible()
            print("PASS source-prioritized diagnostic includes original page citation")
            page.get_by_role("link", name="诊断测试", exact=True).click()
            answers = [
                "1",
                "0",
                "2",
                "4",
                "2*x+2",
                "1/50",
                "1",
                "1/2",
                "x-x^2/2+x^3/3",
                "2",
            ]
            for i, a in enumerate(answers):
                page.locator("#hint").click()
                page.locator("#hint").click()
                if i in (6, 9):
                    page.locator(f'input[value="{a}"]').check()
                else:
                    page.locator("input[name=answer]").fill(a)
                page.get_by_role("button", name="提交答案").click()
                expect(
                    page.get_by_role(
                        "heading", name="这一步需要再检查" if i == 1 else "回答正确"
                    )
                ).to_be_visible()
                if i == 1:
                    expect(
                        page.get_by_text("建议排查 · 忽略相消后的高阶项")
                    ).to_be_visible()
                page.locator("#next").click()
            expect(page.get_by_role("heading", name="诊断报告")).to_be_visible()
            print(
                "PASS 10 diagnostic submissions, progressive hints, cancellation mistake and report"
            )
            page.get_by_role("link", name="查看错题与复习").click()
            page.get_by_role("link", name="回看前置知识").click()
            expect(page.get_by_role("heading", name="函数极限")).to_be_visible()
            page.get_by_role("link", name="错题与复习", exact=True).click()
            page.get_by_role("link", name="重做这道题").click()
            page.locator("input[name=answer]").fill("-1/6")
            page.get_by_role("button", name="提交答案").click()
            page.locator("#next").click()
            expect(page.get_by_text("下次巩固", exact=False)).to_be_visible()
            page.screenshot(path=EVIDENCE / "review.png", full_page=True)
            page.get_by_role("link", name="个人进度").click()
            with page.expect_download() as download:
                page.get_by_role("button", name="导出 JSON").click()
            backup = work / "backup.json"
            download.value.save_as(backup)
            assert len(json.loads(backup.read_bytes())["attempts"]) == 11
            p.terminate()
            p.wait(timeout=10)
            p, url = start(work / "store.db")
            page.goto(url + "/#progress")
            expect(page.get_by_text("复习 · 正确", exact=False)).to_be_visible()
            page.locator("#restore input[type=file]").set_input_files(backup)
            page.locator("#restore input[type=checkbox]").check()
            page.get_by_role("button", name="恢复进度").click()
            expect(page.get_by_text("已恢复 11 条记录")).to_be_visible()
            print(
                "PASS prerequisite lesson, retry, scheduled review, JSON round-trip and server restart"
            )
            page.goto(url + "/#library")
            (work / "scan.pdf").write_bytes(pdf(False))
            page.locator("#upload input").set_input_files(work / "scan.pdf")
            page.get_by_role("button", name="导入资料").click()
            expect(page.locator("#upload .status")).to_contain_text("OCR")
            page.locator("#upload input").set_input_files(
                ROOT / "examples" / "局部近似与相消.pdf"
            )
            page.get_by_role("button", name="导入资料").click()
            expect(
                page.get_by_role("heading", name="局部近似与相消.pdf")
            ).to_be_visible()
            page.locator("#anchor").select_option("1")
            expect(page.locator("section pre").first).to_contain_text("余项除以 x^3")
            expect(page.get_by_role("heading", name="原文回忆")).to_be_visible()
            page.screenshot(path=EVIDENCE / "source.png", full_page=True)
            page.goto(url + "/#unit/8")
            expect(
                page.get_by_role("heading", name="泰勒公式", exact=True)
            ).to_be_visible()
            expect(page.locator(".katex-error")).to_have_count(0)
            page.locator("#degree").select_option("5")
            page.screenshot(path=EVIDENCE / "lesson.png", full_page=True)
            page.get_by_role("link", name="开始单元练习").click()
            page.locator("input[name=answer]").fill("2*x-2*x^2+8*x^3/3")
            page.get_by_role("button", name="提交答案").click()
            expect(page.get_by_role("heading", name="回答正确")).to_be_visible()
            print(
                "PASS scanned-page feedback, Chinese PDF, anchored source recall, KaTeX lesson and unit practice"
            )
            page.set_viewport_size({"width": 390, "height": 844})
            page.goto(url + "/#home")
            expect(page.get_by_role("heading", name="学习总览")).to_be_visible()
            assert page.evaluate("document.documentElement.scrollWidth <= innerWidth")
            page.screenshot(path=EVIDENCE / "mobile.png", full_page=True)
            page.get_by_label("切换导航").click()
            page.get_by_role("link", name="知识图谱").click()
            expect(
                page.get_by_role("heading", name="知识图谱", exact=True)
            ).to_be_visible()
            try:
                urlopen(
                    Request(
                        url + "/api/restore",
                        b"{}",
                        headers={
                            "Origin": "https://other.invalid",
                            "Content-Type": "application/json",
                        },
                    )
                )
                raise AssertionError("cross-origin action was accepted")
            except HTTPError as e:
                assert e.code == 403
            assert not errors, errors
            print(
                "PASS mobile navigation, no horizontal overflow, cross-origin rejection, zero page errors"
            )
            browser.close()
        finally:
            p.terminate()
            p.wait(timeout=10)


if __name__ == "__main__":
    run()
