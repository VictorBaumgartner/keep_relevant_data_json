import json
import argparse
from typing import Any, Dict, List

IGNORED_KEYS = {
    "href", "rel", "type", "term", "title", "scheme", "prefix",
    "id", "Identifiant", "updated", "published", "link", "links",
    "lang", "base", "author", "rights"
}

def is_useful_value(key: str, value: Any) -> bool:
    if not key or not isinstance(key, str):
        return False
    key = key.strip().lower().split(":")[-1]

    # Skip known wrappers / unhelpful metadata
    if key in IGNORED_KEYS or key.startswith("xmlns") or key.startswith("xml"):
        return False

    # Skip nulls, empties, or 0
    if value in [None, "", "0", 0]:
        return False
    if isinstance(value, str) and value.strip() == "":
        return False

    # Skip very short or technical values (like IDs or UUIDs)
    if isinstance(value, str) and len(value.strip()) <= 3 and not value.isalpha():
        return False

    return True

def flatten_relevant(obj: Any, prefix: str = "") -> Dict[str, Any]:
    result = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                result.update(flatten_relevant(value, key))
            elif is_useful_value(key, value):
                key_clean = key.split(":")[-1].strip()
                result[key_clean] = value
    elif isinstance(obj, list):
        for item in obj:
            result.update(flatten_relevant(item, prefix))
    return result

def extract_clean_entries(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    entries = data.get("feed", {}).get("entry", [])
    cleaned = []
    for entry in entries:
        flat = flatten_relevant(entry)
        if flat:
            cleaned.append(flat)
    return cleaned

def main():
    parser = argparse.ArgumentParser(description="Auto-clean Tourinsoft JSON for DB import (smart extract).")
    parser.add_argument("input_json", help="Path to input JSON file")
    parser.add_argument("--output", help="Optional path to output cleaned JSON")
    args = parser.parse_args()

    with open(args.input_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    cleaned_data = extract_clean_entries(data)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as out_f:
            json.dump(cleaned_data, out_f, ensure_ascii=False, indent=2)
    else:
        print(json.dumps(cleaned_data, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
