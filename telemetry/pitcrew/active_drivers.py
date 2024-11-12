import logging
from typing import Dict

import django.utils.timezone

from telemetry.models import Driver


class ActiveDrivers:
    def __init__(self, debug=False, inactive_timeout_seconds=600):
        self.debug = debug
        self.inactive_timeout_seconds = inactive_timeout_seconds
        self.topics: Dict[str, dict] = {}  # Maps topic to metadata including driver and last_seen

    def notify(self, topic, payload, now=None):
        now = now or django.utils.timezone.now()

        if topic not in self.topics:
            try:
                (
                    prefix,
                    driver_name,
                    session_id,
                    game,
                    track,
                    car,
                    session_type,
                ) = topic.split("/")
            except ValueError:
                # ignore invalid topic
                return

            try:
                db_driver, created = Driver.objects.get_or_create(name=driver_name)
                self.topics[topic] = {"driver": db_driver, "last_seen": now, "session_id": session_id, "game": game, "track": track, "car": car, "car_class": payload.get("CarClass", ""), "session_type": session_type}
                logging.debug(f"New topic: {topic}")
            except Exception as e:
                logging.error(f"Error creating driver {driver_name} - {e}")
                return
            # clear inactive topics every time a new topic is added
            self.clear_sessions(now)
        else:
            self.topics[topic]["last_seen"] = now

    def clear_sessions(self, now):
        """Clear inactive topics.

        Removes any topic that hasn't received updates for longer than inactive_timeout_seconds

        Args:
            now (datetime): The current datetime
        """
        delete_topics = []
        for topic, metadata in self.topics.items():
            if (now - metadata["last_seen"]).seconds > self.inactive_timeout_seconds:
                delete_topics.append(topic)

        for topic in delete_topics:
            del self.topics[topic]
            logging.debug(f"{topic}\n\t deleting inactive topic")

    def drivers(self):
        """Return set of all active drivers"""
        return {metadata["driver"] for metadata in self.topics.values()}
