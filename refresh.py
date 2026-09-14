from app import fetch_all_feeds
import sys, os, datetime

LOG = os.path.join(os.path.dirname(os.path.abspath(__file__)), "refresh.log")

def log(msg):
    line = f"{datetime.datetime.now().isoformat()} - {msg}"
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(line + "\n")
    print(line)

try:
    n = fetch_all_feeds()
    log(f"refresh OK: processed {n} rows")
except Exception as e:
    log(f"refresh FAILED: {type(e).__name__}: {e}")
    raise

