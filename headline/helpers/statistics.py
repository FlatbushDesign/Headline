from typing import Dict, List


def most_occurring(items: List[str], descending=True):
    # Associate key and occurrence count
    occurrences_count: Dict[str, int] = {}

    for item in items:
        if not item in occurrences_count:
            occurrences_count[item] = 0

        occurrences_count[item] += 1

    return sorted(
        occurrences_count.items(), key=lambda item: item[1], reverse=descending
    )
