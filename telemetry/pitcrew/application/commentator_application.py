from telemetry.pitcrew.application.application import Application


class CommentatorApplication(Application):
    def __init__(self, session, history, coach):
        super().__init__(session, history, coach)
        self.car = self.session.car
        self.send_response(f"You've selected the {self.car} for this session.")

    def notify(self, distance, telemetry, now):
        pass

    def yield_responses(self):
        while self.responses:
            yield self.responses.pop(0)
