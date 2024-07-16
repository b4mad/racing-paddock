from django.db import models
from model_utils.models import TimeStampedModel
from .landmark import Landmark


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

    def get_landmark(self, distance=0):
        if not hasattr(self, '_landmarks_cache'):
            self._landmarks_cache = list(self.landmarks.filter(kind=Landmark.KIND_SEGMENT))
        
        for landmark in self._landmarks_cache:
            if landmark.start <= distance <= landmark.end:
                return landmark
        return None
