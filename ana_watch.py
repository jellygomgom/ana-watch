import os
import requests
from playwright.sync_api import sync_playwright

URL = "https://ana-blue-hangar-tour.resv.jp/reserve/calendar.php?x=1776780510"

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

TARGET_DATE_TEXTS = ["2025/05/21", "2025-05-21", "5/21", "05/21"]
TARGET_TIME_TEXT = "13:00"


def send_telegram(msg: str) -> None:
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    requests.post(url, data=data, timeout=20).raise_for_status()


def check_target_slot() -> bool:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle")
        page.wait_for_timeout(3000)

        content = page.content()
        page_text = page.locator("body").inner_text()

        browser.close()

    # 1) 페이지에 목표 시간 자체가 없으면 일단 False
    if TARGET_TIME_TEXT not in page_text:
        return False

    # 2) 날짜 텍스트 후보 중 하나라도 페이지에 있어야 함
    if not any(date_text in page_text for date_text in TARGET_DATE_TEXTS):
        return False

    # 3) 가장 단순한 1차 판정:
    #    페이지 전체가 아니라, 목표 날짜/시간이 있는 경우에만
    #    '満席'가 전부인 상황인지 대략 걸러냄
    #
    #    주의: 사이트 구조상 이 부분은 완벽하지 않을 수 있음.
    #    하지만 기존 "페이지 전체에 満席 없으면 알림"보다 훨씬 좁혀집니다.

    # 더 보수적으로: 날짜/시간이 보이는데 '空き' 또는 예약 가능 계열 단어가 있을 때만 알림
    positive_keywords = ["空き", "予約", "予約可", "残"]
    has_positive = any(k in page_text for k in positive_keywords)

    if not has_positive:
        return False

    # 목표 슬롯 주변 문맥이 필요하지만 HTML 구조를 아직 모르는 상태라
    # 우선은 날짜+시간+긍정 키워드 동시 존재 시 True로 판단
    return True


def main() -> None:
    print("ANA 투어 특정 슬롯 체크 시작: 2025-05-21 13:00")

    available = check_target_slot()

    if available:
        print("목표 슬롯 발견")
        send_telegram("🚨 ANA 투어 2025-05-21 13:00 슬롯 빈자리 발견!")
    else:
        print("목표 슬롯 없음")


if __name__ == "__main__":
    main()
