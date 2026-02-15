import time

class FatigueTracker:
    def __init__(self):
        self.bad_posture_start = None
        self.total_bad_time = 0
        self.session_start = time.time()

    def update(self, posture):
        now = time.time()

        if posture == "Bad":
            if self.bad_posture_start is None:
                self.bad_posture_start = now
        else:
            if self.bad_posture_start is not None:
                self.total_bad_time += now - self.bad_posture_start
                self.bad_posture_start = None

    def get_bad_duration(self):
        if self.bad_posture_start:
            return int(time.time() - self.bad_posture_start)
        return 0

    def get_session_duration(self):
        return int(time.time() - self.session_start)

    def get_fatigue_score(self):
        session = self.get_session_duration()
        bad_total = self.total_bad_time + self.get_bad_duration()

        # fatigue increases from posture
        posture_component = bad_total * 0.5

        # fatigue increases from long sitting
        sitting_component = session / 20

        score = posture_component + sitting_component
        return min(100, int(score))

    def should_alert(self):
        return self.get_bad_duration() > 6
