from telemetry.pitcrew.application.application import Application
from telemetry.pitcrew.application.response import ResponseTts


class CommentatorApplication(Application):
    def __init__(self, session, history, coach):
        super().__init__(session, history, coach)
        if session.session_type and session.session_type.type == "NewSession":
            self.car = self.session.car
            txt = f"{self.car}"
            message = ResponseTts(txt)
            self.send_response(message)

            track = self.session.track
            txt = f"{track}"
            message = ResponseTts(txt)
            self.send_response(message)

            message = ResponseTts("Let's go!")
            self.send_response(message)

    def notify(self, distance, telemetry, now):
        # self.log_debug(f"notify: {distance} {telemetry}")
        pass
