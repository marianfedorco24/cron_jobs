from datetime import datetime
from zoneinfo import ZoneInfo
from dotenv import load_dotenv
import os, sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

LOG_PATH = "/root/projects/cron_jobs/db_cleanup.log"
STRAVA_API_DB_PATH = "/root/projects/hosting/API/strava_api/strava_api_cache.db"
SKOLAONLINE_API_DB_PATH = "/root/projects/hosting/API/skolaonline_api/skolaonline_api_cache.db"

def get_db(db_path):
    conn = sqlite3.connect(db_path, timeout=5)
    conn.row_factory = sqlite3.Row
    return conn

def get_current_timestamp():
    return int(datetime.now(ZoneInfo("Europe/Prague")).timestamp())

def main():
    # Connect to Strava API database and delete all entries
    strava_conn = get_db(STRAVA_API_DB_PATH)
    strava_rows_affected = 0
    try:
        strava_c = strava_conn.cursor()
        strava_c.execute("DELETE FROM cached_meals")
        strava_conn.commit()
        strava_rows_affected = strava_c.rowcount
    finally:
        strava_conn.close()

    # Connect to SkolaOnline API database and delete old entries
    skolaonline_conn = get_db(SKOLAONLINE_API_DB_PATH)
    skolaonline_rows_affected = 0
    try:
        skolaonline_c = skolaonline_conn.cursor()
        skolaonline_c.execute("DELETE FROM cached_classes WHERE timestamp < ?", (get_current_timestamp(),))
        skolaonline_conn.commit()
        skolaonline_rows_affected = skolaonline_c.rowcount
    finally:
        skolaonline_conn.close()

    with open(LOG_PATH, "a") as f:
        f.write(f"Job ran at {datetime.now()}\nStrava rows deleted: {strava_rows_affected}\nSkolaOnline rows deleted: {skolaonline_rows_affected}\n\n")

if __name__ == "__main__":
    main()