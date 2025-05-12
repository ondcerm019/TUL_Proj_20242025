"""
This script compares the "category" sequences from two JSON files using Dynamic Time Warping (DTW).
Each JSON file should contain a list of dictionaries with the following structure:

    {
        "words": list[str],
        "category": str | None
    }

Only non-null categories are considered. The DTW algorithm is used to align the sequences,
and the script returns the number of mismatches
(i.e., positions where the aligned categories differ).

Usage:
    Adjust FILE1_PATH and FILE2_PATH constants, then run the script.

Dependencies:
    pip install fastdtw
"""

import json
from collections import defaultdict

# from fastdtw import fastdtw
from dtw_alignment import dtw_alignment

FILE1_PATH = r"validation_text_json.txt"
FILE2_PATH = r"" # <Cesta ke zpracovanému validačnímu textovému json souboru>



def extract_category_words(path: str) -> list[dict]:
    """
    Loads a JSON file and extracts words with their respective categories, 
    assigning a unique UID that increments with each category change.

    :param path: Path to the JSON file.
    :return: List of dictionaries containing words, categories, and UID.
    """
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    result = []
    category_uids = defaultdict(int)

    for d in data:
        category = d["category"]
        if category is not None:
            category_uids[category] += 1
            for word in d["words"]:
                result.append({
                    "text": word,
                    "category": category,
                    "id": category_uids[category]
                })

    return result



