import os
import tempfile
from typing import Iterator

from django.test import TransactionTestCase

from telemetry.pitcrew.tts.tts import TTS

api_key = os.environ.get("ELEVENLABS_API_KEY")


class TestTts(TransactionTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if api_key:
            cls.tts_instance = TTS(api_key)

    def test_generate_mp3(self):
        if not api_key:
            # pytest.skip("ELEVENLABS_API_KEY not set in environment")
            return

        # Prepare test data
        text = "Hello, this is a test."

        # Call the method
        result = self.tts_instance.generate_mp3(text)

        # Assertions
        assert isinstance(result, Iterator)

        if isinstance(result, Iterator):
            result = b"".join(result)

        assert result.startswith(b"\xff\xf3")


