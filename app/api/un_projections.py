import os

import requests
import urllib3

# Suppress only the single InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BASE = "https://population.un.org/dataportalapi/api/v1"


def _resolve_location(country_code):
    code = country_code.strip().upper()
    try:
        r = requests.get(f"{BASE}/locations/{code}", timeout=20)
        r.raise_for_status()
    except requests.exceptions.SSLError:
        r = requests.get(f"{BASE}/locations/{code}", timeout=20, verify=False)
        r.raise_for_status()
    rows = r.json()
    if not rows:
        return None
    return rows[0]


def _extract_projection_value(records, target_year=2030):
    if not isinstance(records, list):
        return None
    best_year = None
    best_val = None
    for row in records:
        if not isinstance(row, dict):
            continue
        year = row.get("time") or row.get("year") or row.get("TimeID")
        val = row.get("value") if "value" in row else row.get("Value")
        if year is None or val is None:
            continue
        try:
            y = int(year)
            v = float(val)
        except (TypeError, ValueError):
            continue
        if y <= target_year and (best_year is None or y > best_year):
            best_year, best_val = y, v
    return best_val


def get_un_projections(country_code):
    token = (os.environ.get("UN_API_TOKEN") or "").strip()

    try:
        loc = _resolve_location(country_code)
        if not loc:
            return {
                "source": "UN Population Division",
                "error": "Unknown location code",
            }

        out = {
            "source": "UN Population Division",
            "location_id": loc.get("id"),
            "location_name": loc.get("name"),
            "iso3": loc.get("iso3"),
            "iso2": loc.get("iso2"),
        }

        if not token:
            out["2030_projection"] = None
            out["note"] = (
                "Indicator data requires a bearer token; set UN_API_TOKEN to enable projections."
            )
            return out

        lid = loc["id"]
        data_url = (
            f"{BASE}/data/indicators/19/locations/{lid}/start/2020/end/2035"
        )
        try:
            dr = requests.get(
                data_url,
                headers={"Authorization": f"Bearer {token}"},
                timeout=25,
            )
        except requests.exceptions.SSLError:
            dr = requests.get(
                data_url,
                headers={"Authorization": f"Bearer {token}"},
                timeout=25,
                verify=False
            )
        if dr.status_code != 200:
            out["error"] = f"UN data API returned HTTP {dr.status_code}"
            return out

        records = dr.json()
        proj = _extract_projection_value(records, target_year=2030)
        out["2030_projection"] = proj
        if proj is None:
            out["note"] = "Could not parse 2030 value from UN response."
        return out
    except Exception as e:
        return {"source": "UN Population Division", "error": str(e)}