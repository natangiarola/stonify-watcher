import requests
import json
from datetime import date, timedelta, datetime, time
from zoneinfo import ZoneInfo

def build_date_window(timezone_str = "America/New_York"):
    tz = ZoneInfo(timezone_str)
    today = date.today()

    start_date = today - timedelta(days=2)
    end_date = today + timedelta(days=3)

    dt_start = datetime.combine(start_date, time.min, tzinfo=tz).astimezone(ZoneInfo("UTC"))
    dt_end = datetime.combine(end_date, time(23, 59, 59), tzinfo=tz).astimezone(ZoneInfo("UTC"))

    dt_start_conv = dt_start.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    dt_end_conv = dt_end.strftime("%Y-%m-%dT%H:%M:%S.000Z")

    window = {"from": dt_start_conv, "to": dt_end_conv}
    return window

def fetch_jobs(session_token, calendar_id):
    window = build_date_window()

    payload = {"0":
                   {"json":
                        {"calendarConfigurationId":calendar_id,
                          "dateFromDayStart": window["from"],
                          "dateFromWeekStart": window["from"],
                          "dateToDayEnd": window["to"],
                          "dateToWeekEnd": window["to"],
                          "timeZone": "America/New_York",
                          "filters": {
                              "taskStatusIds": ["TicketComplete"]
                          }
                        },
                    "meta": {
                        "values": {
                            "dateFromDayStart": ["Date"],
                            "dateFromWeekStart": ["Date"],
                            "dateToDayEnd": ["Date"],
                            "dateToWeekEnd": ["Date"],
                        }
                    }
                    }
               }

    input_str = json.dumps(payload)
    params = {"batch": "1",
              "input": input_str}

    headers = {"cookie": "__Secure-next-auth.session-token=" + session_token,
               "x-timezone": "America/New_York",
               "referer": "https://app.stonify.io"}

    response = requests.get("https://app.stonify.io/api/trpc/calendar.getCalendarData",params=params, headers=headers)
    data = response.json()
    return data

def parse_jobs(data):
    cells = data[0]["result"]["data"]["json"]["calendarData"]["cells"]
    jobs = []
    for cell in cells:
        if cell["projectTasks"]:
            for pt in cell["projectTasks"]:
                job = {"project": pt["task"]["project"]["numericId"],
                       "assignee": pt["task"]["assignedUser"]["name"],
                       "type": pt["task"]["taskType"]["name"],
                       "start": pt["task"]["startAt"],
                       "description": pt["task"]["description"],
                       "task_id": pt["task"]["id"]
                       }
                jobs.append(job)

    return jobs