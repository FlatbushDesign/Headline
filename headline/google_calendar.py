from typing import List
from datetime import datetime, timedelta

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from headline.google_client import get_google_credentials
from headline.provider import Provider


def _parse_iso_datetime(input: str):
    return datetime.strptime(input, "%Y-%m-%dT%H:%M:%S%z")


def _datetime_to_iso(date: datetime):
    return date.isoformat() + "Z"


class GoogleCalendar(Provider):
    def __init__(self) -> None:
        super().__init__()

        self.service = build("calendar", "v3", credentials=get_google_credentials())

    def _get_busy_time(self, time_min: datetime, time_max: datetime, calendars: List[str] = None):
        body = {
            "timeMin": _datetime_to_iso(time_min),
            "timeMax": _datetime_to_iso(time_max),
            "items": [ { "id": calendar } for calendar in (calendars or ["primary"]) ],
        }

        response = self.service.freebusy().query(body=body).execute()

        total_busy = timedelta()

        for calendar_id, calendar in response["calendars"].items():
            for busy in calendar["busy"]:
                total_busy += _parse_iso_datetime(busy["end"]) - _parse_iso_datetime(busy["start"])

        return total_busy

    def run(self, data):
        try:
            # Call the Calendar API
            now = (
                datetime(2022, 1, 1).isoformat() + "Z"
            )  # 'Z' indicates UTC time
            events_result = (
                self.service.events()
                .list(
                    calendarId="primary",
                    timeMin=now,
                    maxResults=10,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])

            result = {
                "meetings_duration_total": 0,
                "meetings_recurrent_count": 0,
                "busy_time": self._get_busy_time(datetime.today(), datetime.today() + timedelta(days=1)).seconds,
            }

            # Prints the start and name of the next 10 events
            for event in events:
                start = _parse_iso_datetime(
                    event["start"].get("dateTime", event["start"].get("date"))
                )
                end = _parse_iso_datetime(
                    event["end"].get("dateTime", event["end"].get("date"))
                )
                duration = end - start

                is_recurrent = bool(event.get("recurringEventId")) or bool(event.get("recurrence"))
                if is_recurrent:
                    result["meetings_recurrent_count"] += 1

                result["meetings_duration_total"] += duration.seconds

            return result

        except HttpError as error:
            print("An error occurred: %s" % error, error.error_details)
