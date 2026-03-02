import subprocess
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scrapers.promed_scraper import main as scrape
from notifications.push import main as push

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CRON_JOB = (
    f'0 8 * * * cd {PROJECT_DIR} && python3 -c '
    '"from scrapers.promed_scraper import main as s; '
    'from notifications.push import main as p; s(); p()" '
    f'>> /var/log/promed.log 2>&1'
)


def install_cron():
    result = subprocess.run(["crontab", "-l"], capture_output=True, text=True)
    existing = result.stdout if result.returncode == 0 else ""

    if CRON_JOB in existing:
        print("Cron job already installed.")
        return

    new_crontab = existing.rstrip("\n") + "\n" + CRON_JOB + "\n"
    subprocess.run(["crontab", "-"], input=new_crontab, text=True, check=True)
    print(f"Cron job installed: {CRON_JOB}")

if __name__ == "__main__":
    install_cron()
