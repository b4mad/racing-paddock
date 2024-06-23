import os
import tempfile

import pytest
from django.test import TransactionTestCase

from telemetry.pitcrew.tts.tts import TTS

api_key = os.environ.get("ELEVENLABS_API_KEY")


@pytest.mark.skipif(not api_key, reason="ELEVENLABS_API_KEY not set in environment")
class TestTts(TransactionTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        if api_key:
            cls.tts_instance = TTS(api_key)

    def test_generate_mp3(self):
        if not api_key:
            pytest.skip("ELEVENLABS_API_KEY not set in environment")

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Prepare test data
            text = "Hello, this is a test."
            output_path = os.path.join(tmp_dir, "test_output.mp3")

            # Call the method
            result = self.tts_instance.generate_mp3(text, str(output_path))

            # Assertions
            assert result == str(output_path)
            assert os.path.exists(output_path)
            assert os.path.getsize(output_path) > 0
