#!/usr/bin/env python3
"""Capture Google Maps / Street View reference imagery of Knott Hall.

Drives Chromium via Playwright and writes screenshots into ref/ for
comparing the real 1896/1988 Knott Hall building against the geometry
in quake_loyola/knott_hall.py.

Usage:
    .venv/bin/python scripts/capture_knott_gmaps.py
"""

import pathlib

from playwright.sync_api import sync_playwright

# Knott Hall, 4501 N Charles St, Baltimore, MD 21210
LAT, LNG = 39.34639, -76.62222

REF = pathlib.Path(__file__).resolve().parent.parent / "ref"

# (name, url, settle_seconds)
SHOTS = [
    (
        "gmaps-kh-satellite",
        f"https://www.google.com/maps/@{LAT},{LNG},120m/data=!3m1!1e3?hl=en",
        6,
    ),
    (
        "gmaps-kh-satellite-tilt",
        f"https://www.google.com/maps/@{LAT},{LNG},250m/data=!3m1!1e3!5m1!1e4?hl=en",
        6,
    ),
    (
        "gmaps-kh-place",
        "https://www.google.com/maps/place/Knott+Hall,+4501+N+Charles+St,"
        f"+Baltimore,+MD+21210/@{LAT},{LNG},18z?hl=en",
        6,
    ),
    (
        # Legacy Street View deep-link; heading ~90deg (east toward KH face)
        "gmaps-kh-streetview-east",
        f"https://maps.google.com/maps?q=&layer=c&cbll={LAT},{LNG}"
        "&cbp=11,90,0,0,0&hl=en",
        7,
    ),
    (
        "gmaps-kh-streetview-north",
        f"https://maps.google.com/maps?q=&layer=c&cbll={LAT},{LNG}"
        "&cbp=11,0,0,0,0&hl=en",
        7,
    ),
]

CONSENT_SELECTORS = [
    "button:has-text('Accept all')",
    "button:has-text('Accept')",
    "button:has-text('I agree')",
    "button:has-text('Reject all')",
    "form[action*='consent'] button",
]


def dismiss_consent(page):
    for sel in CONSENT_SELECTORS:
        try:
            btn = page.locator(sel).first
            if btn.count() and btn.is_visible():
                btn.click(timeout=2000)
                page.wait_for_timeout(1500)
                return True
        except Exception:
            pass
    return False


def main():
    REF.mkdir(exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(
            viewport={"width": 1600, "height": 1000},
            locale="en-US",
            user_agent=(
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
        )
        page = ctx.new_page()
        for name, url, settle in SHOTS:
            print(f"→ {name}: {url}")
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=45000)
            except Exception as e:
                print(f"   goto warning: {e}")
            dismiss_consent(page)
            # let map tiles / WebGL canvas render
            page.wait_for_timeout(settle * 1000)
            out = REF / f"{name}.png"
            page.screenshot(path=str(out))
            print(f"   saved {out} ({out.stat().st_size} bytes)")
        browser.close()


if __name__ == "__main__":
    main()
