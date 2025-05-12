"""Module containing methods for refining the llm output."""

import os
import json
import re

from constants import TAGS, TEXT_CHUNK_WORD_OVERLAP_TOL, OMITTED_TAGS, \
    OUTPUT_LOGS_FOLDER, LOGS_CATEGORY_WORDS, LOGS_LATEST_POS, LOGS_CHANGES, MAIN_OUTPUT
    # OUTPUT_PROCESSED_TEMP_FILE, INPUT_TEXT_TEMP_FILE, \



def parse_tagged_text(text):
    # pylint: disable=too-many-locals
    """
    Parses a text string looking for specific tagged sections.

    The tags it looks for are defined in the TAGS dictionary (imported from tag_constants),
    using the dictionary values as valid tags.
    Any unrecognized tags are ignored. If a tag is not properly closed,
    all nested tags are ignored until the closing tag appears.

    The function returns a list of dictionaries, each containing:
      - "words": A list of words belonging to the section
      - "category": The tag name if within a valid tagged section, otherwise None

    Words and punctuation are preserved in order, allowing the original text to be reconstructed.

    Example:
        Input:  "Ahoj já jsem <pname>Honza</pname>, jdu domu."
        Output: [
            {"words": ["Ahoj", "já", "jsem"], "category": None},
            {"words": ["Honza"], "category": "pname"},
            {"words": [", jdu domu."], "category": None}
        ]

    :param text: The input text string containing tagged sections.
    :return: A list of dictionaries separating words by category.
    """
    tag_pattern = re.compile(r'<(/?)(\w+)>')

    result = []
    current_words = []
    current_category = None
    tag_stack = []

    pos = 0
    while pos < len(text):
        match = tag_pattern.search(text, pos)
        if not match:
            break

        start, end = match.span()
        tag_is_closing, tag_name = match.groups()

        pre_tag_text = text[pos:start].strip()
        pre_words = pre_tag_text.split(" ") if pre_tag_text else []
        if pre_words:
            current_words.extend(pre_words)

        if tag_is_closing:
            if tag_stack and tag_stack[-1] == tag_name:
                tag_stack.pop()
                if not tag_stack:
                    result.append({"words": current_words, "category": current_category})
                    current_words = []
                    current_category = None
        else:
            if tag_name in TAGS.values() and not tag_stack:
                if current_words:
                    result.append({"words": current_words, "category": current_category})
                    current_words = []
                current_category = tag_name
                tag_stack.append(tag_name)

        pos = end

    post_text = text[pos:].strip()
    post_words = post_text.split(" ") if post_text else []
    if post_words:
        current_words.extend(post_words)
    if current_words:
        result.append({"words": current_words, "category": current_category})

    return result


def object_to_json(python_object):
    """
    Converts a Python object into a JSON string.
    
    :param processed_data: Python object
    :return: JSON string
    """
    return json.dumps(python_object, ensure_ascii=False, indent=2)


def json_to_object(json_string: str):
    """
    Converts a JSON string into a Python object.
    
    :param json_data: JSON string
    :return: Python object
    """
    return json.loads(json_string)


def reconstruct_text(processed_data):
    """
    Converts the parsed output back into a plain text string, 
    ensuring punctuation marks like ",", "." are correctly placed 
    without adding extra spaces after a category change.
    
    :param processed_data: The output of process_tagged_text function.
    :return: A string with words joined by spaces.
    """
    reconstructed_text = [""]
    prev_category = ""

    for entry in processed_data:
        if len(entry["words"]) == 0:
            continue
        first_word = entry["words"][0]
        prev_last_word = reconstructed_text[-1]
        is_new_special = \
                bool(re.match(r"^[,.!?;:\"'\)\]\}»…\\/]+$", first_word))
        is_last_special = \
            bool(re.match(r"^[\"'\(\[\{\\/]+$", prev_last_word))
        if prev_category != entry["category"] and is_new_special ^ is_last_special:
            reconstructed_text[-1] += first_word
        else:
            reconstructed_text.append(first_word)

        for word in entry["words"][1:]:
            reconstructed_text.append(word)

        prev_category = entry["category"]

    return " ".join(reconstructed_text)



