import threading
from api import fetch_jobs, parse_jobs

class Poller:
    def __init__(self, session_token, calendar_id, interval = 300, on_update = None):
        self.session_token = session_token
        self.calendar_id = calendar_id
        self.interval = interval
        self.on_update = on_update
        self._timer = None

    def _tick(self):
        data = fetch_jobs(self.session_token, self.calendar_id)
        jobs = parse_jobs(data)

        if self.on_update:
            self.on_update(jobs)

        self._timer = threading.Timer(self.interval, self._tick)
        self._timer.start()

    def start(self):
        self._tick()

    def stop(self):
        if self._timer:
            self._timer.cancel()