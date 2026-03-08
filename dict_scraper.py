from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from bs4 import BeautifulSoup
import time

def bypass_cloudflare():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = browser.new_page()
        stealth_sync(page)
        page.goto("https://dict.gov.ph/", wait_until="domcontentloaded")
        time.sleep(16)
        

        print("success")
        html_string = page.content()
        browser.close()

if __name__ == "__main__":
    bypass_cloudflare()
