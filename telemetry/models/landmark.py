from django.db import models
from model_utils.models import TimeStampedModel


class Landmark(TimeStampedModel):
    name = models.CharField(max_length=200)
    start = models.IntegerField(null=True)
    end = models.IntegerField(null=True)
    is_overtaking_spot = models.BooleanField(null=True)
    from_cc = models.BooleanField(default=False)

    KIND_MISC = "misc"
    KIND_SEGMENT = "segment"
    KIND_TURN = "turn"
    KIND_CHOICES = [
        (KIND_MISC, "Misc"),
        (KIND_SEGMENT, "Segment"),
        (KIND_TURN, "Turn"),
    ]

    kind = models.CharField(max_length=64, default=KIND_MISC, choices=KIND_CHOICES)

    track = models.ForeignKey("Track", on_delete=models.CASCADE, related_name="landmarks")

    def __str__(self):
        return f"{self.name} ({self.kind}) [{self.start}-{self.end}]"