if __name__ == "__main__":
    # pylint: disable=line-too-long
    temp1 = extract_category_words(FILE1_PATH)
    temp2 = extract_category_words(FILE2_PATH)

    align1, align2 = dtw_alignment(temp1, temp2)

    mv_phrases_in_category = defaultdict(int)
    lo_phrases_in_category = defaultdict(int)

    mv_uid_detections = defaultdict(lambda: {"connected_ids": set(), "mis": 0, "cat": 0, "miscat": 0, "old_category": None, "new_categories": set()})
    lo_uid_detections = defaultdict(lambda: {"added": 0, "category": None})

    for a1, a2 in zip(align1, align2):
        if a1:
            if a1["id"] > mv_phrases_in_category[a1["category"]]:
                mv_phrases_in_category[a1["category"]] = a1["id"]
            #-----
            id_category = str(a1["id"]) + a1["category"]

            mv_uid_detections[id_category]["old_category"] = a1["category"]
            if not a2:
                mv_uid_detections[id_category]["mis"] += 1 # Missing word
            else:
                mv_uid_detections[id_category]["connected_ids"].add(str(a2["id"]) + a2["category"])
                mv_uid_detections[id_category]["new_categories"].add(a2["category"])
                if a1["category"] == a2["category"]:
                    mv_uid_detections[id_category]["cat"] += 1 # Word correctly categorised
                else:
                    mv_uid_detections[id_category]["miscat"] += 1 # Word miscategorised

            # print(mv_uid_detections[id_category]["old_category"], mv_uid_detections[id_category]["new_categories"])
        if a2:
            if a2["id"] > lo_phrases_in_category[a2["category"]]:
                lo_phrases_in_category[a2["category"]] = a2["id"]
            #-----
            if not a1:
                id_category = str(a2["id"]) + a2["category"]
                lo_uid_detections[id_category]["added"] += 1
                lo_uid_detections[id_category]["category"] = a2["category"]

        # print(f"{a1} | {a2}")

    MV_TOTAL_PHRASES = 0
    LO_TOTAL_PHRASES = 0
    for v in mv_phrases_in_category.values():
        MV_TOTAL_PHRASES += v
    for v in lo_phrases_in_category.values():
        LO_TOTAL_PHRASES += v


    used_lo_id_category_links = set()

    phrase_detections = []

    for v in mv_uid_detections.values():
        ADDED_WORD_COUNT = 0
        ADDED_CATEGORY = None
        for lo_id_category in v["connected_ids"]:
            if lo_id_category not in used_lo_id_category_links:
                used_lo_id_category_links.add(lo_id_category)
                ADDED_WORD_COUNT = lo_uid_detections[lo_id_category]["added"]
                ADDED_CATEGORY = lo_uid_detections[lo_id_category]["category"]
        merge_set = set([ADDED_CATEGORY]) if ADDED_CATEGORY else set()
        phrase_detections.append({
            "mis": v["mis"],
            "cat": v["cat"],
            "miscat": v["miscat"],
            "added": ADDED_WORD_COUNT,
            "old_category": v["old_category"],
            "new_categories": v["new_categories"] | merge_set
        })
        # print(phrase_detections[-1]["old_category"], phrase_detections[-1]["new_categories"])

    # Fully added words
    for k, v in lo_uid_detections.items():
        if k in used_lo_id_category_links:
            continue
        phrase_detections.append({
            "mis": 0,
            "cat": 0,
            "miscat": 0,
            "added": v["added"],
            "old_category": None,
            "new_categories": set([v["category"]])
        })

    TOTAL_CONST = "TOTAL"
    detection_stats_dict = defaultdict(lambda: {TOTAL_CONST: 0, "pn": 0, "i": 0, "c": 0, "l": 0, "z": 0, "p": 0, "e": 0, "cj": 0, "w": 0})
    misclassified_stats_dict = defaultdict(lambda: {"pn": 0, "i": 0, "c": 0, "l": 0, "z": 0, "p": 0, "e": 0, "cj": 0, "w": 0})

    for item in phrase_detections:
        mis = item["mis"]
        cat = item["cat"]
        miscat = item["miscat"]
        added = item["added"]
        old_cat = item["old_category"]
        new_cats = item["new_categories"]

        if mis > 0 and cat == 0 and miscat == 0 and added == 0:
            detection_stats_dict["full_mis"][TOTAL_CONST] += 1
            detection_stats_dict["full_mis"][old_cat] += 1
        if mis == 0 and cat == 0 and miscat == 0 and added > 0:
            detection_stats_dict["full_added"][TOTAL_CONST] += 1
            detection_stats_dict["full_added"][next(iter(new_cats))] += 1
        if mis == 0 and cat > 0 and miscat == 0 and added == 0:
            detection_stats_dict["full_cat"][TOTAL_CONST] += 1
            detection_stats_dict["full_cat"][old_cat] += 1
        if mis == 0 and cat == 0 and miscat > 0 and added == 0:
            detection_stats_dict["full_miscat"][TOTAL_CONST] += 1
            detection_stats_dict["full_miscat"][old_cat] += 1
        if mis > 0:
            detection_stats_dict["part_mis"][TOTAL_CONST] += 1
            detection_stats_dict["part_mis"][old_cat] += 1
        if added > 0:
            detection_stats_dict["part_added"][TOTAL_CONST] += 1
            if old_cat is None:
                detection_stats_dict["part_added"][next(iter(new_cats))] += 1
            else:
                detection_stats_dict["part_added"][old_cat] += 1
        if cat > 0:
            detection_stats_dict["part_cat"][TOTAL_CONST] += 1
            detection_stats_dict["part_cat"][old_cat] += 1
        if miscat > 0:
            detection_stats_dict["part_miscat"][TOTAL_CONST] += 1
            detection_stats_dict["part_miscat"][old_cat] += 1

        if old_cat and new_cats:
            for new_cat in new_cats:
                misclassified_stats_dict[old_cat][new_cat] += 1

    print("--------------------------------------------------------------------")
    print("                         | Manual validation | LLM output")
    print("-------------------------|-------------------|----------------------")
    print(f"Personal name phrases    | {mv_phrases_in_category["pn"]:<16}  | {lo_phrases_in_category["pn"]:<16}")
    print(f"Institution phrases      | {mv_phrases_in_category["i"]:<16}  | {lo_phrases_in_category["i"]:<16}")
    print(f"Company phrases          | {mv_phrases_in_category["c"]:<16}  | {lo_phrases_in_category["c"]:<16}")
    print(f"Location phrases         | {mv_phrases_in_category["l"]:<16}  | {lo_phrases_in_category["l"]:<16}")
    print(f"Zipcode phrases          | {mv_phrases_in_category["z"]:<16}  | {lo_phrases_in_category["z"]:<16}")
    print(f"Phone phrases            | {mv_phrases_in_category["p"]:<16}  | {lo_phrases_in_category["p"]:<16}")
    print(f"Email phrases            | {mv_phrases_in_category["e"]:<16}  | {lo_phrases_in_category["e"]:<16}")
    print(f"Case number phrases      | {mv_phrases_in_category["cj"]:<16}  | {lo_phrases_in_category["cj"]:<16}")
    print(f"Web phrases              | {mv_phrases_in_category["w"]:<16}  | {lo_phrases_in_category["w"]:<16}")
    print("-------------------------|-------------------|----------------------")
    print(f"Total classified phrases | {MV_TOTAL_PHRASES:<16}  | {LO_TOTAL_PHRASES:<16}")
    print("--------------------------------------------------------------------")
    print(f"Fully correctly classified phrases: {detection_stats_dict["full_cat"][TOTAL_CONST]} (~ {detection_stats_dict["full_cat"][TOTAL_CONST]/MV_TOTAL_PHRASES*100:.2f} %)")
    print(f"Partially correctly classified phrases: {detection_stats_dict["part_cat"][TOTAL_CONST]} (~ {detection_stats_dict["part_cat"][TOTAL_CONST]/MV_TOTAL_PHRASES*100:.2f} %)")
    print(f"Fully misclassified phrases: {detection_stats_dict["full_miscat"][TOTAL_CONST]}")
    print(f"Partially misclassified phrases: {detection_stats_dict["part_miscat"][TOTAL_CONST]}")
    print(f"Phrases with missing words: {detection_stats_dict["part_mis"][TOTAL_CONST]}")
    print(f"Completely removed phrases: {detection_stats_dict["full_mis"][TOTAL_CONST]}")
    print(f"Phrases with added words: {detection_stats_dict["part_added"][TOTAL_CONST]}")
    print(f"Completely added phrases: {detection_stats_dict["full_added"][TOTAL_CONST]}")
    # print(f"Phrases with both missing and added words: {WITH_MISSING_AND_ADDED}")
    # print(f"Phrases with both correctly classified and misclassified words: {WITH_CATEGORISED_AND_MISCATEGORISED}")
    print("-----------------------------------------------------------------------------------------------------------------------------------------------------")
    print("                         | Correct                                     | Incorrect               | Missing                 | Added")
    print("-------------------------|---------------------------------------------|-------------------------|-------------------------|-------------------------")
    print("                         | Full                 | Partial              | Full       | Partial    | Full       | Partial    | Full       | Partial")
    print("-------------------------|----------------------|----------------------|------------|------------|------------|------------|------------|------------")
    def get_output_string(category: str) -> str:
        """returns string output"""
        return f"{detection_stats_dict["full_cat"][category]:<10} {detection_stats_dict["full_cat"][category]/mv_phrases_in_category[category]*100: 7.2f} % | {detection_stats_dict["part_cat"][category]:<10} {detection_stats_dict["part_cat"][category]/mv_phrases_in_category[category]*100: 7.2f} % | {detection_stats_dict["full_miscat"][category]:<10} | {detection_stats_dict["part_miscat"][category]:<10} | {detection_stats_dict["full_mis"][category]:<10} | {detection_stats_dict["part_mis"][category]:<10} | {detection_stats_dict["full_added"][category]:<10} | {detection_stats_dict["part_added"][category]:<10}"
    print(f"Personal name phrases    | {get_output_string("pn")}")
    print(f"Institution phrases      | {get_output_string("i")}")
    print(f"Company phrases          | {get_output_string("c")}")
    print(f"Location phrases         | {get_output_string("l")}")
    print(f"Zipcode phrases          | {get_output_string("z")}")
    print(f"Phone phrases            | {get_output_string("p")}")
    print(f"Email phrases            | {get_output_string("e")}")
    print(f"Case number phrases      | {get_output_string("cj")}")
    print(f"Web phrases              | {get_output_string("w")}")
    print("-----------------------------------------------------------------------------------------------------------------------------------------------------")
    print("Phrases at least partially classified as: (for misclassifications)")
    print("                         | pn         | i          | c          | l          | z          | p          | e          | cj         | w")
    print("-------------------------|------------|------------|------------|------------|------------|------------|------------|------------|------------")
    def get_misclassified_output_string(category: str) -> str:
        """returns string output"""
        temp = ["pn", "i", "c", "l", "z", "p", "e", "cj", "w"]
        stringbuild = ""
        for t in temp:
            stringbuild += f" | {misclassified_stats_dict[category][t] if category != t else "-":<10}"
        return stringbuild
    print(f"Personal name phrases   {get_misclassified_output_string("pn")}")
    print(f"Institution phrases     {get_misclassified_output_string("i")}")
    print(f"Company phrases         {get_misclassified_output_string("c")}")
    print(f"Location phrases        {get_misclassified_output_string("l")}")
    print(f"Zipcode phrases         {get_misclassified_output_string("z")}")
    print(f"Phone phrases           {get_misclassified_output_string("p")}")
    print(f"Email phrases           {get_misclassified_output_string("e")}")
    print(f"Case number phrases     {get_misclassified_output_string("cj")}")
    print(f"Web phrases             {get_misclassified_output_string("w")}")

    # note: partial count includes full count (kind of counter intuitive)
