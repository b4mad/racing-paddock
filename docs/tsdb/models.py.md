from timescale.db.models.fields import TimescaleDateTimeField
from timescale.db.models.models import TimescaleModel


class Telemetry(TimescaleModel):
    # https://www.timescale.com/blog/getting-sensor-data-into-timescaledb-via-django/

    time = models.DateTimeField(blank=False, null=False, primary_key=True)
    # time = TimescaleDateTimeField(interval="1 day")

    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name="telemetry")
    session_id_telemetry = models.CharField(db_column="SessionId", max_length=255)

    current_lap = models.PositiveSmallIntegerField(db_column="CurrentLap")
    current_lap_time = models.FloatField(db_column="CurrentLapTime")

    clutch = models.FloatField(null=True, db_column="Clutch")
    brake = models.FloatField(null=True, db_column="Brake")
    throttle = models.FloatField(null=True, db_column="Throttle")
    handbrake = models.FloatField(null=True, db_column="Handbrake")
    gear = models.PositiveSmallIntegerField(null=True, db_column="Gear")

    current_lap_is_valid = models.BooleanField(db_column="CurrentLapIsValid", null=True)
    distance_round_track = models.FloatField(db_column="DistanceRoundTrack")
    rpms = models.FloatField(db_column="Rpms", null=True)
    speed_ms = models.FloatField(db_column="SpeedMs", null=True)
    steering_angle = models.FloatField(db_column="SteeringAngle", null=True)
    world_position_x = models.FloatField(db_column="WorldPosition_x", null=True)
    world_position_y = models.FloatField(db_column="WorldPosition_y", null=True)
    world_position_z = models.FloatField(db_column="WorldPosition_z", null=True)

    class Meta:
        # unique_together = (('time', 'session_id'),)
        # indexes = [
        #     models.Index(fields=['time', 'session_id']),
        # ]
        # models.UniqueConstraint(fields=['time', 'session_id'], name="time_session_id",)

        managed = False
        # set primary key
