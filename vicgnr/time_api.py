from __future__ import annotations

from datetime import datetime
import requests


def get_current_time(timezone = "Europe/Moscow"):
    url = f"https://time.now/developer/api/timezone/{timezone}"

    try:
        response = requests.get(url, timeout=2)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None

    a = data.get("datetime")

    return _frm_dt(a) if a else None


def _frm_dt(raw):
    try:
        s = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except:
        return 'Error'  

    return s.strftime("%d.%m.%Y %H:%M:%S")
