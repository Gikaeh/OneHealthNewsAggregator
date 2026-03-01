import re
import json
import requests
from bs4 import BeautifulSoup

url = "https://www.promedmail.org/"
response = requests.get(url)

soup = BeautifulSoup(response.content, "html.parser")
target_script = next(
    s for s in reversed(soup.find_all("script"))
    if "alert_id" in s.get_text()
)

raw_text = target_script.get_text()
match = re.match(r'self\.__next_f\.push\(\[1,(\".*\")\]\)$', raw_text, re.DOTALL)

if match:
    inner = json.loads(match.group(1))          
    _, _, payload = inner.partition(":")        
    data = json.loads(payload)
    alerts = data[3].get("alerts", [])
    with open("scrapers/promed_output.html", "w", encoding="utf-8") as file:
        json.dump(alerts, file, indent=2, default=str)
else:
    with open("scrapers/promed_output.html", "w", encoding="utf-8") as file:
        file.write(raw_text)