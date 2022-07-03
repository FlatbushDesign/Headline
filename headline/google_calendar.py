from operator import itemgetter
from typing import List
from datetime import datetime, timedelta

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from headline.provider import Provider


def _parse_iso_datetime(input: str):
    return datetime.strptime(input, "%Y-%m-%dT%H:%M:%S%z")


def _datetime_to_iso(date: datetime):
    return date.isoformat() + "Z"


class GoogleCalendar(Provider):
    name = "google-calendar"
    credentials: str = "google"

    def __init__(self) -> None:
        super().__init__()

    async def get_default_subscription_data(self, user_credentials: dict) -> dict:
        self.service = build(
            "calendar", "v3", credentials=Credentials(user_credentials["access_token"])
        )

        calendars = self.service.calendarList().list().execute()["items"]

        return {"calendars": [calendar["id"] for calendar in calendars]}

    def _get_busy_time(
        self, time_min: datetime, time_max: datetime, calendars: List[str] = None
    ):
        body = {
            "timeMin": _datetime_to_iso(time_min),
            "timeMax": _datetime_to_iso(time_max),
            "items": [{"id": calendar} for calendar in (calendars or ["primary"])],
        }

        response = self.service.freebusy().query(body=body).execute()

        total_busy = timedelta()

        for calendar_id, calendar in response["calendars"].items():
            for busy in calendar["busy"]:
                total_busy += _parse_iso_datetime(busy["end"]) - _parse_iso_datetime(
                    busy["start"]
                )

        return total_busy

    def _get_calendars_events(
        self, time_min: datetime, time_max: datetime, calendars: List[str] = None
    ):
        events_result = (
            self.service.events()
            .list(
                calendarId=calendars[0],
                timeMin=_datetime_to_iso(time_min),
                timeMax=_datetime_to_iso(time_max),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )
        return events_result.get("items", [])

    async def run(self, data: dict, user_credentials: dict):
        self.service = build(
            "calendar", "v3", credentials=Credentials(user_credentials["access_token"])
        )

        user_email_address = user_credentials["user_info"]["email"]
        calendars = data.get("calendars", ["primary"])

        try:
            busy_time_tomorrow = self._get_busy_time(
                time_min=datetime.today(),
                time_max=datetime.today() + timedelta(days=1),
                calendars=calendars,
            ).seconds

            result = {
                "meetings_duration_total": 0,
                "meetings_recurrent_count": 0,
                "meetings_count": 0,
                "most_met": [],
                "busy_time_tomorrow": busy_time_tomorrow,
            }

            time_min = datetime.today().replace(hour=0, minute=0)
            time_max = datetime.today()
            events = self._get_calendars_events(time_min, time_max, calendars)

            attendees_met_count = {}

            for event in events:
                start = _parse_iso_datetime(
                    event["start"].get("dateTime", event["start"].get("date"))
                )
                end = _parse_iso_datetime(
                    event["end"].get("dateTime", event["end"].get("date"))
                )
                duration = end - start

                is_recurrent = bool(event.get("recurringEventId")) or bool(
                    event.get("recurrence")
                )
                if is_recurrent:
                    result["meetings_recurrent_count"] += 1
                else:
                    result["meetings_count"] += 1

                result["meetings_duration_total"] += duration.seconds

                attendees: List[dict] = event.get("attendees", [])
                attendees.append(event.get("organizer"))
                attendees.append(event.get("creator"))

                attendees_emails = set(map(itemgetter("email"), attendees))
                for email in attendees_emails:
                    if not email or email == user_email_address:
                        continue

                    if not email in attendees_met_count:
                        attendees_met_count[email] = 0
                    attendees_met_count[email] += 1

            result["most_met"] = sorted(
                attendees_met_count.items(), key=lambda item: item[1], reverse=True
            )

            return result

        except HttpError as error:
            print("An error occurred: %s" % error, error.error_details)
