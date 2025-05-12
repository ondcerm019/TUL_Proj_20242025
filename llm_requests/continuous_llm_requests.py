"""Module for continuously sending requests and saving the processed output."""
import re

from text_file_extraction import read_text_file
from output_conversion import parse_tagged_text, object_to_json, reconstruct_text, \
    append_json_string_to_file, correct_object_and_get_reverse_index, \
    get_latest_position, write_tagged_sections_to_files, append_to_changes_log, \
        write_latest_position, clean_up_categories
from text_changes_check import text_changes_check, text_changes_string
from openai_api_buffer import OpenAIClientManager

from constants import TAGS, \
    TEMPERATURE, \
    API_INFO

REQUEST_COUNT = -1 # -1 for Inf loop
REQUEST_APPROXIMATE_CHAR_LENGTH = 1000

ADDED_RESEND_TOL = 15 #15
REMOVED_RESEND_TOL = 15 #15


FTELL_MASK = (1 << 64) - 1



INPUT_FILE = \
    r"" # <Cesta ke vstupnímu textovému souboru, který má být zpracován>



chat_prompt = [
    # pylint: disable=line-too-long
    {
        "role": "system",
        "content": f"""
        You are an assistant tasked with classifying Czech words and phrases into categories of personal data.

        Your task is to identify and wrap these sections with <>tags</> that represent one of the following categories:
        - <{TAGS["PERSONAL_NAME"]}> for personal names, inside the tagged section, include the first name, last name, and professional titles such as Ing., JUDr., etc.
        - <{TAGS["INSTITUTION"]}> for names of specific government, political, cultural, educational or scientific agencies/institutions
        - <{TAGS["COMPANY"]}> for company names, includes social media platform names
        - <{TAGS["LOCATION"]}> for place names (e.g., cities, streets, etc.)
        - <{TAGS["DATE"]}> for dates
        - <{TAGS["ZIPCODE"]}> for 5-digit Czech postal codes (e.g., "123 45")
        - <{TAGS["PHONE"]}> for phone numbers
        - <{TAGS["EMAIL"]}> for email addresses
        - <{TAGS["CASE_NUMBER"]}> for court case numbers (číslo jednací, č. j., spisová značka)
        - <{TAGS["ACT"]}> for references to laws and legal acts (e.g., "zákon č. 89/2012 Sb.", "s ř. s.", etc.)
        - <{TAGS["WEB"]}> for web page URL (www addresses)

        Non-relevant text should not be tagged.
        Make sure that tags are closed before another tag starts. In case of category overlap, apply the most relevant one.

        Example Input:
        Here is some text. Jan Novák, Ing., works at XYZ Company and can be reached at jan.novak@example.com +420 123 456 789. More information is available.
        Example Output:
        Here is some text. <{TAGS["PERSONAL_NAME"]}>Jan Novák, Ing.</{TAGS["PERSONAL_NAME"]}>, works at <{TAGS["COMPANY"]}>XYZ Company</{TAGS["COMPANY"]}> and can be reached at <{TAGS["EMAIL"]}>jan.novak@example.com</{TAGS["EMAIL"]}> <{TAGS["PHONE"]}>+420 123 456 789</{TAGS["PHONE"]}>. More information is available.

        Return only the original text with the added tags.
        Do not remove whitespaces.
        Do not include any explanation or additional text content in the response.
        """
    },
    {
        "role": "user",
        "content": ""
    }
]



clientManager = OpenAIClientManager(API_INFO)


COUNT_POSITION = get_latest_position(INPUT_FILE)
PREV_COUNT_POS = COUNT_POSITION
RAW_PREV_COUNT_POS = COUNT_POSITION

WHILE_ITERATOR = 0

while WHILE_ITERATOR != REQUEST_COUNT:
    WHILE_ITERATOR += 1
    #-----

    input_text, positions = read_text_file(INPUT_FILE, \
        COUNT_POSITION, REQUEST_APPROXIMATE_CHAR_LENGTH)
    COUNT_POSITION = positions[-1]

    #-----
    if COUNT_POSITION == RAW_PREV_COUNT_POS:
        print(f"End of text file (most likely) reached ({COUNT_POSITION})")
        break
    #-----

    chat_prompt[1]["content"] = input_text

    llm_response_text = clientManager.chat(chat_prompt, TEMPERATURE)

    #print(llm_response_text)

    llm_response_text = re.sub(r'<think>.*?</think>', '', llm_response_text, flags=re.DOTALL)

    response_parsed_object = parse_tagged_text(llm_response_text)

    # changes log
    POSITION_STRING = \
        f"----- {PREV_COUNT_POS & FTELL_MASK:16} - {COUNT_POSITION & FTELL_MASK:16} -----"
    print(POSITION_STRING)

    a, r = text_changes_check(input_text, reconstruct_text(response_parsed_object))

    # print(response_parsed_object)
    # print(reconstruct_text(response_parsed_object))
    # print(a, r)

    ADDED_COUNT = len(a)
    REMOVED_COUNT = len(r)
    IS_ADDED_OVER_LIMIT = ADDED_COUNT > ADDED_RESEND_TOL
    IS_REMOVED_OVER_LIMIT = REMOVED_COUNT > REMOVED_RESEND_TOL
    if IS_ADDED_OVER_LIMIT:
        print(f"Too many added words: {ADDED_COUNT}, limit is {ADDED_RESEND_TOL}")
    if IS_REMOVED_OVER_LIMIT:
        print(f"Too many removed words: {REMOVED_COUNT}, limit is {REMOVED_RESEND_TOL}")
    if IS_ADDED_OVER_LIMIT or IS_REMOVED_OVER_LIMIT:
        print("--------------------- !!! RESENDING !!! ---------------------")
        PREV_COUNT_POS = positions[1]
        COUNT_POSITION = positions[1]
        continue
    #-----
    RAW_PREV_COUNT_POS = COUNT_POSITION
    #-----

    TEXT_CHANGES_TOSTRING = text_changes_string(a, r)
    print(TEXT_CHANGES_TOSTRING)

    CHANGES_OUTPUT = "\n".join([POSITION_STRING, TEXT_CHANGES_TOSTRING])
    append_to_changes_log(INPUT_FILE, CHANGES_OUTPUT)

    #modifies response_parsed_object
    clean_up_categories(response_parsed_object)

    #modifies response_parsed_object
    REVERSE_INDEX = correct_object_and_get_reverse_index(response_parsed_object, input_text)
    COUNT_POSITION = positions[REVERSE_INDEX]

    append_json_string_to_file(object_to_json(response_parsed_object), INPUT_FILE)

    write_tagged_sections_to_files(response_parsed_object, INPUT_FILE)

    write_latest_position(INPUT_FILE, COUNT_POSITION)


    #-----
    PREV_COUNT_POS = COUNT_POSITION
