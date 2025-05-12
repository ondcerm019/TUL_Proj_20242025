"""Counting words in each category from specified folders"""

import os
from collections import defaultdict

# pylint: disable=line-too-long
FOLDER_PATHS = [
    r"" # <Cesty k textovým json souborům, ze kterých mají být vypsány četnosti kategorií osobních údajů>
]



def count_lines_in_text_files(folders: list[str]) -> None:
    """
    Counts the total and unique number of lines in each .txt file (by base name)
    across multiple folders and prints the results. If the same line appears in 
    multiple folders for the same base file, it's only counted once per category 
    (file), but counted separately if in different files.

    :param folders: List of folder paths to search for .txt files.
    """
    # This will store sets of unique lines for each base filename across all folders
    line_counts = defaultdict(set)
    total_line_counts = defaultdict(int)

    for folder in folders:
        for file_name in os.listdir(folder):
            if file_name.endswith(".txt"):
                file_path = os.path.join(folder, file_name)
                base_name = os.path.splitext(file_name)[0]

                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        lines = f.readlines()
                        total_line_counts[base_name] += len(lines)  # Count all lines
                        for line in lines:
                            line = line.strip()  # Remove any leading/trailing whitespace
                            line_counts[base_name].add(line)  # Add line to set (ensures uniqueness)
                except OSError as e:
                    print(f"Error reading {file_path}: {e}")

    # Printing out the results
    for name in line_counts:
        unique_lines = len(line_counts[name])
        total_lines = total_line_counts[name]
        print(f"{name}: {total_lines}, {unique_lines} unique")








if __name__ == "__main__":
    count_lines_in_text_files(FOLDER_PATHS)
