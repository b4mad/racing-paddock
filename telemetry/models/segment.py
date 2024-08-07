from django.db import models
from loguru import logger
from model_utils.models import TimeStampedModel

from racing_telemetry.analysis import Streaming as StreamingAnalysis


class Segment(TimeStampedModel):
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
    coasting_time = models.PositiveIntegerField(null=True, help_text="Time spent coasting in this segment", verbose_name="Coasting Time in centiseconds")
    launch_wheel_slip_time = models.PositiveIntegerField(null=True, help_text="Duration of wheel slip during launch in centiseconds", verbose_name="Launch Wheel Slip Duration in centiseconds")

    def __str__(self):
        return f"Segment for Lap {self.lap.number} - Landmark: {self.landmark.name}"

    def features_str(self) -> str:
        # return string with all features that are not None, excluding specific fields
        excluded_fields = ["id", "lap", "created", "modified"]
        return ", ".join([f"{field.name}: {getattr(self, field.name)}" for field in self._meta.fields if getattr(self, field.name) is not None and field.name not in excluded_fields])

    def prepare_for_analysis(self):
        self.streaming_analysis = StreamingAnalysis(
            coasting_time=True,
            braking_point=True,
            lift_off_point=True,
            apex=True,
            launch_wheel_slip_time=True,
        )

    def analyze(self, telemetry, distance):
        self.streaming_analysis.notify(telemetry)

    def finalize_analysis(self):
        features = self.streaming_analysis.get_features()
        self.streaming_analysis.calculate_apex()
        self.coasting_time = int(features["coasting_time"] * 100)
        if features["braking_point"] > 0:
            self.braking_point = int(features["braking_point"] * 100)
        if features["lift_off_point"] > 0:
            self.lift_off_point = int(features["lift_off_point"] * 100)
        if features["apex"] > 0:
            self.apex = int(features["apex"] * 100)
        if features["launch_wheel_slip_time"] > 0:
            self.launch_wheel_slip_time = int(features["launch_wheel_slip_time"] * 100)

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