def append_json_string_to_file(json_data: str, input_file_path: str):
    """
    Appends a JSON string (representing an array) to an existing JSON file as a string.
    - If the file is empty or does not exist, it initializes it with the given JSON array.
    - If the file contains a JSON array,
      it appends the new JSON objects while preserving valid JSON format.
    - If the last object in the file and the first object in json_data have `category: null`,
      they are merged.

    :param json_data: A JSON string representing an array of objects.
    :param input_file_path: The path to the input file.
    """
    folder_name = os.path.basename(input_file_path)
    file_path = os.path.join(OUTPUT_LOGS_FOLDER, folder_name, MAIN_OUTPUT)

    if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
        with open(file_path, "r+", encoding="utf-8") as file:
            file.seek(0, os.SEEK_END)

            # Read last JSON array safely
            file.seek(0)
            existing_json_str = file.read().strip()
            if not existing_json_str.endswith("]"):
                raise ValueError("File content is not a valid JSON array.")

            # Parse existing JSON data
            existing_json = json_to_object(existing_json_str)
            if not isinstance(existing_json, list):
                raise ValueError("File content is not a valid JSON array.")

            # Extract last object from existing JSON
            last_object = existing_json[-1] if existing_json else None

            # Extract first object from new JSON data
            new_objects = json_to_object(json_data)
            if not isinstance(new_objects, list):
                raise ValueError("Input json_data must be a JSON array.")
            first_object = new_objects[0] if new_objects else None

            # Check if merging is possible
            if last_object and first_object and last_object.get("category") is None \
            and first_object.get("category") is None:
                last_object["words"].extend(first_object["words"])
                new_objects.pop(0)  # Remove first object since it's merged

            # Write updated JSON back
            file.seek(0)
            file.write(object_to_json(existing_json[:-1] + [last_object] + new_objects))
            file.truncate()

    else:
        # Create new file if empty or missing
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(json_data)



# text_file_extraction
def correct_object_and_get_reverse_index(processed_data, original_text: str):
    # pylint: disable=too-many-branches
    """
    :param processed_data: The output of process_tagged_text function.
    :param original_text: Original text string.
    :return: The sum of characters for the considered words,
    a value that should be subtracted from text_file_extraction's return count for the next call
    """
    last_words = []
    last_categories = []

    for entry in reversed(processed_data):
        last_words = entry["words"] + last_words
        last_categories = [entry["category"]] * len(entry["words"]) + last_categories

        if len(last_words) >= TEXT_CHUNK_WORD_OVERLAP_TOL:
            break

    full_len = len(last_words)
    last_category = last_categories[-1]

    word_index = full_len

    if last_category is not None:
        for i in range(1, full_len):
            if last_categories[-(i+1)] != last_category:
                word_index = i
                break
    else:
        for i in range(1, TEXT_CHUNK_WORD_OVERLAP_TOL):
            if last_categories[-(i+1)] is not None:
                word_index = i
                break
        else:
            word_index = TEXT_CHUNK_WORD_OVERLAP_TOL

    original_words = original_text.split()
    original_word_index = 0
    for lw, ow in zip(reversed(last_words[-word_index:]), reversed(original_words[-word_index:])):
        if lw != ow:
            break
        original_word_index += 1

    if last_category is None:
        words_to_remove = original_word_index
    else:
        words_to_remove = word_index

    while words_to_remove > 0:
        word_count = len(processed_data[-1]["words"])

        if word_count <= words_to_remove:
            processed_data.pop()
            words_to_remove -= word_count
            continue

        del processed_data[-1]["words"][-words_to_remove:]

        words_to_remove = 0

    return -(original_word_index + 1)





def get_latest_position(input_file_path: str) -> int:
    """
    Ensures a log folder exists for the given input file
    and retrieves the latest position from a tracking file.

    - If the folder does not exist, it creates it.
    - If the latest position file exists, it reads the first line and converts it to an integer.
    - If the file does not exist, it returns 0.

    :param input_file_path: Path to the input file.
    :return: The last recorded position as an integer, or 0 if not found.
    """
    folder_name = os.path.basename(input_file_path)
    log_folder_path = os.path.join(OUTPUT_LOGS_FOLDER, folder_name)

    os.makedirs(log_folder_path, exist_ok=True)

    latest_pos_file = os.path.join(log_folder_path, LOGS_LATEST_POS)

    if os.path.exists(latest_pos_file):
        with open(latest_pos_file, "r", encoding="utf-8") as file:
            first_line = file.readline().strip()
            return int(first_line) if first_line.isdigit() else 0
    return 0


def write_tagged_sections_to_files(parsed_data, input_file_path: str):
    """
    Writes each section with a category (not None) into separate text files 
    inside `{OUTPUT_LOGS_FOLDER}/name_of_input_file/{LOGS_CATEGORY_WORDS}/`.

    Each file is named after the category and contains lines of text from that category.

    :param parsed_data: The output of `parse_tagged_text`, 
                        a list of dicts with "words" and "category".
    :param input_file_path: The path to the input file.
    """
    folder_name = os.path.basename(input_file_path)
    folder_path = os.path.join(OUTPUT_LOGS_FOLDER, folder_name, LOGS_CATEGORY_WORDS)
    os.makedirs(folder_path, exist_ok=True)

    categorized_data = {}

    for section in parsed_data:
        category = section["category"]
        if category is not None:
            categorized_data.setdefault(category, []).append(" ".join(section["words"]))

    for category, lines in categorized_data.items():
        file_path = os.path.join(folder_path, f"{category}.txt")
        with open(file_path, "a", encoding="utf-8") as file:
            file.write("\n".join(lines) + "\n")

