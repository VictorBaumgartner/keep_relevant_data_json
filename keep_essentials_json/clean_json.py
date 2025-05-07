import json
from pathlib import Path
from typing import Any, Dict, List

# Define keys to ignore during the cleaning process
IGNORED_KEYS = {
    "href", "rel", "type", "term", "title", "scheme", "prefix",
    "id", "Identifiant", "updated", "published", "link", "links",
    "lang", "base", "author", "rights"
}

# Function to check if a value should be kept based on key and value
def is_useful_value(key: str, value: Any) -> bool:
    if not key or not isinstance(key, str):
        return False
    key = key.strip().lower().split(":")[-1]  # Remove any XML namespace prefix

    # Ignore keys that match those in IGNORED_KEYS or have XML-related prefixes
    if key in IGNORED_KEYS or key.startswith("xmlns") or key.startswith("xml"):
        return False

    # Ignore empty or irrelevant values
    if value in [None, "", "0", 0]:
        return False
    if isinstance(value, str) and value.strip() == "":
        return False
    if isinstance(value, str) and len(value.strip()) <= 3 and not value.isalpha():
        return False

    return True

# Recursive function to flatten nested dictionaries and lists
def flatten_relevant(obj: Any, prefix: str = "") -> Dict[str, Any]:
    result = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            # If the value is a dictionary or list, recurse
            if isinstance(value, (dict, list)):
                result.update(flatten_relevant(value, key))
            # If the value is useful, include it
            elif is_useful_value(key, value):
                key_clean = key.split(":")[-1].strip()  # Clean the key
                result[key_clean] = value
    elif isinstance(obj, list):
        for item in obj:
            result.update(flatten_relevant(item, prefix))
    return result

# Extract and clean entries from the 'feed' section of the data
def extract_clean_entries(data: Dict[str, Any]) -> List[Dict[str, Any]]:
    feed = data.get("feed")
    
    if feed is None:
        print("Warning: 'feed' key is missing in the data.")
        return []

    entries = feed.get("entry", [])
    cleaned = []
    for entry in entries:
        flat = flatten_relevant(entry)
        if flat:
            cleaned.append(flat)
    return cleaned

# Main function to clean the JSON
def clean_json(input_path: Path, output_path: Path):
    try:
        # Read the input JSON file
        with input_path.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Clean the data
        cleaned_data = extract_clean_entries(data)

        if not cleaned_data:
            print("No cleaned data found. Check the input JSON structure.")

        # Ensure the output directory exists
        output_dir = output_path.parent
        if not output_dir.exists():
            print(f"Creating output directory: {output_dir}")
            output_dir.mkdir(parents=True, exist_ok=True)

        # Write the cleaned data to the output file
        with output_path.open("w", encoding="utf-8") as out_f:
            json.dump(cleaned_data, out_f, ensure_ascii=False, indent=2)
        print(f"Cleaned JSON has been written to: {output_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    input_path = Path("./source1.json")  # Input file
    output_path = Path("./output/source1_clean.json")  # Output file

    clean_json(input_path, output_path)
