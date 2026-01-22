import json
import csv
import os
import sys

def convert_jl(input_file):
    if not os.path.exists(input_file):
        print(f"Error: File not found: {input_file}")
        return

    base_name = os.path.splitext(input_file)[0]
    json_output = base_name + "_pretty.json"
    csv_output = base_name + ".csv"

    print(f"Reading {input_file}...")
    data = []
    with open(input_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if line:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError as e:
                    print(f"Skipping invalid line: {e}")

    if not data:
        print("No data found in file.")
        return

    # 1. Export to Pretty JSON (Like README)
    print(f"Saving to {json_output}...")
    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # 2. Export to CSV (Excel compatible)
    print(f"Saving to {csv_output}...")
    
    # Collect all possible keys from all items (in case some items miss fields)
    all_keys = set()
    for item in data:
        all_keys.update(item.keys())
    
    # Sort keys for consistent column order
    # Prioritize common fields
    priority_fields = ['id', 'title', 'app_name', 'price', 'sentiment', 'release_date']
    fieldnames = [k for k in priority_fields if k in all_keys]
    fieldnames += sorted([k for k in all_keys if k not in priority_fields])

    with open(csv_output, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for item in data:
            # Flatten lists (like tags or genres) into strings for CSV
            row = item.copy()
            for k, v in row.items():
                if isinstance(v, list):
                    row[k] = ', '.join(map(str, v))
            writer.writerow(row)

    print("Done!")
    print(f"1. Pretty JSON: {json_output}")
    print(f"2. Excel CSV:   {csv_output}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_file = sys.argv[1]
    else:
        # Default target
        target_file = os.path.join(os.path.dirname(__file__), '..', 'output', 'products_all.jl')
    
    convert_jl(os.path.abspath(target_file))
