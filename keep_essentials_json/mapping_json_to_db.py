import json
from datetime import datetime

def format_date(date_str):
    try:
        return datetime.fromisoformat(date_str).strftime("%Y-%m-%d")
    except Exception:
        return None

def clean_tourinsoft_data(raw_json):
    output = []
    for idx, entry in enumerate(raw_json):
        item = {
            "id": entry.get("SyndicObjectID", f"event_{idx}"),
            "title": entry.get("SyndicObjectName") or entry.get("NOMMANIFESTATION", "Sans titre"),
            "insee": "",  # Requires external INSEE lookup
            "city": entry.get("Commune", ""),
            "start_date": format_date(entry.get("Datedebut", "")),
            "end_date": format_date(entry.get("Datefin", "")),
            "type": entry.get("ObjectTypeName", ""),
            "description": entry.get("DESCRIPTIFCOMMERCIAL") or entry.get("DESCRIPTIFSYNTHETIQUE", ""),
            "theme": "",  # Not present directly
            "category": entry.get("ObjectTypeName", ""),
            "geopoint": f"{entry.get('GmapLatitude')}, {entry.get('GmapLongitude')}" if entry.get("GmapLatitude") and entry.get("GmapLongitude") else "",
            "epci": "",  # Not in data
            "activities": "Marché" if "marché" in (entry.get("DESCRIPTIFCOMMERCIAL", "").lower()) else ""
        }
        output.append(item)
    return output

# Exemple d'utilisation
if __name__ == "__main__":
    with open("input.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    
    cleaned = clean_tourinsoft_data(data)
    
    with open("filament_format_output/output.json", "w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)
