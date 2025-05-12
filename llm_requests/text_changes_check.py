"""
Module for comparing two texts and calculating the differences.
This module includes functions to check the differences between two given texts 
and print out the count and content of added and removed words.
"""
from difflib import ndiff


def text_changes_check(text1, text2):
    """
    Compares two texts and identifies added and removed words by using the ndiff method.
    
    This function splits the texts into words, compares them, and identifies the words that 
    were added to or removed from the second text. It then prints the count and list of 
    added and removed words using the `print_changes` function.

    Args:
        text1 (str): The first text to be compared.
        text2 (str): The second text to be compared.

    Returns:
        string
    """
    words1 = text1.split()
    words2 = text2.split()

    diff = list(ndiff(words1, words2))

    added_words = []
    removed_words = []

    for change in diff:
        if change.startswith('+ '):
            added_words.append(change[2:])
        elif change.startswith('- '):
            removed_words.append(change[2:])

    return added_words, removed_words

def text_changes_string(added_words, removed_words) -> str:
    """text_changes_check result to string"""
    # pylint: disable=line-too-long
    return f"{len(added_words):3}   added: {' '.join(added_words)}\n{len(removed_words):3} removed: {' '.join(removed_words)}"


if __name__ == "__main__":
    TEXT1 = "Dnes je zítra a dnes hezké slunečné ráno. taky"
    TEXT2 = "Dnes bylo a bude hezké slunečné ráno."
    a, r = text_changes_check(TEXT1, TEXT2)
    print(text_changes_string(a, r))
