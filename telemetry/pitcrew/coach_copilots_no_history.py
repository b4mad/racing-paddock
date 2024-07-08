import json

import django.utils.timezone

from b4mad_racing_website.models import CopilotInstance
from telemetry.models import Coach
from telemetry.pitcrew.logging_mixin import LoggingMixin

from .application.commentator_application import CommentatorApplication
from .application.session import Session
from .persister import Persister


class CoachCopilotsNoHistory(LoggingMixin):
    def __init__(self, coach_model: Coach, debug=False):
        self.coach_model = coach_model
        self.response_topic = f"/coach/{coach_model.driver.name}"
        self.persister = Persister(debug=debug)
        self.init_variables()

    def init_variables(self):
        self.responses = []
        self.topic = ""
        self.session_id = ""
        self.distance = 0
        self.track_length = 1
        self._crashed = False
        self.telemetry = {}
        self.apps = []
        self.driver_name = self.coach_model.driver.name

    def filter_from_topic(self, topic):
        frags = topic.split("/")
        driver = frags[1]
        session = frags[2]  # noqa
        game = frags[3]
        track = frags[4]
        car = frags[5]
        session_type = frags[6]
        filter = {
            "Driver": driver,
            "GameName": game,
            "TrackCode": track,
            "CarModel": car,
            "SessionId": session,
            "SessionType": session_type,
        }
        return filter

    def new_session(self, topic):
        self._new_session_starting = True
        self.init_variables()
        self.topic = topic
        filter = self.filter_from_topic(topic)
        self.log_debug("new session %s", topic)
        self.coach_model.refresh_from_db()
        self.filter = filter
        if self.coach_model.enabled is False:
            return

    def ready(self):
        if self._new_session_starting:
            self.session = Session(self.filter)
            self.track_length = self.session.track_length()
            self.init_apps()
            self._new_session_starting = False
        return True

    def init_apps(self):
        # find all copilot instances for this driver
        # where the mqtt_drivername on the driver relation matches self.driver_name
        copilot_instances = CopilotInstance.objects.filter(driver__mqtt_drivername=self.driver_name)
        for copilot_instance in copilot_instances:
            if copilot_instance.enabled():
                copilot = copilot_instance.copilot
                # if copilot.slug == "debug":
                #     self.add_copilot(DebugApplication)
                # elif copilot.slug == "track_guide":
                #     self.add_copilot(TrackGuideApplication)
                # elif copilot.slug == "braker":
                #     self.add_copilot(BrakeApplication)
                if copilot.slug == "commentator":
                    self.add_copilot(CommentatorApplication)

    def add_copilot(self, copilot_klass):
        copilot = copilot_klass(self.session, self)
        if copilot.ready:
            self.log_debug(f"adding copilot: {copilot}")
            self.apps.append(copilot)
        else:
            self.log_debug(f"copilot {copilot} not ready")

        for response in copilot.yield_responses():
            self.respond(response)

    def respond(self, response):
        self.responses.append(response)

    def get_and_reset_error(self):
        if self._error:
            error = self._error
            self._error = None
            return error

    def return_messages(self, store_play_at=True):
        if self.responses:
            responses = []
            for resp in self.responses:
                responses.append(json.dumps(resp.response()))

            self.responses = []
            return (self.response_topic, responses)

    def on_stop(self):
        self.persister.on_stop()

    def notify(self, topic, telemetry, now=None):
        now = now or django.utils.timezone.now()
        self.persister.notify(topic, telemetry, now)
        if self.driver_name == "Jim":
            return

        if self.topic != topic:
            # self.previous_distance = int(telemetry["DistanceRoundTrack"])
            self.previous_distance = -1
            self.previous_delta = 0
            self.new_session(topic)

        if self.coach_model.enabled is False:
            return

        if not self.ready():
            return self.return_messages(store_play_at=False)

        self.distance = int(telemetry["DistanceRoundTrack"])
        if self.distance == self.previous_distance:
            return None

        self.telemetry = telemetry
        self.tick(topic, telemetry, now)
        self.previous_distance = self.distance

        for app in self.apps:
            for response in app.yield_responses():
                self.respond(response)

        return self.return_messages()

    def distance_add(self, distance, meters):
        return (distance + meters) % self.track_length

    def tick(self, topic, telemetry, now=None):

        # for distance in range(start, stop):
        delta = int(3 * int(telemetry["SpeedMs"]) + 10)
        distance = self.distance_add(self.previous_distance, self.previous_delta)

        stop_delta = delta
        if delta < self.previous_delta:
            stop_delta = self.previous_delta
        stop = self.distance_add(self.distance, stop_delta)

        # self.log_debug(f"start at {distance} to {stop} - delta: {delta} - speed: {telemetry['SpeedMs']} m/s {telemetry['SpeedMs'] * 3.6} km/h")
        while distance != stop:
            # self.log_debug(f"d: {distance} ({self.distance})")
            if distance % 100 == 0:
                self.log_debug(f"distance: {distance} ({self.distance})")

            # notify all registered apps
            for app in self.apps:
                app.notify(distance, telemetry, now)

            distance = self.distance_add(distance, 1)

        self.previous_delta = delta
