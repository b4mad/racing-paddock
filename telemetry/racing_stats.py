from datetime import timedelta

import django.utils.timezone
from django.db import connection
from django.db.models import CharField, Count, Max, Q, Value
from loguru import logger  # noqa F401

from telemetry.models import FastLap, Game, Lap, Session, Track


class RacingStats:
    def __init__(self, using="default"):
        """Initialize RacingStats with database connection.

        Args:
            using (str, optional): Database connection to use. Defaults to "default".
        """
        self.using = using
        pass

    def combos(self, type="", **kwargs):
        """Convenience method that calls driver_combos().

        Args:
            type (str, optional): Type of racing to filter for ("circuit" or "rally"). Defaults to "".
            **kwargs: Additional arguments passed to driver_combos().

        Returns:
            QuerySet: Results from driver_combos().
        """
        return self.driver_combos(type=type, **kwargs)

    def driver_combos(self, driver=None, range=30, type="circuit", **kwargs):
        """Get combinations of game/track/car with statistics.

        Args:
            driver (str, optional): Filter by driver name. Defaults to None.
            range (int, optional): Number of days to look back. Defaults to 30.
            type (str, optional): Type of racing to filter for:
                - "circuit": Only circuit racing games
                - "rally": Only rally games
                - "": All games
            **kwargs: Additional filter arguments

        Returns:
            QuerySet: Contains for each combo:
                - session__game__name: Game name
                - track__name: Track name ("Multiple" for rally)
                - car__name: Car name
                - lap_count: Total number of laps
                - valid_lap_count: Number of valid laps
                - latest_lap_end: Most recent lap end time

        Example:
            >>> stats = RacingStats()
            >>> # Get circuit combos for last 7 days
            >>> circuit_combos = stats.driver_combos(range=7, type="circuit")
            >>> # Get rally combos for specific driver
            >>> rally_combos = stats.driver_combos(driver="John", type="rally")
        """
        filter = {}
        if driver is not None:
            filter["session__driver__name"] = driver

        # Calculate the start date based on the range
        start_date = django.utils.timezone.now() - timedelta(days=range)

        laps = Lap.objects.filter(**filter)
        # Filter laps based on the end time within the range
        laps = laps.filter(session__end__gte=start_date)
        # group by game, track, and car
        if type == "circuit" or type == "":
            laps = laps.values("session__game__name", "track__name", "car__name", "session__game__id", "track__id", "car__id")
            # annotate with count of laps, valid laps, and latest lap end time
            laps = laps.annotate(lap_count=Count("id"), valid_lap_count=Count("id", filter=Q(valid=True)), latest_lap_end=Max("end"))
            if type == "circuit":
                # exclude all rally games: Richard Burns Rally, Dirt Rally, Dirt Rally 2.0
                laps = laps.exclude(session__game__name__in=["Richard Burns Rally", "Dirt Rally", "Dirt Rally 2.0"])
        elif type == "rally":
            laps = laps.values("session__game__name", "car__name", "session__game__id", "car__id", "track__game__id")
            # add a field called track__name with a hardcoded value of "Multiple"
            laps = laps.annotate(
                track__name=Value("Multiple", output_field=CharField()),
                track__id=Value(0, output_field=CharField()),
                lap_count=Count("id"),
                valid_lap_count=Count("id", filter=Q(valid=True)),
                latest_lap_end=Max("end"),
            )
            # only include rally games: Richard Burns Rally, Dirt Rally, Dirt Rally 2.0
            laps = laps.filter(session__game__name__in=["Richard Burns Rally", "Dirt Rally", "Dirt Rally 2.0"])
        # order by latest lap end time
        laps = laps.order_by("-latest_lap_end")

        # show the sql of the query
        # print(laps.query)

        return laps

    def known_combos_list(self, game=None, track=None, car=None, **kwargs):
        """Generator yielding tuples of known game/car/track combinations.

        Args:
            game (str, optional): Filter by game name. Defaults to None.
            track (str, optional): Filter by track name. Defaults to None.
            car (str, optional): Filter by car name. Defaults to None.
            **kwargs: Additional filter arguments

        Yields:
            tuple: (game_name, car_name, track_name, lap_count)

        Example:
            >>> stats = RacingStats()
            >>> # List all AC combos
            >>> for game, car, track, count in stats.known_combos_list(game="Assetto Corsa"):
            ...     print(f"{car} on {track}: {count} laps")
        """
        laps = self.known_combos(game, track, car, **kwargs)
        for row in laps:
            yield row["track__game__name"], row["car__name"], row["track__name"], row["count"]

    def known_combos(self, game=None, track=None, car=None, **kwargs):
        """Get known combinations of game/car/track with valid lap counts.

        Args:
            game (str, optional): Filter by game name. Defaults to None.
            track (str, optional): Filter by track name. Defaults to None.
            car (str, optional): Filter by car name. Defaults to None.
            **kwargs: Additional filter arguments

        Returns:
            QuerySet: Contains for each combo:
                - track__name: Track name
                - car__name: Car name
                - track__game__name: Game name
                - count: Number of valid laps

        Example:
            >>> stats = RacingStats()
            >>> # Get all GT3 car combos
            >>> gt3_combos = stats.known_combos(car="GT3")
        """
        filter = {}
        if game:
            filter["track__game__name"] = game
        if track:
            filter["track__name"] = track
        if car:
            filter["car__name"] = car

        filter["valid"] = True
        laps = Lap.objects.using(self.using).filter(**filter)
        # group by track and car and game
        laps = laps.values("track__name", "car__name", "track__game__name")
        laps = laps.annotate(count=Count("id"))
        laps = laps.order_by("track__game__name", "car__name", "track__name")
        return laps

    def fast_lap_values(self, game=None, track=None, car=None, **kwargs):
        """Get combinations that have fast lap records.

        Args:
            game (str, optional): Filter by game name. Defaults to None.
            track (str, optional): Filter by track name. Defaults to None.
            car (str, optional): Filter by car name. Defaults to None.
            **kwargs: Additional filter arguments

        Returns:
            QuerySet: Contains for each combo:
                - track__name: Track name
                - car__name: Car name
                - game__name: Game name

        Example:
            >>> stats = RacingStats()
            >>> # Get all fast lap combos for Spa
            >>> spa_records = stats.fast_lap_values(track="Spa")
        """
        filter = {}
        if game:
            filter["game__name"] = game
        if track:
            filter["track__name"] = track
        if car:
            filter["car__name"] = car

        filter["driver"] = None

        laps = FastLap.objects.filter(**filter)
        # group by track and car and game
        laps = laps.values("track__name", "car__name", "game__name")
        # laps = laps.annotate(count=Count("id"))
        laps = laps.order_by("game__name", "car__name", "track__name")
        return laps
        # for row in laps:
        #     yield row["track__game__name"], row["car__name"], row["track__name"], row["count"]

    def fast_laps(self, game=None, track=None, car=None, **kwargs):
        """Get FastLap records for a specific game/track/car combination.

        Args:
            game (str): Game name to filter by
            track (str): Track name to filter by
            car (str): Car name to filter by
            **kwargs: Additional filter arguments

        Returns:
            QuerySet[FastLap]: Matching FastLap records

        Example:
            >>> stats = RacingStats()
            >>> # Get fastest laps for GT3 cars at Spa in AC
            >>> records = stats.fast_laps(game="Assetto Corsa",
            ...                          track="Spa",
            ...                          car="GT3")
        """
        filter = {}
        filter["game__name"] = game
        filter["track__name"] = track
        filter["car__name"] = car

        laps = FastLap.objects.filter(**filter)
        return laps

    def laps(self, game=None, track=None, car=None, driver=None, valid=None, **kwargs):
        """Get lap records filtered by various criteria.

        Args:
            game (str, optional): Filter by game name. Defaults to None.
            track (str, optional): Filter by track name. Defaults to None.
            car (str, optional): Filter by car name. Defaults to None.
            driver (str, optional): Filter by driver name. Defaults to None.
            valid (bool, optional): Filter by lap validity. Defaults to None.
            **kwargs: Additional filter arguments

        Returns:
            QuerySet[Lap]: Matching Lap records, ordered by time

        Example:
            >>> stats = RacingStats()
            >>> # Get all valid laps by a driver
            >>> driver_laps = stats.laps(driver="John", valid=True)
        """
        filter = {}
        if game:
            filter["track__game__name"] = game
        if track:
            filter["track__name"] = track
        if car:
            filter["car__name"] = car

        if valid is not None:
            filter["valid"] = valid

        if driver is not None:
            filter["session__driver__name"] = driver

        laps = Lap.objects.filter(**filter)
        laps = laps.order_by("time")
        # limit to 10
        # laps = laps[:10]
        return laps

        # for lap in laps:
        #     yield lap

    def sessions(self, game=None, track=None, car=None, driver=None, session_ids=None, **kwargs):
        """Get racing sessions filtered by various criteria.

        Args:
            game (str, optional): Filter by game name. Defaults to None.
            track (str, optional): Filter by track name. Defaults to None.
            car (str, optional): Filter by car name. Defaults to None.
            driver (str, optional): Filter by driver name. Defaults to None.
            session_ids (list, optional): Filter by specific session IDs. Defaults to None.
            **kwargs: Additional filter arguments

        Returns:
            QuerySet[Session]: Matching Session records, ordered by start time

        Example:
            >>> stats = RacingStats()
            >>> # Get all sessions for a specific driver
            >>> driver_sessions = stats.sessions(driver="John")
            >>> # Get specific sessions by ID
            >>> specific_sessions = stats.sessions(session_ids=[1,2,3])
        """
        filter = {}
        if game:
            filter["game__name"] = game
        if track:
            filter["track__name"] = track
        if car:
            filter["car__name"] = car

        if driver is not None:
            filter["driver__name"] = driver

        if session_ids is not None:
            filter["session_id__in"] = session_ids

        sessions = Session.objects.using(self.using).filter(**filter).order_by("start")
        return sessions

    def fast_laps_cursor(self, game=None, track=None, car=None, **kwargs):
        """Get lap counts by track and car using direct database cursor.

        Uses raw SQL for potentially better performance when getting aggregate counts.

        Args:
            game (str, optional): Filter by game name. Defaults to None.
            track (str, optional): Filter by track name. Defaults to None.
            car (str, optional): Filter by car name. Defaults to None.
            **kwargs: Additional filter arguments

        Returns:
            list[tuple]: Each tuple contains (count, track_id, car_id)

        Example:
            >>> stats = RacingStats()
            >>> # Get lap counts for all track/car combos in AC
            >>> counts = stats.fast_laps_cursor(game="Assetto Corsa")
        """
        where = []
        filter_game = None
        if game:
            filter_game = Game.objects.get(name=game)
        if track:
            track = Track.objects.get(name=track)
            where.append(f" track_id={track.pk}")
        if car:
            # get the first car with this name
            car = filter_game.cars.filter(name=car).first()
            where.append(f"car_id={car.pk}")

        where_clause = ""
        if where:
            where_clause = "where " + " and ".join(where)

        sql = f"select count(id) as c, track_id, car_id from telemetry_lap {where_clause} group by track_id, car_id"

        with connection.cursor() as cursor:
            cursor.execute(sql)
            rows = cursor.fetchall()

        return rows
