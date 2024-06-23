import os

from elevenlabs import save
from elevenlabs.client import ElevenLabs


class TTS:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.environ.get("ELEVENLABS_API_KEY")
        if not self.api_key:
            raise ValueError("ElevenLabs API key is required. Set it in the environment or pass it to the constructor.")

        self.client = ElevenLabs(api_key=self.api_key)

    def generate_mp3(self, text, output_path):
        """
        Generate an MP3 file from the given text using ElevenLabs API.

        :param text: The text to convert to speech
        :param output_path: The path where the MP3 file should be saved
        :return: The path to the generated MP3 file
        """
        audio = self.client.generate(text=text, voice="Josh", model="eleven_monolingual_v1")

        save(audio, output_path)
        return output_path