def append_to_changes_log(input_file_path: str, log_entry: str):
    """
    Appends a log entry to a file inside `{OUTPUT_LOGS_FOLDER}/name_of_input_file/{LOGS_CHANGES}/`.

    :param input_file_path: The path to the input file.
    :param log_entry: The string to append to the log file.
    """
    folder_name = os.path.basename(input_file_path)
    log_file_path = os.path.join(OUTPUT_LOGS_FOLDER, folder_name, LOGS_CHANGES)

    with open(log_file_path, "a", encoding="utf-8") as file:
        file.write(log_entry + "\n")

def write_latest_position(input_file_path: str, position: int) -> None:
    """
    Writes the given position number to the latest position tracking file.

    :param input_file_path: Path to the input file.
    :param position: The position number to write.
    """
    folder_name = os.path.basename(input_file_path)
    log_folder_path = os.path.join(OUTPUT_LOGS_FOLDER, folder_name)

    os.makedirs(log_folder_path, exist_ok=True)

    latest_pos_file = os.path.join(log_folder_path, LOGS_LATEST_POS)

    with open(latest_pos_file, "w", encoding="utf-8") as file:
        file.write(str(position))



# additional filtering
def filter_categories(processed_data: list[dict]) -> None:
    # pylint: disable=line-too-long
    # pylint: disable=too-many-locals
    # pylint: disable=too-many-branches
    # pylint: disable=too-many-statements
    """
    Modifies the input list of dictionaries by applying various category filtering rules.
    Each category's "category" field is set to None based on specific conditions.
    The modified list is rebuilt using a buffer and replaced in-place.
    """
    if not processed_data:
        return

    filtered = []

    for obj in processed_data:
        category = obj.get("category")
        words = obj.get("words", [])

        # Default to keeping the category
        keep_category = True

        if category in OMITTED_TAGS:
            keep_category = False

        elif category == TAGS["CASE_NUMBER"]:
            has_two_digits = any(re.search(r'\d{2,}', word) for word in words)
            has_slash = any('/' in word for word in words)

            if not (has_two_digits and has_slash):
                keep_category = False
            else:
                # Check for specific keywords that trigger a split
                special_keywords = {"čj.", "j.", "zn.", "č.j.", "sp.zn.", "zn", "čj", ".", "j.:", "zn.:", "značka:", "číslo:", "jednací:", "spisu:", "značkou"}
                split_index = None

                for i, word in enumerate(words):
                    if word.lower() in special_keywords:
                        split_index = i
                        break

                if split_index is not None:
                    # First part goes into a null category
                    null_part = {
                        "category": None,
                        "words": words[:split_index + 1]
                    }
                    # Remaining part stays as CASE_NUMBER
                    remaining_part = {
                        "category": category,
                        "words": words[split_index + 1:]
                    }

                    # Add both parts and skip normal append
                    filtered.append(null_part)
                    if remaining_part["words"]:  # Avoid empty word lists
                        filtered.append(remaining_part)
                    continue  # Skip normal append outside


        elif category == TAGS["ZIPCODE"]:
            zip_index = None

            for i in range(len(words) - 1):
                if words[i].isdigit() and len(words[i]) == 3 and \
                words[i + 1].isdigit() and len(words[i + 1]) == 2:
                    zip_index = i
                    break

            if zip_index is None:
                keep_category = False
            else:
                # Split into parts: before, zipcode, after
                before = words[:zip_index]
                zipcode = words[zip_index:zip_index + 2]
                after = words[zip_index + 2:]

                if before:
                    filtered.append({"category": None, "words": before})
                filtered.append({"category": category, "words": zipcode})
                if after:
                    filtered.append({"category": None, "words": after})
                continue  # Skip normal append outside


        elif category == TAGS["EMAIL"]:
            at_index = next((i for i, word in enumerate(words) if "@" in word), None)

            if at_index is None:
                keep_category = False
            else:
                before = words[:at_index]
                email = [words[at_index]]
                after = words[at_index + 1:]

                if before:
                    filtered.append({"category": None, "words": before})
                filtered.append({"category": category, "words": email})
                if after:
                    filtered.append({"category": None, "words": after})
                continue  # Skip the default append


        elif category == TAGS["PHONE"]:
            # Count total digits in the words
            total_digits = sum(char.isdigit() for word in words for char in word)

            if total_digits < 9:
                keep_category = False
            else:
                # Create lists to hold the parts of the words
                null_part_before = []
                null_part_after = []
                digits_and_special = []  # Keep this as a list of words, not a concatenated string

                # Split the words into parts before digits/special characters (but not letters)
                i = 0
                while i < len(words) and any(char.isalpha() for char in words[i]):
                    null_part_before.append(words[i])
                    i += 1

                # Collect all words with digits and special characters
                while i < len(words) and any(char.isdigit() or not char.isalpha() for char in words[i]):
                    digits_and_special.append(words[i])  # keep words with digits and special characters separate
                    i += 1

                # Collect all words after digits that contain letters
                while i < len(words):
                    null_part_after.append(words[i])
                    i += 1

                # Add parts to filtered list
                if null_part_before:
                    filtered.append({"category": None, "words": null_part_before})
                if digits_and_special:
                    filtered.append({"category": category, "words": digits_and_special})  # Add the phone number part
                if null_part_after:
                    filtered.append({"category": None, "words": null_part_after})

                continue  # Skip normal append outside


        elif category == TAGS["WEB"]:
            dot_index = next((i for i, word in enumerate(words) if "." in word), None)

            if dot_index is None:
                keep_category = False
            else:
                before = words[:dot_index]
                web_word = [words[dot_index]]
                after = words[dot_index + 1:]

                if before:
                    filtered.append({"category": None, "words": before})
                filtered.append({"category": category, "words": web_word})
                if after:
                    filtered.append({"category": None, "words": after})

                continue  # Skip normal append outside

        elif category == TAGS["LOCATION"]:
            # Check if there's at least one capital letter or digit
            if not any(word[0].isupper() or any(char.isdigit() for char in word) for word in words):
                # If no capital letter or digit, classify as None
                filtered.append({"category": None, "words": words})
            else:
                # Look for a 3-digit word followed by a 2-digit word
                for i in range(len(words) - 1):
                    if words[i].isdigit() and len(words[i]) == 3 and words[i+1].isdigit() and len(words[i+1]) == 2:
                        # Split the words
                        before_zipcode = words[:i]
                        zipcode = [words[i], words[i+1]]
                        after_zipcode = words[i+2:]

                        # Add the words before the zipcode to LOCATION
                        if before_zipcode:
                            filtered.append({"category": TAGS["LOCATION"], "words": before_zipcode})

                        # Add the zipcode to the ZIPCODE category
                        filtered.append({"category": TAGS["ZIPCODE"], "words": zipcode})

                        # Add the words after the zipcode to LOCATION
                        if after_zipcode:
                            filtered.append({"category": TAGS["LOCATION"], "words": after_zipcode})

                        break  # Stop after processing the first match
                else:
                    # If no 3-digit + 2-digit pair is found, keep as LOCATION
                    filtered.append({"category": category, "words": words})

            continue  # Skip the default append outside

        elif category in [TAGS["INSTITUTION"], TAGS["COMPANY"]]:
            if not any(word and (word[0].isupper() or word[0].isdigit()) for word in words):
                keep_category = False

        elif category == TAGS["PERSONAL_NAME"]:
            if not any(word and word[0].isupper() for word in words):
                keep_category = False

        # Apply change
        filtered.append({
            "category": category if keep_category else None,
            "words": words
        })

    # Replace the original list content
    processed_data.clear()
    processed_data.extend(filtered)


