from telemetry.pitcrew.application.application_no_history import ApplicationNoHistory
from telemetry.pitcrew.application.response import ResponseTts


class CommentatorApplication(ApplicationNoHistory):
    def __init__(self, session, coach):
        super().__init__(session, coach)
        if session.session_type and session.session_type.type == "NewSession":
            self.car = self.session.car
            txt = f"{self.car}"
            message = ResponseTts(txt, immediate=True)
            self.send_response(message)

            track = self.session.track
            txt = f"{track}"
            message = ResponseTts(txt, immediate=True)
            self.send_response(message)

            message = ResponseTts("Let's go!", immediate=True)
            self.send_response(message)

    def notify(self, distance, telemetry, now):
        # self.log_debug(f"notify: {distance} {telemetry}")
        pass
