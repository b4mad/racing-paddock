import os

from django.core.files.base import ContentFile
from elevenlabs import save
from elevenlabs.client import ElevenLabs

from telemetry.models import SoundClip


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

    def create_sound_clip(self, text, subtitle=None, voice="Josh", model="eleven_monolingual_v1"):
        """
        Create a SoundClip model instance with generated audio.

        :param text: The text to convert to speech
        :param subtitle: The subtitle for the SoundClip (defaults to the text if not provided)
        :param voice: The voice to use for text-to-speech (default: "Josh")
        :param model: The model to use for text-to-speech (default: "eleven_monolingual_v1")
        :return: The created SoundClip instance
        """
        audio = self.client.generate(text=text, voice=voice, model=model)

        sound_clip = SoundClip(subtitle=subtitle or text, voice=voice, model=model)

        # Save the audio content to the FileField
        sound_clip.audio_file.save(f"{voice}_{text[:30]}.mp3", ContentFile(audio), save=False)
        sound_clip.save()

        return sound_clip
