"""
Module with text dtw alignment methods
"""

import difflib

# pylint: disable=line-too-long

def dtw_alignment(seq1: list[dict], seq2: list[dict], gap=0.1, dist=None):
    """
    DTW alignment for lists of dictionaries where each dictionary contains a 'text' and 'id' field.

    :param seq1: First list of dictionaries with "text" and "id".
    :param seq2: Second list of dictionaries with "text" and "id".
    :param gap: The cost of inserting a gap.
    :param dist: A custom distance function. Defaults to 1 - similarity ratio.
    :return: Tuple of two aligned sequences.
    """

    if dist is None:
        def dist(a, b):
            return 1 - difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()

    n, m = len(seq1), len(seq2)
    dtw = [[float('inf')] * (m + 1) for _ in range(n + 1)]
    dtw[0][0] = 0

    for i in range(1, n + 1):
        dtw[i][0] = dtw[i - 1][0] + gap
    for j in range(1, m + 1):
        dtw[0][j] = dtw[0][j - 1] + gap

    # Fill matrix
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            cost = dist(seq1[i - 1]["text"], seq2[j - 1]["text"])
            dtw[i][j] = min(
                dtw[i - 1][j] + gap,     # insertion in seq2
                dtw[i][j - 1] + gap,     # insertion in seq1
                dtw[i - 1][j - 1] + cost # match/mismatch
            )

    # Backtrack
    aligned1, aligned2 = [], []
    i, j = n, m
    while i > 0 or j > 0:
        if i > 0 and j > 0 and dtw[i][j] == dtw[i - 1][j - 1] + dist(seq1[i - 1]["text"], seq2[j - 1]["text"]):
            aligned1.append(seq1[i - 1])
            aligned2.append(seq2[j - 1])
            i -= 1
            j -= 1
        elif i > 0 and dtw[i][j] == dtw[i - 1][j] + gap:
            aligned1.append(seq1[i - 1])
            aligned2.append({})
            i -= 1
        else:
            aligned1.append({})
            aligned2.append(seq2[j - 1])
            j -= 1

    return aligned1[::-1], aligned2[::-1]


if __name__ == "__main__":
    # Příklad použití:
    SEQ1 = [{"text": "hello", "category": "idk", "id": 1}, {"text": "world", "id": 2}, {"text": "this", "id": 2}, {"text": "is", "id": 3}, {"text": "DTW", "id": 4}, {"text": "test", "id": 3}]
    SEQ2 = [{"text": "hello", "id": 1}, {"text": "this", "id": 2}, {"text": "DTW", "id": 4}, {"text": "world", "id": 5}]

    align1, align2 = dtw_alignment(SEQ1, SEQ2)
    for a1, a2 in zip(align1, align2):
        print(f"Seq1: {a1}, Seq2: {a2}")
