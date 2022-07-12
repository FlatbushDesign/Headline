from operator import attrgetter
from typing import List
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class Event:
    start: datetime
    end: datetime

    @property
    def duration(self):
        return self.end - self.start


BACK_TO_BACK_THRESHOLD = timedelta(minutes=5)


def count_back_to_back_events(events: List[Event]):
    total = 1

    sorted_events = sorted(events, key=attrgetter("start"))

    for i, event in enumerate(sorted_events):
        if i == 0:
            continue

        previous_event = sorted_events[i - 1]

        if (event.start - previous_event.end) <= BACK_TO_BACK_THRESHOLD:
            total += 1

    return total if total > 1 else 0
