import datetime
import logging

from django.core.management.base import BaseCommand
from django.db.models import F, Prefetch, Q

from telemetry.influx import Influx
from telemetry.models import FastLap, Lap, Session
from telemetry.pitcrew.segment import Segment


class Command(BaseCommand):
    help = "clean stuff"

    def add_arguments(self, parser):
        # add argument for list of lap ids as integers separated by commas
        parser.add_argument(
            "-d",
            "--delete-influx",
            help="Delete old telemetry data from InfluxDB within the specified date range",
            action="store_true",
        )

        parser.add_argument(
            "--delete-sessions",
            help="Delete all sessions from the database (use with caution)",
            action="store_true",
        )

        parser.add_argument(
            "-s",
            "--start",
            help="Start date for deletion in YYYY-MM-DD format",
            type=str,
            default=None,
        )
        parser.add_argument(
            "-e",
            "--end",
            help="End date for deletion in YYYY-MM-DD format",
            type=str,
            default=None,
        )

        parser.add_argument(
            "--fix-rbr-sessions",
            help="Fix Richard Burns Rally sessions with incorrect end times",
            action="store_true",
        )

        parser.add_argument(
            "--fix-fastlaps",
            help="Clean up orphaned FastLap records that have no associated Laps",
            action="store_true",
        )

        parser.add_argument(
            "--fix-fastlaps-data",
            help="Validate and clean up FastLap data structures and segments",
            action="store_true",
        )

        parser.add_argument(
            "--dump-session",
            help="Debug utility to dump session telemetry data",
            action="store_true",
        )

        parser.add_argument(
            "--fix-cars",
            help="Identify and resolve duplicate car names within the same game",
            action="store_true",
        )

        parser.add_argument(
            "--fix-session-car-track",
            help="Repair sessions with missing car/track info by using data from their first lap",
            action="store_true",
        )

    def handle(self, *args, **options):
        """
        Main command handler that routes to specific maintenance tasks based on command line arguments.
        """
        if options["delete_influx"]:
            self.influx = Influx()
            self.delete_influx(options["start"], options["end"])
        elif options["delete_sessions"]:
            self.delete_sessions(options["start"], options["end"])
        elif options["fix_rbr_sessions"]:
            self.fix_rbr_sessions()
        elif options["fix_fastlaps_data"]:
            self.fix_fastlaps_data()
        elif options["fix_fastlaps"]:
            self.fix_fastlaps()
        elif options["dump_session"]:
            self.dump_session()
        elif options["fix_cars"]:
            self.fix_cars()
        elif options["fix_session_car_track"]:
            self.fix_session_car_track()

    def fix_cars(self):
        from django.db.models import Count

        from telemetry.models import Car, Game, Session

        # Check for duplicate cars
        duplicate_cars = Car.objects.values("name", "game").annotate(name_count=Count("name")).filter(name_count__gt=1)

        if duplicate_cars:
            print("Found cars with duplicate names within the same game:")
            for car_data in duplicate_cars:
                game = Game.objects.get(id=car_data["game"])
                cars = Car.objects.filter(name=car_data["name"], game=game)
                print(f"Game: {game.name}, Car: {car_data['name']}")

                cars_with_sessions = []
                for car in cars:
                    session_count = Session.objects.filter(car=car).count()
                    print(f"  - Car ID: {car.id}, Sessions: {session_count}")
                    if session_count == 0:
                        print(f"    Deleting car with ID: {car.id} (no sessions)")
                        car.delete()
                    else:
                        cars_with_sessions.append((car, session_count))

                if len(cars_with_sessions) > 1:
                    # Sort cars by session count in descending order
                    cars_with_sessions.sort(key=lambda x: x[1], reverse=True)
                    # Keep the car with the most sessions, delete others
                    for car, count in cars_with_sessions[1:]:
                        print(f"    Deleting car with ID: {car.id} (fewer sessions: {count})")
                        car.delete()
        else:
            print("No cars with duplicate names within the same game found.")

        # # Check for cars with no sessions
        # cars_without_sessions = Car.objects.annotate(session_count=Count('sessions')).filter(session_count=0)
        # if cars_without_sessions:
        #     print("\nFound cars with no associated sessions:")
        #     for car in cars_without_sessions:
        #         print(f"Deleting car: Game: {car.game.name}, Car: {car.name}, ID: {car.id}")
        #         car.delete()
        # else:
        #     print("\nNo cars without associated sessions found.")

    def fix_session_car_track(self):
        """
        Find sessions missing car or track and set them from the first lap's data.
        Process in batches to handle large numbers of sessions efficiently.
        """

        batch_size = 1000
        sessions = Session.objects.filter(Q(car__isnull=True) | Q(track__isnull=True)).prefetch_related(Prefetch("laps", queryset=Lap.objects.order_by("number")))

        total = sessions.count()
        print(f"Found {total} sessions with missing car or track")

        processed = 0
        for session in sessions.iterator(chunk_size=batch_size):
            first_lap = session.laps.first()
            if first_lap:
                updated = False
                if not session.car and first_lap.car:
                    session.car = first_lap.car
                    updated = True
                if not session.track and first_lap.track:
                    session.track = first_lap.track
                    updated = True

                if updated:
                    session.save()
                    processed += 1
                    if processed % 100 == 0:
                        print(f"Processed {processed}/{total} sessions")

        print(f"Updated {processed} sessions with car/track data from their laps")

    def dump_session(self):
        """
        Debug utility to dump session telemetry data.
        Currently disabled - needs implementation with proper Telemetry model.
        """
        # TODO: Revisit this method. The Telemetry model is not defined.
        # Uncomment and fix the code below once the Telemetry model is available.
        # session_id = "1689266594"
        # query_set = Telemetry.timescale.time_bucket("time", "1 hour").values("time", "session_id_telemetry")
        # print(query_set)
        pass

    def fix_fastlaps(self):
        """
        Deletes fastlaps that have no associated laps.

        This method retrieves all primary keys for fastlaps and all ids for laps.
        It then removes the lap ids from the fastlap ids and deletes the fastlaps
        that have no associated laps.

        Returns:
            None
        """
        # get all primary keys for fastlaps
        fastlap_ids = list(FastLap.objects.all().values_list("id", flat=True))
        print(f"found {len(fastlap_ids)} fastlaps")

        # get all ids for laps
        lap_fast_laps_ids = list(Lap.objects.all().values_list("fast_lap", flat=True))

        # remove all lap_fast_laps_ids from fastlap_ids
        rm_fastlap_ids = list(set(fastlap_ids) - set(lap_fast_laps_ids))

        print(f"deleting {len(rm_fastlap_ids)} fastlaps")

        # delete all fastlaps that have no laps
        FastLap.objects.filter(id__in=rm_fastlap_ids).delete()

    def fix_fastlaps_data(self):
        """
        Checks the data attribute of each fastlap. The data attribute should be a dict with a key called 'segment'
        that contains a list of instances of type `Segment`.

        Returns:
            None
        """

        batch_size = 10
        fastlaps = FastLap.objects.all().iterator(chunk_size=batch_size)
        for fastlap in fastlaps:
            data = fastlap.data
            if data is None:
                continue

            if not isinstance(data, dict):
                logging.warning(f"FastLap {fastlap.id} has invalid data format. dict")
                fastlap.delete()
                continue

            segments = data.get("segments", [])
            if not isinstance(segments, list):
                logging.warning(f"FastLap {fastlap.id} has invalid segments format. segments")
                fastlap.delete()
                continue

            for segment in segments:
                if not isinstance(segment, Segment):
                    logging.warning(f"FastLap {fastlap.id} has invalid segment instance. class segment")
                    fastlap.delete()
                    break

    def fix_rbr_sessions(self):
        """Fix Richard Burns Rally laps where end time equals start time."""
        batch_size = 100

        # Get all RBR laps where end equals start
        laps = Lap.objects.filter(session__game__name="Richard Burns Rally", end=F("start"))

        total_laps = laps.count()
        logging.info(f"Found {total_laps} RBR laps to fix")

        processed = 0
        for lap in laps.iterator(chunk_size=batch_size):
            # Set end time to start + lap time + 60 second buffer
            lap.end = lap.start + datetime.timedelta(seconds=lap.time + 60)
            lap.number = 0
            lap.save()

            processed += 1
            if processed % batch_size == 0:
                logging.info(f"Processed {processed}/{total_laps} laps")

        logging.info(f"Completed fixing {processed} RBR laps")

    def delete_sessions(self, start, end):
        """
        Delete all sessions from the database.

        Args:
            start: Start date (unused)
            end: End date (unused)
        """
        Session.objects.all().delete()

    def delete_influx(self, start, end):
        """
        Delete telemetry data from InfluxDB within a specified date range.

        Args:
            start (str): Start date in YYYY-MM-DD format. Defaults to 30 days ago if not specified.
            end (str): End date in YYYY-MM-DD format. Defaults to start + 1 day if not specified.
        """
        if start:
            start = datetime.datetime.strptime(start, "%Y-%m-%d")
        else:
            start = datetime.datetime.now() - datetime.timedelta(days=30)

        if end:
            end = datetime.datetime.strptime(end, "%Y-%m-%d")
        else:
            end = start + datetime.timedelta(days=1)

        # delete in on hour chunks
        while start < end:
            end_delta = start + datetime.timedelta(hours=4)
            logging.debug(f"Deleting data from {start} to {end_delta}")
            now = datetime.datetime.now()
            self.influx.delete_data(start=start, end=end_delta)
            # log how long it took
            logging.debug(f"... {datetime.datetime.now() - now}")
            start = end_delta
