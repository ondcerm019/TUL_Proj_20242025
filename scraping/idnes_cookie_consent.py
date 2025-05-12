"""
Module to save cookies from iDNES after accepting the cookie consent.
"""

import json
from playwright.sync_api import sync_playwright

def save_idnes_cookies(cookie_file_path: str) -> None:
    """
    Launches a browser, accepts cookies on iDNES, and saves them to a JSON file.

    :cookie_file_path: Path to the file where cookies will be saved.
    """
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto("https://www.idnes.cz/nastaveni-souhlasu?url=https%3a%2f%2fwww.idnes.cz%2fzpravy")

        page.wait_for_selector('a.btn-cons.contentwall_ok')
        page.click('a.btn-cons.contentwall_ok')

        page.wait_for_load_state('load')

        cookies = page.context.cookies()

        with open(cookie_file_path, 'w', encoding='utf-8') as f:
            json.dump(cookies, f, indent=4)

        print(f"Cookies saved to '{cookie_file_path}'.")

        browser.close()


if __name__ == "__main__":
    save_idnes_cookies(r"") # <Cesta pro uložení cookies json souboru>
