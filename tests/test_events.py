from datetime import datetime
import unittest

from headline.helpers.events import Event, count_back_to_back_events


class TestBackToBackEvents(unittest.TestCase):
    def test_b2b_events(self):
        self.assertEqual(
            count_back_to_back_events(
                [
                    Event(datetime(2022, 1, 1, 18, 0), datetime(2022, 1, 1, 19, 0)),
                    Event(datetime(2022, 1, 1, 17, 0), datetime(2022, 1, 1, 18, 0)),
                    Event(datetime(2022, 1, 1, 13, 0), datetime(2022, 1, 1, 14, 0)),
                ]
            ),
            2,
        )

    def test_b2b_events_with_gap(self):
        self.assertEqual(
            count_back_to_back_events(
                [
                    Event(datetime(2022, 1, 1, 13, 0), datetime(2022, 1, 1, 14, 0)),
                    Event(datetime(2022, 1, 1, 10, 0), datetime(2022, 1, 1, 11, 0)),
                    Event(datetime(2022, 1, 1, 11, 5), datetime(2022, 1, 1, 11, 30)),
                ]
            ),
            2,
        )
