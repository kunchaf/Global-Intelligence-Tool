import functools
import re
from difflib import SequenceMatcher

import requests
import urllib3

# Suppress only the single InsecureRequestWarning from urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .api.un_projections import _resolve_location


def _similarity(a, b):
    a, b = a.lower(), b.lower()
    if a == b:
        return 1.0
    return SequenceMatcher(None, a, b).ratio()


@functools.lru_cache(maxsize=1)
def _wb_country_rows():
    url = "https://api.worldbank.org/v2/country?format=json&per_page=500"
    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()
    except requests.exceptions.SSLError:
        # Fallback for environments with strict SSL/proxy issues
        r = requests.get(url, timeout=30, verify=False)
        r.raise_for_status()
    except Exception:
        # Final fallback to prevent app crash if WB is down
        return tuple()
        
    data = r.json()
    raw = data[1] if len(data) > 1 else []
    out = []
    for c in raw:
        iso2 = (c.get("iso2Code") or "").strip().upper()
        if len(iso2) != 2 or not iso2.isalpha():
            continue
        
        # Filter out World Bank aggregates instead of checking for capitalCity,
        # which excludes real countries like Somalia.
        region = c.get("region", {})
        if isinstance(region, dict) and region.get("value") == "Aggregates":
            continue
            
        name = (c.get("name") or "").strip()
        iso3 = (c.get("id") or "").strip().upper()
        if not name:
            continue
        out.append({"iso2": iso2, "iso3": iso3, "name": name})
    return tuple(out)


def resolve_country_input(user_text):
    text = (user_text or "").strip()
    if not text:
        return {"error": "Empty country name."}

    rows = _wb_country_rows()
    upper = text.upper()
    
    # Exact Code match
    if re.fullmatch(r"[A-Z]{2}", upper):
        for r in rows:
            if r["iso2"] == upper:
                return _with_coords(r["iso2"], r["name"])
        return {"error": f"No country found for code {upper}."}

    if re.fullmatch(r"[A-Z]{3}", upper):
        for r in rows:
            if r["iso3"] == upper:
                return _with_coords(r["iso2"], r["name"])
        return {"error": f"No country found for code {upper}."}

    # Exact Name match shortcut
    for r in rows:
        if r["name"].lower() == text.lower():
            return _with_coords(r["iso2"], r["name"])

    best = []
    best_score = 0.0
    for r in rows:
        name = r["name"]
        s = max(
            _similarity(text, name),
            _similarity(text, r["iso2"]),
            _similarity(text, r["iso3"]),
        )
        # Only boost substring score if it's a very significant substring (e.g. at word boundaries)
        # to prevent "Mali" matching "Somalia". We use a simple length check.
        if text.lower() in name.lower() and len(text) >= 4:
            s = max(s, 0.72)
        elif name.lower() in text.lower() and len(name) >= 4:
            # If the user typed "Republic of Somalia", "Somalia" is in it
            s = max(s, 0.72)
            
        if s > best_score:
            best_score = s
            best = [r]
        elif s == best_score and s > 0:
            best.append(r)

    seen_iso = set()
    deduped = []
    for b in best:
        if b["iso2"] in seen_iso:
            continue
        seen_iso.add(b["iso2"])
        deduped.append(b)
    best = deduped

    if best_score < 0.55 or not best:
        return {"error": f'Could not match "{text}" to a country. Try the English name or a 2-letter ISO code.'}

    if len(best) > 1 and best_score < 0.92:
        names = ", ".join(sorted({b["name"] for b in best[:5]}))
        return {"error": f'Ambiguous name "{text}". Possibilities include: {names}. Use a clearer name or ISO code.'}

    pick = best[0]
    return _with_coords(pick["iso2"], pick["name"])


def _with_coords(iso2, display_name):
    lat = lng = None
    try:
        loc = _resolve_location(iso2)
        if loc:
            lat = loc.get("latitude")
            lng = loc.get("longitude")
            if loc.get("name"):
                display_name = loc["name"]
    except Exception:
        pass
    return {"iso2": iso2, "display_name": display_name, "latitude": lat, "longitude": lng}
