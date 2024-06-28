from telemetry.pitcrew.application.application import Application
from telemetry.pitcrew.application.response import ResponseTts


class CommentatorApplication(Application):
    def __init__(self, session, history, coach):
        super().__init__(session, history, coach)
        self.car = self.session.car
        txt = f"You've selected the {self.car} for this session."
        message = ResponseTts(txt)
        self.send_response(message)

    def notify(self, distance, telemetry, now):
        self.log_debug(f"notify: {distance} {telemetry}")
        pass
