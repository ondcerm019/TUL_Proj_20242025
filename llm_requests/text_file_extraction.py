"""
Module for reading a specified number of valid characters from a text file.

This module provides a function to extract a given number of characters from a text file,
ignoring line breaks and reducing consecutive spaces to a single space.
It ensures that the extracted text does not end in the middle of a word.
"""


def read_text_file(file_path: str, position: int, char_count: int) -> tuple[str, list[int]]:
    """
    Reads a section of the file from a given position, ensuring whole words are not split.
    Also returns a list of byte positions marking the ends of words (i.e., the position where
    the whitespace after the word begins).

    :param file_path: Path to the text file.
    :param position: Starting position in the file (byte-based).
    :param char_count: Number of printable characters to read.
    :return: Tuple of the text read and list of byte positions at the ends of words.
    """
    result = []
    word_end_positions = []
    last_space_index = -1
    valid_chars_seen = 0
    previous_was_space = True
    skipping_word = False
    word_in_progress = False

    with open(file_path, "r", encoding="utf-8") as file:
        file.seek(position)

        while True:
            char = file.read(1)
            if not char:
                # EOF, close any open word
                if word_in_progress:
                    word_end_positions.append(file.tell())
                break

            if not char.isprintable():
                char = " "

            if skipping_word:
                if char.isspace():
                    skipping_word = False
                continue

            if valid_chars_seen >= char_count:
                if last_space_index != -1:
                    return "".join(result[:last_space_index]), word_end_positions
                return "".join(result), word_end_positions

            if char.isspace():
                if word_in_progress:
                    word_end_positions.append(file.tell())
                word_in_progress = False
                if previous_was_space:
                    continue
                last_space_index = len(result)
                previous_was_space = True
            else:
                previous_was_space = False
                word_in_progress = True

            result.append(char)
            valid_chars_seen += 1

    return "".join(result), word_end_positions





if __name__ == "__main__":
    TEMP_PATH = r"" # <Cesta k textovému souboru, ze kterého má být vypsán text>
    txt, positions = read_text_file(TEMP_PATH, 0, 100)
    pos = positions[-1]
    print(txt)
    print(pos)
    txt, positions = read_text_file(TEMP_PATH, pos, 100)
    pos = positions[-1]
    print(txt)
    print(pos)
    txt, positions = read_text_file(TEMP_PATH, pos, 100)
    pos = positions[-1]
    print(txt)
    print(pos)
    #36595560 (bytes)
