#!/usr/bin/env python3

from typing import Dict, List

from datetime import datetime
import json
from pathlib import Path

from headline.gmail import Gmail
from headline.google_calendar import GoogleCalendar
from headline.provider import Provider
from headline.slack import Slack


DATA_PROVIDERS: Dict[str, Provider] = {
    "slack": Slack(),
    "google.calendar": GoogleCalendar(),
    "google.gmail": Gmail(),
}


def get_data_file(name: str):
    return Path().parent / "data" / name


def get_subscriptions() -> List[dict]:
    with open(get_data_file("subscriptions.json")) as f:
        return json.load(f)


def save_data(data: dict, date: datetime = None):
    data["date"] = date or datetime.today().isoformat()
    data["created_at"] = datetime.today().isoformat()

    with open(get_data_file("output.jsonl"), "a") as f:
        f.write(json.dumps(data) + "\n")


def main():
    for subscription in get_subscriptions():
        provider_id = subscription.get("provider")
        provider = DATA_PROVIDERS[provider_id]

        data = provider.run(subscription.get("data"))

        save_data({
            "provider": provider_id,
            "data": data,
        })


if __name__ == "__main__":
    main()
