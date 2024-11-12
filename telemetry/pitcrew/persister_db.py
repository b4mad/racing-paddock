from typing import Dict, Optional

import django.utils.timezone
from loguru import logger

from telemetry.models import CarClass, Driver, Game, Session, SessionType


class PersisterDb:
    def __init__(self, driver: Driver, debug=False):
        self.debug = debug
        self.driver = driver
        self.sessions: Dict[str, Optional[Session]] = {}
        self.clear_ticks = 0
        self.clear_interval = 60 * 60 * 5  # ticks. telemetry is sent at 60hz, so 60*60*5 = 5 minutes
        self.save_ticks = 0
        self.save_interval = 60 * 60 * 1  # ticks. telemetry is sent at 60hz, so 60*60*1 = 1 minute
        # self.save_interval = 60

    def notify(self, topic, payload, now=None):
        now = now or django.utils.timezone.now()
        if topic not in self.sessions:
            logger.debug(f"New session: {topic}")
            try:
                (
                    prefix,
                    driver,
                    session_id,
                    game,
                    track,
                    car,
                    session_type,
                ) = topic.split("/")
            except ValueError:
                # ignore invalid session
                return

            if session_type == "NewSession":
                logger.info(f"Ignoring NewSession for {topic}")
                return

            car_class = payload.get("CarClass", "")
            session = self.get_session(
                session_id=session_id,
                game=game,
                track=track,
                car=car,
                session_type=session_type,
                car_class=car_class,
            )
            self.sessions[topic] = session
            if session:
                session.prepare_for_analysis()

        session = self.sessions[topic]
        if session:
            session.signal(payload, now)
        self.save_sessions(now)

    def get_session(self, session_id, game, track, car, session_type, car_class) -> Optional[Session]:
        try:
            r_game = Game.objects.get(name=game)
            if car_class:
                r_car_class, car_class_created = CarClass.objects.get_or_create(name=car_class, game=r_game)
                if car_class_created:
                    logger.debug(f"Created new car class: {r_car_class}")
                r_car, car_created = r_game.cars.get_or_create(name=car, car_class=r_car_class)
            else:
                r_car, car_created = r_game.cars.get_or_create(name=car)

            if car_created:
                logger.debug(f"Created new car: {r_car}")

            r_track, track_created = r_game.tracks.get_or_create(name=track)
            if track_created:
                logger.debug(f"Created new track: {r_track}")
                # Set a default track length if it's a new track
                r_track.length = 10  # Default length in meters
                r_track.save()
            r_session_type, _created = SessionType.objects.get_or_create(type=session_type)
            session, session_created = Session.objects.get_or_create(
                session_id=session_id,
                driver=self.driver,
                game=r_game,
                track=r_track,
                car=r_car,
                session_type=r_session_type,
            )
            if session_created:
                logger.debug(f"Created new session: {session}")
            else:
                logger.debug(f"Found existing session: {session}")
        except Exception as e:
            logger.error(f"Error creating session: {e}")
            logger.error(f"session_id: {session_id}, game: {game}, track: {track}, car: {car}, session_type: {session_type}, car_class: {car_class}")
            return None

        return session

    def on_stop(self):
        logger.debug("Persister: on_stop")
        self.save_sessions(django.utils.timezone.now(), force=True)

    def save_sessions(self, now, force=False):
        if not force:
            if self.save_ticks < self.save_interval:
                self.save_ticks += 1
                return
            self.save_ticks = 0

        for topic, session in self.sessions.items():
            if session:
                session.save_analysis()
        self.clear_sessions(now)

    def clear_sessions(self, now):
        """Clear inactive telemetry sessions.

        Loops through all sessions and deletes:
        - Any session inactive for more than 10 minutes
        - Any lap marked for deletion

        Args:
            now (datetime): The current datetime

        """

        max_session_age = 60 * 60  # 1 hour
        delete_sessions = []
        for topic, session in self.sessions.items():
            if session:
                if (now - session.end).seconds > max_session_age:
                    delete_sessions.append(topic)

            # # Delete any lap marked for deletion
            # for i in range(len(session.laps) - 1, -1, -1):
            #     lap = session.laps[i]
            #     if lap.get("delete", False):
            #         logging.debug(f"{topic}\n\t deleting lap {lap['number']}")
            #         del session.laps[i]

        if len(delete_sessions) > 0:
            logger.debug(f"Inactive sessions: {len(delete_sessions)}")
            logger.debug(f"Active sessions: {len(self.sessions) - len(delete_sessions)}")

        # Delete all inactive sessions
        for topic in delete_sessions:
            session = self.sessions.pop(topic, None)
            if session:
                session.save_analysis()
            logger.debug(f"Deleting inactive session: {session}")
