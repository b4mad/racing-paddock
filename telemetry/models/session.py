from __future__ import annotations

import datetime
from typing import Optional

import django.utils.timezone
from dirtyfields import DirtyFieldsMixin
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin
from loguru import logger
from model_utils.models import TimeStampedModel

from .landmark import Landmark
from .lap import Lap
from .segment import Segment
from .track import Track


class Session(ExportModelOperationsMixin("session"), DirtyFieldsMixin, TimeStampedModel):
    session_id = models.CharField(max_length=200)
    start = models.DateTimeField(default=datetime.datetime.now)
    end = models.DateTimeField(default=datetime.datetime.now)

    driver = models.ForeignKey("Driver", on_delete=models.CASCADE, related_name="sessions")
    session_type = models.ForeignKey("SessionType", on_delete=models.CASCADE, related_name="sessions")
    game = models.ForeignKey("Game", on_delete=models.CASCADE, related_name="sessions")
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="sessions", null=True)
    car = models.ForeignKey("Car", on_delete=models.CASCADE, related_name="sessions", null=True)

    class Meta:
        unique_together = (
            "driver",
            "session_id",
            "session_type",
            "game",
        )

    def __str__(self):
        return self.session_id

    def analyze(self, telemetry, now) -> None:
        raise Exception("Call 'prepare_for_analysis' first")

    def prepare_for_analysis(self):
        self.current_lap_time = -1
        self.distance_round_track = 1_000_000_000
        self.current_lap: Optional[Lap] = None
        self.previous_lap = None
        self.previous_distance = -1
        self.previous_lap_time = -1
        self.previous_lap_time_previous = -1
        self.telemetry_valid = True
        self.current_landmark: Optional[Landmark] = None
        self.current_segment: Optional[Segment] = None
        if self.game.name == "Richard Burns Rally":
            self.analyze = self.analyze_rbr
        else:
            self.analyze = self.analyze_other

    def save_analysis(self):
        self.save_dirty_fields()
        if self.current_lap:
            self.current_lap.save_dirty_fields()

    def signal(self, telemetry, now=None):
        now = now or django.utils.timezone.now()
        self.end = now
        self.analyze(telemetry, now)
        self.analyze_segment(telemetry, now)

    def analyze_segment(self, telemetry, now):
        if not self.current_lap or not self.track:
            return

        distance = telemetry.get("DistanceRoundTrack")
        if distance is None:
            return

        # Check if distance is in the current landmark
        if not self.current_landmark or not (self.current_landmark.start <= distance <= self.current_landmark.end):
            # Get the new landmark for the distance
            new_landmark = self.track.get_landmark(distance)
            if not new_landmark:
                return
            self.current_landmark = new_landmark

            if self.current_segment:
                logger.debug(f"Saving segment: {self.current_segment} with coasting time: {self.current_segment.coasting_time}")
                self.current_segment.save()

            # Create a new segment for the current_lap based on the new landmark
            self.current_segment = Segment.get_or_create_for_lap_and_landmark(self.current_lap, self.current_landmark)

        if self.current_segment:
            self.current_segment.analyze(telemetry, distance)

    def new_lap(self, now, number) -> "Lap":
        # lap = self.laps.model(number=number, start=now, end=now)
        lap, lap_created = self.laps.get_or_create(
            number=number, track=self.track, car=self.car, defaults={"start": now, "end": now}
        )
        if lap_created:
            logger.debug(f"Creating new lap: {lap}")
        else:
            logger.debug(f"Found existing lap: {lap}")
        self.previous_lap = self.current_lap
        if self.previous_lap:
            self.previous_lap.end = now
            self.previous_lap.save_dirty_fields()
        self.current_lap = lap

        logger.debug(f"new lap: {number}")
        # self.log_debug(f"\tdistance: {distance} / {self.previous_distance}")
        # self.log_debug(f"\tcurrent_lap: {self.current_lap.number}") if self.current_lap else None
        return lap

    def analyze_rbr(self, telemetry, now):
        try:
            distance = telemetry["DistanceRoundTrack"]
            current_lap = telemetry["CurrentLap"]
            lap_time = telemetry["CurrentLapTime"]
        except (KeyError, TypeError):
            if self.telemetry_valid:
                logger.debug(f"Invalid telemetry: {telemetry}")
                self.telemetry_valid = False
            return

        if distance is None or current_lap is None or lap_time is None:
            if self.telemetry_valid:
                logger.debug(f"fields are None: {telemetry}")
                self.telemetry_valid = False
            return

        self.telemetry_valid = True

        if not self.current_lap:
            # RBR has only one lap
            self.new_lap(now, current_lap)
            self.previous_tick_time = -1
            self.previous_tick_distance = 100_000_000
            self.counter_time_not_updated = 0
            self.counter_distance_updated = 0
            self.current_lap.valid = True

        if self.current_lap:
            if distance > self.current_lap.length:
                self.current_lap.length = distance
            self.current_lap.time = lap_time

        # self.current_lap.touch(now)
        # at the end of the session, lap_time stops, but distance keeps increasing
        if self.previous_tick_time == lap_time:
            self.counter_time_not_updated += 1
        else:
            self.counter_time_not_updated = 0

        if self.previous_tick_distance < distance:
            self.counter_distance_updated += 1
        else:
            self.counter_distance_updated = 0

        if self.counter_time_not_updated > 10 and self.counter_distance_updated > 10:
            self.current_lap.completed = True
            self.current_lap.end = now

        self.previous_tick_time = lap_time
        self.previous_tick_distance = distance

    def analyze_other(self, telemetry, now) -> None:
        try:
            distance = telemetry["DistanceRoundTrack"]
            current_lap = telemetry["CurrentLap"]
            lap_time = telemetry["CurrentLapTime"]
            lap_time_previous = telemetry["LapTimePrevious"]
            lap_is_valid = telemetry["CurrentLapIsValid"]
            previous_lap_was_valid = telemetry["PreviousLapWasValid"]
        except (KeyError, TypeError):
            if self.telemetry_valid:
                logger.debug(f"Invalid telemetry: {telemetry}")
                self.telemetry_valid = False
            return

        if distance is None or current_lap is None or lap_time is None or lap_is_valid is None:
            if self.telemetry_valid:
                logger.debug(f"fields are None: {telemetry}")
                self.telemetry_valid = False
            return

        self.telemetry_valid = True
        # check if we're in a new lap, i.e. we're driving over the finish line
        #   ie. distance is lower than the previous distance
        #   and below a threshold of 100 meters
        # self.log_debug(f"distance: {distance}")

        # FIXME: the "crossed_finish_line" logic is brittle
        #  for ACC its 100 meters, for iRacing its 10 meters

        crossed_finish_line = distance < self.previous_distance and distance < 100
        lap_number_increased = self.current_lap and current_lap > self.current_lap.number

        if crossed_finish_line and not self.current_lap:
            # first lap
            self.new_lap(now, current_lap)
        elif lap_number_increased:
            self.new_lap(now, current_lap)

        if self.current_lap:
            if distance > self.current_lap.length:
                self.current_lap.length = distance
            self.current_lap.valid = lap_is_valid
            # self.current_lap.time = lap_time

        if lap_time_previous != self.previous_lap_time_previous:
            if self.previous_lap:
                self.previous_lap.time = lap_time_previous
                self.previous_lap.valid = previous_lap_was_valid
                self.previous_lap.finished = True
                logger.debug(f"lap {self.previous_lap.number} time {lap_time_previous} valid {previous_lap_was_valid}")

        self.previous_distance = distance
        self.previous_lap_time = lap_time
        self.previous_lap_time_previous = lap_time_previous
        return
