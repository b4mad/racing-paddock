from telemetry.pitcrew.application.application import Application
from telemetry.pitcrew.application.response import ResponseInstant


class CommentatorApplication(Application):
    def __init__(self, session, history, coach):
        super().__init__(session, history, coach)
        self.car = None

    def notify(self, distance, telemetry, now):
        if self.car is None:
            self.car = self.session.car
            if self.car:
                self.respond(ResponseInstant(f"You've selected the {self.car} for this session."))

    def yield_responses(self):
        while self.responses:
            yield self.responses.pop(0)
