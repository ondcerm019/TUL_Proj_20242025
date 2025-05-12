"""JSON load test"""
# pylint: disable=line-too-long


import json
from collections import Counter

# Load the data
FILE_PATH = \
    r"" # <Cesta k textovému json souboru, ze kterého mají být vypsány četnosti kategorií osobních údajů>


with open(FILE_PATH, "r", encoding="utf-8") as file:
    data = json.load(file)

# Count categories
category_counts = Counter(item["category"] for item in data)

# Create structured output
output_lines = []
for category, count in category_counts.items():
    output_lines.append(f"{category}: {count}")

# Join lines and print
OUTPUT_STRING = "\n".join(output_lines)
print(OUTPUT_STRING)
