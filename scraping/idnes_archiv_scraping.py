"""
Scrapes news articles from the iDNES archive and saves them to a text file.
"""

import json
import random
import time
import re
import os

import requests
from bs4 import BeautifulSoup

from idnes_cookie_consent import save_idnes_cookies


COOKIE_FILE_PATH = r"" # <Cesta k uloženému cookies json souboru>
OUTPUT_FILE_PATH = r"" # <Cesta k souboru pro zapisování textového výstupu>
# pylint: disable=C0103


if not os.path.exists(COOKIE_FILE_PATH):
    save_idnes_cookies(COOKIE_FILE_PATH)


with open(COOKIE_FILE_PATH, 'r', encoding='utf-8') as f:
    cookies = json.load(f)

cookie_dict = {cookie['name']: cookie['value'] for cookie in cookies}

session = requests.session()
session.cookies.update(cookie_dict)

i = 0
while True:
    archiv_url = f"https://www.idnes.cz/zpravy/archiv/{i}"

    # log
    print(f"Fetching page: {archiv_url}")

    time.sleep(random.uniform(0.05, 0.15))

    try:
        response = session.get(archiv_url)
        response.raise_for_status()  # Raises an error for 4xx and 5xx responses
    except requests.RequestException as e:
        print(f"Failed to retrieve page {i}. Error: {e}")
        i += 1
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    for article_div in soup.find_all("div", class_="art"):
        a_tag = article_div.find("a", recursive=False)

        if a_tag:
            if not a_tag.find(class_="premlab"):
                article_url = a_tag.get("href")

                if article_url:
                    time.sleep(random.uniform(0.05, 0.15))

                    try:
                        article_response = session.get(article_url)
                        article_response.raise_for_status()
                    except requests.RequestException as e:
                        print(f"Skipping article {article_url} due to request error: {e}")
                        continue

                    article_soup = BeautifulSoup(article_response.text, "html.parser")

                    try:
                        headline_tag = article_soup.find("h1", class_="arttit")
                        if headline_tag:
                            headline = headline_tag.get_text(strip=True)
                        else:
                            print("Skipping article: No title found")
                            continue

                        opener_tag = article_soup.find("div", class_="opener")
                        opener = (
                            opener_tag.get_text(strip=True).replace("\n", " ") + " "
                            if opener_tag
                            else ""
                        )

                        content_list = [headline + " ", opener]

                        content_list += [
                            (p.get_text(strip=True).replace("\n", " ") + " ")
                            for p in article_soup.select("div#art-text p")
                            if p.get_text(strip=True)
                        ]

                        full_text = "".join(content_list)
                        full_text = re.sub(r'\s+', ' ', full_text).strip()

                        with open(OUTPUT_FILE_PATH, "a", encoding="utf-8") as f:
                            f.write(full_text + "\n\n")

                        print(f"\"{headline}\" article saved")

                    except (AttributeError, ValueError) as e:
                        print(f"Skipping article due to parsing error: {e}")

    i += 1
