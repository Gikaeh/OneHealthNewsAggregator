import os
import json
import time
import datetime
import requests
from dotenv import load_dotenv

load_dotenv()

NTFY_TOPIC = os.getenv("NTFY_TOPIC", "alert").strip()
NTFY_BASE_URL = os.getenv("NTFY_BASE_URL", "https://ntfy.sh").strip()
NTFY_URL = f"{NTFY_BASE_URL}/{NTFY_TOPIC}"
ALERTS_PATH = os.getenv("ALERTS_PATH", "scrapers/promed_output.html").strip()
PROMED_URL = os.getenv("PROMED_URL", "https://www.promedmail.org/").strip()

def send_alert(alert: dict):
    title = alert["Title"]
    locations = ", ".join(alert["Location"]) or "Unknown"
    diseases = ", ".join(alert["Disease"]) or "Unknown"
    species = ", ".join(alert["Species"]) or "Unknown"
    summary = alert.get("Summary") or "No summary available."

    message = f"📍 {locations}\n🦠 {diseases} | {species}\n\n{summary}"

    safe_title = title.encode("ascii", errors="ignore").decode("ascii").strip()

    requests.post(
        NTFY_URL,
        data=message.encode("utf-8"),
        headers={
            "Title": safe_title,
            "Actions": f"view, View on ProMED, {PROMED_URL}, clear=true",
        },
    )


def send_summary(count: int):
    date_str = datetime.date.today().strftime("%Y-%m-%d")
    requests.post(
        NTFY_URL,
        data=f"{count} alert(s) sent.".encode("utf-8"),
        headers={"Title": f"ProMED Daily Digest - {date_str}"},
    )


def main():
    with open(ALERTS_PATH, encoding="utf-8") as f:
        alerts = json.load(f)

    if isinstance(alerts, str):
        requests.post(NTFY_URL, data=alerts.encode("utf-8"), headers={"Title": "ProMED - No Alerts"})
        return

    for alert in reversed(alerts):
        send_alert(alert)
        time.sleep(0.5)

    send_summary(len(alerts))


if __name__ == "__main__":
    main()