import os
import re
import json
import datetime
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

PROMED_URL = os.getenv("PROMED_URL", "https://www.promedmail.org/")
OUTPUT_PATH = os.getenv("ALERTS_PATH", "scrapers/promed_output.html")


def fetch_alerts_script(url: str) -> str:
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    target = next(
        s for s in reversed(soup.find_all("script"))
        if "alert_id" in s.get_text()
    )
    return target.get_text()


def parse_alerts(raw_text: str) -> list:
    match = re.match(r'self\.__next_f\.push\(\[1,(".*")\]\)$', raw_text, re.DOTALL)
    if not match:
        return []
    inner = json.loads(match.group(1))
    _, _, payload = inner.partition(":")
    data = json.loads(payload)
    alerts_data = next((item["alerts"] for item in data if isinstance(item, dict) and "alerts" in item), [])
    return alerts_data


def filter_todays_alerts(alerts: list, today: str) -> list:
    result = []
    for alert in alerts:
        if today not in alert["issue_date"]:
            continue
        result.append({
            "Title": alert["post_title"],
            "Location": [p["name"] for p in alert["places"]],
            "Disease": [d["name"] for d in alert["diseases"]],
            "Species": [s["name"] for s in alert["species"]],
            "Summary": alert["generated_summary"],
        })
    return result


def main():
    today = datetime.date.today().strftime("%Y-%m-%d")
    raw_text = fetch_alerts_script(PROMED_URL)
    all_alerts = parse_alerts(raw_text)

    if not all_alerts:
        output = "No data found for today"
    else:
        output = filter_todays_alerts(all_alerts, today)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, default=str)


if __name__ == "__main__":
    main()