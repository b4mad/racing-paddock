import logging
import threading

from django.db import IntegrityError

from telemetry.models import Driver, Game, SessionType


class SessionSaver:
    def __init__(self, firehose, save=True):
        self.firehose = firehose
        self.sleep_time = 10
        self.save = save

        self._stop_event = threading.Event()
        self.ready = False

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    # def save_sessions_loop(self):
    #     while True and not self.stopped():
    #         if self.save:
    #             self.save_sessions()
    #         else:
    #             self.fetch_sessions()
    #         self.ready = True
    #         time.sleep(self.sleep_time)

    # def fetch_sessions(self):
    #     session_ids = list(self.firehose.sessions.keys())
    #     for session_id in session_ids:
    #         session = self.firehose.sessions.get(session_id)
    #         if not session.record:
    #             try:
    #                 session.driver = Driver.objects.get(name=session.driver)
    #                 session.game = Game.objects.get(name=session.game_name)
    #                 session.session_type = SessionType.objects.get(type=session.session_type)
    #                 session.car, created = session.game.cars.get_or_create(name=session.car)
    #                 session.car.car_class, created = session.game.car_classes.get_or_create(name=session.car_class)
    #                 session.track, created = session.game.tracks.get_or_create(name=session.track)
    #                 session.record = session.driver.sessions.filter(
    #                     session_id=session.session_id,
    #                     session_type=session.session_type,
    #                     game=session.game,
    #                     car=session.car,
    #                     track=session.track,
    #                 ).first() or Session(
    #                     session_id=session.session_id,
    #                     session_type=session.session_type,
    #                     game=session.game,
    #                     car=session.car,
    #                     track=session.track,
    #                     start=session.start,
    #                     end=session.end,
    #                 )
    #                 logging.debug(f"{session.session_id}: Fetched session {session_id}")
    #             except Exception as e:
    #                 # TODO add error to session to expire
    #                 logging.error(f"{session.session_id}: Error fetching session {session_id}: {e}")
    #                 continue

    def save_sessions(self):
        session_ids = list(self.firehose.sessions.keys())
        for session_id in session_ids:
            session = self.firehose.sessions.get(session_id)

            # save session to database
            # TODO: update session details if they change (e.g. end time)
            if session.ready_to_save():
                try:
                    session.driver, created = Driver.objects.get_or_create(name=session.driver)
                    session.game, created = Game.objects.get_or_create(name=session.game_name)
                    (
                        session.session_type,
                        created,
                    ) = SessionType.objects.get_or_create(type=session.session_type)
                    session.car, created = session.game.cars.get_or_create(name=session.car)
                    session.car.car_class, created = session.game.car_classes.get_or_create(name=session.car_class)
                    session.track, created = session.game.tracks.get_or_create(name=session.track)
                    (
                        session.record,
                        created,
                    ) = session.driver.sessions.get_or_create(session_id=session.session_id, session_type=session.session_type, game=session.game)
                    session.record.car = session.car
                    session.record.track = session.track
                    session.record.start = session.start
                    session.record.save_dirty_fields()
                    logging.debug(f"{session.session_id}: Saving session {session_id}")
                except Exception as e:
                    # TODO add error to session to expire
                    logging.error(f"{session.session_id}: Error saving session {session_id}: {e}")
                    continue

            lap_numbers = list(session.laps.keys())
            for lap_number in lap_numbers:
                lap = session.laps.get(lap_number)
                if session.record and lap.ready_to_save():
                    # check if lap length is within 98% of the track length
                    track = session.track

                    # track_length = track.length
                    # if lap.length < track_length * 0.98:
                    #     lstring = (
                    #         f"{lap.number}: {lap.time}s {lap.length}m"
                    #     )
                    #     logging.info(
                    #         f"{session.session_id}: Discard lap {lstring} - track length {track_length}m"
                    #     )
                    #     # FIXME: this is a hack to prevent the lap from being saved again
                    #     lap.persisted = True
                    #     continue

                    try:
                        lap_record, created = session.record.laps.get_or_create(number=lap.number, car=session.car, track=track)
                        if created:
                            logging.info(f"{session.session_id}: Created lap {lap_record}")
                        else:
                            logging.info(f"{session.session_id}: Found lap {lap_record}")

                        lap_record.start = lap.start
                        lap_record.end = lap.end
                        lap_record.length = lap.length
                        lap_record.valid = lap.valid
                        lap_record.time = lap.time
                        lap_record.completed = lap.finished
                        lap_record.save_dirty_fields()

                        logging.info(f"{session.session_id}: Saving lap {lap_record}")
                        session.record.end = session.end
                        session.record.save_dirty_fields()
                        lap.persist(lap_record)
                    except IntegrityError as e:
                        logging.error(f"{session.session_id}: Error saving lap {lap.number}: {e}")
                        lap.persist()
                    except Exception as e:
                        logging.error(f"{session.session_id}: Error saving lap {lap.number}: {e}")

                    lap_length = int(lap.length)
                    if lap_length > track.length:
                        track.refresh_from_db()
                        if lap_length > track.length:
                            logging.info(f"{session.session_id}: updating {track.name} " + f"length from {track.length} to {lap_length}")
                            track.length = lap_length
                            track.save()

    # def run(self):
    #     self.save_sessions_loop()
