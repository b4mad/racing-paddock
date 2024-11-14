import datetime

from dirtyfields import DirtyFieldsMixin
from django.db import models
from django_prometheus.models import ExportModelOperationsMixin
from model_utils.models import TimeStampedModel


class Lap(ExportModelOperationsMixin("lap"), DirtyFieldsMixin, TimeStampedModel):
    number = models.IntegerField()
    start = models.DateTimeField(default=datetime.datetime.now)
    end = models.DateTimeField(default=datetime.datetime.now)
    time = models.FloatField(default=0)
    official_time = models.FloatField(default=0)
    length = models.IntegerField(default=0)
    valid = models.BooleanField(default=False)
    completed = models.BooleanField(default=True)

    session = models.ForeignKey("Session", on_delete=models.CASCADE, related_name="laps")
    track = models.ForeignKey("Track", on_delete=models.CASCADE, related_name="laps")
    car = models.ForeignKey("Car", on_delete=models.CASCADE, related_name="laps")
    fast_lap = models.ForeignKey("FastLap", on_delete=models.CASCADE, related_name="laps", null=True)

    # class Meta:
    #     ordering = [
    #         "number",
    #     ]

    def __str__(self):
        return f"{self.number}: {self.start.strftime('%H:%M:%S')} - {self.end.strftime('%H:%M:%S')} " + f"{self.time}s {self.length}m valid: {self.valid}"

    def time_human(self):
        minutes = int(self.time // 60)
        seconds = round(self.time % 60, 2)
        # milliseconds = int((coach_lap_time % 1) * 1000)
        time_string = ""
        if minutes > 1:
            time_string += f"{minutes} minutes "
        elif minutes == 1:
            time_string += f"{minutes} minute "

        time_string += f"{seconds:.2f} seconds "

        return time_string
