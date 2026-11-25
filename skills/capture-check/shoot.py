"""PC·모바일 전체 화면 캡처 + 한 장 비교 이미지.

사용: python shoot.py <URL 또는 html 경로> <출력 폴더> [--widths 1440,390,360] [--wait 1500]
출력: <이름>_<폭>.png 들과 <이름>_비교.png, 폭마다 가로 넘침 여부를 출력.
"""
import argparse
import os
import re
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont
from playwright.sync_api import sync_playwright

MOBILE = {"is_mobile": True, "has_touch": True, "device_scale_factor": 2}


def slug(target):
    name = Path(target).stem if os.path.exists(target) else re.sub(r"^https?://", "", target)
    return re.sub(r"[^\w가-힣.-]+", "_", name).strip("_")[:60] or "page"


def shoot(target, out, widths, wait):
    url = Path(target).resolve().as_uri() if os.path.exists(target) else target
    out.mkdir(parents=True, exist_ok=True)
    base, files = slug(target), []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for w in widths:
            opts = {"viewport": {"width": w, "height": 900 if w > 500 else 800}}
            if w <= 500:
                opts.update(MOBILE)
            page = browser.new_context(**opts).new_page()
            page.goto(url, wait_until="networkidle", timeout=60000)
            page.wait_for_timeout(wait)
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(800)
            page.evaluate("window.scrollTo(0, 0)")
            overflow = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
            path = out / f"{base}_{w}.png"
            page.screenshot(path=str(path), full_page=True)
            files.append((w, path))
            print(f"{w}px: {path}" + (f"  가로 넘침 {overflow}px" if overflow > 0 else ""))
        browser.close()
    return base, files


def sheet(base, files, out, max_h=6000):
    cols = []
    for w, path in files:
        col_w = 900 if w > 500 else 420
        im = Image.open(path)
        im = im.resize((col_w, int(im.height * col_w / im.width)))
        cols.append((w, im.crop((0, 0, col_w, min(im.height, max_h)))))
    gap, head = 24, 48
    H = max(im.height for _, im in cols) + head
    canvas = Image.new("RGB", (sum(im.width + gap for _, im in cols) + gap, H + gap), "#F2F3F5")
    draw = ImageDraw.Draw(canvas)
    try:
        font = ImageFont.truetype("malgun.ttf", 22)
    except OSError:
        font = ImageFont.load_default()
    x = gap
    for w, im in cols:
        draw.text((x, 12), f"{w}px", fill="#363739", font=font)
        canvas.paste(im, (x, head))
        x += im.width + gap
    path = out / f"{base}_비교.png"
    canvas.save(path)
    print(f"비교: {path}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("out")
    ap.add_argument("--widths", default="1440,390,360")
    ap.add_argument("--wait", type=int, default=1500)
    a = ap.parse_args()
    out = Path(a.out)
    base, files = shoot(a.target, out, [int(x) for x in a.widths.split(",")], a.wait)
    sheet(base, files, out)


if __name__ == "__main__":
    main()
