from django.db import models
from model_utils.models import TimeStampedModel


class Track(TimeStampedModel):
    class Meta:
        ordering = [
            "name",
        ]

    name = models.CharField(max_length=200)
    length = models.IntegerField(default=0)

    game = models.ForeignKey("Game", on_delete=models.CASCADE, related_name="tracks")

    def __str__(self):
        return self.name
