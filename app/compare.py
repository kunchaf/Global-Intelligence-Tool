import re

from .api.scraper import get_ethnicity_placeholder, get_religious_breakdown
from .api.world_bank import fetch_country_data, fetch_indicator_latest
from .country_resolve import resolve_country_input

ALLOWED_DIMENSIONS = frozenset({"population", "religion", "ethnic", "cities", "others"})

DIM_LABELS = {
    "population": "Population",
    "religion": "Religion",
    "ethnic": "Ethnicity",
    "cities": "Cities / urbanization",
    "others": "Other indicators",
}


def _religion_cell(data):
    if not isinstance(data, dict):
        return "—"
    
    rel_data = data.get("identity", {}).get("religious_breakdown", {})
    if not rel_data:
        return "Data Unavailable"
        
    kept = []
    other_sum = 0.0
    
    for k, v in rel_data.items():
        if k == "source":
            continue
            
        # Find the first float in the string (e.g., "43.8%", "~40-43%", "<1%")
        match = re.search(r"(\d+(\.\d+)?)", v)
        if match:
            val = float(match.group(1))
            if k.lower() == "other":
                other_sum += val
            elif val >= 1.0:
                # Assign appropriate icons based on religion keyword
                icon = "🏛️"
                lower_k = k.lower()
                if "islam" in lower_k or "muslim" in lower_k: icon = "🕌"
                elif "christian" in lower_k or "catholic" in lower_k or "protestant" in lower_k or "orthodox" in lower_k: icon = "⛪"
                elif "hindu" in lower_k: icon = "🕉️"
                elif "buddhis" in lower_k: icon = "☸️"
                elif "judai" in lower_k or "jewish" in lower_k: icon = "🕍"
                elif "secular" in lower_k or "atheist" in lower_k or "unaffiliated" in lower_k: icon = "🌍"
                elif "shinto" in lower_k: icon = "⛩️"
                elif "sikh" in lower_k: icon = "🪯"
                
                # Create a clickable Wikipedia link for the religion
                link = f'<a href="https://en.wikipedia.org/wiki/{k.replace(" ", "_")}" target="_blank" style="text-decoration: none; color: #2563eb; font-weight: 500;" title="Read more about {k} on Wikipedia">{k}</a>'
                
                kept.append(f"{icon} {link} {v}")
            else:
                other_sum += val
        else:
            if k.lower() == "other":
                continue
            kept.append(f"{k} {v}")
            
    if other_sum > 0:
        kept.append(f"Other (~{other_sum:.1f}%)")
        
    return "<br>".join(kept)


def _ethnic_cell(data):
    if not isinstance(data, dict):
        return "—"
    return data.get("summary", "—")


def _others_cell(life_exp, gni_pc):
    bits = []
    if life_exp is not None:
        try:
            bits.append(f"Life exp. {float(life_exp):.1f} yr")
        except (TypeError, ValueError):
            bits.append("Life exp. —")
    else:
        bits.append("Life exp. —")
    if gni_pc is not None:
        try:
            v = float(gni_pc)
            bits.append(f"GNI/cap ${v:,.0f}")
        except (TypeError, ValueError):
            bits.append("GNI/cap —")
    else:
        bits.append("GNI/cap —")
    return " · ".join(bits)


def build_compare_payload(country_inputs, dimensions):
    dims = [d for d in dimensions if d in ALLOWED_DIMENSIONS]
    if not dims:
        dims = ["population"]

    rows = []
    for raw in country_inputs:
        resolved = resolve_country_input(raw)
        if resolved.get("error"):
            rows.append(
                {
                    "input": raw,
                    "error": resolved["error"],
                    "country": None,
                    "country_code": None,
                }
            )
            continue

        code = resolved["iso2"]
        name = resolved["display_name"]
        row = {
            "input": raw,
            "country": name,
            "country_code": code,
            "latitude": resolved.get("latitude"),
            "longitude": resolved.get("longitude"),
        }

        if "population" in dims:
            wb = fetch_country_data(code)
            if wb.get("error"):
                row["population"] = "Unavailable"
            else:
                pd = wb.get("population_display")
                row["population"] = "—" if pd in (None, "", "Unknown") else pd
            row["_population_detail"] = wb

        if "religion" in dims:
            rel = get_religious_breakdown(code, country_name=name)
            row["religion"] = _religion_cell(rel)
            row["_religion_detail"] = rel

        if "ethnic" in dims:
            eth = get_ethnicity_placeholder(code, name)
            row["ethnic"] = _ethnic_cell(eth)
            row["_ethnic_detail"] = eth

        if "cities" in dims:
            urban_pct = fetch_indicator_latest(code, "SP.URB.TOTL.IN.ZS")
            urban_tot = fetch_indicator_latest(code, "SP.URB.TOTL")
            pct_s = "—"
            if urban_pct is not None:
                try:
                    pct_s = f"{float(urban_pct):.1f}% urban"
                except (TypeError, ValueError):
                    pct_s = "—"
            tot_s = "—"
            if urban_tot is not None:
                try:
                    tot_s = f"{float(urban_tot):,.0f} urban pop."
                except (TypeError, ValueError):
                    tot_s = "—"
            row["cities"] = f"{pct_s} · {tot_s}"

        if "others" in dims:
            life = fetch_indicator_latest(code, "SP.DYN.LE00.IN")
            gni = fetch_indicator_latest(code, "NY.GNP.PCAP.CD")
            row["others"] = _others_cell(life, gni)

        rows.append(row)

    out = {"dimensions": dims, "rows": [_strip_private(r) for r in rows]}
    return out


def _strip_private(row):
    return {k: v for k, v in row.items() if not k.startswith("_")}
