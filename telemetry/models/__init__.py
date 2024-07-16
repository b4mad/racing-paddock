from django.db import models
from django.db.models import CASCADE
from django_prometheus.models import ExportModelOperationsMixin
from model_utils.models import TimeStampedModel
from picklefield.fields import PickledObjectField

from .landmark import Landmark
from .lap import Lap  # noqa
from .session import Session  # noqa
from .track import Track


class Driver(ExportModelOperationsMixin("driver"), TimeStampedModel):
    class Meta:
        ordering = [
            "name",
        ]

    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Game(TimeStampedModel):
    class Meta:
        ordering = [
            "name",
        ]

    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Car(TimeStampedModel):
    class Meta:
        ordering = [
            "name",
        ]

    name = models.CharField(max_length=200)

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="cars")
    car_class = models.ForeignKey("CarClass", on_delete=models.CASCADE, related_name="cars", null=True)

    def __str__(self):
        return self.name


class CarClass(TimeStampedModel):
    class Meta:
        ordering = [
            "name",
        ]

    name = models.CharField(max_length=200)

    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="car_classes")

    def __str__(self):
        return self.name


class SessionType(TimeStampedModel):
    type = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.type


class FastLap(ExportModelOperationsMixin("fastlap"), TimeStampedModel):
    game = models.ForeignKey("Game", on_delete=CASCADE, related_name="fast_laps")
    car = models.ForeignKey("Car", on_delete=CASCADE, related_name="fast_laps")
    track = models.ForeignKey("Track", on_delete=CASCADE, related_name="fast_laps")
    driver = models.ForeignKey("Driver", on_delete=CASCADE, related_name="fast_laps", null=True)
    # add binary field to hold arbitrary data
    data = PickledObjectField(null=True)

    class Meta:
        ordering = ["game", "car", "track"]

    def __str__(self):
        return f"{self.pk}: {self.game} {self.car} {self.track}"


class FastLapSegment(TimeStampedModel):
    turn = models.CharField(max_length=200)
    start = models.IntegerField(default=0)
    end = models.IntegerField(default=0)
    brake = models.IntegerField(default=0)
    turn_in = models.IntegerField(default=0)
    force = models.IntegerField(default=0)
    gear = models.IntegerField(default=0)
    # stop is the time the brake force starts to decrease
    stop = models.IntegerField(default=0)
    accelerate = models.IntegerField(default=0)
    speed = models.IntegerField(default=0)
    mark = models.CharField(max_length=256, default="")

    fast_lap = models.ForeignKey(FastLap, on_delete=models.CASCADE, related_name="fast_lap_segments")

    def __str__(self):
        repr = f"{self.turn}: {self.start} - {self.end} brake: {self.brake} "
        repr += f"turn_in: {self.turn_in} force: {self.force} gear: {self.gear} stop: {self.stop} "
        repr += f"acc: {self.accelerate} speed: {self.speed} mark: {self.mark}"
        return repr


class Coach(ExportModelOperationsMixin("coach"), TimeStampedModel):
    driver = models.OneToOneField(
        Driver,
        on_delete=models.CASCADE,
        primary_key=True,
    )

    error = models.TextField(default="")
    status = models.TextField(default="")
    enabled = models.BooleanField(default=False)

    fast_lap = models.ForeignKey(FastLap, on_delete=models.SET_NULL, related_name="coaches", null=True)

    MODE_DEFAULT = "default"
    MODE_TRACK_GUIDE = "track_guide"
    MODE_TRACK_GUIDE_APP = "track_guide_app"
    MODE_DEBUG_APP = "debug_app"
    MODE_DEBUG = "debug"
    MODE_ONLY_BRAKE = "only_brake"
    MODE_ONLY_BRAKE_DEBUG = "only_brake_debug"
    MODE_COPILOTS = "copilots"
    MODE_CHOICES = [
        (MODE_DEFAULT, "Default"),
        (MODE_COPILOTS, "Copilots"),
        (MODE_TRACK_GUIDE, "Track Guide"),
        (MODE_TRACK_GUIDE_APP, "Track Guide Application"),
        (MODE_DEBUG_APP, "Debug Application"),
        (MODE_DEBUG, "Debug"),
        (MODE_ONLY_BRAKE, "Only Brakepoints"),
        (MODE_ONLY_BRAKE_DEBUG, "Only Brakepoints (Debug))"),
    ]
    mode = models.CharField(max_length=64, default=MODE_DEFAULT, choices=MODE_CHOICES)

    def __str__(self):
        return self.driver.name


class TrackGuide(TimeStampedModel):
    name = models.CharField(max_length=200)
    description = models.TextField(default="")
    car = models.ForeignKey("Car", on_delete=CASCADE)
    track = models.ForeignKey("Track", on_delete=CASCADE)

    def car_game(self):
        return self.car.game

    def __str__(self):
        return f"{self.name}"


class TrackGuideNote(TimeStampedModel):
    track_guide = models.ForeignKey(TrackGuide, on_delete=models.CASCADE, related_name="notes")

    landmark = models.ForeignKey(Landmark, on_delete=models.CASCADE, related_name="notes", null=True)
    segment = models.IntegerField(default=0)
    finish_at = models.TextField(null=True)
    at = models.CharField(max_length=64, default="")

    priority = models.IntegerField(default=0)
    ref_id = models.CharField(max_length=64, default="")
    ref_eval = models.CharField(max_length=64, default="")

    sort_key = models.CharField(max_length=64, default="")
    mode = models.CharField(max_length=64, default="")

    message = models.TextField(default="")
    eval = models.TextField(default="")
    notes = models.TextField(default="")
    score = models.CharField(max_length=64, default="")

    def __str__(self):
        repr = f"{self.segment or self.landmark} - at {self.at or self.finish_at}: {self.message}"
        return repr


class Segment(TimeStampedModel):
    lap = models.ForeignKey("Lap", on_delete=models.CASCADE, related_name="segments")
    landmark = models.ForeignKey(Landmark, on_delete=models.CASCADE, related_name="segments")

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
    coasting_time = models.PositiveIntegerField(null=True)

    def __str__(self):
        return f"Segment for Lap {self.lap.number} - Landmark: {self.landmark.name}"


class ReferenceSegment(Segment):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name="reference_segments")
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name="reference_segments")


class SoundClip(TimeStampedModel):
    subtitle = models.TextField()
    voice = models.CharField(max_length=200)
    model = models.CharField(max_length=200)
    audio_file = models.FileField(upload_to="sound_clips/")

    def __str__(self):
        return f"{self.voice} - {self.subtitle[:50]}"
