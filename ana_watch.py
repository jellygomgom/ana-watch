import os
import requests
from playwright.sync_api import sync_playwright

URL = "https://ana-blue-hangar-tour.resv.jp/reserve/calendar.php?x=1776780510"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def send_telegram(msg: str) -> None:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    requests.post(url, data=data, timeout=20).raise_for_status()


def check_slot() -> bool:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(3000)
        content = page.content()
        browser.close()

        return "満席" not in content


def main() -> None:
    print("ANA 투어 1회 체크 시작")

    available = check_slot()

    if available:
        print("자리 발견")
        send_telegram("🚨 ANA 투어 빈자리 발견!")
    else:
        print("없음")


if __name__ == "__main__":
    main()