def merge_null_category_sections(data: list[dict]) -> None:
    """
    Merges consecutive dictionaries in the input list where the "category" is None.
    All "words" fields from dictionaries with a None category are combined into a single
    entry with the "category" set to None. Non-null category entries are kept separate.
    The input list is modified in place.
    """
    if not data:
        return

    merged = []
    buffer = None

    for item in data:
        if item.get("category") is None:
            if buffer is None:
                buffer = {"category": None, "words": []}
            buffer["words"].extend(item["words"])
        else:
            if buffer:
                merged.append(buffer)
                buffer = None
            merged.append(item)

    if buffer:
        merged.append(buffer)

    data.clear()
    data.extend(merged)


def clean_up_categories(processed_data: list[dict]) -> None:
    """
    Applies a sequence of cleanup transformations to processed_data.

    Modifies the list in-place.
    """

    cleanup_steps = [
        filter_categories,
        merge_null_category_sections
    ]

    for step in cleanup_steps:
        step(processed_data)




TEST_TEXT_TAGGED_PATH = \
    r"validation_text_manual_tags.txt"
TEST_TEXT_JSON_PATH = r"validation_text_json.txt"


if __name__ == "__main__":
    # with (
    #     open(TEST_TEXT_TAGGED_PATH, "r", encoding="utf-8") as input_file,
    #     open(TEST_TEXT_JSON_PATH, "w", encoding="utf-8") as output_file
    # ):
    #     text_temp = input_file.read()
    #     text_object = parse_tagged_text(text_temp)

    #     clean_up_categories(text_object)

    #     write_tagged_sections_to_files(text_object, TEST_TEXT_TAGGED_PATH)

    #     output_file.write(object_to_json(text_object))
    pass
