from django.db import models
from model_utils.models import TimeStampedModel
from loguru import logger
from racing_telemetry.analysis import Streaming as StreamingAnalysis


class Segment(TimeStampedModel):
    streaming_analysis = None
    lap = models.ForeignKey("Lap", on_delete=models.CASCADE, related_name="segments")
    landmark = models.ForeignKey("Landmark", on_delete=models.CASCADE, related_name="segments")

    kind = models.CharField(max_length=200, null=True)

    # these are in centimeters
    braking_point = models.PositiveIntegerField(null=True)
    lift_off_point = models.PositiveIntegerField(null=True)
    acceleration_point = models.PositiveIntegerField(null=True)

    # these are from 0 to 100 (percent)
    brake_pressure = models.PositiveSmallIntegerField(null=True)
    brake_application_rate = models.PositiveSmallIntegerField(null=True)
    brake_release_rate = models.PositiveSmallIntegerField(null=True)

    throttle_lift = models.PositiveSmallIntegerField(null=True)
    throttle_application_rate = models.PositiveSmallIntegerField(null=True)
    throttle_release_rate = models.PositiveSmallIntegerField(null=True)

    # these are in centimeters
    apex = models.PositiveIntegerField(null=True)

    # these are in meters per second
    entry_speed = models.PositiveSmallIntegerField(null=True)
    corner_speed = models.PositiveSmallIntegerField(null=True)
    exit_speed = models.PositiveSmallIntegerField(null=True)

    gear = models.PositiveSmallIntegerField(null=True)

    # this is in hundreds of a second
    coasting_time = models.PositiveIntegerField(
        null=True, help_text="Time spent coasting in this segment", verbose_name="Coasting Time in centiseconds"
    )

    def __str__(self):
        return f"Segment for Lap {self.lap.number} - Landmark: {self.landmark.name}"

    def analyze(self, telemetry, distance):
        if not self.streaming_analysis:
            self.streaming_analysis = StreamingAnalysis(coasting_time=True)

        self.streaming_analysis.notify(telemetry)
        features = self.streaming_analysis.get_features()
        self.coasting_time = int(features["coasting_time"] * 100)

    @classmethod
    def get_or_create_for_lap_and_landmark(cls, lap, landmark):
        segment, created = cls.objects.get_or_create(
            lap=lap,
            landmark=landmark,
        )
        if created:
            logger.debug(f"New segment: {segment}")
        else:
            logger.debug(f"Found existing segment: {segment}")
        return segment


class ReferenceSegment(Segment):
    track = models.ForeignKey("Track", on_delete=models.CASCADE, related_name="reference_segments")
    driver = models.ForeignKey("Driver", on_delete=models.CASCADE, related_name="reference_segments")
