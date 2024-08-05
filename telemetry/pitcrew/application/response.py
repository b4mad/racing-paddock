import logging

from django.conf import settings

from telemetry.pitcrew.tts import TTS


class Response:
    MESSAGE = "message"
    PRIORITY = "priority"
    AT = "distance"
    MAX_DISTANCE = "max_distance"

    # response has a timeout of 10 seconds
    # i.e. it will be discarded by CrewChief if it is not played within 10 seconds
    # so we need to make sure that we send the response at least 10 seconds before the event

    def __init__(self, message, priority=5, max_distance=None, at=None, immediate=False):
        self.message = message
        self.at = at
        self.priority = priority
        self.max_distance = max_distance
        self.immediate = immediate

        self._sent = False
        self._discarded = False

    def __str__(self) -> str:
        return f"At {self.at}: {self.message}"

    def copy(self):
        return Response(self.message, priority=self.priority, max_distance=self.max_distance, at=self.at)

    def send(self):
        self._sent = True

    def discard(self):
        self._discarded = True

    # One commonly used average reading speed for English is around 150 words per minute
    # when spoken. This translates to 2.5 words per second. So you can estimate the time
    # it takes to read a phrase out loud by counting the words and dividing by 2.5.
    # or check https://github.com/alanhamlett/readtime
    def read_time(self):
        words = len(self.message.split(" "))
        # r_time = words / 1.5
        r_time = words / 2.2
        # delta_add = 2.0
        delta_add = 0.2
        # self.log_debug(f"read_time: '{msg}' ({words}) {r_time:.1f} seconds + {delta_add:.1f} seconds")
        # return words * 0.8  # avg ms per word
        # return words / 2.5  # avg ms per word
        return r_time + delta_add

    def response(self):
        response_dict = {self.MESSAGE: self.message, self.PRIORITY: self.priority}

        if self.at is not None:
            response_dict[self.AT] = self.at

        if self.max_distance is not None:
            response_dict[self.MAX_DISTANCE] = self.max_distance

        if self.immediate:
            response_dict["immediate"] = True

        return response_dict


class ResponseInstant(Response):
    def __init__(self, message, **kwargs):
        super().__init__(message, **kwargs)


class ResponseTts(Response):
    def __init__(self, message, **kwargs):
        super().__init__(message, **kwargs)
        self.sound_clip = None

    def create_sound_clip(self):
        try:
            tts = TTS()
            voice = "smOo3538WLyYkRnbULCJ"
            model = "eleven_turbo_v2_5"
            self.sound_clip = tts.create_sound_clip(self.message, voice=voice, model=model)
            # domain = Site.objects.get_current().domain
            # if development protocol is http
            # protocol = "https://"
            if settings.DEBUG:
                protocol = "http://"
                domain = "localhost:8000"
            else:
                protocol = "https://"
                domain = "b4mad.racing"
            self.message = f"{protocol}{domain}{self.sound_clip.audio_file.url}"
        except ValueError as e:
            logging.error(f"Error creating sound clip: {e}")

    def response(self):
        if not self.sound_clip:
            self.create_sound_clip()
        return super().response()
